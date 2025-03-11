from ChessEngine import GameState
import numpy as np
from Chess_Engine.Engine.ChessEngine import CastleRights

game_state = GameState()
'''
Function to set custom board configuration using FEN notation
'''
def Custom_Board_using_FEN_Not(game_state, fen_string):
    board_array = np.array([
        ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],  # Columns are called "Files"
        ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],  # Rows are called "Ranks"
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
    ], dtype=object)
    # Mapping from FEN pieces to internal representation
    fen_to_piece = {
        'p': 'bP', 'n': 'bN', 'b': 'bB', 'r': 'bR', 'q': 'bQ', 'k': 'bK',
        'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK'
    }
    # clearing the board
    board_array = np.array([["--"] * 8 for _ in range(8)])
    # Parsing the FEN string
    pieces, turn, castling, en_passant, half_move, full_move = fen_string.split()

    # Placing pieces
    ranks = pieces.split('/')
    for row, rank in enumerate(ranks):
        col = 0
        for char in rank:
            if char.isdigit():
                col += int(char) # skip empty squares
            else:
                board_array[row][col] = fen_to_piece[char]
                col += 1

    # setting turn
    if turn == 'w':
        game_state.whiteToMove = True
    elif turn == 'b':
        game_state.whiteToMove = False
    else:
        raise ValueError("Invalid active color: must be 'w' or 'b'")

    # Setting Castling Rights
    game_state.CurrentCastlingRights = CastleRights(True, True, True, True)
    if castling != '-':
        for char in castling:
            if char == 'K':
                game_state.CurrentCastlingRights.WhiteKSide = True
            elif char == 'Q':
                game_state.CurrentCastlingRights.WhiteQSide = True
            elif char == 'k':
                game_state.CurrentCastlingRights.BlackKSide = True
            elif char == 'q':
                game_state.CurrentCastlingRights.BlackQSide = True
            else:
                raise ValueError(f"Invalid castling character: {char}")

    #  En Passant Target Square
    if en_passant == '-':
        game_state.EnPassantPossible = None
    else:
        if (len(en_passant) != 2 or en_passant[0] not in 'abcdefgh' or
                en_passant[1] not in '12345678'):
            raise ValueError(f"Invalid en passant square: {en_passant}")
        file = en_passant[0]
        rank = int(en_passant[1])
        col = ord(file) - ord('a')  # 'a' -> 0, 'b' -> 1, etc.
        row = 8 - rank  # rank 8 -> row 0, rank 1 -> row 7
        game_state.EnPassantPossible = (row, col)

    # Halfmove Clock
    try:
        game_state.halfmoveclock = int(half_move)
    except ValueError:
        raise ValueError("Halfmove clock must be an integer")

    # Fullmove Number**
    try:
        game_state.fullmovecounter = int(full_move)
    except ValueError:
        raise ValueError("Fullmove number must be an integer")

    # **Step 7: Reset Move Log**
    # Since this is a new position, clear the move history
    game_state.moveLog = []

    return board_array, game_state.whiteToMove, game_state.CurrentCastlingRights, game_state.EnPassantPossible, game_state.halfmoveclock, game_state.fullmovecounter

fen_string = 'r3kb1r/1pp1ppp1/2nq1n1p/pB1p1b2/P3P1P1/2NP1N2/1PP2P1P/R1BQK2R b KQkq - 0 1'
Custom_Board_using_FEN_Not(game_state, fen_string)
print(Custom_Board_using_FEN_Not(game_state, fen_string))

# import numpy as np
# from Chess_Engine.Engine.ChessEngine import CastleRights
#
#
# def Custom_Board_using_FEN_Not(game_state, fen_string):
#     """
#     Updates the game_state object with a position specified by a FEN string.
#
#     Args:
#         game_state (GameState): The game state object to modify.
#         fen_string (str): FEN string representing the position.
#     """
#     # FEN string into its components
#     parts = fen_string.split()
#     if len(parts) != 6:
#         raise ValueError("Invalid FEN string: must have 6 parts")
#     pieces, turn, castling, en_passant, half_move, full_move = parts
#
#     # Mapping from FEN pieces to internal representation
#     fen_to_piece = {
#         'p': 'bP', 'n': 'bN', 'b': 'bB', 'r': 'bR', 'q': 'bQ', 'k': 'bK',
#         'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK'
#     }
#
#     # piece placement parsing
#     ranks = pieces.split('/')
#     if len(ranks) != 8:
#         raise ValueError("Invalid piece placement: must have 8 ranks")
#     board = [['--' for _ in range(8)] for _ in range(8)]
#     for row, rank in enumerate(ranks):
#         col = 0
#         for char in rank:
#             if char.isdigit():
#                 col += int(char)  # Skip empty squares
#             elif char in fen_to_piece:
#                 board[row][col] = fen_to_piece[char]
#                 col += 1
#             else:
#                 raise ValueError(f"Invalid character in piece placement: {char}")
#         if col != 8:
#             raise ValueError(f"Rank {8 - row} does not span 8 squares")
#     game_state.board_array = np.array(board, dtype=object)
#
#     # turn set
#     if turn == 'w':
#         game_state.whiteToMove = True
#     elif turn == 'b':
#         game_state.whiteToMove = False
#     else:
#         raise ValueError("Invalid active color: must be 'w' or 'b'")
#
#     # castling rights
#     wks = 'K' in castling
#     bks = 'k' in castling
#     wqs = 'Q' in castling
#     bqs = 'q' in castling
#     game_state.CurrentCastlingRights = CastleRights(wks, bks, wqs, bqs)
#
#     # en passant target square
#     if en_passant == '-':
#         game_state.EnPassantPossible = ()
#     else:
#         if len(en_passant) != 2 or en_passant[0] not in 'abcdefgh' or en_passant[1] not in '12345678':
#             raise ValueError(f"Invalid en passant square: {en_passant}")
#         file = en_passant[0]
#         rank = int(en_passant[1])
#         col = ord(file) - ord('a')  # 'a' -> 0, 'b' -> 1, etc.
#         row = 8 - rank  # rank 8 -> row 0, rank 1 -> row 7
#         game_state.EnPassantPossible = (row, col)
#
#     # halfmove clock and fullmove counter
#     try:
#         game_state.halfmoveclock = int(half_move)
#     except ValueError:
#         raise ValueError("Halfmove clock must be an integer")
#     try:
#         game_state.fullmovecounter = int(full_move)
#     except ValueError:
#         raise ValueError("Fullmove number must be an integer")
#
#     # updating king locations
#     for row in range(8):
#         for col in range(8):
#             piece = game_state.board_array[row][col]
#             if piece == 'wK':
#                 game_state.WhiteKingLocation = (row, col)
#             elif piece == 'bK':
#                 game_state.BlackKingLocation = (row, col)
#
#     # Reset game state attributes for a new position
#     game_state.moveLog = []
#     game_state.EnPassantPossibleLog = [game_state.EnPassantPossible]
#     game_state.CastleRightsLog = [game_state.CurrentCastlingRights]
#     game_state.Checkmate = False
#     game_state.Stalemate = False
#
#     white_pieces = sum(1 for row in game_state.board_array for piece in row if piece[0] == 'w')
#     black_pieces = sum(1 for row in game_state.board_array for piece in row if piece[0] == 'b')
#     game_state.white_pieces = white_pieces
#     game_state.black_pieces = black_pieces

