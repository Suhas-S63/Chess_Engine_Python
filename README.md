# Chess Engine in Python

A fully functional chess engine built with Python and Pygame, designed to simulate a complete chess game with an intuitive graphical interface and robust game logic. This project includes a variety of features inspired by professional platforms like Chess.com, such as algebraic notation, scrollable move logs, and support for all standard chess rules.

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
- **Pawn Promotion UI**: Interactive overlay for selecting promotion pieces (Queen, Rook, Bishop, Knight), styled like Chess.com.
- **Move Log Panel**:
  - Scrollable log displaying move history in algebraic notation.
  - Clean, table-like layout with columns for move number, White’s move, and Black’s move.
  - Styled with a white background and black text for readability.

### Technical Details
- **Algebraic Notation**: Comprehensive move notation in the `Move` class, supporting:
  - Disambiguation for identical piece types (e.g., `Nbd2` for knights).
  - Capture notation (e.g., `exd5`).
  - Promotion (e.g., `e8=Q`).
  - Check (`+`) and checkmate (`#`) indicators.
- **AI Opponent**: Basic random-move AI (placeholder for future enhancements).
- **Modular Design**:
  - `ChessMain.py`: Handles the game loop, input, and rendering.
  - `ChessEngine.py`: Core logic for game state, move generation, and validation.

## Installation

### Prerequisites
- **Python 3.6+**: Ensure Python is installed on your system.
- **Pygame**: Required for rendering the GUI.

### Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Suhas-S63/Chess_Engine_Python.git
   cd Chess_Engine_Python
   ```
2. **Install Dependencies**:
   ```bash
   pip install pygame
   ```
3. **Add Piece Images**:
   - Place high-quality chess piece PNGs (e.g., `wP.png`, `bK.png`) in a `piece_images/` folder within the project directory.
   - Recommended resolution: At least 128x128 pixels for smooth scaling.
4. **Run the Game**:
   ```bash
   python ChessMain.py
   ```

## Usage
- **Playing**: Click squares to select and move pieces. Use the mouse wheel to scroll the move log.
- **Undo**: Press `Z` to undo the last move.
- **Reset**: Press `R` to start a new game.
- **Promotion**: When a pawn reaches the last rank, a UI appears to choose a promotion piece.

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

## Future Improvements
- **Advanced AI**: Replace random-move AI with minimax or alpha-beta pruning.
- **Time Controls**: Add clock functionality for timed games.
- **Zobrist Hashing**: Optimize threefold repetition detection for performance.


## **Built With**: Python and Pygame

---