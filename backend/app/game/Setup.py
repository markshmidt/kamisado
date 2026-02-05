# backend/app/game/setup.py
from .Piece import Piece
from .Board import Board

def setup_pieces(board: Board) -> None:
    board.pieces.clear() # clear the board of all pieces
    pid = 0 # piece id

    # Black at row 0, direction down
    for col, color in enumerate(Board.COLORS):
        board.pieces.append(Piece(id=pid, col=col, row=0, 
                                  color=color, # color of the piece is the color of the tile
                                  team="black", direction="down"))
        pid += 1

    # White at row 7, direction up
    for col, color in enumerate(Board.COLORS):
        board.pieces.append(Piece(id=pid, col=col, row=7, color=color, team="white", direction="up"))
        pid += 1
