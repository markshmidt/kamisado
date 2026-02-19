import { useEffect, useMemo, useState } from "react";
import { Board } from "../components/Board";
import { getState, getValidMoves, makeMove, resetGame } from "../services/api";
import type { GameStateDTO, MovePosition, PieceDTO } from "../types";

export function Game() {
    //state hooks
    const [game, setGame] = useState<GameStateDTO | null>(null);
    const [selectedPiece, setSelectedPiece] = useState<PieceDTO | null>(null);
    const [validMoves, setValidMoves] = useState<MovePosition[]>([]);

    // ------------------------------
    // EFFECTS
    // ------------------------------
    useEffect(() => {
        loadState();
    }, []);

    // ------------------------------
    // MEMO HOOK (MUST BE BEFORE RETURN)
    // ------------------------------
    const forcedColorLabel = useMemo(
        () => game?.forced_color ?? "any",
        [game?.forced_color]
    );

    // ------------------------------
    // EARLY RETURN AFTER ALL HOOKS
    // ------------------------------
    if (!game) return <div>Loading…</div>;

    // ------------------------------
    // HELPERS
    // ------------------------------
    async function loadState() {
        const state = await getState();
        setGame(state);
        setSelectedPiece(null);
        setValidMoves([]);
    }
    function deselect() {
        setSelectedPiece(null);
        setValidMoves([]);
    }


    async function handleSelectPiece(piece: PieceDTO) {
        if (game.winner) return;

        if (piece.team !== game.turn) return;
        if (game.forced_color && piece.color !== game.forced_color) return;
        if (selectedPiece?.id === piece.id) {
            setSelectedPiece(null);
            setValidMoves([]);
            return;
        }

        setSelectedPiece(piece);
        const res = await getValidMoves(piece.id);
        setValidMoves(res.moves);
    }

    async function handleTryMove(toCol: number, toRow: number) {
        if (game.winner) return;

        if (!selectedPiece) return;

        const allowed = validMoves.some(
            (m) => m.col === toCol && m.row === toRow
        );
        if (!allowed) return;

        const newState = await makeMove({
            piece_id: selectedPiece.id,
            to_col: toCol,
            to_row: toRow,
        });

        setGame(newState);
        setSelectedPiece(null);
        setValidMoves([]);
    }
    const isGameOver = Boolean(game.winner);


    // ------------------------------
    // RENDER
    // ------------------------------
    return (
        <div style={{ padding: 16, display: "grid", placeItems: "center" }}>
            {
                game.winner && (
                    <div
                        style={{
                            position: "absolute",
                            inset: 0,
                            background: "rgba(0,0,0,0.6)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "white",
                            fontSize: 32,
                            fontWeight: "bold",
                            zIndex: 100,
                        }}
                    >
                        <p>{game.winner.toUpperCase()} WINS!!</p>
                        <br></br>
                        <button
                            onClick={async () => {
                                await resetGame();
                                await loadState();
                            }}
                        >
                            Restart Game
                        </button>
                    </div>
                )
            }
            < h2 > Turn: {game.turn}</h2 >
            <h3>Forced color: {forcedColorLabel}</h3>

            <Board
                game={game}
                selectedPiece={selectedPiece}
                validMoves={isGameOver ? [] : validMoves}
                onSelectPiece={isGameOver ? () => { } : handleSelectPiece}
                onTryMove={isGameOver ? () => { } : handleTryMove}
                onDeselect={deselect}
            />

            <div style={{ marginTop: 16, display: "flex", gap: 12 }}>
                <button
                    onClick={async () => {
                        await resetGame();
                        await loadState();
                    }}
                >
                    Restart Game
                </button>

            </div>
        </div >
    );
}
