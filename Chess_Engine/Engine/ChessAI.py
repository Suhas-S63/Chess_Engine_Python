import random

next_move = None
counter = 0

# Piece Scores as per Chess rules
pieceScore = {"K": 200, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

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
                    score = -turn_multiplier * scoreMaterial(game_state.board)
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
def FindMove_MinMax(game_state, validMoves, depth, whiteToMove):
    global next_move, counter
    counter += 1 # Counting the number of position states visited
    if depth == 0:
        return scoreMaterial(game_state.board)

    if whiteToMove:
        max_score = -CHECKMATE
        for move in validMoves:
            game_state.MakeMove(move)
            next_moves = game_state.GetValidMoves()
            score = FindMove_MinMax(game_state, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            game_state.UndoMove()
        return max_score
    else:
        min_score = CHECKMATE
        for move in validMoves:
            game_state.MakeMove(move)
            next_moves = game_state.GetValidMoves()
            score = FindMove_MinMax(game_state, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
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
    FindMove_MinMax(game_state, validMoves, DEPTH, game_state.whiteToMove)
    print(f"Position's seen by Recursive MinMax Algorithm: {counter}")
    return next_move



############################################################################################################

'''
NegaMax implementation of AI (Improved version of MinMax Algorithm)
'''
def FindMove_NegaMax(game_state, validMoves, depth, turn_multiplier):
    global next_move, counter
    counter += 1 # Counting the number of position states visited
    if depth == 0:
        return turn_multiplier * BoardScore(game_state)

    max_score = -CHECKMATE
    for move in validMoves:
        game_state.MakeMove(move)
        next_moves = game_state.GetValidMoves()
        score = -FindMove_NegaMax(game_state, next_moves, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
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
    FindMove_NegaMax(game_state, validMoves, DEPTH, 1 if game_state.whiteToMove else -1)
    print(f"Position's seen by NegaMax Algorithm: {counter}")
    return next_move

############################################################################################################
'''
NegaMax with Alpha-Beta pruning implementation 
'''
def FindMove_NegaMax_AB_Pruning(game_state, validMoves, depth, alpha, beta, turn_multiplier): # alpha -> Upper bound value, beta -> Lower bound value
    global next_move, counter
    counter += 1 # Counting the number of position states visited
    if depth == 0:
        return turn_multiplier * BoardScore(game_state)

    # Move ordering - has to be implemented
    max_score = -CHECKMATE
    for move in validMoves:
        game_state.MakeMove(move)
        next_moves = game_state.GetValidMoves()
        score = -FindMove_NegaMax_AB_Pruning(game_state, next_moves, depth - 1, -beta, -alpha,  -turn_multiplier) # switching alpha and beta for the opponent moves
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
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
def FindBestMove_NegaMax_AB_Pruning(game_state, validMoves):
    global next_move, counter
    next_move = None # default
    counter = 0
    random.shuffle(validMoves)
    FindMove_NegaMax_AB_Pruning(game_state, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if game_state.whiteToMove else -1)
    # in the above function call -CHECKMATE is the alpha value and CHECKMATE is the beta value
    print(f"Position's seen by NegaMax AB Pruning Algorithm: {counter}")
    return next_move

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
    for row in game_state.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]

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