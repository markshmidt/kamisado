# backend/app/cli/render.py
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.game.Game import Game

def piece_symbol(color: str, team: str) -> str:
    # e.g. pink white -> Pw, yellow black -> Yb
    return f"{color[0].upper()}{'w' if team=='white' else 'b'}"

def render(game: Game) -> None:
    b = game.board
    print()
    print(f"Turn: {game.turn} | Forced color: {game.forced_color} | Winner: {game.winner}")
    print("    " + "  ".join(str(c) for c in range(8)))

    for r in range(8):
        row_cells = []
        for c in range(8):
            p = b.get_piece_at(c, r)
            if p:
                row_cells.append(piece_symbol(p.color, p.team))
            else:
                # show tile color initial for empties (helps understand forced-color)
                row_cells.append(b.tile_color(c, r)[0].lower() + ".")
        print(f"{r} | " + " ".join(row_cells))
    print()
