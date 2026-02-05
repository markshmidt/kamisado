# backend/app/game/piece.py
from dataclasses import dataclass

@dataclass
class Piece:
    id: int
    col: int
    row: int
    color: str        
    team: str         # "white" | "black"
    direction: str    # "up" | "down"
