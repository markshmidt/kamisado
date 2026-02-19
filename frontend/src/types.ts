export type Team = "white" | "black";

export type TileColor =
    | "brown"
    | "turquoise"
    | "blue"
    | "yellow"
    | "pink"
    | "green"
    | "red"
    | "orange";

export interface PieceDTO {
    id: number;
    col: number;
    row: number;
    color: TileColor;
    team: Team;
}

export interface GameStateDTO {
    turn: Team;
    forced_color: TileColor | null;
    winner: Team | null;
    pieces: PieceDTO[];
}

export interface MovePosition {
    col: number;
    row: number;
}

export interface ValidMovesDTO {
    piece_id: number;
    moves: MovePosition[];
}

export interface MoveDTO {
    piece_id: number;
    to_col: number;
    to_row: number;
}
