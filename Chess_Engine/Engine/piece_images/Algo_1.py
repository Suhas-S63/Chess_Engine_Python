def MakeMove(self, move):
    self.board[move.startRow][move.startCol] = "--"
    self.board[move.endRow][move.endCol] = move.pieceMoved
    self.moveLog.append(move)  # keeping logs/track of piece move
    # update King's location is moved
    if move.pieceMoved == "wK":
        self.WhiteKingLocation = (move.endRow, move.endCol)
    elif move.pieceMoved == "bK":
        self.BlackKingLocation = (move.endRow, move.endCol)

    self.whiteToMove = not self.whiteToMove  # swap players


'''
Undo the last move
'''


def UndoMove(self):
    if len(self.moveLog) != 0:  # checking so that there exists a move to undo
        move = self.moveLog.pop()  # remove the last move from the logs
        self.board[move.startRow][move.startCol] = move.pieceMoved
        self.board[move.endRow][move.endCol] = move.pieceCaptured
        # update King's location if move undone
        if move.pieceMoved == "wK":
            self.WhiteKingLocation = (move.startRow, move.startCol)
        elif move.pieceMoved == "bK":
            self.BlackKingLocation = (move.startRow, move.startCol)
        self.whiteToMove = not self.whiteToMove  # switch turns back


def RedoMove(self):
    pass


'''
Get all moves considering checks of the pieces
'''


def GetValidMoves(self):
    # 1. Generating all possible moves
    moves = self.GetAllPossibleMoves()
    # 2. for each move, we make a move
    for i in range(len(moves) - 1, -1, -1):  # going through the list backwards
        self.MakeMove(moves[i])
        # now we generate all the moves of the opponent and check if the King is under check by the opponent
        self.whiteToMove = not self.whiteToMove  # switch turns back as MakeMove() switches the turn to opposite color
        if self.inCheck():
            moves.remove(moves[i])  # if the King is under attack that's an invalid move for the same piece
        self.whiteToMove = not self.whiteToMove
        self.UndoMove()  # undo the move as we don't need to check for the same piece again
    if len(moves) == 0:  # indicates that there are no valid moves in the moves list to check if there checkmate or stalemate
        if self.inCheck():
            self.Checkmate = True
        else:
            self.Stalemate = True
    else:
        self.Checkmate = False
        self.Stalemate = False
    return moves


'''
Check function that checks if the king is in check with enemy pieces
'''


def inCheck(self):
    if self.whiteToMove:
        return self.SquareUnderAttack(self.WhiteKingLocation[0],
                                      self.WhiteKingLocation[1])  # checking if white square under attack
    else:
        return self.SquareUnderAttack(self.BlackKingLocation[0],
                                      self.BlackKingLocation[1])  # checking if black square under attack


'''
Function determines if the enemy can attack the square
'''


def SquareUnderAttack(self, row, col):
    self.whiteToMove = not self.whiteToMove
    Opponent_Moves = self.GetAllPossibleMoves()
    self.whiteToMove = not self.whiteToMove  # switch turns back
    for move in Opponent_Moves:  # get all possible moves
        if move.endRow == row and move.endCol == col:  # Square under attack
            return True
    return False