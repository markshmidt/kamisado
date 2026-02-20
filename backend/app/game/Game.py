# backend/app/game/engine.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from app.game.Board import Board
from app.game.Rules import Rules
from app.game.Setup import setup_pieces


@dataclass
class Game:
    board: Board
    turn: str = "white"
    forced_color: Optional[str] = None # the color of the tile that the piece must land on
    winner: Optional[str] = None
    last_player: Optional[str] = None

    @staticmethod
    def new() -> "Game": # create a new game
        b = Board()
        setup_pieces(b)
        return Game(board=b)

    def allowed_piece_ids(self) -> list[int]: # get the ids of the pieces that are allowed to move
        ids = []
        for p in self.board.pieces:
            if p.team != self.turn:
                continue
            if self.forced_color is None or p.color == self.forced_color:
                ids.append(p.id)
        return ids

    def apply_move(self, piece_id: int, to_col: int, to_row: int) -> None:
        if self.winner:
            raise ValueError("Game is over. Reset to play again.")

        piece = self.board.pieces[piece_id]

        if piece.team != self.turn:
            raise ValueError(f"Not your turn. It is {self.turn}'s turn.")

        if self.forced_color is not None and piece.color != self.forced_color:
            raise ValueError(f"Forced color is {self.forced_color}. You must move the {self.forced_color} piece.")

        moves = Rules.valid_moves(piece, self.board)
        if (to_col, to_row) not in moves:
            raise ValueError("Illegal move for this piece.")

        # move
        piece.col = to_col
        piece.row = to_row
        
        # last player is the player who made the move
        self.last_player = piece.team

        # forced color becomes the TILE color you landed on
        self.forced_color = self.board.tile_color(to_col, to_row)

        # win check (reach opponent baseline)
        if piece.direction == "down" and piece.row == 7:
                self.winner = piece.team
                return

        if piece.direction == "up" and piece.row == 0:
            self.winner = piece.team
            return

        # swap turn
        self.turn = "black" if self.turn == "white" else "white"
        
        # Special case: if the piece is forced to move but does not have any valid moves, it is considered as move with 
        # zero mobility, so the opponent does a move again depending on the last player's piece color tile
        forced_piece = None
        for p in self.board.pieces:
            if p.team == self.turn and p.color == self.forced_color:
                forced_piece = p
                break

        if forced_piece:
            forced_moves = Rules.valid_moves(forced_piece, self.board)

            # If forced piece is blocked -> skip turn
            if not forced_moves:

                # Skip turn
                self.turn = "black" if self.turn == "white" else "white"

                # Forced color becomes color under blocked piece
                self.forced_color = self.board.tile_color(
                    forced_piece.col,
                    forced_piece.row
                )

                # Deadlock case
                # Now check if this forced piece also blocked
                next_forced_piece = None
                for p in self.board.pieces:
                    if p.team == self.turn and p.color == self.forced_color:
                        next_forced_piece = p
                        break

                if next_forced_piece:
                    next_moves = Rules.valid_moves(next_forced_piece, self.board)

                    if not next_moves:
                        # DEADLOCK
                        # Player who caused it (last_player) loses
                        self.winner = (
                            "black" if self.last_player == "white" else "white"
                        )
                        return
        
        if self.winner:
            raise ValueError("Game is already over")

