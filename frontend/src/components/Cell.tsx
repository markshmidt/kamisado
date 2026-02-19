import type { TileColor } from "../types";

const TILE_COLORS: Record<TileColor, string> = {
    brown: "#8B4513",
    turquoise: "#40E0D0",
    blue: "#1E90FF",
    yellow: "#FFD700",
    pink: "#FF69B4",
    green: "#32CD32",
    red: "#DC143C",
    orange: "#FFA500",
};

interface CellProps {
    tileColor: TileColor;
    size: number;
    // highlight if this cell is a valid move destination
    highlighted: boolean;
    onClick: () => void;
}

export function Cell({ tileColor, size, highlighted, onClick }: CellProps) {
    return (
        <div
            onClick={onClick}
            style={{
                width: size,
                height: size,

                // tile color
                backgroundColor: TILE_COLORS[tileColor],

                boxSizing: "border-box",
                position: "relative",
            }}
        >
            {highlighted && (
                <div
                    style={{
                        position: "absolute",
                        inset: 0,
                        border: "4px solid white",
                        pointerEvents: "none",
                        boxSizing: "border-box",
                    }}
                />
            )}
        </div>
    );
}
