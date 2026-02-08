from pydantic import BaseModel
from typing import List, Optional

class PieceDTO(BaseModel):
    id: int
    col: int
    row: int
    color: str
    team: str