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
      Convert a game state into a number:
        - high number = good for ai_team
        - low number = good for opponent

    RETURNS:
      A float score.

    KEY IDEA:
      Minimax explores into the future, but it needs a scoring rule for leaf nodes.
    """
    
    score = 0
    opponent = "black" if ai_team == "white" else "white"
    
    if game.winner == ai_team:
        return 1_000_000 
    if game.winner and game.winner != ai_team:
        return -1_000_000  
    
    
    if game.forced_color:
      # check if forced color piece is stuck / has little mobility
      forced_piece = None
      for p in game.board.pieces:
          if p.team == game.turn and p.color == game.forced_color:
              forced_piece = p
              break

      if forced_piece:
          forced_moves = Rules.valid_moves(forced_piece, game.board)
          if len(forced_moves) <= 2:
              if game.turn == opponent:
                  score += 50


    for p in game.board.pieces:
        if p.direction == "down":
            progress = p.row
        else:
            progress = 7 - p.row


            
    # tactical evaluation: check if the opponent has any moves that will win the game
    if game.turn == opponent:
        moves = get_all_legal_moves(game)
        
        # if len(moves) < 4:
        #     score += (4 - len(moves)) * 20
            
        for move in moves:
            g2 = copy.deepcopy(game)
            g2.apply_move(*move)
            if g2.winner == opponent:
                score -= 500_000  # huge danger
                break
            g2_op = copy.deepcopy(g2)

            if len(get_all_legal_moves(g2_op)) <= 2:
                score += 25
         
    if game.turn == ai_team:
        moves = get_all_legal_moves(game)
        for move in moves:
            g2 = copy.deepcopy(game)
            g2.apply_move(*move)
            if g2.winner == ai_team:
                score += 500_000
                
                break
              
    # center bonus: give a bonus to pieces that are closer to the center of the board
    for p in game.board.pieces:
      center_bonus = 3 - abs(p.col - 3.5)

      if p.team == ai_team:
          score += center_bonus * 2
      else:
          score -= center_bonus * 2

    # AI mobility
    g_ai = copy.deepcopy(game)
    g_ai.turn = ai_team
    ai_mobility = len(get_all_legal_moves(g_ai))

    # Opponent mobility
    g_op = copy.deepcopy(game)
    g_op.turn = opponent
    opp_mobility = len(get_all_legal_moves(g_op))

    score += (ai_mobility - opp_mobility) * 3
    total_progress = sum(
    p.row if p.direction == "down" else 7 - p.row
    for p in game.board.pieces
  )
    #mobility
    color_mobility = {}  # (team, color) → mobility count

    for p in game.board.pieces:
        mobility = len(Rules.valid_moves(p, game.board))
        color_mobility[(p.team, p.color)] = mobility

        if total_progress < 20:
            score += (ai_mobility - opp_mobility) * 5
        else:
            score += progress * 8
    # -----------------------------------------
# Forced color quality
# -----------------------------------------
    if game.forced_color:
        forced_team = game.turn
        forced_mobility = color_mobility.get(
            (forced_team, game.forced_color), 0
        )

        if forced_team != ai_team:
            # opponent forced into weak tower
            if forced_mobility == 0:
                score += 100
            elif forced_mobility == 1:
                score += 50
            elif forced_mobility == 2:
                score += 20
            elif forced_mobility >= 5:
                score -= 10  # we gave opponent flexibility

        else:
            # we are forced into weak tower
            if forced_mobility == 0:
                score -= 100
            elif forced_mobility == 1:
                score -= 50
            elif forced_mobility == 2:
                score -= 20
            elif forced_mobility >= 5:
                score += 10
    # -----------------------------------------
    # Opponent bad color pressure
    # -----------------------------------------
    opponent = "black" if ai_team == "white" else "white"

    for (team, color), mobility in color_mobility.items():
        if team == opponent:
            if mobility == 0:
                score += 15
            elif mobility == 1:
                score += 8
    for (team, color), mobility in color_mobility.items():
        if team == ai_team:
            if mobility == 0:
                score -= 15
            elif mobility == 1:
                score -= 8
            
    if game.forced_color:
      forced_piece = None
      for p in game.board.pieces:
          if p.team == game.turn and p.color == game.forced_color:
              forced_piece = p
              break

      if forced_piece:
          forced_moves = Rules.valid_moves(forced_piece, game.board)

          mobility = len(forced_moves)

          # If opponent's forced tower is weak → good
          if game.turn != ai_team:
              if mobility == 0:
                  score += 80  # skip turn imminent
              elif mobility == 1:
                  score += 30  # almost blocked
              elif mobility == 2:
                  score += 10

          # If OUR forced tower is weak → bad
          else:
              if mobility == 0:
                  score -= 80
              elif mobility == 1:
                  score -= 30
              elif mobility == 2:
                  score -= 10
    # If opponent forced piece is completely blocked
    if game.forced_color:
        forced_piece = None
        for p in game.board.pieces:
            if p.team == game.turn and p.color == game.forced_color:
                forced_piece = p
                break

        if forced_piece:
            forced_moves = Rules.valid_moves(forced_piece, game.board)

            if not forced_moves and game.turn != ai_team:
                score += 120  # double move opportunity
                
    total_opp_moves = 0
    for p in game.board.pieces:
        if p.team == opponent:
            total_opp_moves += len(Rules.valid_moves(p, game.board))

    if total_opp_moves <= 4:
        score += 25

          
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