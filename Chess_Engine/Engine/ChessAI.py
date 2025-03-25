import random
import numpy as np
import chess, chess.polyglot
from ChessEngine import Move
import os

# Global variable to hold the book reader
_book = None
_book_path = os.path.join(os.path.dirname(__file__), "komodo.bin")

next_move = None
counter = 0


# Piece Scores as per Chess rules
pieceScore = {"K": 200, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 5
Q_SEARCH_DEPTH = 2

# Killer moves: two slots per depth (adjust MAX_DEPTH as needed)
killer_moves = [[] for _ in range(DEPTH + 1)]

# History table: tracks successful moves (move identifier -> score)
history_table = {}

# Counter moves: to keep track of moves that gave strong responses to the opponent's last move
counter_moves = {} # Key: (opponent_move_id), Value: best_response_move

# defining piece influence value/weights for improved evaluation
KnightScores = np.array([
    [3, 10, 20, 20, 20, 20, 10, 3],
    [10, 30, 40, 40, 40, 40, 30, 10],
    [20, 40, 50, 55, 55, 50, 40, 20],
    [20, 45, 55, 65, 65, 55, 45, 20],
    [20, 45, 55, 65, 65, 55, 45, 20],
    [20, 40, 50, 55, 55, 50, 40, 20],
    [10, 30, 40, 40, 40, 40, 30, 10],
    [3, 10, 20, 20, 20, 20, 10, 3]
])

BishopScores = np.array([
    [10, 10, 10, 10, 10, 10, 10, 10],
    [10, 20, 20, 20, 20, 20, 20, 10],
    [10, 25, 30, 30, 30, 30, 25, 10],
    [10, 25, 35, 40, 40, 35, 25, 10],
    [10, 25, 40, 40, 40, 40, 25, 10],
    [10, 30, 30, 30, 30, 30, 30, 10],
    [10, 20, 25, 20, 20, 25, 20, 10],
    [10, 10, 10, 10, 10, 10, 10, 10]
])

RookScores = np.array([
    [10, 10, 10, 15, 15, 10, 10, 10],
    [20, 20, 20, 20, 20, 20, 20, 20],
    [5, 7, 10, 15, 15, 10, 7, 5],
    [5, 7, 10, 10, 10, 10, 7, 5],
    [5, 7, 10, 10, 10, 10, 7, 5],
    [5, 7, 10, 15, 15, 10, 7, 5],
    [20, 20, 20, 20, 20, 20, 20, 20],
    [10, 10, 10, 15, 15, 10, 10, 10]
])

QueenScores = np.array([
    [5, 10, 10, 15, 15, 10, 10, 5],
    [10, 20, 25, 25, 25, 25, 20, 10],
    [10, 25, 30, 35, 35, 30, 25, 10],
    [15, 25, 35, 40, 40, 35, 25, 15],
    [15, 25, 35, 40, 40, 35, 25, 15],
    [10, 25, 30, 35, 35, 30, 25, 10],
    [10, 20, 25, 25, 25, 25, 20, 10],
    [5, 10, 10, 15, 15, 10, 10, 5]
])

KingScores = np.array([
    [20, 30, 10, 5, 5, 10, 30, 20],
    [10, 20, 5, 2, 2, 5, 20, 10],
    [5, 10, 2, 2, 2, 2, 10, 5],
    [1, 5, 1, 10, 10, 1, 5, 0],
    [1, 5, 1, 10, 10, 1, 5, 0],
    [5, 10, 2, 2, 2, 2, 10, 5],
    [10, 20, 5, 2, 2, 5, 20, 10],
    [20, 30, 10, 5, 5, 10, 30, 20]
])

WhitePawnScores = np.array([
    [50, 50, 50, 50, 50, 50, 50, 50],# promotion incentive
    [40, 40, 40, 40, 40, 40, 40, 40],
    [30, 30, 35, 35, 35, 35, 30, 30],
    [20, 20, 25, 30, 30, 25, 20, 20],
    [10, 10, 15, 25, 25, 15, 10, 10],
    [5, 5, 10, 15, 15, 10, 5, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],         # starting position
    [0, 0, 0, 0, 0, 0, 0, 0]
])


BlackPawnScores = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],        # starting position
    [5, 5, 10, 15, 15, 10, 5, 5],
    [10, 10, 15, 25, 25, 15, 10, 10],
    [20, 20, 25, 30, 30, 25, 20, 20],
    [30, 30, 35, 35, 35, 35, 30, 30],
    [40, 40, 40, 40, 40, 40, 40, 40],
    [50, 50, 50, 50, 50, 50, 50, 50]  # promotion incentive
])

Piece_Influence_Scores = {"N" : KnightScores, "B": BishopScores, "R": RookScores, "Q": QueenScores,
                          "K": KingScores, "wP": WhitePawnScores, "bP": BlackPawnScores }
'''
Choosing a random move from the validMoves list
'''
def RandomChessMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

############################################################################################################

'''
Finding Best move on material on board alone (Primitive and extremely simple MinMax implementation)
'''
def FindBestMove(game_state, validMoves):
    # Basic Algorithm with depth of 2
    turn_multiplier = -1 if game_state.whiteToMove else 1
    opponent_min_max_score = CHECKMATE
    best_player_move = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        game_state.MakeMove(playerMove)
        opponent_moves = game_state.GetValidMoves()
        if game_state.Stalemate:
            opponent_max_score = STALEMATE
        elif game_state.Checkmate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponent_move in opponent_moves:
                game_state.MakeMove(opponent_move)
                game_state.GetValidMoves()
                if game_state.Checkmate:
                    score = CHECKMATE
                elif game_state.Stalemate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * scoreMaterial(game_state.board_array)
                if score > opponent_max_score:
                    opponent_max_score = score
                game_state.UndoMove()
        if  opponent_max_score < opponent_min_max_score :
            opponent_min_max_score = opponent_max_score
            best_player_move = playerMove
        game_state.UndoMove()
    return best_player_move

############################################################################################################

'''
Recursive MinMax implementation for Chess AI
'''
def MinMax(game_state, validMoves, depth, whiteToMove):
    global next_move, counter
    counter += 1 # Counting the number of position states visited
    if depth == 0:
        return BoardScore(game_state.board_array)

    if whiteToMove:
        max_score = -CHECKMATE
        for move in validMoves:
            game_state.MakeMove(move)
            next_moves = game_state.GetValidMoves()
            score = MinMax(game_state, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
                    print(f"Move: {move}, Score: {score}")
            game_state.UndoMove()
        return max_score
    else:
        min_score = CHECKMATE
        for move in validMoves:
            game_state.MakeMove(move)
            next_moves = game_state.GetValidMoves()
            score = MinMax(game_state, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
                    print(f"Move: {move}, Score: {score}")
            game_state.UndoMove()
        return min_score

'''
Helper method for MinMax implementation for Chess AI
its purpose is to call the initial recursive call to FindMove_MinMax() and return results
'''
def FindBestMove_MinMax(game_state, validMoves):
    global next_move, counter
    next_move = None # default
    counter = 0
    random.shuffle(validMoves)
    MinMax(game_state, validMoves, DEPTH, game_state.whiteToMove)
    print(f"Position's seen by Recursive MinMax Algorithm: {counter}")
    return next_move



############################################################################################################

'''
NegaMax implementation of AI (Improved version of MinMax Algorithm)
'''
def NegaMax(game_state, validMoves, depth, turn_multiplier):
    global next_move, counter
    counter += 1 # Counting the number of position states visited
    if depth == 0:
        return turn_multiplier * BoardScore(game_state)

    max_score = -CHECKMATE
    for move in validMoves:
        game_state.MakeMove(move)
        next_moves = game_state.GetValidMoves()
        score = -NegaMax(game_state, next_moves, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
                print(f"Move: {move}, Score: {score}")
        game_state.UndoMove()
    return max_score

'''
Helper method for Negamax implementation for Chess AI
its purpose is to call the initial recursive call to FindMove_NegaMax() and return results
'''
def FindBestMove_NegaMax(game_state, validMoves):
    global next_move, counter
    next_move = None # default
    counter = 0
    random.shuffle(validMoves)
    NegaMax(game_state, validMoves, DEPTH, 1 if game_state.whiteToMove else -1)
    print(f"Position's seen by NegaMax Algorithm: {counter}")
    return next_move

############################################################################################################
'''
NegaMax with Alpha-Beta pruning implementation 
'''
def NegaMax_AB_Pruning(game_state, validMoves, depth, alpha, beta, turn_multiplier, previous_move=None): # alpha -> Upper bound value, beta -> Lower bound value
    global next_move, counter
    counter += 1 # Counting the number of position states visited
    if depth == 0:
        return Quiescence_Search(game_state, alpha, beta, turn_multiplier, Q_SEARCH_DEPTH)

    # Move ordering
    ordered_moves = Move_Ordering(game_state, validMoves, depth)
    max_score = -CHECKMATE
    # starting the search process
    for move in ordered_moves:
        game_state.MakeMove(move)
        next_moves = game_state.GetValidMoves()
        if game_state.Checkmate: # checking for checkmates during searching
            game_state.UndoMove()
            score = CHECKMATE - (DEPTH - depth) # adjusting score to checkmate exponentially more value based on how quickly deliverable
            if depth == DEPTH: # Root Node
                print(f"Move: {move}, Score: {score} (Checkmate)")
            return score # Return immediately to prioritize checkmate
        # calling decision algorithm recursively
        score = -NegaMax_AB_Pruning(game_state, next_moves, depth - 1, -beta, -alpha,  -turn_multiplier) # switching alpha and beta for the opponent moves
        game_state.UndoMove()

        if score > max_score:
            max_score = score
            if depth == DEPTH: # Root Node
                next_move = move
                print(f"Move: {move}, Score: {score}")

        # Pruning bad game state trees which don't much of an advantage
        if max_score > alpha:
            alpha = max_score # set the max_score to alpha for the best game state tree

        # Beta Cutoff: updating heuristics here
        if alpha >= beta:
            # updating history table for the move causing cutoff
            promoted_to = move.Pawn_Promoted_to if move.PawnPromotion else None
            move_id = (move.startRow, move.startCol, move.endRow, move.endCol, promoted_to)
            if move_id not in history_table:
                history_table[move_id] = 0
            history_table[move_id] += min(history_table[move_id] + depth ** 2, 30)  # Cap at 30
            # as the goal is to keep quite moves scores below 60(the score of checks)

            # Updating counter moves if there was a previous move
            if previous_move is not None:
                opponent_move_id = (previous_move.startRow, previous_move.startCol,
                                    previous_move.endRow, previous_move.endCol)
                counter_moves[opponent_move_id] = move

            # Updating killer moves
            if not move.IsCaptured: # Quiet moves only
                if move not in killer_moves[depth]:
                    if len(killer_moves[depth]) < 2:
                        killer_moves[depth].append(move)
                    else:
                        killer_moves[depth][1] = killer_moves[depth][0] # Shifting older killer move
                        killer_moves[depth][0] = move # New killer in first slot
            break # prune the rest of the game state tree for the current move
    return max_score

'''
Helper method for NegaMax with Alpha-Beta pruning implementation  for Chess AI
its purpose is to call the initial recursive call to FindMove_NegaMax_AB_Pruning() and return results
'''
def FindBestMove_NegaMax_AB_Pruning(game_state, validMoves, return_queue):
    global next_move, counter
    next_move = None # default
    counter = 0

    # Get the book reader and load the database(reuses it if already opened)
    book = get_book()

    # converting GameState to chess.Board()
    fen = game_state.game_state_to_fen()
    board = chess.Board(fen)

    # checking the opening book
    try:
        entries = list(book.find_all(board))
        if entries:
                # selecting a move weighted by frequency
                # moves = [entry.move for entry in entries] # selecting a move
                # weights = [entry.weight for entry in entries] # selecting weights of the move
                # selected_move = random.choices(moves, weights=weights, k=1)[0] # for random book moves by selecting a move by weighted frequency
            selected_move = max(entries, key = lambda e: e.weight).move # For deterministic moves
            next_move = chess_pack_move_to_Move_class(selected_move, game_state, board)
            print(f"Book move: {board.san(selected_move)}")
        else:
            # No book entries found, proceed with NegaMax with Alpha-Beta pruning
            NegaMax_AB_Pruning(game_state, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if game_state.whiteToMove else -1,previous_move=None)
            print(f"Position's seen by NegaMax AB Pruning Algorithm: {counter}")
    except KeyError:
        # Position not in book, proceeding with search
        NegaMax_AB_Pruning(game_state, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if game_state.whiteToMove else -1,previous_move=None)
        # in the above function call -CHECKMATE is the alpha value and CHECKMATE is the beta value
        print(f"Position's seen by NegaMax AB Pruning Algorithm: {counter}")
    return_queue.put(next_move)

############################################################################################################

'''
Move Ordering function to improve move searching and evaluation for Engine Optimization
'''
def Move_Ordering(game_state, validMoves, depth, previous_move=None):
    def move_score(move):
        score = 0

        # Captures using MVV-LVA heuristic (Most Valuable Victim - Least Valuable Attacker)
        if move.IsCaptured:
            victim_value = pieceScore[move.pieceCaptured[1]] # e.g., 'P' from 'wP'
            attacker_value = pieceScore[move.pieceMoved[1]]
            score += 100 + (victim_value * 10 - attacker_value)

        # Bonus for advancing to promotion rank
        if (move.pieceMoved[1] == 'P' and
                ((move.endRow == 6 and game_state.whiteToMove) or (move.endRow == 1 and not game_state.whiteToMove))):
            score += 90

        # Promotions: score based on promoted piece
        if move.PawnPromotion:
            promoted_piece = move.Pawn_Promoted_to
            if promoted_piece == 'Q':
                score += 99
            elif promoted_piece == 'R':
                score += 95
            elif promoted_piece == 'B':
                score += 93
            elif promoted_piece == 'N':
                score += 91

        # Killer Moves: boost if move is a killer at this depth
        if 0 <= depth < len(killer_moves) and move in killer_moves[depth]:
            score += 80 # Killer move bonus

        # Counter Moves: boost if move counters the opponent's last move
        if previous_move is not None:
            opponent_move_id = (previous_move.startRow, previous_move.startCol,
                                    previous_move.endRow, previous_move.endCol)
            counter_move = counter_moves.get(opponent_move_id)
            if counter_move is not None and move == counter_move:
                score += 70

        # Checks: encouraging forcing moves
        if move.in_check:
            score += 60

        # Ordering quiet moves to prioritize moves that improve the piece's position marginally
        if not move.IsCaptured and not move.PawnPromotion:
            start_score = Piece_Influence_Scores[move.pieceMoved[1] if move.pieceMoved[1] != "P" else move.pieceMoved][move.startRow][move.startCol]
            end_score = Piece_Influence_Scores[move.pieceMoved[1] if move.pieceMoved[1] != "P" else move.pieceMoved][move.endRow][move.endCol]
            score += (end_score - start_score) # Adjusted scaling

        # History heuristics: add score is available and stored
        promoted_to = move.Pawn_Promoted_to if move.PawnPromotion else None
        move_id = (move.startRow, move.startCol, move.endRow, move.endCol, promoted_to)
        if move_id in history_table:
            score += history_table[move_id]

        return score

    # Sorting moves in descending order (highest score first)
    return sorted(validMoves, key=move_score, reverse=True)

'''
Quiescence Search implementation to improve performance
Def: Quiescence search extends the evaluation beyond the main search depth in dynamic positions 
(e.g., during capture sequences or checks) to avoid the “horizon effect”—where a critical move is missed just past the depth limit.
It ensures the evaluation is stable by continuing until a “quiet” position is reached.
'''
def Quiescence_Search(game_state, alpha, beta, turn_multiplier, max_depth=2):
    if max_depth == 0:
        return turn_multiplier * BoardScore(game_state)

    # Stand Pat: evaluate the position without making a move
    stand_pat = turn_multiplier * BoardScore(game_state)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    # Only consider capture and promotion moves (can be improved, but we are just keeping these considerations for now)
    capture_promotion_moves = [move for move in game_state.GetValidMoves() if move.IsCaptured or move.PawnPromotion]
    Ordered_Moves = Move_Ordering(game_state, capture_promotion_moves, depth = 2) # Setting depth for quiescence search

    for move in Ordered_Moves:
        # Delta Pruning: skip moves that can't improve alpha value
        if move.IsCaptured:
            gain = pieceScore[move.pieceCaptured[1]]
        elif move.PawnPromotion:
            gain = pieceScore[move.Pawn_Promoted_to] - pieceScore['P']
        else:
            gain = 0

        if stand_pat + gain < alpha and not move.in_check: # Skipping non-check moves that don't improve alpha
            continue

        game_state.MakeMove(move)
        if game_state.Checkmate: # checkmate found
            game_state.UndoMove()
            return turn_multiplier * CHECKMATE if game_state.whiteToMove else -turn_multiplier * CHECKMATE
        score = -Quiescence_Search(game_state, -beta, -alpha, -turn_multiplier, max_depth - 1)
        game_state.UndoMove()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha

############################################################################################################

'''
Board Evaluation Function (Positive Score -> Good for White, Negative Score -> Good for Black)
'''
def BoardScore(game_state):
    if game_state.Checkmate:
        if game_state.whiteToMove:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE # white wins
    elif game_state.Stalemate: # Penalising stalemate positions
        material_score = 0
        for row in range(len(game_state.board_array)):
            for col in range(len(game_state.board_array[row])):
                square = game_state.board_array[row, col]
                if square != '--':
                    piece_value = pieceScore[square[1]]
                    material_score += piece_value if square[0] == 'w' else -piece_value
        # Penalising stalemate if the side to move has material advantage
        if game_state.whiteToMove and material_score > 35:
            return -50 # discouraging stalemate for White
        elif not game_state.whiteToMove and material_score < -35:
            return 50 # discouraging stalemate for Black
        return STALEMATE # neither side wins

    # Based on pure captures and board material
    score = 0
    for row in range(len(game_state.board_array)):
        for col in range(len(game_state.board_array[row])):
            square = game_state.board_array[row, col]
            if square != "--":
                # Scoring positionally based on  piece
                if square[1] == "P": # For pawns
                    piece_position_score = Piece_Influence_Scores[square][row, col]
                else: # For other pieces
                    piece_position_score = Piece_Influence_Scores[square[1]][row, col]

                if square[0] == 'w':
                    score += pieceScore[square[1]] + piece_position_score
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piece_position_score

    # Additional advanced evaluation function for evaluating the piece (only to be used if host machine is powerful to run
    # as it will be computationally heavier than the simple evaluation
    score += Piece_Coordination_Evaluation(game_state)
    return score

############################################################################################################

'''
Score the board based on material (Dummy Function not used mainly but only in other primitive decision functions)
'''
def scoreMaterial(board):
    # Current logic based on pure captures and board material
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]

    # we will improve this material score by having positional advantages as well(Done in BoardScore)
    # will be done later (positional understanding converts to better AI (Done in BoardScore)

    return score

############################################################################################################

def get_book():
    global _book
    if _book is None:  # Only opens the book the first time
        if not os.path.exists(_book_path):
            raise FileNotFoundError(f"Opening book not found at: {_book_path}")
        _book = chess.polyglot.open_reader(_book_path)
    return _book

'''
The opening book returns moves in python-chess’s format,
which we need to convert to our Move class.
'''
def chess_pack_move_to_Move_class(chess_move, game_state, board):
    start_square = chess_move.from_square
    end_square = chess_move.to_square
    # Converting to our implementation of  row indexing (row 0 = rank 8, row 7 =rank 1)
    start_row = 7 - (start_square // 8)
    start_col = start_square % 8
    end_row = 7 - (end_square // 8)
    end_col = end_square % 8
    promotion = chess.piece_symbol(chess_move.promotion).upper() if chess_move.promotion else None
    is_castle = board.is_castling(chess_move)
    is_en_passant = board.is_en_passant(chess_move)
    return Move((start_row, start_col), (end_row, end_col), game_state.board_array,EnPassant= is_en_passant, IsCastleMove= is_castle, Promotion_Piece=promotion)

############################################################################################################
'''
Function which checks multiple board position concepts and piece coordination concepts for advanced evaluation 
which will be used by BoardScore() function to evaluate the board and provide the correct move to be done
'''
def Piece_Coordination_Evaluation(game_state):
    """
    This function evaluates the co-ordination concepts of the pieces mentioned below.
    """
    piece_coord_score = 0

    # Now we evaluate the various positions on the board by calling functions of each coordination and evaluation concept
    piece_coord_score += Pawn_Structure_Evaluation(game_state)
    piece_coord_score += King_Safety_Check(game_state)
    piece_coord_score += Bishop_Pair_Bonus(game_state)
    piece_coord_score += Rooks_On_Open_File(game_state)
    piece_coord_score += Connected_Rooks(game_state)
    piece_coord_score += Knight_Outposts(game_state)
    piece_coord_score += Queen_And_Minor_Piece_Co_ordination(game_state)
    piece_coord_score += Pawn_Support(game_state)

    return piece_coord_score

############################################################################################################
'''
Board piece position checking functions contributing for board evaluation for stronger moves
'''
def Pawn_Structure_Evaluation(game_state):
    # Add bonuses or penalties for:
    # -> Passed Pawns: Pawns with no enemy pawns ahead or on adjacent files(Bonus).
    # -> Doubled Pawns: Two pawns of the same color on one file(penalty).
    # -> Isolated Pawns: Pawns with no friendly pawns on adjacent files (penalty).
    pawn_files = {"w": [0] * 8, "b": [0] * 8}
    score_adjust = 0
    for row in range(8):
        for col in range(8):
            square = game_state.board_array[row, col]
            if square != "--" and square[1] == "P":
                color = square[0]
                pawn_files[color][col] += 1
                # passed pawn checking
                is_passed = True
                for r in range(row + 1 if color == "b" else 0, row if color == "b" else 8):
                    if game_state.board_array[r, col] != "--" or \
                       (col > 0 and game_state.board_array[r, col-1] != "--") or \
                       (col < 7 and game_state.board_array[r, col+1] != "--"):
                        is_passed = False
                        break
                if is_passed:
                    score_adjust += 50 if color == "w" else -50  # Bonus for passed pawn
    # Check doubled pawns
    for col in range(8):
        if pawn_files["w"][col] > 1:
            score_adjust -= 20 * (pawn_files["w"][col] - 1)
        if pawn_files["b"][col] > 1:
            score_adjust += 20 * (pawn_files["b"][col] - 1)
    return score_adjust


def King_Safety_Check(game_state):
    #  A king under check is a major disadvantage therefore,
    # we check for pawn shields( pawns in front of the king) and penalise the absense based on the number of pawns
    safety_score = 0
    for color, row in [("w", 7), ("b", 0)]:  # kings on back rank
        king_col = None
        for col in range(8):
            if game_state.board_array[row, col] == color + "K":
                king_col = col
                break
        if king_col is not None:
            shield = sum(1 for c in range(max(0, king_col-1), min(8, king_col+2))
                        if game_state.board_array[row-1 if color == "w" else row+1, c] == color + "P")
            penalty = (3 - shield) * 10  # Max 3 pawns, 10 points per missing pawn
            safety_score += -penalty if color == "w" else penalty
    return safety_score

############################################################################################################
'''
Piece Coordination Functions for improved evaluation (check for co-ordination like Bishop pairs, Rooks on open files, 
Connected Rooks, Knight Outposts, Queen and Minor Piece Co-ordination Functions, Pawn Support
'''
def Bishop_Pair_Bonus(game_state):
    """
    Bonus is awarded for having two bishops (the "bishop pair"), which is a strong advantage in open positions.
    """
    # Bishop pair bonus
    coord_score = 0
    bishops = {"w": 0, "b": 0}
    for row in range(8):
        for col in range(8):
            square = game_state.board_array[row, col]
            if square != "--" and square[1] == "B":
                bishops[square[0]] += 1
    if bishops["w"] == 2:
        coord_score += 50
    if bishops["b"] == 2:
        coord_score -= 50

    return coord_score

def Rooks_On_Open_File(game_state):
    """
    Rooks are most effective when placed on open files (files with no pawns), as they can control the file and potentially invade the opponent’s position.
    -> First, we check for pawn in each file (columns)
    -> if a file has no pawns, we award a bonus for any rook present on the file
    """
    open_file_score = 0
    for col in range(8):
        has_pawn = False
        for row in range(8):
            if game_state.board_array[row, col][1] == "P": # checking for any pawn in the present rook file
                has_pawn = True
                break
        if not has_pawn:
            for row in range(8):
                piece = game_state.board_array[row, col]
                if piece == "wR":
                    open_file_score += 10 # Bonus for white rook
                if piece == "bR":
                    open_file_score -= 10 # Penalty for black rook
    return open_file_score

def Connected_Rooks(game_state):
    """
    Connected rooks (two rooks of the same color on the same rank or file with no pieces between them)
    can work together to dominate a line.
    -> First, we find all the rooks of each color
    -> Then, we check the pairs to see if they are on the same rank or file and unobstructed
    """
    connected_score = 0
    for color in ["w", "b"]:
        rooks = []
        for row in range(8):
            for col in range(8):
                if game_state.board_array[row, col] == color + "R":
                    rooks.append((row, col))

        for i in range(len(rooks)):
            for j in range(i + 1, len(rooks)):
                row1, col1 = rooks[i]
                row2, col2 = rooks[j]
                if row1 == row2: # Same Rank(row)
                    # checking the rooks by going through the columns
                    if all(game_state.board_array[row1, k] == '--' for k in range(min(col1, col2) + 1, max(col1, col2))):
                        connected_score += 15 if color == 'w' else -15
                elif col1 == col2: #Same File(col)
                    # checking the rooks by going through the rows
                    if all(game_state.board_array[k, col1] == '--' for k in range(min(row1, row2) + 1, max(row1, row2))):
                        connected_score += 15 if color == 'w' else -15
    return connected_score

def Knight_Outposts(game_state):
    """
    Knight outposts are squares that are controlled by a knight and a pawn. They are powerful on outposts as they can't
    be captured by the opponent's pawns especially in advanced central positions.
    -> First, we find all the knights positions
    -> Then, we check if it's safe from pawn attacks by opponent
    """
    outpost_score = 0
    for row in range(8):
        for col in range(8):
            piece = game_state.board_array[row, col]
            if piece == "wN" and 2 <= row <= 4: # White knight on ranks 4 to 6
                if not Can_Be_Attacked_By_Pawn(game_state, row, col, 'b'):
                    outpost_score += 10
            elif piece == "bN" and 3 <= row <= 5: # Black rook on ranks 3 to 5
                if not Can_Be_Attacked_By_Pawn(game_state, row, col, 'w'):
                    outpost_score -= 10
    return outpost_score

def Can_Be_Attacked_By_Pawn(game_state, row, col, attacker_color):
    """
    returns boolean if a pawn is able to attack (helper function for Knight Outposts function)
    """
    if attacker_color == "w" and row > 0:
        if col > 0 and game_state.board_array[row - 1, col - 1] == "wP":
            return True
        if col < 7 and game_state.board_array[row - 1, col + 1] == "wP":
            return True
    elif attacker_color == "b" and row < 7:
        if col > 0 and game_state.board_array[row + 1, col - 1] == "bP":
            return True
        if col < 7 and game_state.board_array[row + 1, col + 1] == "bP":
            return True
    return False

def Queen_And_Minor_Piece_Co_ordination(game_state):
    """
    Queen and minor piece co-ordination is a powerful evaluation metric for positions evaluation.
    The queen often pairs effectively with a knight or bishop to control key lines (ranks, files, or diagonals).
    -> First, we find the queen and the minor pieces(knights and bishops)
    -> Then, a bonus is awarded if they are on same rank, file or diagonal
    """
    coord_score = 0
    for color in ['w', 'b']:
        queen_position = None
        minor_pieces = []
        for row in range(8):
            for col in range(8):
                piece = game_state.board_array[row, col]
                if piece == color + "Q":
                    queen_position = (row, col)
                elif piece[1] in [color + 'N', color + 'B']:
                    minor_pieces.append((row, col))

        if queen_position is not None:
            queen_row, queen_col = queen_position
            for minor_piece_row, minor_piece_col in minor_pieces:
                # checking if the queen and the current minor piece is on same rank, same file or same diagonal
                if queen_row == minor_piece_row or abs(queen_row - minor_piece_row) == abs(queen_col - minor_piece_col):
                    coord_score += 5 if color == 'w' else -5
    return coord_score

def Pawn_Support(game_state):
    """
    Pieces defended by pawns are more stable and hard to attack
    for each non-pawn piece, we check if a friendly pawn defends it
    """
    support_score = 0
    for row in range(8):
        for col in range(8):
            piece = game_state.board_array[row, col]
            if piece != '--' and piece[1] != 'P':
                color = piece[0]
                if Is_Defended_By_Pawn(game_state, row, col, color): # checks if a friendly pawn defends an ally piece
                    support_score += 5 if color == 'w' else -5
    return support_score

def Is_Defended_By_Pawn(game_state, row, col, color):
    """
    returns boolean if a piece is defended by a pawn (helper function for Pawn Support function)
    """
    if color == "w" and row < 7:
        if col > 0 and game_state.board_array[row + 1, col - 1] == "wP":
            return True
        if col < 7 and game_state.board_array[row + 1, col + 1] == "wP":
            return True
    elif color == "b" and row > 0:
        if col > 0 and game_state.board_array[row - 1, col - 1] == "bP":
            return True
        if col < 7 and game_state.board_array[row - 1, col + 1] == "bP":
            return True
    return False