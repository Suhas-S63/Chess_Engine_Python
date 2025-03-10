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
DEPTH = 4

# Killer moves: two slots per depth (adjust MAX_DEPTH as needed)
MAX_DEPTH = 10
killer_moves = [[None, None] for _ in range(MAX_DEPTH)]

# History table: tracks successful moves (move identifier -> score)
history_table = {}

# defining piece influence value/weights for improved evaluation
KnightScores = np.array([
    [0, 10, 20, 20, 20, 20, 10, 0],
    [10, 30, 50, 55, 55, 50, 30, 10],
    [20, 55, 60, 65, 65, 60, 55, 20],
    [20, 50, 65, 70, 70, 65, 50, 20],
    [20, 55, 65, 70, 70, 65, 55, 20],
    [20, 50, 60, 65, 65, 60, 50, 20],
    [10, 30, 50, 50, 50, 50, 30, 10],
    [0, 10, 20, 20, 20, 20, 10, 0]
])

BishopScores = np.array([
    [0, 10, 10, 10, 10, 10, 10, 0],
    [10, 20, 20, 20, 20, 20, 20, 10],
    [10, 20, 25, 30, 30, 25, 20, 10],
    [10, 25, 25, 30, 30, 25, 25, 10],
    [10, 20, 30, 30, 30, 30, 20, 10],
    [10, 30, 30, 30, 30, 30, 30, 10],
    [10, 25, 20, 20, 20, 20, 25, 10],
    [0, 10, 10, 10, 10, 10, 10, 0]
])

RookScores = np.array([
    [5, 5, 5, 5, 5, 5, 5, 5],
    [10, 15, 15, 15, 15, 15, 15, 10],
    [0, 5, 5, 5, 5, 5, 5, 0],
    [0, 5, 5, 5, 5, 5, 5, 0],
    [0, 5, 5, 5, 5, 5, 5, 0],
    [0, 5, 5, 5, 5, 5, 5, 0],
    [0, 5, 5, 5, 5, 5, 5, 0],
    [5, 5, 5, 10, 10, 5, 5, 5]
])

QueenScores = np.array([
    [0, 10, 10, 15, 15, 10, 10, 0],
    [10, 20, 20, 20, 20, 20, 20, 10],
    [10, 20, 25, 25, 25, 25, 20, 10],
    [15, 20, 25, 25, 25, 25, 20, 15],
    [20, 20, 25, 25, 25, 25, 20, 15],
    [10, 25, 25, 25, 25, 25, 20, 10],
    [10, 20, 25, 20, 20, 20, 20, 10],
    [0, 10, 10, 15, 15, 10, 10, 0]
])

KingScores = np.array([
    [20, 10, 10, 0, 0, 10, 10, 20],
    [20, 10, 10, 0, 0, 10, 10, 20],
    [20, 10, 10, 0, 0, 10, 10, 20],
    [30, 20, 20, 10, 10, 20, 20, 30],
    [40, 30, 30, 30, 30, 30, 30, 40],
    [70, 70, 50, 50, 50, 50, 70, 70],
    [70, 80, 60, 50, 50, 60, 80, 70],
    [70, 80, 60, 50, 50, 60, 80, 70]
])

WhitePawnScores = np.array([
    [20, 20, 20, 20, 20, 20, 20, 20],
    [70, 70, 70, 70, 70, 70, 70, 70],
    [30, 30, 40, 50, 50, 40, 30, 30],
    [25, 25, 30, 45, 45, 30, 25, 25],
    [20, 20, 20, 40, 40, 20, 20, 20],
    [25, 15, 10, 20, 20, 10, 15, 25],
    [25, 30, 30, 0, 0, 30, 30, 25],
    [20, 20, 20, 20, 20, 20, 20, 20]
])


BlackPawnScores = np.array([
    [20, 20, 20, 20, 20, 20, 20, 20],
    [25, 30, 30, 0, 0, 30, 30, 25],
    [25, 15, 10, 20, 20, 10, 15, 25],
    [20, 20, 20, 40, 40, 20, 20, 20],
    [25, 25, 30, 45, 45, 30, 25, 25],
    [30, 30, 40, 50, 50, 40, 30, 30],
    [70, 70, 70, 70, 70, 70, 70, 70],
    [20, 20, 20, 20, 20, 20, 20, 20]
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
def NegaMax_AB_Pruning(game_state, validMoves, depth, alpha, beta, turn_multiplier): # alpha -> Upper bound value, beta -> Lower bound value
    global next_move, counter
    counter += 1 # Counting the number of position states visited
    if depth == 0:
        return turn_multiplier * BoardScore(game_state)

    # Move ordering - has to be implemented
    ordered_moves = Move_Ordering(validMoves, depth)
    max_score = -CHECKMATE
    for move in ordered_moves:
        game_state.MakeMove(move)
        next_moves = game_state.GetValidMoves()
        score = -NegaMax_AB_Pruning(game_state, next_moves, depth - 1, -beta, -alpha,  -turn_multiplier) # switching alpha and beta for the opponent moves
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
                print(f"Move: {move}, Score: {score}")
        game_state.UndoMove()
        # Pruning bad game state trees which don't much of an advantage
        if max_score > alpha:
            alpha = max_score # set the max_score to alpha for the best game state tree
        if alpha >= beta:
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
            next_move = chess_pack_move_to_Move_class(selected_move, game_state)
            print(f"Book move: {board.san(selected_move)}")
        else:
            # No book entries found, proceed with NegaMax with Alpha-Beta pruning
            NegaMax_AB_Pruning(game_state, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if game_state.whiteToMove else -1)
            print(f"Position's seen by NegaMax AB Pruning Algorithm: {counter}")
    except KeyError:
        # Position not in book, proceeding with search
        NegaMax_AB_Pruning(game_state, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if game_state.whiteToMove else -1)
        # in the above function call -CHECKMATE is the alpha value and CHECKMATE is the beta value
        print(f"Position's seen by NegaMax AB Pruning Algorithm: {counter}")
    return_queue.put(next_move)

############################################################################################################

'''
Move Ordering function to improve move searching and evaluation for Engine Optimization
'''
def Move_Ordering(validMoves, depth):
    def move_score(move):
        score = 0

        # Captures using MVV-LVA heuristic (Most Valuable Victim - Least Valuable Attacker)
        if move.IsCaptured:
            victim_value = pieceScore[move.pieceCaptured[1]] # e.g., 'P' from 'wP'
            attacker_value = pieceScore[move.pieceMoved[1]]
            score += 10000 + (victim_value * 10 - attacker_value)

        # Promotions: score based on promoted piece
        if move.PawnPromotion:
            promoted_piece = move.Pawn_Promoted_to
            if promoted_piece == 'Q':
                score += 20000
            elif promoted_piece == 'R':
                score += 15000
            elif promoted_piece == 'B':
                score += 10000
            elif promoted_piece == 'N':
                score += 8000

        # Killer Moves: boost if move is a killer at this depth
        if 0 <= depth < len(killer_moves) and move in killer_moves[depth]:
            score += 30000 # Killer move bonus

        # Checks: encouraging forcing moves
        if move.in_check:
            score += 5000

        # History heuristics: add score is available and stored
        move_id = (move.startRow, move.startCol, move.endRow, move.endCol)
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
    Ordered_Moves = Move_Ordering(capture_promotion_moves, depth = 2) # Setting depth for quiescence search

    for move in Ordered_Moves:
        # Delta Pruning: skip moves that can't improve alpha value
        if move.IsCaptured:
            gain = pieceScore[move.pieceCaptured[1]]
        elif move.PawnPromotion:
            gain = pieceScore[move.Pawn_Promoted_to] - pieceScore['P']
        else:
            gain = 0

        if stand_pat + gain < alpha:
            continue # Skipping the move

        game_state.MakeMove(move)
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
    elif game_state.Stalemate:
        return STALEMATE # neither side wins

    # Based on pure captures and board material
    score = 0
    for row in range(len(game_state.board_array)):
        for col in range(len(game_state.board_array[row])):
            square = game_state.board_array[row, col]
            if square != "--":
                # Scoring positionally based on  piece (Need to change)
                if square[1] == "P": # For pawns
                    piece_position_score = Piece_Influence_Scores[square][row, col]
                else: # For other pieces
                    piece_position_score = Piece_Influence_Scores[square[1]][row, col]

                if square[0] == 'w':
                    score += pieceScore[square[1]] + piece_position_score
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piece_position_score
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
def chess_pack_move_to_Move_class(chess_move, game_state):
    start_square = chess_move.from_square
    end_square = chess_move.to_square
    # Convert to your row indexing (0=rank8, 7=rank1)
    start_row = 7 - (start_square // 8)
    start_col = start_square % 8
    end_row = 7 - (end_square // 8)
    end_col = end_square % 8
    promotion = chess.piece_symbol(chess_move.promotion).upper() if chess_move.promotion else None
    return Move((start_row, start_col), (end_row, end_col), game_state.board_array, Promotion_Piece=promotion)
