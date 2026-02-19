import { useEffect, useRef, useState } from "react";
import type { MovePosition, PieceDTO } from "../types";

interface PieceProps {
    piece: PieceDTO;

    // whether this piece is allowed to be interacted with
    disabled: boolean;

    tileSize: number;

    validMoves: MovePosition[];

    // called when user starts interacting
    onSelect: () => void;

    // called when user drops on a destination cell
    onDropTo: (col: number, row: number) => void;

    // called when user clicks on piece second time / clicks outside of piece
    onDeselect?: () => void;

    isSelected: boolean;
}

export function Piece({
    piece,
    disabled,
    tileSize,
    validMoves,
    onSelect,
    onDropTo,
    onDeselect,
    isSelected,
}: PieceProps) {

    const [dragging, setDragging] = useState(false);

    // pixel position of dragging piece ralively to board
    const [dragPos, setDragPos] = useState<{ x: number; y: number } | null>(null);

    // Where inside the piece the user grabbed (so it doesn't jump)
    const offsetRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

    // pixel pos of piece
    const baseLeft = piece.col * tileSize;
    const baseTop = piece.row * tileSize;

    // where to render piece
    const left = dragPos ? dragPos.x : baseLeft;
    const top = dragPos ? dragPos.y : baseTop;


    useEffect(() => {
        function onMouseMove(e: MouseEvent) {
            if (!dragging) return;

            // new pixel position = mouse - offset
            setDragPos({
                x: e.clientX - offsetRef.current.x,
                y: e.clientY - offsetRef.current.y,
            });
        }

        function onMouseUp() {
            if (!dragging) return;
            setDragging(false);

            if (!dragPos) return;

            // convert pixel back to board cell indices
            const dropCol = Math.round(dragPos.x / tileSize);
            const dropRow = Math.round(dragPos.y / tileSize);

            // if dropped outside board -> cancel back to base
            if (dropCol < 0 || dropCol > 7 || dropRow < 0 || dropRow > 7) {
                setDragPos(null);
                return;
            }

            // only allow if destination is in validMoves
            const allowed = validMoves.some((m) => m.col === dropCol && m.row === dropRow);

            if (allowed) {
                onDropTo(dropCol, dropRow);
            }

            // reset local drag position so it snaps to backend-updated state
            setDragPos(null);
        }

        window.addEventListener("mousemove", onMouseMove);
        window.addEventListener("mouseup", onMouseUp);

        return () => {
            window.removeEventListener("mousemove", onMouseMove);
            window.removeEventListener("mouseup", onMouseUp);
        };
    }, [dragging, dragPos, tileSize, validMoves, onDropTo]);


    function handleMouseDown(e: React.MouseEvent) {
        if (disabled) return;

        // ensure parent selects piece and loads valid moves
        onSelect();

        // start dragging
        setDragging(true);
        // compute offset
        offsetRef.current = {
            x: e.clientX - baseLeft,
            y: e.clientY - baseTop,
        };
    }


    const imgSrc = `/src/assets/pieces/${piece.color}_${piece.team}.png`;

    return (
        <div
            // absolutely positioned within board
            style={{
                position: "absolute",
                left,
                top,
                width: tileSize,
                height: tileSize,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",


                // show selection
                outline: isSelected ? "3px solid white" : "none",
                borderRadius: 8,

                opacity: disabled ? 0.7 : 1,
                cursor: disabled ? "not-allowed" : dragging ? "grabbing" : "grab",

                // make dragging render above other pieces
                zIndex: dragging ? 10 : 5,
            }}
            onMouseDown={handleMouseDown}
            // prevent browser image dragging behavior
            onDragStart={(e) => e.preventDefault()}

        >
            <img
                src={imgSrc}
                alt=""
                draggable={false}
                style={{
                    width: "95%",
                    height: "95%",
                    userSelect: "none",


                }}
            />
        </div>
    );
}
