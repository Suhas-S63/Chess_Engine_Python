"""
Main driver file. The file will be handling user move input and display current game state object
"""
import pygame as pyg
import ChessEngine, ChessAI


BOARD_WIDTH = BOARD_HEIGHT = 640
MOVE_LOG_PANEL_WIDTH = 270
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
BOARD_DIMENSION = 8  #  dimensions of the chess board
SQUARE_SIZE = BOARD_HEIGHT // BOARD_DIMENSION  # size of each square on the board
MAX_FPS = 30  # game loop frequency and animation cycles
PIECE_IMAGES = {}
global colors, game_mode, HEADER_HEIGHT, manual_scroll # some global constants used
# scroll variables
MOVE_LOG_SCROLL_OFFSET = 0
MOVE_LOG_SCROLL_SPEED = 50 # Pixels per scroll step


'''
Initialising a global dictionary of images. The function will be called once in main
'''


def LoadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
    for piece in pieces:
        PIECE_IMAGES[piece] = pyg.transform.smoothscale(pyg.image.load(f'piece_images/{piece}.png'),
                                                  (SQUARE_SIZE, SQUARE_SIZE))

        # we can now access an image by passing the piece notation in the dictionary
        # for example: PIECE_IMAGES['bR'] will return the image of a black rook


'''
Main driver code to handle user move input and update the graphics according to game state
'''


def main():
    # Initialize pygame
    global MOVE_LOG_SCROLL_OFFSET, manual_scroll, HEADER_HEIGHT
    pyg.init()
    screen = pyg.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    pyg.display.set_caption("Chess Engine")
    clock = pyg.time.Clock()
    screen.fill(pyg.Color('white'))
    game_state = ChessEngine.GameState()
    validMoves = game_state.GetValidMoves()
    MoveLogFont = pyg.font.SysFont("Tahoma", 22, False, False)
    info_font = pyg.font.SysFont("Arial", 20, bold=True)
    moveMade = False  # flag variable for when a move is made so that validMoves are generated only when one side makes a move
    animate = False # flag variable for when the move animation should be animated or not
    LoadImages()  # loaded only once before the game loop
    running = True  # Game loop flag
    square_selected = ()  #keeps track of last square selected, tuple to store the mouse position
    player_clicks = []  #keeps track of player clicks
    gameOver = False # flag to indicate the game is over
    # Can also be used to change the piece by which the player or the AI plays
    Human = False # Flag to indicate if the human is playing with white, False if AI is playing
    P2_AI = True # Same as above flag but for AI
    # For 2 AIs this will be True and False

    # Some Constants Used
    line_height = MoveLogFont.get_height() + 5 # for DrawMoveLog()
    HEADER_HEIGHT = 85 + (info_font.get_height() + 2) * 2 # for DrawMoveLog()
    MOVE_LOG_SCROLL_OFFSET = 0
    manual_scroll = False
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
                        start_square = player_clicks[0]
                        end_square = player_clicks[1]
                        piece_moved = game_state.board[start_square[0]][start_square[1]]
                        if piece_moved[1] == 'P' and end_square[0] == (0 if game_state.whiteToMove else 7):
                            selected_piece = DrawPawnPromotionWindow(screen, piece_moved[0])
                            move = ChessEngine.Move(start_square, end_square, game_state.board, Promotion_Piece=selected_piece)
                        else:
                            move = ChessEngine.Move(start_square, end_square, game_state.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                game_state.MakeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                square_selected = () # Reset user clicks after move is made
                                player_clicks = []

                        if not moveMade:
                            player_clicks = [square_selected]
            # move log rendering
            elif event.type == pyg.MOUSEWHEEL and pyg.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT).collidepoint(pyg.mouse.get_pos()):
                # Scrolling the move log panel
                manual_scroll = True # true only if mouse over move log panel
                MOVE_LOG_SCROLL_OFFSET -= event.y * MOVE_LOG_SCROLL_SPEED
                num_move_pairs = (len(game_state.moveLog) + 1) // 2
                panel_height = num_move_pairs * line_height
                visible_area = MOVE_LOG_PANEL_HEIGHT - HEADER_HEIGHT
                MOVE_LOG_SCROLL_OFFSET = max(0, min(MOVE_LOG_SCROLL_OFFSET, max(0, panel_height - visible_area)))

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
            manual_scroll = False # reset scroll when a new move is made
            # for updating moveLog panel
            num_move_pairs = (len(game_state.moveLog) + 1) // 2
            panel_height = num_move_pairs * line_height
            visible_area = MOVE_LOG_PANEL_HEIGHT - HEADER_HEIGHT
            if panel_height > visible_area:
                MOVE_LOG_SCROLL_OFFSET = panel_height - visible_area
            else:
                MOVE_LOG_SCROLL_OFFSET = 0 # no scrolling needed if content withing moveLog panel

        # Update the screen with the current game state and move log
        DrawGameState(screen, game_state, validMoves, square_selected)
        DrawMoveLog(screen, game_state,MoveLogFont, Human, P2_AI)

        # Checking EndGameStatus like checkmate, stalemate, Material count, 3-fold repetition
        # and fifty move draw to see if the game is over
        end_game_text, gameOver = game_state.CheckEndGameStatus()
        if end_game_text:
            DrawEndGameText(screen, end_game_text)
            # If the game is over, we stop the game loop

        clock.tick(MAX_FPS)
        pyg.display.flip()


'''
The following function is responsible for all the graphics with the current game state
'''

def DrawGameState(screen, game_state, validMoves, square_selected):
    DrawBoard(screen)  # draw the game board which are the squares
    HighlightSquares(screen, game_state, validMoves, square_selected)  # highlight the possible moves at the current game state
    DrawPieces(screen, game_state.board)  # draw the pieces on the board

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
Drawing Pawn Promotion window if pawn is able to promote
'''
def DrawPawnPromotionWindow(screen, color):
    # defining the piece options and load the images
    pieces = ['Q', 'R', 'B', 'N']
    piece_images = [PIECE_IMAGES[color + piece] for piece in pieces]

    # window dimensions
    panel_width = 4 * SQUARE_SIZE # 4 pieces width
    panel_height = SQUARE_SIZE # 1 row height
    panel_x = (BOARD_WIDTH - panel_width) // 2 # Center horizontally
    panel_y = (BOARD_HEIGHT - panel_height) // 2 # Center vertically

    # drawing the window
    promotion_panel = pyg.Surface((panel_width, panel_height), pyg.SRCALPHA)
    promotion_panel.set_alpha(150)
    promotion_panel.fill(pyg.Color('chocolate')) # Gray wth transparency
    screen.blit(promotion_panel, (panel_x, panel_y))

    # drawing the piece options
    for i , image in enumerate(piece_images):
        screen.blit(image, (panel_x + i * SQUARE_SIZE, panel_y))

    pyg.display.flip() # update the game display

    # wait for user input to select a piece
    piece_selected = None
    while piece_selected is None:
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                pyg.quit()
            elif event.type == pyg.MOUSEBUTTONDOWN:
                position = pyg.mouse.get_pos()  # (x,y) coords of mouse
                if panel_y <= position[1] <= panel_y + SQUARE_SIZE: # within UI height
                    for i in range(4):
                        if panel_x + i * SQUARE_SIZE <= position[0] <= panel_x + (i + 1) * SQUARE_SIZE:
                            piece_selected = pieces[i]
                            break
    return piece_selected


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
def DrawMoveLog(screen, game_state, font, Human_Flag, AI_Flag):
    global game_mode, MOVE_LOG_SCROLL_OFFSET
    header_font = pyg.font.SysFont("Arial", 26, bold=True)
    info_font = pyg.font.SysFont("Arial",20, bold=True)

    # Move Log Panel
    MoveLogRect = pyg.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    pyg.draw.rect(screen, pyg.Color('black'), MoveLogRect)

    # heading
    header_height = 70 + (info_font.get_height() + 2) * 2  # 70 for heading + 2 extra lines
    heading_text = font.render("Chess Game", True, pyg.Color("White"))
    screen.blit(heading_text, (BOARD_WIDTH + 5, 5)) # 5 px padding from top/left

    # Info Lines
    if Human_Flag and AI_Flag:
        game_mode = "Player vs AI"
    elif not Human_Flag  and AI_Flag == True:
        game_mode = "AI vs AI"
    elif Human_Flag and not AI_Flag:
        game_mode = "Player vs Player"
    turn = "White to Move" if game_state.whiteToMove else "Black to Move"
    move_count = len(game_state.moveLog) // 2 + 1
    info_str1 = "Move History"
    info_str2 = f"| {game_mode} | {turn} |"
    info_str3 = f"Move {move_count}"
    # Rendering Info Lines
    info_y = 5 + header_font.get_height() + 2 # Starting below heading
    line_spacing = info_font.get_height() + 2 # Space between lines

    screen.blit(info_font.render(info_str1, True, pyg.Color("white")), (BOARD_WIDTH + 5, info_y))
    screen.blit(info_font.render(info_str2, True, pyg.Color("white")), (BOARD_WIDTH + 5, info_y + line_spacing))
    screen.blit(info_font.render(info_str3, True, pyg.Color("white")), (BOARD_WIDTH + 5, info_y + 2 * line_spacing))

    # Move List
    move_log = game_state.moveLog
    Move_Texts = []
    # Pair moves (white and black) with move numbers
    for i in range(0, len(move_log), 2): # step by 2
        move_number =  str(i // 2 + 1) + "." # move counter
        white_move = str(move_log[i]) if i < len(move_log) else "" # white move (half move)
        black_move = str(move_log[i + 1]) if i + 1 < len(move_log) else "" # black move (half move)
        Move_Texts.append((move_number, white_move, black_move))

    # defining the move column widths and line heights
    move_num_width = 40 # Move number column width
    move_width = 50 # Move column width for each move
    line_height = font.get_height() + 5 # 5 pixels of vertical spacing between lines

    # Rendering the visible moves now based on the scroll offset
    y_axis = header_height - MOVE_LOG_SCROLL_OFFSET # start position adjusted
    for move_number, white_move, black_move in Move_Texts:
        if y_axis + line_height > header_height and y_axis < MOVE_LOG_PANEL_HEIGHT: # now we check if the row is withing visible region
            # Render the move contents
            screen.blit(font.render(move_number,True, pyg.Color('white')), (BOARD_WIDTH + 5, y_axis))
            screen.blit(font.render(white_move, True, pyg.Color('white')), (BOARD_WIDTH + 10 + move_num_width, y_axis))
            screen.blit(font.render(black_move, True, pyg.Color('white')), (BOARD_WIDTH + 25 + move_num_width + move_width, y_axis))

        y_axis += line_height # Move next row


if __name__ == "__main__":
    main()
