# backend/app/game/rules.py
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Piece import Piece
    from .Board import Board

class Rules:
    @staticmethod
    def valid_moves(piece: Piece, board: Board) -> list[tuple[int, int]]:
        moves: list[tuple[int, int]] = []

        if piece.team == "white":
            directions = [(0, -1), (-1, -1), (1, -1)] # up, up-left, up-right
        else:
            directions = [(0, 1), (-1, 1), (1, 1)] # down, down-left, down-right 

        for dx, dy in directions:
            step = 1
            while True:
                c = piece.col + dx * step # column of the new position
                r = piece.row + dy * step # row of the new position

                if not (0 <= c < board.WIDTH and 0 <= r < board.HEIGHT): # check if the new position is on the board
                    break

                if board.get_piece_at(c, r) is None: # check if the new position is empty (if there is another piece there, the move is not valid)
                    moves.append((c, r)) # add the new position to the list of valid moves
                    step += 1 # increment the step
                else:
                    break

        return moves
