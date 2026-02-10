from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.game.Game import Game
from app.game.Rules import Rules

from app.schemas.game_state import GameStateDTO
from app.schemas.move import MoveDTO, MovePositionDTO, ValidMovesDTO
from app.schemas.piece import PieceDTO

app = FastAPI()

# CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SINGLE in-memory game
game = Game.new()


@app.get("/state", response_model=GameStateDTO)
def get_state():
    return GameStateDTO(
        turn=game.turn,
        forced_color=game.forced_color,
        winner=game.winner,
        pieces=[
            PieceDTO(
                id=p.id,
                col=p.col,
                row=p.row,
                color=p.color,
                team=p.team,
            )
            for p in game.board.pieces
        ],
    )


@app.post("/move", response_model=GameStateDTO)
def make_move(move: MoveDTO):
    try:
        game.apply_move(
            piece_id=move.piece_id,
            to_col=move.to_col,
            to_row=move.to_row,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return get_state()


@app.get("/valid-moves/{piece_id}", response_model=ValidMovesDTO)
def get_valid_moves(piece_id: int):
    piece = next((p for p in game.board.pieces if p.id == piece_id), None)
    if piece is None:
        raise HTTPException(status_code=404, detail="Piece not found")

    # turn & forced color guards
    if piece.team != game.turn:
        return ValidMovesDTO(piece_id=piece_id, moves=[])

    if game.forced_color and piece.color != game.forced_color:
        return ValidMovesDTO(piece_id=piece_id, moves=[])

    moves = Rules.valid_moves(piece, game.board)

    return ValidMovesDTO(
        piece_id=piece_id,
        moves=[MovePositionDTO(col=c, row=r) for c, r in moves],
    )
@app.post("/reset")
def reset():
    global game
    game = Game.new()
    return {"status": "ok"}
