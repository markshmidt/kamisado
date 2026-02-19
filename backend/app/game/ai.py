import copy
from typing import List, Tuple

from app.game.Game import Game
from app.game.Rules import Rules


# A "move" in our AI is represented as:
# (piece_id, to_col, to_row)
# Example: (12, 3, 5) means:
#   "Move piece with id=12 to column 3, row 5"
Move = Tuple[int, int, int]


def get_all_legal_moves(game: Game) -> List[Move]:
    """
    PURPOSE:
      Build the FULL list of legal moves for the *current player* in the given game state.

    WHY WE NEED IT:
      - Rules.valid_moves(piece, board) gives moves for ONE piece
      - Minimax needs ALL possible actions from the current state (branching).

    RETURNS:
      A list of tuples: [(piece_id, to_col, to_row), ...]
      If game is over -> returns empty list
    """

    moves: List[Move] = []

    if game.winner:
        return moves  # []

    allowed_ids = game.allowed_piece_ids()

    for pid in allowed_ids:
        piece = game.board.pieces[pid]

        # Rules.valid_moves(piece, board) RETURNS:
        # list[(col, row)] e.g. [(3,2), (4,3), ...]
        valid_destinations = Rules.valid_moves(piece, game.board)

        for col, row in valid_destinations:
            moves.append((pid, col, row))

    return moves


def evaluate(game: Game, ai_team: str) -> float:
    """
    PURPOSE:
      Convert a game state into a number:
        - high number = good for ai_team
        - low number = good for opponent

    RETURNS:
      A float score.

    KEY IDEA:
      Minimax explores into the future, but it needs a scoring rule for leaf nodes.
    """


    if game.winner == ai_team:
        return 1_000_000 
    if game.winner and game.winner != ai_team:
        return -1_000_000  

    score = 0

    for p in game.board.pieces:
        if p.direction == "down":
            progress = p.row
        else:
            progress = 7 - p.row

        # If this piece belongs to the AI -> add progress
        # If it belongs to opponent -> subtract progress
        if p.team == ai_team:
            score += progress * 10
        else:
            score -= progress * 10


    # Mobility = number of legal moves available RIGHT NOW
    mobility = len(get_all_legal_moves(game))

    # If it's AI's turn and AI has lots of moves -> good
    # If it's opponent's turn and opponent has lots of moves -> bad 
    if game.turn == ai_team:
        score += mobility
    else:
        score -= mobility

    return score


def minimax(
    game: Game,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    ai_team: str,
    indent: int = 0
) -> float:
    """
    PURPOSE:
      Search forward (simulate future moves) and return the best achievable score.

    PARAMETERS:
      game        : current game state
      depth       : how many moves ahead we search
      alpha/beta  : pruning boundaries (speed optimization)
      maximizing  : True if it's AI's "best choice" turn in this recursion layer
      ai_team     : which side is AI ("white" or "black")

    RETURNS:
      A float score representing how good this position is for ai_team.
    """
    
    #logging the current state of the game
    prefix = "  " * indent
    print(f"{prefix}Depth: {depth}, Turn: {game.turn}, Maximizing: {maximizing}")


    if depth == 0 or game.winner:
        return evaluate(game, ai_team)

    moves = get_all_legal_moves(game)

    # no moves? then treat it like a leaf
    if not moves:
        return evaluate(game, ai_team)

    if maximizing:
        max_eval = float("-inf")

        for move in moves:
            g2 = copy.deepcopy(game)

           #apply the move to the new game state
            g2.apply_move(*move)

            # Recursively evaluate next state:
            eval_score = minimax(g2, depth - 1, alpha, beta, False, ai_team, indent + 1)
            print(f"{prefix}Move {move} → Score {eval_score}")

            # Keep best score
            max_eval = max(max_eval, eval_score)

            # Update alpha
            alpha = max(alpha, eval_score)
            

            # Alpha-beta pruning:
            # If alpha >= beta, opponent will avoid this branch, so stop exploring
            if beta <= alpha:
                break

        print(f"{prefix}Returning {max_eval}")
        return max_eval

    # "Opponent turn" in minimax terms: choose the move with lowest score (worst for AI)
    else:
        min_eval = float("inf")

        for move in moves:
            g2 = copy.deepcopy(game)
            g2.apply_move(*move)

            eval_score = minimax(g2, depth - 1, alpha, beta, True, ai_team)

            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        
        return min_eval


def choose_best_move(game: Game, ai_team: str, depth: int = 5) -> Move | None:
    """
    PURPOSE:
      1) generate all legal moves for current position
      2) simulate each move
      3) call minimax for the opponent response
      4) pick the move with highest score

    RETURNS:
      best_move: (piece_id, to_col, to_row)
      or None if no moves exist
    """

    best_score = float("-inf")
    best_move: Move | None = None

    moves = get_all_legal_moves(game)

    for move in moves:
        g2 = copy.deepcopy(game)
        g2.apply_move(*move)

        # After AI makes 1 move, it's opponent's "turn" in minimax tree,
        # so maximizing=False here
        score = minimax(
            g2,
            depth - 1,
            float("-inf"),
            float("inf"),
            False,
            ai_team
        )
        print(f"Top-level move: {move}")
        print(f"Score: {score}")

        # Keep the move with highest minimax score
        if score > best_score:
            best_score = score
            best_move = move

    print(f"Best move: {best_move}")
    print(f"Best score: {best_score}")
    return best_move
