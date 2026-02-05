# backend/app/cli/cli.py
from app.game.Game import Game
from app.cli.render import render
from app.cli.input import read_move


def main():
    game = Game.new()

    while True:
        render(game)

        if game.winner:
            cmd = input("Game over. Type 'r' to restart or 'q' to quit: ").strip().lower()
            if cmd == "r":
                game = Game.new()
                continue
            if cmd == "q":
                break
            continue

        print("Allowed piece ids:", game.allowed_piece_ids())

        try:
            pid, c, r = read_move()
            game.apply_move(pid, c, r)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
