import type { GameStateDTO, MovePosition, PieceDTO, TileColor } from "../types";
import { Cell } from "./Cell";
import { Piece } from "./Piece";

// ------------------------------
// Board uses Kamisado tile pattern:
// (row + col) % 8 maps to color
// ------------------------------;

const TILE_SIZE = 90;

interface BoardProps {
    game: GameStateDTO;

    // Which piece is selected (for highlight + drag rules)
    selectedPiece: PieceDTO | null;

    // Valid moves for selected piece
    validMoves: MovePosition[];

    // When user tries to select a piece
    onSelectPiece: (piece: PieceDTO) => void;

    onDeselect: () => void;
    // When user tries to move selected piece to col,row
    onTryMove: (col: number, row: number) => void;
}
const TILE_COLORS_ORDER: TileColor[] = [
    "brown",
    "turquoise",
    "blue",
    "yellow",
    "pink",
    "green",
    "red",
    "orange",
];

function getTileColor(row: number, col: number): TileColor {
    return TILE_COLORS_ORDER[(row + col) % 8];
}

export function Board({
    game,
    selectedPiece,
    validMoves,
    onSelectPiece,
    onTryMove,
    onDeselect
}: BoardProps) {
    return (
        <div
            style={{
                position: "relative",
                width: TILE_SIZE * 8,
                height: TILE_SIZE * 8,
            }}
        >
            {/* TILE GRID */}
            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: `repeat(8, ${TILE_SIZE}px)`,
                    gridTemplateRows: `repeat(8, ${TILE_SIZE}px)`,
                    position: "absolute",
                    inset: 0,
                    zIndex: 1,
                }}
                onClick={() => onDeselect()}

            >
                {Array.from({ length: 8 }).map((_, row) =>
                    Array.from({ length: 8 }).map((_, col) => (
                        <Cell
                            key={`${row}-${col}`}
                            tileColor={getTileColor(row, col)}
                            size={TILE_SIZE}
                            highlighted={validMoves.some(
                                (m) => m.col === col && m.row === row
                            )}
                            onClick={() => onTryMove(col, row)}
                        />
                    ))
                )}
            </div>

            {/* VALID MOVE DOTS */}
            {validMoves.map((m, i) => (
                <div
                    key={i}
                    style={{
                        position: "absolute",
                        left: m.col * TILE_SIZE + TILE_SIZE / 2 - 5,
                        top: m.row * TILE_SIZE + TILE_SIZE / 2 - 5,
                        width: 10,
                        height: 10,
                        borderRadius: "50%",
                        background: "rgba(0,0,0,0.6)",
                        zIndex: 2,
                        pointerEvents: "none",
                    }}
                />
            ))}

            {/*PIECES (ABSOLUTE = DRAG WORKS) */}
            {game.pieces.map((piece) => {
                const disabled =
                    piece.team !== game.turn ||
                    (game.forced_color !== null && piece.color !== game.forced_color);


                return (
                    <Piece
                        piece={piece}
                        disabled={disabled}
                        tileSize={TILE_SIZE}
                        validMoves={validMoves}
                        isSelected={selectedPiece?.id === piece.id}
                        onSelect={() => onSelectPiece(piece)}
                        onDeselect={onDeselect}


                        onDropTo={(col, row) => onTryMove(col, row)}
                    />


                );
            })}
        </div>
    );
}
