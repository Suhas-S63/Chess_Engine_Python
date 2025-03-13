# Outwit, outplay, and checkmate—your move, genius! ♟️♔

# Chess Engine in Python
A fully functional chess engine built with Python and Pygame, designed to simulate a complete chess game with an intuitive graphical interface and robust game logic. This project includes a variety of features inspired by professional platforms like Chess.com, such as algebraic notation, scrollable move logs, and support for all standard chess rules.

![ChessGif](https://github.com/Suhas-S63/Chess_Engine_Python/blob/main/Chess_Engine/Engine/ChessGif.gif)

## Project Background and Structure
This project is a graphical chess implementation using Python, leveraging Pygame for the user interface. It comprises three main files:
- **ChessMain.py**: Acts as the entry point, handling user inputs and displaying the game state via Pygame. It supports an intro screen for selecting player color, board color scheme, and game mode (Player vs AI, Player vs Player, AI vs AI).
- **ChessEngine.py**: Manages the game state, including board configuration, move validation, and rules like castling and en passant, using NumPy for efficient board representation.
- **ChessAI.py**: Implements the AI logic, offering algorithms from random moves to advanced negamax with alpha-beta pruning, enhanced by an opening book for early-game strategies.

The integration of these files creates a robust chess game with visual and AI capabilities, suitable for educational purposes and casual play.
## Features

### Gameplay
- **Full Chess Rules**: Implements all fundamental chess mechanics:
  - Moves for all pieces: Pawns, Knights, Bishops, Rooks, Queens, and Kings.
  - Special moves: Castling (king-side and queen-side), en passant, and pawn promotion.
  - Check, checkmate, and stalemate detection with move validation to prevent illegal moves.
- **Draw Conditions**:
  - **Insufficient Material**: Detects draws for King vs. King, King vs. King + Bishop/Knight, and King + Bishop vs. King + Bishop (same color squares).
  - **Threefold Repetition**: Tracks position history to identify when the same position occurs three times.
  - **Fifty-Move Rule**: Enforces a draw after 50 moves (100 half-moves) without a capture or pawn move.
- **Undo Moves**: Ability to revert the last move with proper state restoration (e.g., castling rights, en passant possibilities).

### User Interface
- **Graphical Board**: An 8x8 chessboard rendered with Pygame, featuring:
  - Smooth, anti-aliased piece images scaled using `pygame.transform.smoothscale`.
  - Highlighted squares for valid moves and special states (e.g., check, castling).
  - Move animations for a fluid gameplay experience.
- **Pawn Promotion UI**: Interactive overlay for selecting promotion pieces (Queen, Rook, Bishop, Knight).
- **Move Log Panel**:
  - Scrollable log displaying move history in algebraic notation.
  - Clean, table-like layout with columns for move number, White’s move, and Black’s move.
  - Styled with a greyed-black background and white text for readability.

### Technical Details
- **Algebraic Notation**: Comprehensive move notation in the `Move` class, supporting:
  - Disambiguation for identical piece types (e.g., `Nbd2` for knights).
  - Capture notation (e.g., `exd5`).
  - Promotion (e.g., `e8=Q`).
  - Check (`+`) and checkmate (`#`) indicators.
- **AI Opponent**: NegaMax Algorithm with Alpha-Beta Pruning. Move Ordering and Quiescence Search is integrated for better move selection
- **Modular Design**:
  - `ChessMain.py`: Handles the game loop, input, and rendering.
  - `ChessEngine.py`: Core logic for game state, move generation, validation and other rules.

## Installation and Setup Instructions
To ensure proper set up of the project, follow the included steps:

1. **Cloning the Repository**:
   - To clone the repository:
     ```bash
     git clone https://github.com/Suhas-S63/Chess_Engine_Python.git
     ```

2. **Virtual Environment Setup**:
   - A virtual environment is recommended for dependency management:
     ```bash
     python -m venv venv
     ```

3. **Library Installation**:
   - Dependencies are listed, and installation is facilitated via a `requirements.txt` file:
     ```bash
     pip install -r requirements.txt
     ```
   - Required libraries / Key Dependencies include:
     - Pygame: For graphical interface ([Pygame Documentation](https://www.pygame.org/docs/))
     - NumPy: For array operations in board management ([NumPy Documentation](https://numpy.org/doc/))
     - chess: For chess rules and AI logic, which also supports the `chess.polyglot` module for opening books ([chess Documentation](https://pypi.org/project/chess/))

4. **Opening Book File**:
   - The AI relies on an opening book file, `Cerebellum3Merge.bin` or `komodo.bin`, which is not included in the repository due to size (except for `komodo.bin`). Users must download this file from a reliable source and place it in the root directory. This step is crucial for early-game AI performance, as it uses the file for informed move selection.

## Usage Instructions

1. **Running the Game**:
   - Execute the game by running:
     ```bash
     python ChessMain.py
     ```
   - This launches the intro screen.

2. **Intro Screen Options**:
   - Users can select:
     - Player color (White or Black), affecting who moves first.
     - The board color scheme (e.g., Tournament Standard, Classic Wood, Modern Glass, etc.) enhances visual appeal.
     - Game mode, offering:
       - Player vs AI: Human plays against the AI, with the option to choose color.
       - Player vs Player: Two humans play, ideal for local multiplayer.
       - AI vs AI: Observes two AIs playing, useful for testing or entertainment.
   - Selections are made via mouse interactions, with visual feedback like hover and selected states.

3. **Game Controls and Features**:
   - **Mouse Interaction**: Click to select a piece, click again to move, and right-click to cancel.
   - **Keyboard Shortcuts**:
     - 'Z': Undo the last move, supporting learning and analysis.
     - 'R': Reset the game to initial positions, allowing restarts.
   - **Move Log**: A panel displays move history, with scroll wheel support for reviewing past moves.
   - **Additional Features**: Includes pawn promotion (via a selection window), castling, en passant, and move animation for smoother visuals, all detailed in the game interface.

4. **AI Details**:
   - The AI, used in Player vs AI and AI vs AI modes, employs Negamax Alpha-Beta pruning with a search depth of 4. It also integrates an opening book for early-game moves, improving initial strategy. The search depth is fixed for now.

## Project Structure
```
Chess_Engine/Engine
├── ChessMain.py         # Main game loop and UI rendering
├── ChessEngine.py       # Game state and move logic
├── ChessAI.py           # Basic AI (random moves)
├── piece_images/        # Folder for chess piece images
│   ├── wP.png, bP.png, etc.
└── README.md            # Project Information
```

## Technical Highlights
- **Move Validation**: Ensures all moves adhere to chess rules, including pinned pieces and king safety.
- **Position Tracking**: Uses a dictionary to monitor game positions for threefold repetition, with plans for Zobrist hashing optimization.
- **Smooth Rendering**: Anti-aliased images enhance visual quality, adjustable via `SQUARE_SIZE`.
- **NegaMax Algorithm with Alpha Beta Pruning with Move Ordering and Quiescence Search**

## Miscellaneous Details
- **Code Style**: Adherence to PEP 8 for consistency, ensuring readability.
- **Commit Messages**: Clear descriptions to facilitate review.

## Future Improvements
- **Advanced AI**: Adding a Neural Network Engine to make the AI more complex and enhanced without much dependence on Decision Algorithms like NegaMax or MiniMax.
- **Time Controls**: Add clock functionality for timed games.
- **Zobrist Hashing**: Optimize threefold repetition detection for performance.
- **Using the concept of BitBoards to increase performance of engine**
- **Changing move calculation to make it more efficient. Instead of recalculating all moves, start with moves from previous board and change based on last move made**

#### Tables for Clarity
The following table summarizes the dependencies:

| Library       | Purpose                              | Installation Command [`pip` / `conda`]                      |
|---------------|--------------------------------------|-------------------------------------------------------------|
| Pygame        | Graphical interface                  | `pip install pygame` or `conda install conda-forge::pygame` |
| NumPy         | Board state management               | `pip install numpy` or `conda install anaconda::numpy`      |
| chess         | Chess rules and AI logic             | `pip install chess` or `conda install conda-forge::chess`   |

Game modes and controls:

| Game Mode        | Description                          | Controls                     |
|------------------|--------------------------------------|------------------------------|
| Player vs AI     | Human vs AI, choose color            | Mouse clicks, 'Z' for undo   |
| Player vs Player | Two humans play locally              | Mouse clicks, 'R' for reset  |
| AI vs AI         | Watch AIs play                       | Scroll wheel for move log    |

---

### Key Citations
- [Pygame Official Documentation Page](https://www.pygame.org/docs/)
- [NumPy User Guide and Reference](https://numpy.org/doc/)
- [chess Documentation](https://pypi.org/project/chess/)
- [Chess Engine Tutorial by Eddie Sharick](https://www.youtube.com/playlist?list=PLBwF487qi8MGU81nDGaeNE1EnNEPYWKY_)
