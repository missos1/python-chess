import chess
import chess.engine

ENGINE_PATH = r"E:\Workspace\Project\stockfish\stockfish.exe"  # hoặc đường dẫn đầy đủ tới stockfish.exe

INPUT_FILE = "openings_fen.txt"
OUTPUT_FILE = "output1.txt"

# Ngưỡng centipawn
LOW = -50
HIGH = 50

def is_balanced(score):
    """
    Kiểm tra score có nằm trong [-0.5, 0.5] hay không
    """
    if score.is_mate():
        return False  # bỏ qua các thế có mate

    cp = score.white().score()  # centipawn
    if cp is None:
        return False

    return LOW <= cp <= HIGH


def main():
    with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as engine:
        with open(INPUT_FILE, "r") as fin, open(OUTPUT_FILE, "w") as fout:
            for line in fin:
                fen = line.strip()
                if not fen:
                    continue

                try:
                    board = chess.Board(fen)
                except ValueError:
                    continue  # bỏ qua FEN lỗi

                # Analyse position
                info = engine.analyse(board, chess.engine.Limit(depth=10))
                score = info["score"]

                if is_balanced(score):
                    fout.write(fen + "\n")


if __name__ == "__main__":
    main()