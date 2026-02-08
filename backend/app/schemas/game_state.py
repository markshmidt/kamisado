from pydantic import BaseModel
from typing import List, Optional
from app.schemas.piece import PieceDTO

class GameStateDTO(BaseModel):
    turn: str
    forced_color: Optional[str]
    winner: Optional[str]
    pieces: List[PieceDTO]
