import random
import numpy as np

next_move = None
counter = 0

# Piece Scores as per Chess rules
pieceScore = {"K": 200, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4

# defining piece influence value/weights for improved evaluation
KnightScores = np.array([
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]
            ])

BishopScores = np.array([
                [4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]
            ])

RookScores = np.array([
              [4, 3, 4, 4, 4, 4, 3, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 4, 4, 4, 4, 3, 4]
            ])

QueenScores = np.array([
               [1, 1, 1, 3, 1, 1, 1, 1],
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]
            ])

KingScores = np.array([
               []
            ])

WhitePawnScores = np.array([
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]
                ])


BlackPawnScores = np.array([
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]
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
    max_score = -CHECKMATE
    for move in validMoves:
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
    random.shuffle(validMoves)
    NegaMax_AB_Pruning(game_state, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if game_state.whiteToMove else -1)
    # in the above function call -CHECKMATE is the alpha value and CHECKMATE is the beta value
    print(f"Position's seen by NegaMax AB Pruning Algorithm: {counter}")
    return_queue.put(next_move)

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
                piece_position_score = 0  # Initialize score for positioning of piece
                # Scoring positionally based on  piece (Need to change)
                if square[1] != "K":
                    if square[1] == "P": # For pawns
                        piece_position_score = Piece_Influence_Scores[square][row, col]
                    else: # For other pieces
                        piece_position_score = Piece_Influence_Scores[square[1]][row, col]

                if square[0] == 'w':
                    score += pieceScore[square[1]] + piece_position_score
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piece_position_score

    return score


'''
Score the board based on material
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

    # we will improve this material score by having positional advantages as well
    # will be done later (positional understanding converts to better AI

    return score