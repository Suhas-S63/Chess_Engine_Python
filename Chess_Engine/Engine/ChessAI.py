import random

def RandomChessMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]