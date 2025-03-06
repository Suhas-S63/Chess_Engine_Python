""" The GameState() class is responsible for storing and managing all the information of the current state of the game
. Also determines the valid move sets in the current state and the move logs"""
import numpy as np

class GameState:
    def __init__(self):
        # board is the 8x8 2d list containing the pieces and represented by 2 characters
        # first character represents the "Color" of the piece(White or Black)
        # second character represents the "Type" of the piece(King, Queen, Rook)
        # "--" represents empty board space
        self.board_array = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],  # Columns are called "Files"
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],  # Rows are called "Ranks"
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ], dtype=object)
        # Test Board
        # self.board = [
        #     ["--", "--", "--", "--", "bK", "--", "--", "--"],  # Columns are called "Files"
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],  # Rows are called "Ranks"
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "wK", "--", "--", "--"]
        # ]
        # mapping the piece type letter to the function having the logic of that piece
        self.PieceMoveFunctions = {'P': self.GetPawnMoves, "R": self.GetRookMoves, "N": self.GetKnightMoves,
                                   "B": self.GetBishopMoves, "Q": self.GetQueenMoves, "K": self.GetKingMoves}
        self.whiteToMove = True
        self.white_pieces = 16  # Total white pieces at the start
        self.black_pieces = 16  # Total black pieces at the start
        self.moveLog = []
        self.WhiteKingLocation = (7, 4)
        self.BlackKingLocation = (0, 4)
        self.Checkmate = False
        self.Stalemate = False
        self.inCheckFlag = False
        self.pins = []
        self.checks = []
        self.EnPassantPossible = ()  # coordinates of square where enpassant is possible
        self.EnPassantPossibleLog = [self.EnPassantPossible] # Logs to keep track of the Enpassant Capture moves
        self.halfmoveclock = 0 # tracking moves since last capture or pawn move
        self.CurrentCastlingRights = CastleRights(True, True, True, True)
        self.CastleRightsLog = [CastleRights(self.CurrentCastlingRights.WhiteKSide, self.CurrentCastlingRights.BlackKSide,
                                             self.CurrentCastlingRights.WhiteQSide, self.CurrentCastlingRights.BlackQSide)]
        # tracking positions of the game with a hashing like ID
        self.position_history = {} # dictionary to track position occurrences
        self.position_key = self.GetPositionKey() # initial position
        self.position_history[self.position_key] = 1

    '''
    Function to create a unique string for the current board state (can be improved with Zobrist Hashing for Transposition Tables)
    Might be done in the future
    '''
    def GetPositionKey(self):
        board_string = str(self.board_array) # Board Configuration
        castling_string = str(self.CurrentCastlingRights) # Castling availability
        enpassant_string = str(self.EnPassantPossible) # En Passant target square
        side_to_move = "w" if self.whiteToMove else "b"
        return board_string + castling_string + enpassant_string + side_to_move

    '''
    The MakeMove() method is used to update the game state when a move is made.
    '''
    def MakeMove(self, move):
        self.board_array[move.startRow, move.startCol] = "--"
        self.board_array[move.endRow, move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # keeping logs/track of piece move
        # updating piece count if piece is captured
        if move.pieceCaptured != '--' or move.pieceMoved[1] == "P":
            # update half move clock and pieces captured count
            self.halfmoveclock = 0 # Reset on capture or pawn move
            if move.pieceCaptured[0] == 'w':
                self.white_pieces -= 1
            else:
                self.black_pieces -= 1
        else:
            self.halfmoveclock += 1 # increment otherwise
        self.whiteToMove = not self.whiteToMove  # swap players

        # update King's location is moved
        if move.pieceMoved == "wK":
            self.WhiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.BlackKingLocation = (move.endRow, move.endCol)

        # Pawn promotion logic
        if move.PawnPromotion:
            # print(f'Pawn promotion enabled')  # UI will be done
            # PromotedPiece = input("Promote to Queen(Q), Rook(R), Bishop(B), or Knight(N): ")  # UI will be done
            # self.board[move.endRow][move.endCol] = move.pieceMoved[0] + PromotedPiece
            self.board_array[move.endRow, move.endCol] = move.pieceMoved[0] + move.Pawn_Promoted_to
        else:
            self.board_array[move.endRow, move.endCol] = move.pieceMoved

        # if enpassant move, must update the board to capture the piece i.e. pawn
        if move.EnPassant:
            self.board_array[move.startRow, move.endCol] = "--"  # capturing the pawn

        # if pawn moves twice next move can capture enpassant
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2: # only on 2 square pawn advances
            self.EnPassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.EnPassantPossible = ()
        # appending enpassant move to logs
        self.EnPassantPossibleLog.append(self.EnPassantPossible)

        # castle moves
        if move.IsCastleMove:
            if move.endCol - move.startCol == 2: # King Side Castling
                self.board_array[move.endRow, move.endCol - 1] = self.board_array[move.endRow, move.endCol + 1] # Moves the Rook
                self.board_array[move.endRow, move.endCol + 1] = "--" # Remove the Rook
            else: # Queen Side Castling
                self.board_array[move.endRow, move.endCol + 1] = self.board_array[move.endRow, move.endCol - 2] # Move rook to new square
                self.board_array[move.endRow, move.endCol - 2] = '--' # Remove the rook

        # checking if the current move offers a check to opponent king (purely for chess notation purposes)
        # we check this explicitly in ChessMain function for proper game handling
        if self.inCheck():
            move.in_check = True
            # checking for checkmate (no legal moves for enemy)
            if not self.GetValidMoves(): # no valid moves present
                move.is_checkmate = True
        else:
            move.in_check = False
            move.is_checkmate = False

        # update castling rights - happens when it's a rook or king move
        self.UpdateCastleRights(move)
        self.CastleRightsLog.append(CastleRights(self.CurrentCastlingRights.WhiteKSide, self.CurrentCastlingRights.BlackKSide,
                                                 self.CurrentCastlingRights.WhiteQSide, self.CurrentCastlingRights.BlackQSide))

        # After the move is made, we update the position history
        self.position_key = self.GetPositionKey()
        self.position_history[self.position_key] = self.position_history.get(self.position_key, 0) + 1

    '''
    Undo the last move
    '''
    def UndoMove(self):
        if len(self.moveLog) != 0:  # checking so that there exists a move to undo
            move = self.moveLog.pop()  # remove the last move from the logs
            self.board_array[move.startRow, move.startCol] = move.pieceMoved
            self.board_array[move.endRow, move.endCol] = move.pieceCaptured
            # updating piece count when move is undone
            if move.pieceCaptured != '--':
                if move.pieceCaptured[0] == 'w':
                    self.white_pieces += 1
                else:
                    self.black_pieces += 1
            self.whiteToMove = not self.whiteToMove  # switch turns back

            # update King's location if move undone
            if move.pieceMoved == "wK":
                self.WhiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.BlackKingLocation = (move.startRow, move.startCol)

            # Logic for undoing enpassant is different
            if move.EnPassant:
                self.board_array[move.endRow, move.endCol] = "--"  # remove the pawn that was added in the wrong square
                self.board_array[move.startRow, move.endCol] = move.pieceCaptured  # puts the captured pawn back on the board
            self.EnPassantPossibleLog.pop()
            self.EnPassantPossible = self.EnPassantPossibleLog[-1] # set the EnPassantPossible to the last one in the list of EnPassantPossible

            # Undo a 2 square advance should make EnPassantPossible=() again
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.EnPassantPossible = ()

            # undoing Castling Rights
            self.CastleRightsLog.pop() # get rid of the new castle rights from the move we are undoing
            self.CurrentCastlingRights = self.CastleRightsLog[-1] # set the current castle rights to the last one in the list of Castle Rights

            # Undo Castle Move
            if move.IsCastleMove:
                if move.endCol - move.startCol == 2: # King Side Castle
                    self.board_array[move.endRow, move.endCol + 1] = self.board_array[move.endRow, move.endCol -1]
                    self.board_array[move.endRow, move.endCol - 1] = "--"
                else: # Queen Side Castle
                    self.board_array[move.endRow, move.endCol - 2] = self.board_array[move.endRow, move.endCol + 1]
                    self.board_array[move.endRow, move.endCol + 1] = '--'

            #Flag reset(possible use by AI)
            self.Checkmate = False
            self.Stalemate = False

    def RedoMove(self):
        pass


    '''
    Get all moves considering checks of the pieces
    '''

    def GetValidMoves(self):
        # Temporary store of castling rights
        Temp_Castle_Rights = CastleRights(self.CurrentCastlingRights.WhiteKSide, self.CurrentCastlingRights.BlackKSide,
                                          self.CurrentCastlingRights.WhiteQSide, self.CurrentCastlingRights.BlackQSide)

        # Algorithm to check for validMoves after generating all the possible moves
        moves = []
        self.inCheckFlag, self.pins, self.checks = self.CheckForPinsAndChecks()
        if self.whiteToMove:  # white piece
            kingRow = self.WhiteKingLocation[0]
            kingCol = self.WhiteKingLocation[1]
        else:
            kingRow = self.BlackKingLocation[0]
            kingCol = self.BlackKingLocation[1]
        if self.inCheckFlag:
            if len(self.checks) == 1:  # only 1 check, block check with piece or move kind
                moves = self.GetAllPossibleMoves()
                # to block check, we must put a piece on a square in front of the king and the enemy piece
                check = self.checks[0]  # check information
                checkRow, checkCol = check[0], check[1]
                pieceChecking = self.board_array[checkRow, checkCol]
                validSquares = []  # squares that pieces can move to
                # if knight, must capture knight or move king, other pieces are blocked
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]  # to capture the knight as it's the only valid move
                else:  # blocking check with pieces
                    for i in range(1,8):  # to generate a list of coordinates where the pieces can be moved to block the checks
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2] and check[3] are check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:  # to get to the piece end checks
                            break
                # To get rid of moves that don't block check or to move the king
                for i in range(len(moves) - 1, -1, -1):  # going through the list in reverse to maintain iteration index
                    if moves[i].pieceMoved[1] != 'K':  # move doesn't move king so it must be blocked or captured
                        if not (moves[i].endRow,moves[i].endCol) in validSquares:  # move doesn't block check or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.GetKingMoves(kingRow, kingCol, moves)
        else:  # not in check so all moves are totally valid
            moves = self.GetAllPossibleMoves()
            if self.whiteToMove:
                self.GetCastleMoves(self.WhiteKingLocation[0], self.WhiteKingLocation[1], moves)
            else:
                self.GetCastleMoves(self.BlackKingLocation[0], self.BlackKingLocation[1], moves)

        if len(moves) == 0:
            if self.inCheck():
                self.Checkmate = True
            else:
                self.Stalemate = True
        else:
            self.Checkmate = False
            self.Stalemate = False

        self.CurrentCastlingRights = Temp_Castle_Rights
        return moves

    '''
    Get all moves while not considering checks being done by evaluating the possible moves from both sides
    '''

    def GetAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board_array)):  # number of rows
            for col in range(len(self.board_array[row])):  # number of cols in given row
                color_turn = self.board_array[row, col][0]  # to store the turn (white/black)
                if (color_turn == "w" and self.whiteToMove) or (
                        color_turn == "b" and not self.whiteToMove):  # checking turns
                    piece = self.board_array[row][col][1]  # to store the piece
                    self.PieceMoveFunctions[piece](row, col, moves)  # get the function associated with the piece type

        # Grouping moves by (piece type, endRow, endCol)
        move_groups = {}
        for move in moves:
            key = (move.pieceMoved[1], move.endRow, move.endCol)
            if key not in move_groups:
                move_groups[key] = []
            move_groups[key].append(move)

        # setting disambiguation for group with multiple moves
        # if multiple moves exist in a group, we check for each move's start position with others
        # if file (column) is unique, we use it (e.g., "b" for Nbd4), if rank (row) is unique, we use it (e.g., "1" for N1d4)
        # if either is unique, we use both of them (e.g., "b1" for Nb1d4)
        # if only one move, then no disambiguation
        for key, group in move_groups.items():
            if len(group) > 1:
                start_files = [move.startCol for move in group]
                start_ranks = [move.startRow for move in group]
                for move in group:
                    # Excluding the current move's own position when checking for others
                    other_files = [file for file in start_files if file != move.startCol]
                    other_ranks = [rank for rank in start_ranks if rank!= move.startRow]
                    if move.startCol not in other_files:
                        move.disambiguate = move.colsToFiles[move.startCol]
                    elif move.startRow not in other_ranks:
                        move.disambiguate = move.rowsToRanks[move.startRow]
                    else:
                        move.disambiguate = move.getRankFile(move.startRow, move.startCol)
            else:
                group[0].disambiguate = "" # no disambiguation needed
        return moves

    '''
    Method to check for Pins and Checks from the list of generated moved
    '''

    def CheckForPinsAndChecks(self):
        pins = []  # squares where the allied pinned piece is and direction pinned from
        checks = []  # squares where enemy is applying a check
        inCheckFlag = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.WhiteKingLocation[0]
            startCol = self.WhiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.BlackKingLocation[0]
            startCol = self.BlackKingLocation[1]
        # now we check the squares radially with king as the center point for pins and checks, and keep track of them
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1),
                      (1, 1))  # Up , Left, Down, Right, D_ULeft, D_URight, D_LLeft, D_LRight
        for j in range(len(directions)):
            direction = directions[j]
            possiblePin = ()  # reset possible Pins
            for i in range(1, 8):
                endRow = startRow + direction[0] * i
                endCol = startCol + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # check that the moves are within the board space
                    endPiece = self.board_array[endRow, endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, direction[0], direction[1])
                        else:  # 2nd allied piece check, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        piece_type = endPiece[1]
                        # 5 possibilities present here for a complex conditional algorithm
                        # 1. Orthogonally away from the king and piece is Rook
                        # 2. Diagonally away from the king and piece is a Bishop
                        # 3. One square away diagonally from king and piece is a pawn
                        # 4. All direction and piece is queen
                        # 5. All direction, one square away and piece is King(This is needed to prevent a king move to a
                        #    square controlled by the enemy King
                        if (0 <= j <= 3 and piece_type == 'R') or \
                                (4 <= j <= 7 and piece_type == 'B') or \
                                (i == 1 and piece_type == 'P' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (piece_type == 'Q') or (i == 1 and piece_type == 'K'):
                            if possiblePin == ():  # No piece is blocking, so check
                                inCheckFlag = True
                                checks.append((endRow, endCol, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:
                    break  # off board
        # check for Knight moves
        KnightMoves = ((-2, -1), (-1, -2), (-2, 1), (1, -2), (-1, 2), (2, -1), (1, 2), (2, 1))  # possible squares
        for move in KnightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board_array[endRow, endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':  # enemy knight attacking the king
                    inCheckFlag = True
                    checks.append((endRow, endCol, move[0], move[1]))
        return inCheckFlag, pins, checks

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
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
        Opponent_Moves = self.GetAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in Opponent_Moves:  # get all possible moves
            if move.endRow == row and move.endCol == col:  # Square under attack
                return True
        return False

    '''
    Function to check sufficient material is present on the board (As per Chess rules)
    '''
    def InsufficientMaterialDraw(self):
        # Collecting pieces by color by scanning the board
        whitePieces = []
        blackPieces = []
        for row in self.board_array:
            for piece in row:
                if piece != "--":
                    if piece[0] == "w":
                        whitePieces.append(piece[1])
                    else:
                        blackPieces.append(piece[1])

        # helper function to check if a side has only a king or kind + one piece (mainly bishop or knight)
        def HasOnlyKing_OrKingandPiece(pieceList, specific_piece = None):
            if "K" not in pieceList: # if King not on board return False
                return False
            piece_list = pieceList.copy()
            piece_list.remove("K")
            if specific_piece: # checking for specific piece being Bishop or Knight
                return len(piece_list) == 1 and piece_list[0] == specific_piece
            return len(piece_list) == 0 or (len(piece_list) == 1 and piece_list[0] in ["B", "N"])

        # Case 1: King vs King
        # if only King (whitePieces=1) and (blackPieces=1) is present then it's a draw
        if len(whitePieces) == 1 and len(blackPieces) == 1 and whitePieces[0] == "K" and blackPieces[0] == "K":
            return True

        # Case 2: King vs King and Bishop or Knight:
        # if any one of the side has King only and the other has King and Bishop or Knight then it's a draw
        if HasOnlyKing_OrKingandPiece(whitePieces) and HasOnlyKing_OrKingandPiece(blackPieces):
            return True

        # Case 3: King and Bishop vs King and Bishop (same color)
        # if both sides have King and same colored square Bishops then it's a draw
        if HasOnlyKing_OrKingandPiece(whitePieces, "B") and HasOnlyKing_OrKingandPiece(blackPieces, "B"):
            white_bishop_square_color = self.GetBishopSquareColor("w")
            black_bishop_square_color = self.GetBishopSquareColor("b")
            if white_bishop_square_color is not None and black_bishop_square_color is not None and white_bishop_square_color == black_bishop_square_color:
                return True
        return False

    '''
    Function to get Bishop Square color (helper function for InsufficientMaterialDraw function)
    '''
    def GetBishopSquareColor(self, color):
        # returns 0 for light square, 1 for dark square, or none if no bishop is present
        for row in range(8):
            for col in range(8):
                if self.board_array[row, col] == color + "B":
                    return (row + col) % 2 # sum of row and col decides square color
        return None

    '''
    Function to check if the 50 moves have passes without a capture or pawn move
    '''
    def IsFiftyMoveDraw(self):
        return self.halfmoveclock >=100 # 50 moves per side = 100 half moves

    '''
    Function to check if a certain board position has occurred 3 times during a game
    '''
    def IsThreeFoldRepetition(self):
        return self.position_history.get(self.position_key, 0) >= 3


    '''
    Function to determine the different Endgame conditions at the end phase 
    '''
    def CheckEndGameStatus(self):
        status = False
        text = ""
        if self.Checkmate:
            status = True
            if self.whiteToMove:
                text = "Black wins by Checkmate!!"
            else:
                text = "White wins by Checkmate!!"
            return text, status
        elif self.Stalemate:
            status = True
            text = "Game ends: Stalemate"
            return text, status
        elif self.InsufficientMaterialDraw():
            text = "Game ends: Draw by insufficient material"
            status = True
            return text, status
        elif self.IsThreeFoldRepetition():
            text = "Game ends: Draw by three-fold repetition"
            status = True
            return text, status
        elif self.IsFiftyMoveDraw():
            text = "Game ends: Draw by fifty-move rule"
            status = True
            return text, status
        return text, status


    '''
    Method to get all the Pawn moves for the pawn located at the row and col and add the moves to the ValidMoves list
    '''

    def GetPawnMoves(self, row, col, validMoves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:  # if the pawn is pinned
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = 'b'
            kingRow, kingCol = self.WhiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = 'w'
            kingRow, kingCol = self.BlackKingLocation

        # 1 Square move, Forward Moves
        if self.board_array[row + moveAmount, col] == "--":
            if not piecePinned or pinDirection == (moveAmount, 0):
                if (self.whiteToMove and row + moveAmount == 0) or (not self.whiteToMove and row + moveAmount == 7):
                    for piece in ['Q', 'R', 'B', 'N']:
                       validMoves.append(Move((row, col), (row + moveAmount, col), self.board_array, Promotion_Piece=piece))
                else:
                    validMoves.append(Move((row, col), (row + moveAmount, col), self.board_array))
                if row == startRow and self.board_array[row + 2 * moveAmount, col] == '--':  # 2 Square moves
                    validMoves.append(Move((row, col), (row + 2 * moveAmount, col), self.board_array))
        # Capture to left side
        if col - 1 >= 0:
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board_array[row + moveAmount, col - 1][0] == enemyColor:
                    if (self.whiteToMove and row + moveAmount == 0) or (not self.whiteToMove and row + moveAmount == 7):
                        for piece in ['Q', 'R', 'B', 'N']:
                            validMoves.append(Move((row, col), (row + moveAmount, col - 1), self.board_array, Promotion_Piece=piece))
                    else:
                        validMoves.append(Move((row, col), (row + moveAmount, col - 1), self.board_array))
                if (row + moveAmount, col - 1) == self.EnPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col: # King is left of pawn
                            # inside: between king and the pawn
                            # outside: between pawn and border
                            in_range = range(kingCol + 1, col - 1)
                            out_range = range(col + 1, 8)
                        else: # King is right of pawn
                            in_range = range(kingCol - 1, col, -1)
                            out_range = range(col - 2, 0, -1)
                        for i in in_range:
                            if self.board_array[row, i] != "--": # some other piece beside enpassant pawn is blocking
                                blockingPiece = True
                        for i in out_range:
                            square = self.board_array[row, i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        validMoves.append(Move((row, col), (row + moveAmount, col - 1), self.board_array, EnPassant=True))
        # Capture to right side
        if col + 1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board_array[row + moveAmount, col + 1][0] == enemyColor:
                    if (self.whiteToMove and row + moveAmount == 0) or (not self.whiteToMove and row + moveAmount == 7):
                        for piece in ['Q', 'R', 'B', 'N']:
                            validMoves.append(Move((row, col), (row + moveAmount, col + 1), self.board_array, Promotion_Piece=piece))
                    else:
                        validMoves.append(Move((row, col), (row + moveAmount, col + 1), self.board_array))
                if (row + moveAmount, col + 1) == self.EnPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col: # King is left of pawn
                            # inside: between king and the pawn
                            # outside: between pawn and border
                            in_range = range(kingCol + 1, col)
                            out_range = range(col + 2, 8)
                        else: # King is right of pawn
                            in_range = range(kingCol - 1, col + 1, -1)
                            out_range = range(col - 1, 0, -1)
                        for i in in_range:
                            if self.board_array[row, i] != "--": # some other piece beside enpassant pawn is blocking
                                blockingPiece = True
                        for i in out_range:
                            square = self.board_array[row, i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        validMoves.append(Move((row, col), (row + moveAmount, col + 1), self.board_array, EnPassant=True))

    '''
    Method to get all the Rook moves for the pawn located at the row and col and add the moves to the ValidMoves list
    '''

    def GetRookMoves(self, row, col, validMoves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board_array[row, col][1] != "Q":  # cant remove queen from pin on rook, only removing it on bishop moves(This code can be removed as the implementation that is done here is on pure logic rather than depending on two other functions
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))  # Up , Down , Left , Right
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # condition to check that piece will be withing board boundaries
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        endPiece = self.board_array[endRow, endCol]
                        if endPiece == "--":  # empty square valid
                            validMoves.append(Move((row, col), (endRow, endCol), self.board_array))  # just place the piece
                        elif endPiece[0] == enemyColor:  # enemy piece valid
                            validMoves.append(Move((row, col), (endRow, endCol), self.board_array))
                            break
                        else:  # friendly piece invalid
                            break
                    else:  # outside board boundaries
                        break

    '''
    Method to get all the Knight moves for the pawn located at the row and col and add the moves to the ValidMoves list
    '''

    def GetKnightMoves(self, row, col, validMoves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        KnightMoves = ((-2, -1), (-1, -2), (-2, 1), (1, -2), (-1, 2), (2, -1), (1, 2), (2, 1))  # possible squares
        allyColor = "w" if self.whiteToMove else "b"
        for move_square in KnightMoves:
            endRow = row + move_square[0]
            endCol = col + move_square[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board_array[endRow, endCol]
                    if endPiece[0] != allyColor:  # if the piece is an enemy piece or an empty square
                        validMoves.append(Move((row, col), (endRow, endCol), self.board_array))  # append move

    '''
    Method to get all the Bishop moves for the pawn located at the row and col and add the moves to the ValidMoves list
    '''

    def GetBishopMoves(self, row, col, validMoves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, 1), (1, 1), (1, -1), (-1, -1))  # D_URight, D_LRight, D_LLeft, D_ULeft diagonal moves
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1, 8):  # withing board dimension hence 7 steps
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # condition to check that piece will be withing board boundaries
                    if not piecePinned or pinDirection == direction or pinDirection == (
                    -direction[0], -direction[1]):  # if not pinned or not in pin direction
                        endPiece = self.board_array[endRow, endCol]
                        if endPiece == "--":  # empty square valid
                            validMoves.append(Move((row, col), (endRow, endCol), self.board_array))  # just place the piece
                        elif endPiece[0] == enemyColor:  # enemy piece valid
                            validMoves.append(Move((row, col), (endRow, endCol), self.board_array))
                            break
                        else:  # friendly piece invalid
                            break
                    else:  # outside board boundaries
                        break

    '''
    Method to get all the Queen moves for the pawn located at the row and col and add the moves to the ValidMoves list
    '''

    def GetQueenMoves(self, row, col, validMoves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1),  # Up , Down , Left , Right,
                      (-1, 1), (1, 1), (1, -1), (-1, -1))  #  D_URight, D_LRight, D_LLeft, D_ULeft
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # condition to check that piece will be withing board boundaries
                    if not piecePinned or pinDirection == direction or pinDirection == (
                    -direction[0], -direction[1]):  # if not pinned or not in pin direction
                        endPiece = self.board_array[endRow, endCol]
                        if endPiece == "--":  # empty square valid
                            validMoves.append(Move((row, col), (endRow, endCol), self.board_array))  # just place the piece
                        elif endPiece[0] == enemyColor:  # enemy piece valid
                            validMoves.append(Move((row, col), (endRow, endCol), self.board_array))
                            break
                        else:  # friendly piece invalid
                            break
                    else:  # outside board boundaries
                        break
            # or this function can also be written as by the following code
            '''
            self.GetRookMoves(row, col, validMoves)
            self.GetBishopMoves(row, col, validMoves)
            '''

    '''
    Method to get all the King moves for the pawn located at the row and col and add the moves to the ValidMoves list
    '''

    def GetKingMoves(self, row, col, validMoves):
        # KingMoves = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1), (1, -1),(-1, -1))  # Up , Down , Left , Right, D_URight, D_LRight, D_LLeft, D_ULeft
        RowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        ColMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = row + RowMoves[i]
            endCol = col + ColMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board_array[endRow, endCol]
                if endPiece[0] != allyColor:  # not an ally piece(empty or enemy piece)
                    # We place the king on end square and check for checks
                    if allyColor == 'w':
                        self.WhiteKingLocation = (endRow, endCol)
                    else:
                        self.BlackKingLocation = (endRow, endCol)

                    inCheckFlag, pins, checks = self.CheckForPinsAndChecks()
                    if not inCheckFlag:
                        validMoves.append(Move((row, col), (endRow, endCol), self.board_array))
                    # place king back on original location
                    if allyColor == 'w':
                        self.WhiteKingLocation = (row, col)
                    else:
                        self.BlackKingLocation = (row, col)

    '''
    Function to update the castle rights from a given move
    '''
    def UpdateCastleRights(self, move):
        # King moves rights
        if move.pieceMoved == "wK":
            self.CurrentCastlingRights.WhiteKSide = False
            self.CurrentCastlingRights.WhiteQSide = False
        elif move.pieceMoved == "bK":
            self.CurrentCastlingRights.BlackKSide = False
            self.CurrentCastlingRights.BlackQSide = False

        # White Rook move rights
        if move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: # Left Rook
                    self.CurrentCastlingRights.WhiteQSide = False
                elif move.startCol == 7: # Right Rook
                    self.CurrentCastlingRights.WhiteKSide = False

        # Black Rook move rights
        if move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: # Left Rook
                    self.CurrentCastlingRights.BlackQSide = False
                elif move.startCol == 7: # Right Rook
                    self.CurrentCastlingRights.BlackKSide = False

        # Logic to check if the Rooks have been captured
        if move.pieceCaptured == "wR":
            if move.endCol == 0: # Left rook
                self.CurrentCastlingRights.WhiteQSide = False
            elif move.endCol == 7: # Right Rook
                self.CurrentCastlingRights.WhiteKSide = False
        elif move.pieceCaptured == "bR":
            if move.endCol == 0: # Left rook
                self.CurrentCastlingRights.BlackQSide = False
            elif move.endCol == 7: # Right Rook
                self.CurrentCastlingRights.BlackKSide = False

    '''
    Function which checks and generates valid Castle moves and the corresponding helper functions
    '''
    def GetCastleMoves(self, row, col, validMoves):
        if self.SquareUnderAttack(row, col):
            return # Cuz we can't castle if in check
        if (self.whiteToMove and self.CurrentCastlingRights.WhiteKSide) or (
                not self.whiteToMove and self.CurrentCastlingRights.BlackKSide):
            self.GetKingSideCastleMoves(row, col, validMoves)
        if (self.whiteToMove and self.CurrentCastlingRights.WhiteQSide) or (
                not self.whiteToMove and self.CurrentCastlingRights.BlackQSide):
            self.GetQueenSideCastleMoves(row, col, validMoves)

    def GetKingSideCastleMoves(self, row, col, validMoves):
        if self.board_array[row, col + 1] == "--" and self.board_array[row, col + 2] == "--":
            if not self.SquareUnderAttack(row, col + 1) and not self.SquareUnderAttack(row, col + 2):
                validMoves.append(Move((row, col), (row, col + 2), self.board_array, IsCastleMove = True))


    def GetQueenSideCastleMoves(self, row, col, validMoves):
        if self.board_array[row, col - 1] == '--' and self.board_array[row, col - 2] == '--' and self.board_array[row, col - 3] == "--":
            if not self.SquareUnderAttack(row, col - 1) and not self.SquareUnderAttack(row, col - 2):
                validMoves.append(Move((row, col), (row, col - 2), self.board_array, IsCastleMove = True))

'''
Class to store the data on the castling rules on the board
'''
class CastleRights:
    def __init__(self, WhiteKSide, BlackKSide, WhiteQSide, BlackQSide):
        self.WhiteKSide = WhiteKSide
        self.BlackKSide = BlackKSide
        self.WhiteQSide = WhiteQSide
        self.BlackQSide = BlackQSide

'''
Move Class containing all the logic regarding movement of the piece and not the actual piece Logic which abides by the Chess Rules
'''

class Move:
    # mapping ranks and files to rows and columns
    ranksToRanks = {"1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRanks.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, start_square, end_square, board, EnPassant=False, IsCastleMove = False, Promotion_Piece = None):
        self.startRow = start_square[0]
        self.startCol = start_square[1]
        self.endRow = end_square[0]
        self.endCol = end_square[1]
        self.pieceMoved = board[self.startRow, self.startCol]
        self.pieceCaptured = board[self.endRow, self.endCol]
        # Pawn Promotion
        self.PawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (
            self.pieceMoved == 'bP' and self.endRow == 7)
        self.Pawn_Promoted_to = Promotion_Piece
        # EnPassant Rules
        self.EnPassant = EnPassant
        if self.EnPassant:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"  #EnPassant captures opposite colored pawn
        # Castling Logs
        self.IsCastleMove = IsCastleMove
        self.IsCaptured = self.pieceCaptured != "--"
        # Chess notation attribute
        self.disambiguate = ""
        self.in_check = False # Flag for check
        self.is_checkmate = False # Flag for checkmate
        # Move ID for piece identification
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol  # Move ID to keep track of moves

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            if self.PawnPromotion:
                return self.moveID == other.moveID and self.Pawn_Promoted_to == other.Pawn_Promoted_to
            return self.moveID == other.moveID
        return False

    '''
    Overriding the string method for Chess move notations
    '''
    def __str__(self):
        # Castle Move
        if self.IsCastleMove:
            MoveString = "0-0" if self.endCol == 6 else "0-0-0"
        else:
            # Pawn moves
            # end or target square
            EndSquare = self.getRankFile(self.endRow, self.endCol)
            if self.pieceMoved[1] == "P":
                MoveString = ""
                if self.IsCaptured:
                    MoveString += self.colsToFiles[self.startCol] + "x"
                MoveString += EndSquare
                if self.PawnPromotion:
                    MoveString += "=" + self.Pawn_Promoted_to
            else:
            # Piece Moves (Two pieces of same type moving to a square, Especially with Knights)
                MoveString = self.pieceMoved[1]
                if self.disambiguate: # adding disambiguate move algebra
                    MoveString += self.disambiguate
                if self.IsCaptured:
                    MoveString += "x"
                MoveString += EndSquare
        # adding + for check move, and # for checkmate move
        if self.is_checkmate:
            MoveString += "#"
        elif self.in_check:
            MoveString += "+"

        return MoveString

    '''
    Returns the string representation of Chess terms of ranks and files from row and column representations
    '''
    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
