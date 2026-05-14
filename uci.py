import importlib
import os
import sys
import time

def _extract_package(argv):
    if "--package" in argv:
        idx = argv.index("--package")
        if idx + 1 < len(argv):
            return argv[idx + 1]
    return "data.classes.chess_bot"

BOT_PACKAGE = _extract_package(sys.argv)

if __package__ is None or __package__ == "":
    repo_root = os.path.abspath(os.path.dirname(__file__))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

bot_module = importlib.import_module(f"{BOT_PACKAGE}.Bot")
game_state_module = importlib.import_module(f"{BOT_PACKAGE}.GameState")
constants_module = importlib.import_module(f"{BOT_PACKAGE}.constants")
move_gens_module = importlib.import_module(f"{BOT_PACKAGE}.move_gens")

Bot = bot_module.Bot
GameState = game_state_module.GameState
WHITE = constants_module.WHITE
BLACK = constants_module.BLACK
W_PAWN = constants_module.W_PAWN
W_KNIGHT = constants_module.W_KNIGHT
W_BISHOP = constants_module.W_BISHOP
W_ROOK = constants_module.W_ROOK
W_QUEEN = constants_module.W_QUEEN
W_KING = constants_module.W_KING
B_PAWN = constants_module.B_PAWN
B_KNIGHT = constants_module.B_KNIGHT
B_BISHOP = constants_module.B_BISHOP
B_ROOK = constants_module.B_ROOK
B_QUEEN = constants_module.B_QUEEN
B_KING = constants_module.B_KING
W_PIECES = constants_module.W_PIECES
B_PIECES = constants_module.B_PIECES
OCCUPIED = constants_module.OCCUPIED
WK_RIGHT = constants_module.WK_RIGHT
WQ_RIGHT = constants_module.WQ_RIGHT
BK_RIGHT = constants_module.BK_RIGHT
BQ_RIGHT = constants_module.BQ_RIGHT
FLAG_PROMOTION = constants_module.FLAG_PROMOTION
create_piece_array_from_bitboards = move_gens_module.create_piece_array_from_bitboards

STARTPOS_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

PIECE_FROM_FEN = {
    "P": W_PAWN,
    "N": W_KNIGHT,
    "B": W_BISHOP,
    "R": W_ROOK,
    "Q": W_QUEEN,
    "K": W_KING,
    "p": B_PAWN,
    "n": B_KNIGHT,
    "b": B_BISHOP,
    "r": B_ROOK,
    "q": B_QUEEN,
    "k": B_KING,
}


def send(msg):
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def algebraic_to_index(square):
    file_char = square[0]
    rank_char = square[1]
    file_index = ord(file_char) - ord("a")
    rank_index = int(rank_char) - 1
    return rank_index * 8 + file_index


def index_to_algebraic(index):
    file_char = chr((index % 8) + ord("a"))
    rank_char = str((index // 8) + 1)
    return file_char + rank_char


def parse_fen(fen):
    parts = fen.split()
    board_part = parts[0] if len(parts) > 0 else "8/8/8/8/8/8/8/8"
    turn_part = parts[1] if len(parts) > 1 else "w"
    castling_part = parts[2] if len(parts) > 2 else "-"
    en_passant_part = parts[3] if len(parts) > 3 else "-"

    bitboards = [0] * 16

    ranks = board_part.split("/")
    for fen_rank, rank_str in enumerate(ranks):
        file_index = 0
        board_rank = 7 - fen_rank
        for ch in rank_str:
            if ch.isdigit():
                file_index += int(ch)
                continue
            piece_id = PIECE_FROM_FEN.get(ch)
            if piece_id is None:
                file_index += 1
                continue
            square_index = board_rank * 8 + file_index
            bitboards[piece_id] |= 1 << square_index
            file_index += 1

    bitboards[W_PIECES] = (
        bitboards[W_PAWN]
        | bitboards[W_KNIGHT]
        | bitboards[W_BISHOP]
        | bitboards[W_ROOK]
        | bitboards[W_QUEEN]
        | bitboards[W_KING]
    )
    bitboards[B_PIECES] = (
        bitboards[B_PAWN]
        | bitboards[B_KNIGHT]
        | bitboards[B_BISHOP]
        | bitboards[B_ROOK]
        | bitboards[B_QUEEN]
        | bitboards[B_KING]
    )
    bitboards[OCCUPIED] = bitboards[W_PIECES] | bitboards[B_PIECES]

    castling_rights = 0
    if "K" in castling_part:
        castling_rights |= WK_RIGHT
    if "Q" in castling_part:
        castling_rights |= WQ_RIGHT
    if "k" in castling_part:
        castling_rights |= BK_RIGHT
    if "q" in castling_part:
        castling_rights |= BQ_RIGHT

    en_passant_target = None
    if en_passant_part != "-" and len(en_passant_part) == 2:
        en_passant_target = algebraic_to_index(en_passant_part)

    turn_color = WHITE if turn_part == "w" else BLACK
    piece_array = create_piece_array_from_bitboards(bitboards)
    return GameState(bitboards, piece_array, castling_rights, en_passant_target=en_passant_target, color=turn_color)


def apply_uci_move(state, uci_move):
    if len(uci_move) < 4:
        return False

    source = algebraic_to_index(uci_move[0:2])
    target = algebraic_to_index(uci_move[2:4])
    promotion = uci_move[4].lower() if len(uci_move) > 4 else None

    legal_moves = state.get_strictly_legal_moves(state.turn_color)
    for move in legal_moves:
        if move[0] != source or move[1] != target:
            continue
        if promotion and move[2] != FLAG_PROMOTION:
            continue
        if move[2] == FLAG_PROMOTION:
            return state.make_move(move) is None
        return state.make_move(move) is None

    return False


def moves_from_position_command(line):
    tokens = line.split()
    if len(tokens) < 2:
        return parse_fen(STARTPOS_FEN), []

    if tokens[1] == "startpos":
        state = parse_fen(STARTPOS_FEN)
        if "moves" in tokens:
            move_index = tokens.index("moves")
            return state, tokens[move_index + 1 :]
        return state, []

    if tokens[1] == "fen":
        if "moves" in tokens:
            move_index = tokens.index("moves")
            fen = " ".join(tokens[2:move_index])
            moves = tokens[move_index + 1 :]
            return parse_fen(fen), moves
        fen = " ".join(tokens[2:])
        return parse_fen(fen), []

    return parse_fen(STARTPOS_FEN), []


def choose_time_limit_ms(tokens, turn_color, default_ms):
    time_ms = default_ms
    depth = None

    if "movetime" in tokens:
        idx = tokens.index("movetime")
        if idx + 1 < len(tokens):
            time_ms = int(tokens[idx + 1])
            return time_ms, depth

    if "depth" in tokens:
        idx = tokens.index("depth")
        if idx + 1 < len(tokens):
            depth = int(tokens[idx + 1])

    wtime = btime = winc = binc = None
    if "wtime" in tokens:
        idx = tokens.index("wtime")
        if idx + 1 < len(tokens):
            wtime = int(tokens[idx + 1])
    if "btime" in tokens:
        idx = tokens.index("btime")
        if idx + 1 < len(tokens):
            btime = int(tokens[idx + 1])
    if "winc" in tokens:
        idx = tokens.index("winc")
        if idx + 1 < len(tokens):
            winc = int(tokens[idx + 1])
    if "binc" in tokens:
        idx = tokens.index("binc")
        if idx + 1 < len(tokens):
            binc = int(tokens[idx + 1])

    if wtime is not None and btime is not None:
        remaining = wtime if turn_color == WHITE else btime
        increment = winc if turn_color == WHITE else binc
        increment = increment or 0
        budget = (remaining / 30) + (increment * 0.8)
        budget = min(budget, max(remaining * 0.5, 1))
        time_ms = max(50, int(budget))

    return time_ms, depth


def move_to_uci(move):
    source, target, flag = move
    uci = index_to_algebraic(source) + index_to_algebraic(target)
    if flag == FLAG_PROMOTION:
        uci += "q"
    return uci


def main():
    bot = Bot(color=WHITE, time_limit=6, verbose=False)
    state = parse_fen(STARTPOS_FEN)

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue

        if line == "uci":
            send("id name ChessAI_VNU")
            send("id author VNU")
            send("uciok")
            continue

        if line == "isready":
            send("readyok")
            continue

        if line == "ucinewgame":
            bot = Bot(color=WHITE, time_limit=6, verbose=False)
            state = parse_fen(STARTPOS_FEN)
            continue

        if line.startswith("position"):
            state, moves = moves_from_position_command(line)
            for uci_move in moves:
                applied = apply_uci_move(state, uci_move)
                if not applied:
                    break
            continue

        if line.startswith("go"):
            tokens = line.split()
            time_ms, depth = choose_time_limit_ms(tokens, state.turn_color, int(bot.time_limit * 1000))
            bot.time_limit = max(0.05, time_ms / 1000)
            bot.color = state.turn_color
            max_depth = depth if depth is not None else 1000

            start_time = time.time()
            best_move = bot.get_best_move(state, max_depth=max_depth)
            elapsed = time.time() - start_time

            if best_move is None:
                info_line = f"info time {int(elapsed * 1000)} nodes {bot.nodes_searched}"
                send(info_line)
                send("bestmove 0000")
            else:
                info_line = f"info time {int(elapsed * 1000)} nodes {bot.nodes_searched}"
                send(info_line)
                send("bestmove " + move_to_uci(best_move))
            continue

        if line == "quit":
            break


if __name__ == "__main__":
    main()
