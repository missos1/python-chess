import chess
import chess.engine
import chess.svg
import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path
import webbrowser

BASE_DIR = Path(__file__).resolve().parent
THIS_BOT_PATH = str((BASE_DIR / "main.py").resolve())
STOCKFISH_PATH = r"C:\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"
SVG_PATH = BASE_DIR / "board.svg"
HTML_PATH = BASE_DIR / "board_viewer.html"
THINK_TIME = 3.0


def ask_render_svg():
    while True:
        user_input = input("Render SVG ? [y/n]:").strip().lower()
        if user_input == "y":
            print("Starting game with rendering...")
            return True
        if user_input == "n":
            print("Starting game without rendering...")
            return False
        
def ask_match_config():
    while True:
        user_input = input("Run single match at specific ELO or full hard coded? [elo/full]:").strip().lower()
        if user_input == "elo":
            while True:
                # Hard coded test. Tweak later.
                elo_input = input("Enter Stockfish ELO:").strip()
                if elo_input.isdigit() and int(elo_input) in range(3000):
                    game_nums = input("Enter number of games to play at this ELO:").strip()
                    if game_nums.isdigit() and int(game_nums) > 0:
                        print(f"Starting match at ELO {elo_input} for {game_nums} games...")
                        return int(elo_input), int(game_nums)
                    else:
                        print("Invalid number of games. Please enter a positive integer.")
        if user_input == "full":
            return None, None
        print("Invalid choice. Please enter 'single' or 'full'.")


def write_viewer(html_path):
    html_path.write_text(
        """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Chess Board</title>
<style>
    body { margin: 0; background: #111; display: grid; place-items: center; height: 100vh; }
    img { width: 720px; height: 720px; }
</style>
</head>
<body>
<img id="board" src="board.svg">
<script>
    setInterval(() => {
        document.getElementById("board").src = "board.svg?t=" + Date.now();
    }, 200);
</script>
</body>
</html>
""",
        encoding="utf-8",
    )


def update_board_svg(board, svg_path):
    svg = chess.svg.board(
        board=board,
        size=720,
        lastmove=board.peek() if board.move_stack else None,
    )
    svg_path.write_text(svg, encoding="utf-8")


def parse_and_record_result(bot_stats, current_elo, is_bot_white, board_result):
    if board_result == "1/2-1/2":
        bot_stats[current_elo][1] += 1
    elif (board_result == "1-0" and is_bot_white) or (board_result == "0-1" and not is_bot_white):
        bot_stats[current_elo][0] += 1
    else:
        bot_stats[current_elo][2] += 1


def configure_stockfish(stockfish, elo):
    stockfish.configure({
        "UCI_Elo": elo,
        "UCI_LimitStrength": True,
    })

def run_match_at_elo(elo, games_per_elo=10, render_svg=False):
    this_bot = chess.engine.SimpleEngine.popen_uci([sys.executable, THIS_BOT_PATH])
    stockfish = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    bot_stats = {elo: np.zeros(3, dtype=int)}

    try:
        if render_svg:
            update_board_svg(chess.Board(), SVG_PATH)
            write_viewer(HTML_PATH)
            webbrowser.open(HTML_PATH.as_uri())

        configure_stockfish(stockfish, elo)

        for i in range(games_per_elo):
            board = chess.Board()
            move_count = 0

            bot_color = chess.WHITE if i % 2 == 0 else chess.BLACK
            white_player = this_bot if bot_color == chess.WHITE else stockfish
            black_player = stockfish if bot_color == chess.WHITE else this_bot
            white_player_string = "this Bot (White)" if bot_color == chess.WHITE else "Stockfish (White)"
            black_player_string = "Stockfish (Black)" if bot_color == chess.WHITE else "this Bot (Black)"

            while not board.is_game_over():
                move_count += 1
                if board.turn == chess.WHITE:
                    print(f"Move {move_count}: {white_player_string} thinking...")
                    result = white_player.play(board, chess.engine.Limit(time=THINK_TIME))
                else:
                    print(f"Move {move_count}: {black_player_string} thinking...")
                    result = black_player.play(board, chess.engine.Limit(time=THINK_TIME))

                board.push(result.move)
                if render_svg:
                    update_board_svg(board, SVG_PATH)
                print(f"  {result.move} played\n")

            result = board.result()
            parse_and_record_result(bot_stats, elo, bot_color == chess.WHITE, result)
            print(f"Game over: {result}")

        print(f"Results at ELO {elo}: Wins: {bot_stats[elo][0]}, Draws: {bot_stats[elo][1]}, Losses: {bot_stats[elo][2]}")
        
        x = np.arange(3)
        width = 0.5
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(x, bot_stats[elo], width, color=["green", "gray", "red"])
        ax.set_xticks(x)
        ax.set_xticklabels(["Wins", "Draws", "Losses"])
        ax.set_ylabel("Number of Games")
        ax.set_title(f"Bot Performance vs Stockfish at ELO {elo} with thinking time {THINK_TIME} seconds")
        ax.legend()
        plt.tight_layout()
        plt.show()
    finally:
        this_bot.quit()
        stockfish.quit()

def run_match(render_svg=False, stats_range=30):
    this_bot = chess.engine.SimpleEngine.popen_uci([sys.executable, THIS_BOT_PATH])
    stockfish = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    bot_stats = {
        1600: np.zeros(3, dtype=int),
        1700: np.zeros(3, dtype=int),
        1800: np.zeros(3, dtype=int),
    }

    try:
        if render_svg:
            update_board_svg(chess.Board(), SVG_PATH)
            write_viewer(HTML_PATH)
            webbrowser.open(HTML_PATH.as_uri())

        for i in range(stats_range):
            board = chess.Board()
            move_count = 0

            if i >= 20:
                elo = 1800
            elif i >= 10:
                elo = 1700
            else:
                elo = 1600

            configure_stockfish(stockfish, elo)

            bot_color = chess.WHITE if i % 2 == 0 else chess.BLACK
            white_player = this_bot if bot_color == chess.WHITE else stockfish
            black_player = stockfish if bot_color == chess.WHITE else this_bot
            white_player_string = "this Bot (White)" if bot_color == chess.WHITE else "Stockfish (White)"
            black_player_string = "Stockfish (Black)" if bot_color == chess.WHITE else "this Bot (Black)"

            while not board.is_game_over():
                move_count += 1
                if board.turn == chess.WHITE:
                    print(f"Move {move_count}: {white_player_string} thinking...")
                    result = white_player.play(board, chess.engine.Limit(time=THINK_TIME))
                else:
                    print(f"Move {move_count}: {black_player_string} thinking...")
                    result = black_player.play(board, chess.engine.Limit(time=THINK_TIME))

                board.push(result.move)
                if render_svg:
                    update_board_svg(board, SVG_PATH)
                print(f"  {result.move} played\n")

            result = board.result()
            parse_and_record_result(bot_stats, elo, bot_color, result)
            print(f"Game over: {result}")

        elos = list(bot_stats.keys())
        wins = [bot_stats[elo][0] for elo in elos]
        draws = [bot_stats[elo][1] for elo in elos]
        losses = [bot_stats[elo][2] for elo in elos]

        x = np.arange(len(elos))
        width = 0.25

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width, wins, width, label="Wins", color="green")
        ax.bar(x, draws, width, label="Draws", color="gray")
        ax.bar(x + width, losses, width, label="Losses", color="red")
        ax.set_xlabel("Stockfish ELO")
        ax.set_ylabel("Number of Games")
        ax.set_title("Bot Performance vs Stockfish")
        ax.set_xticks(x)
        ax.set_xticklabels(elos)
        ax.legend()
        plt.tight_layout()
        plt.show()
    finally:
        this_bot.quit()
        stockfish.quit()


def main():
    render_svg = ask_render_svg()
    elo, games_per_elo = ask_match_config()
    
    if elo is not None and games_per_elo is not None:
        run_match_at_elo(elo, games_per_elo, render_svg)
    else:
        run_match(render_svg=render_svg, stats_range=30)


if __name__ == "__main__":
    main()
