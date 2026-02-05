from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .Piece import Piece

class Board:
    WIDTH = 8
    HEIGHT = 8
    COLORS = ["brown", "turquoise", "blue", "yellow", "pink", "green", "red", "orange"]

    def __init__(self):
        self.pieces: list[Piece] = []

    def tile_color(self, col: int, row: int) -> str:
        return self.COLORS[(col + row) % len(self.COLORS)]

    def get_piece_at(self, col: int, row: int) -> Optional[Piece]:
        for p in self.pieces:
            if p.col == col and p.row == row:
                return p
        return None
