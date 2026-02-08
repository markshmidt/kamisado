from pydantic import BaseModel
from typing import List, Optional

class MoveDTO(BaseModel):
    piece_id: int
    to_col: int
    to_row: int
    
class MovePositionDTO(BaseModel):
    col: int
    row: int

class ValidMovesDTO(BaseModel):
    piece_id: int
    moves: List[MovePositionDTO]