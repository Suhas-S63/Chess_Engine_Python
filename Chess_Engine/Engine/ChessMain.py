"""
Main driver file. The file will be handling user move input and display current game state object
"""
import pygame as pyg
from Engine import ChessEngine, ChessAI


BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 270
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
BOARD_DIMENSION = 8  #  dimensions of the chess board
SQUARE_SIZE = BOARD_HEIGHT // BOARD_DIMENSION  # size of each square on the board
MAX_FPS = 30  # game loop frequency and animation cycles
PIECE_IMAGES = {}

'''
Initialising a global dictionary of images. The function will be called once in main
'''


def LoadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
    for piece in pieces:
        PIECE_IMAGES[piece] = pyg.transform.scale(pyg.image.load(f'piece_images/{piece}.png'),
                                                  (SQUARE_SIZE, SQUARE_SIZE))

        # we can now access an image by passing the piece notation in the dictionary
        # for example: PIECE_IMAGES['bR'] will return the image of a black rook


'''
Main driver code to handle user move input and update the graphics according to game state
'''


def main():
    # Initialize pygame
    pyg.init()
    screen = pyg.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = pyg.time.Clock()
    screen.fill(pyg.Color('white'))
    game_state = ChessEngine.GameState()
    validMoves = game_state.GetValidMoves()
    MoveLogFont = pyg.font.SysFont("Tahoma", 14, False, False)
    moveMade = False  # flag variable for when a move is made so that validMoves are generated only when one side makes a move
    animate = False # flag variable for when the move animation should be animated or not
    LoadImages()  # loaded only once before the game loop
    running = True  # Game loop flag
    square_selected = ()  #keeps track of last square selected, tuple to store the mouse position
    player_clicks = []  #keeps track of player clicks
    gameOver = False # flag to indicate the game is over
    # Can also be used to change the piece by which the player or the AI plays
    Human = True # Flag to indicate if the human is playing with white, False if AI is playing
    P2_AI = False # Same as above flag but for AI
    # For 2 AIs this will false and false
    while running:
        human_turn = (game_state.whiteToMove and Human) or (not game_state.whiteToMove and not P2_AI)
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False
            # Mouse event handler
            elif event.type == pyg.MOUSEBUTTONDOWN:
                if not gameOver and human_turn:  # only when game is not over
                    position = pyg.mouse.get_pos()  #(x,y) coords of mouse
                    col = position[0] // SQUARE_SIZE
                    row = position[1] // SQUARE_SIZE
                    if square_selected == (row, col) or col >= 8: # col >=8 is added to remove an error where Index bugs comes from selecting out of a board
                        square_selected = ()  # deselect the square
                        player_clicks = []  # clear player clicks
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)  # append for both 1st and 2nd click
                    if len(player_clicks) == 2:  # after 2nd click which is selecting the target square
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                game_state.MakeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                square_selected = () # Reset user clicks after move is made
                                player_clicks = []

                        if not moveMade:
                            player_clicks = [square_selected]

            # Key Handler
            elif event.type == pyg.KEYDOWN:
                if event.key == pyg.K_z:  # undo when Z arrow key is used
                    game_state.UndoMove()
                    moveMade = True
                    animate = False

                if event.key == pyg.K_r: # Reset the game by setting the game state to default
                    game_state = ChessEngine.GameState()
                    validMoves = game_state.GetValidMoves()
                    square_selected = ()
                    player_clicks = []
                    moveMade = False
                    animate = False

        # AI Move Generation
        if not gameOver and not human_turn:
            AI_Move = ChessAI.RandomChessMove(validMoves)
            game_state.MakeMove(AI_Move)
            moveMade = True
            animate = True

        if moveMade:  #checking so that when move is undone and new set of moves are generated
            if animate:
                MoveAnimation(game_state.moveLog[-1], screen, game_state.board, clock)
            validMoves = game_state.GetValidMoves() # for moves to be made
            moveMade = False
            animate = False

        # Update the screen with the current game state
        DrawGameState(screen, game_state, validMoves, square_selected, MoveLogFont)

        # Check if the game is over
        if game_state.Checkmate:
            gameOver = True
            if game_state.whiteToMove:
                text = "Black wins by Checkmate!!"
            else:
                text = "White wins by Checkmate!!"
            DrawEndGameText(screen, text)
        elif game_state.Stalemate:
            gameOver = True
            text = "Stalemate!!"
            DrawEndGameText(screen, text)
        elif game_state.OnlyKingsPresent():
            gameOver = True
            text =  "Draw!!"
            DrawEndGameText(screen, text)


        clock.tick(MAX_FPS)
        pyg.display.flip()


'''
The following function is responsible for all the graphics with the current game state
'''


def DrawGameState(screen, game_state, validMoves, square_selected, MoveLogFont):
    DrawBoard(screen)  # draw the game board which are the squares
    HighlightSquares(screen, game_state, validMoves, square_selected)  # highlight the possible moves at the current game state
    DrawPieces(screen, game_state.board)  # draw the pieces on the board
    DrawMoveLog(screen, game_state, MoveLogFont) # draw the move log for the moves done next to board


'''
Draw squares on the board using current GameState.Board
'''
def DrawBoard(screen):
    global colors
    colors = [pyg.Color("white"), pyg.Color("gray")]
    for row in range(BOARD_DIMENSION):
        for col in range(BOARD_DIMENSION):
            color = colors[(row + col) % 2]
            pyg.draw.rect(screen, color, pyg.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


'''
Draw squares on the board
'''
def DrawPieces(screen, board):
    for row in range(BOARD_DIMENSION):
        for col in range(BOARD_DIMENSION):
            piece = board[row][col]
            if piece != '--':  # not an empy space
                screen.blit(PIECE_IMAGES[piece],
                            pyg.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

''' 
Functions regarding highlighting moves and animating the moves to improve UI for good gameplay 
'''
'''
Function to highlight the possible moves at the current game state
'''
def HighlightSquares(screen, game_state, validMoves, square_selected):
    surface = pyg.Surface((SQUARE_SIZE, SQUARE_SIZE))
    surface.set_alpha(150)  # Transparency value to display how transparent or opaque the highlighted square is blitted
    # highlighting on normal and danger squares
    if square_selected != ():
        row, col = square_selected
        piece = game_state.board[row][col]
        if game_state.board[row][col][0] == ('w' if game_state.whiteToMove else 'b'): # square selected is the piece that can be moved based on turns
            # Highlight the square (semi transparent surface)
            surface.fill(pyg.Color('slateblue1'))
            screen.blit(surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            for move in validMoves: # Here we go through the valid moves to highlight the squares to which the piece can be moved
                if move.startRow == row and move.startCol == col: # to check if the square selected is present in the validMoves list
                    # Highlighting the moves from the origin piece square to show the valid Moves
                    # Red for captures, gold for regular moves
                    surface.fill(pyg.Color('red') if move.pieceCaptured != '--' else pyg.Color('gold1'))
                    screen.blit(surface, (move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE))
                    if piece[1] == "K" and move.IsCastleMove:
                        surface.fill(pyg.Color('magenta'))
                        screen.blit(surface, (move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE))

    # Highlighting if the King is under check
    if game_state.inCheck() or game_state.Checkmate:
        if game_state.whiteToMove:
            kingRow, kingCol = game_state.WhiteKingLocation
        else:
            kingRow, kingCol = game_state.BlackKingLocation
        surface.fill(pyg.Color('red'))
        screen.blit(surface, (kingCol * SQUARE_SIZE, kingRow * SQUARE_SIZE))
    # Highlighting if the Game Ends in Stalemate
    if game_state.Stalemate:
        if game_state.whiteToMove:
            kingRow, kingCol = game_state.WhiteKingLocation
        else:
            kingRow, kingCol = game_state.BlackKingLocation
        surface.fill(pyg.Color('darkorange1'))
        screen.blit(surface, (kingCol * SQUARE_SIZE, kingRow * SQUARE_SIZE))


'''
Function for animating the piece movement from selected to destination square
'''
def MoveAnimation(move, screen, board, clock):
    global colors
    delta_Row = move.endRow - move.startRow
    delta_Col = move.endCol - move.startCol
    FramesPerSquare = 10 # number of frames to move to one square
    FrameCount = (abs(delta_Row) + abs(delta_Col)) * FramesPerSquare
    for frame in range(FrameCount + 1):
        row, col = (move.startRow + delta_Row * frame/FrameCount, move.startCol + delta_Col * frame/FrameCount)
        DrawBoard(screen)
        DrawPieces(screen, board)
        # Next, we erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        end_square = pyg.Rect(move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pyg.draw.rect(screen, color, end_square)
        # drawing the captured piece onto the rectangle
        if move.pieceCaptured != '--':
            if move.EnPassant:
                EnPassantRow = (move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1)
                end_square = pyg.Rect(move.endCol * SQUARE_SIZE, EnPassantRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(PIECE_IMAGES[move.pieceCaptured], end_square)
        # drawing the moving piece to the end of its destination square
        screen.blit(PIECE_IMAGES[move.pieceMoved], pyg.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pyg.display.flip()
        clock.tick(60) # changeable FPS only for animation

'''
Function to draw text on the board
'''
def DrawEndGameText(screen, text):
    text_font = pyg.font.SysFont("Open Sans", 42, True, False)
    TextObj = text_font.render(text, 1,  pyg.Color('Gray'))
    TextLocation = pyg.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - TextObj.get_width()/2, BOARD_HEIGHT/2 - TextObj.get_height()/2)
    screen.blit(TextObj, TextLocation)
    TextObj = text_font.render(text, 1,  pyg.Color('Black'))
    screen.blit(TextObj, TextLocation.move(2,2))

'''
Function to draw move log next to the board
'''
def DrawMoveLog(screen, game_state, font):
    MoveLogRect = pyg.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    pyg.draw.rect(screen, pyg.Color('black'), MoveLogRect)
    move_log = game_state.moveLog
    Move_Texts = []
    for i in range(0, len(move_log), 2): # step by 2
        move_string =  str(i // 2 + 1)+ ")" + " " + str(move_log[i]) + " "
        if i + 1 < len(move_log): # to make sure black made a move
            move_string += str(move_log[i + 1]) + " "
        Move_Texts.append(move_string)

    moves_per_row = 3 # variable
    padding = 5
    text_Y = padding
    line_spacing = 5
    for i in range(0, len(Move_Texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(Move_Texts):
                text += Move_Texts[i + j]
        TextObj = font.render(text, True, pyg.Color('white'))
        TextLocation = MoveLogRect.move(padding, text_Y)
        screen.blit(TextObj, TextLocation)
        text_Y += TextObj.get_height() + line_spacing


if __name__ == "__main__":
    main()
