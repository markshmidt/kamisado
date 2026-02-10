# backend/app/game/setup.py
from .Piece import Piece
from .Board import Board

def setup_pieces(board: Board) -> None:
    board.pieces.clear() # clear the board of all pieces
    pid = 0 # piece id

    black_row = 0
    for col in range(Board.WIDTH):
        tile_color = board.tile_color(col, black_row)
        board.pieces.append(
            Piece(
                id=pid,
                col=col,
                row=black_row,
                color=tile_color,
                team="black",
                direction="down",
            )
        )
        pid += 1

    # --- WHITE: bottom home row (row = 7), moves UP ---
    white_row = Board.HEIGHT - 1
    for col in range(Board.WIDTH):
        tile_color = board.tile_color(col, white_row)
        board.pieces.append(
            Piece(
                id=pid,
                col=col,
                row=white_row,
                color=tile_color,
                team="white",
                direction="up",
            )
        )
        pid += 1
