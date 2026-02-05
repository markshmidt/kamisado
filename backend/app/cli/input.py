# backend/app/cli/input.py
def read_move() -> tuple[int, int, int]:
    raw = input("Enter move: piece_id to_col to_row (e.g. 9 3 4): ").strip()
    parts = raw.split()
    if len(parts) != 3:
        raise ValueError("Please enter exactly 3 numbers: piece_id to_col to_row")
    pid, c, r = map(int, parts)
    return pid, c, r
