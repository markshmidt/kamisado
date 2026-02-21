import copy
from typing import List, Tuple

from app.game.Game import Game
from app.game.Rules import Rules
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)

logger = logging.getLogger("AI")
DEBUG = True


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
        Convert a game state into a numerical score.
        Positive score  = good for ai_team
        Negative score  = good for opponent

    FACTORS USED:
        1) Terminal win/loss
        2) Progress toward winning row
        3) Center control
        4) Color mobility (Kamisado-specific)
        5) Forced color pressure 
    """

    opponent = "black" if ai_team == "white" else "white"
    score = 0.0

   # 1) Terminal state (highest priority)
    if game.winner == ai_team:
        return 1_000_000
    if game.winner == opponent:
        return -1_000_000
    
    # Immediate 1-move win detection
    for p in game.board.pieces:
        if p.team == ai_team:
            for col, row in Rules.valid_moves(p, game.board):
                if (p.direction == "down" and row == 7) or \
                (p.direction == "up" and row == 0):
                    score += 300_000

        if p.team == opponent:
            for col, row in Rules.valid_moves(p, game.board):
                if (p.direction == "down" and row == 7) or \
                (p.direction == "up" and row == 0):
                    score -= 300_000

   # 2) Progress toward winning row
   # Each piece gets points for being closer to its goal row.
   # This drives forward movement but is NOT dominant.
    PROGRESS_WEIGHT = 6

    for p in game.board.pieces:
        if p.direction == "down":      
            progress = p.row
        else:                       
            progress = 7 - p.row

        if p.team == ai_team:
            score += progress * PROGRESS_WEIGHT
        else:
            score -= progress * PROGRESS_WEIGHT
            
    ADVANCE_BONUS = 20
    for p in game.board.pieces:
        if p.team == ai_team:
            if p.direction == "down" and p.row >= 5:
                score += ADVANCE_BONUS * (p.row - 4)
            if p.direction == "up" and p.row <= 2:
                score += ADVANCE_BONUS * (3 - p.row)

        if p.team == opponent:
            if p.direction == "down" and p.row >= 5:
                score -= ADVANCE_BONUS * (p.row - 4)
            if p.direction == "up" and p.row <= 2:
                score -= ADVANCE_BONUS * (3 - p.row)

   # 3) Center control
   # Towers near the center have more diagonal options.
    CENTER_WEIGHT = 2

    for p in game.board.pieces:
        center_bonus = 3.5 - abs(p.col - 3.5)  # max around center

        if p.team == ai_team:
            score += center_bonus * CENTER_WEIGHT
        else:
            score -= center_bonus * CENTER_WEIGHT

   # 4) Color mobility map
   # Landing tile color determines
   # which tower opponent must move next.
   # So mobility of each colored tower matters.
    color_mobility = {}

    for p in game.board.pieces:
        mobility = len(Rules.valid_moves(p, game.board))
        color_mobility[(p.team, p.color)] = mobility

    # 5) Forced color pressure
    # If forced_color exists, current player must move the tower of that color.
    # Low mobility forced tower = positional pressure.
    if game.forced_color is not None:
        forced_team = game.turn
        forced_mob = color_mobility.get((forced_team, game.forced_color), 0)

        # If opponent is forced = good for us
        # If we are forced = bad for us
        if forced_team == opponent:
            if forced_mob == 0:
                score += 120  # skip turn likely 
            elif forced_mob == 1:
                score += 60
            elif forced_mob == 2:
                score += 25
        else:
            if forced_mob == 0:
                score -= 120
            elif forced_mob == 1:
                score -= 60
            elif forced_mob == 2:
                score -= 25

    # 6) Global color weakness
    # Long-term pressure: if opponent has many nearly-blocked colored towers, future forced sequences become strong
    BAD_ZERO_WEIGHT = 12
    BAD_ONE_WEIGHT = 6

    for (team, color), mobility in color_mobility.items():
        if team == opponent:
            if mobility == 0:
                score += BAD_ZERO_WEIGHT
            elif mobility == 1:
                score += BAD_ONE_WEIGHT
        else:
            if mobility == 0:
                score -= BAD_ZERO_WEIGHT
            elif mobility == 1:
                score -= BAD_ONE_WEIGHT

    return score


def minimax(
    game: Game,
    depth: int,
    alpha: float,
    beta: float,
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
    print(f"{prefix}Depth: {depth}, Turn: {game.turn}, ")


    if depth == 0 or game.winner:
        return evaluate(game, ai_team)

    moves = get_all_legal_moves(game)

    # no moves? then treat it like a leaf
    if not moves:
        return evaluate(game, ai_team)

    if game.turn == ai_team:

        max_eval = float("-inf")

        for move in moves:
            g2 = copy.deepcopy(game)

           #apply the move to the new game state
            g2.apply_move(*move)

            # Recursively evaluate next state:
            eval_score = minimax(g2, depth - 1, alpha, beta, ai_team, indent + 1)
            print(f"{prefix}Move {move} → Score {eval_score}")

            # Keep best score
            max_eval = max(max_eval, eval_score)

            # Update alpha
            alpha = max(alpha, eval_score)
            

            # Alpha-beta pruning:
            # If alpha >= beta, opponent will avoid this branch, so stop exploring
        
            if beta <= alpha:
              if DEBUG:
                    logger.info(f"Pruned branch at depth {depth}")
              break

        print(f"{prefix}Returning {max_eval}")
        return max_eval

    # "Opponent turn" in minimax terms: choose the move with lowest score (worst for AI)
    else:
        min_eval = float("inf")

        for move in moves:
            g2 = copy.deepcopy(game)
            g2.apply_move(*move)

            eval_score = minimax(g2, depth - 1, alpha, beta, ai_team)

            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
              if DEBUG:
                    logger.info(f"Pruned branch at depth {depth}")
              break
        
        return min_eval


def choose_best_move(game: Game, ai_team: str, depth: int = 5) -> Move | None:


    best_score = float("-inf")
    best_move: Move | None = None

    moves = get_all_legal_moves(game)
    logger.info(f"\nAI ({ai_team}) evaluating {len(moves)} moves at depth {depth}")


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
            ai_team
        )
        logger.info(f"Move {move} → Score {score}")

        # Keep the move with highest minimax score
        if score > best_score:
            best_score = score
            best_move = move

    logger.info(f"BEST MOVE: {best_move}")
    logger.info(f"BEST SCORE: {best_score}")
    logger.info("-" * 40)
    return best_move