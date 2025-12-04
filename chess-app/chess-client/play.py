import requests
from chess import Board
import os

API_URL = os.getenv("API_URL", "http://backend-test:80")  # default if running inside minikube

def print_board(board):
    print(board)
    print()

def main():
    print("Starting a new game...")

    try:
        game_id = requests.get(f"{API_URL}/start").json()["game_id"]
    except Exception as e:
        print("ERROR contacting backend:", API_URL)
        print(e)
        return

    board = Board()
    print_board(board)

    while not board.is_game_over():
        move_uci = input("Your move (e.g., e2e4): ").strip()

        try:
            board.push_uci(move_uci)
        except Exception:
            print("Invalid move, try again.")
            continue

        print("\nYou played:", move_uci)
        print_board(board)

        print("Waiting for engine response...")
        res = requests.post(
            f"{API_URL}/move",
            json={
                "game_id": game_id,
                "move": move_uci,
                "fen": board.fen()
            }
        )

        if not res.ok:
            print("Backend error:", res.text)
            break

        data = res.json()
        engine_move = data["best_move"]

        print("Engine plays:", engine_move)
        board.push_uci(engine_move)
        print_board(board)

    print("Game over!")
    print(board.result())

if __name__ == "__main__":
    main()
