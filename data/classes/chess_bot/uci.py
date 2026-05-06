import sys
import threading

from .Bot import Bot
from .GameState import GameState
from .constants import *
from .move_gens import create_piece_array_from_bitboards

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

FEN_CHAR_TO_PIECE = {
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

PIECE_TO_FEN_CHAR = {
    W_PAWN: "P",
    W_KNIGHT: "N",
    W_BISHOP: "B",
    W_ROOK: "R",
    W_QUEEN: "Q",
    W_KING: "K",
    B_PAWN: "p",
    B_KNIGHT: "n",
    B_BISHOP: "b",
    B_ROOK: "r",
    B_QUEEN: "q",
    B_KING: "k",
}

PROMOTION_SUFFIX_TO_PIECE = {
    "q": (W_QUEEN, B_QUEEN),
    "r": (W_ROOK, B_ROOK),
    "b": (W_BISHOP, B_BISHOP),
    "n": (W_KNIGHT, B_KNIGHT),
}


def square_to_index(square):
    file_index = ord(square[0].lower()) - ord("a")
    rank_index = int(square[1]) - 1
    return rank_index * 8 + file_index


def index_to_square(index):
    file_char = chr((index % 8) + ord("a"))
    rank_char = str((index // 8) + 1)
    return file_char + rank_char


def build_bitboards_from_fen_board(board_part):
    bitboards = [0] * 16
    rows = board_part.split("/")
    if len(rows) != 8:
        raise ValueError(f"Invalid FEN board: {board_part}")

    for fen_rank, row in enumerate(rows):
        file_index = 0
        board_rank = 7 - fen_rank

        for char in row:
            if char.isdigit():
                file_index += int(char)
                continue

            piece_id = FEN_CHAR_TO_PIECE.get(char)
            if piece_id is None:
                raise ValueError(f"Invalid FEN piece: {char}")

            square_index = board_rank * 8 + file_index
            bitboards[piece_id] |= 1 << square_index
            file_index += 1

        if file_index != 8:
            raise ValueError(f"Invalid FEN row width: {row}")

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
    return bitboards


def parse_castling_rights(castling_token):
    rights = 0
    if "K" in castling_token:
        rights |= WK_RIGHT
    if "Q" in castling_token:
        rights |= WQ_RIGHT
    if "k" in castling_token:
        rights |= BK_RIGHT
    if "q" in castling_token:
        rights |= BQ_RIGHT
    return rights


def build_state_from_fen(fen):
    parts = fen.split()
    if len(parts) < 4:
        raise ValueError(f"Invalid FEN: {fen}")

    board_part, active_color, castling_token, en_passant_token = parts[:4]
    bitboards = build_bitboards_from_fen_board(board_part)
    piece_values = create_piece_array_from_bitboards(bitboards)
    color = WHITE if active_color == "w" else BLACK
    castling_rights = parse_castling_rights(castling_token)
    en_passant_target = None if en_passant_token == "-" else square_to_index(en_passant_token)
    return GameState(bitboards, piece_values, castling_rights, en_passant_target=en_passant_target, color=color)


def build_start_state():
    return build_state_from_fen(START_FEN)


def move_to_uci(move):
    if move is None:
        return "0000"

    source, target, flag = move
    move_text = index_to_square(source) + index_to_square(target)
    if flag == FLAG_PROMOTION:
        move_text += "q"
    return move_text


def find_legal_move(state, move_text):
    if len(move_text) < 4:
        return None, None

    source = square_to_index(move_text[:2])
    target = square_to_index(move_text[2:4])
    promotion_suffix = move_text[4:].lower() if len(move_text) > 4 else ""

    legal_moves = state.get_strictly_legal_moves(state.turn_color)
    for move in legal_moves:
        if move[0] != source or move[1] != target:
            continue

        promotion_piece = None
        if move[2] == FLAG_PROMOTION:
            if promotion_suffix:
                promotion_piece_pair = PROMOTION_SUFFIX_TO_PIECE.get(promotion_suffix[0])
                if promotion_piece_pair is None:
                    return None, None
                promotion_piece = promotion_piece_pair[0 if state.turn_color == WHITE else 1]
            else:
                promotion_piece = W_QUEEN if state.turn_color == WHITE else B_QUEEN

        return move, promotion_piece

    return None, None


def apply_uci_move(state, move_text):
    move, promotion_piece = find_legal_move(state, move_text)
    if move is None:
        return False

    if move[2] == FLAG_PROMOTION:
        state.make_move(move, promotion_piece=promotion_piece)
    else:
        state.make_move(move)
    return True


class UCIEngine:
    def __init__(self):
        self.state = build_start_state()
        self.bot = Bot(color=self.state.turn_color, verbose=False)
        self._search_thread = None
        self._search_stop_event = None
        self._search_lock = threading.Lock()

    def _clear_search_state(self):
        with self._search_lock:
            self._search_thread = None
            self._search_stop_event = None

    def is_searching(self):
        thread = self._search_thread
        return thread is not None and thread.is_alive()

    def stop_search(self, wait=True):
        with self._search_lock:
            thread = self._search_thread
            stop_event = self._search_stop_event

        if stop_event is not None:
            stop_event.set()

        if thread is not None and thread.is_alive() and wait:
            thread.join()

        self._clear_search_state()

    def set_position(self, tokens):
        self.stop_search()

        if len(tokens) < 2:
            return

        if tokens[1] == "startpos":
            self.state = build_start_state()
            moves_start = 3 if len(tokens) > 2 and tokens[2] == "moves" else len(tokens)
            move_tokens = tokens[moves_start:] if moves_start < len(tokens) else []
        elif tokens[1] == "fen":
            moves_index = tokens.index("moves") if "moves" in tokens else len(tokens)
            fen = " ".join(tokens[2:moves_index])
            self.state = build_state_from_fen(fen)
            move_tokens = tokens[moves_index + 1:] if moves_index < len(tokens) else []
        else:
            return

        for move_text in move_tokens:
            if not apply_uci_move(self.state, move_text):
                print(f"info string ignored illegal move {move_text}", file=sys.stderr)
                break

    def _time_limit_from_go(self, tokens):
        if "movetime" in tokens:
            index = tokens.index("movetime")
            return max(0.001, int(tokens[index + 1]) / 1000.0)

        if "depth" in tokens:
            return None

        side_prefix = "w" if self.state.turn_color == WHITE else "b"
        time_key = f"{side_prefix}time"
        inc_key = f"{side_prefix}inc"

        remaining_ms = None
        increment_ms = 0
        move_count = 30

        if time_key in tokens:
            remaining_ms = int(tokens[tokens.index(time_key) + 1])
        if inc_key in tokens:
            increment_ms = int(tokens[tokens.index(inc_key) + 1])
        if "movestogo" in tokens:
            move_count = max(1, int(tokens[tokens.index("movestogo") + 1]))

        if remaining_ms is None:
            return 6.0

        base_ms = remaining_ms / move_count
        limit_ms = max(50, int(base_ms + increment_ms * 0.8))
        limit_ms = min(limit_ms, max(50, int(remaining_ms * 0.9)))
        return limit_ms / 1000.0

    def _max_depth_from_go(self, tokens):
        if "depth" not in tokens:
            return None
        return int(tokens[tokens.index("depth") + 1])

    def _search_worker(self, stop_event, max_depth=None, time_limit=None):
        try:
            if time_limit is not None:
                self.bot.time_limit = time_limit
            self.bot.color = self.state.turn_color
            best_move = self.bot.get_best_move(
                self.state,
                max_depth=max_depth,
                stop_event=stop_event,
            )
            best_move_text = move_to_uci(best_move)
        except Exception as exc:
            print(f"info string search failed: {exc}", file=sys.stderr)
            best_move_text = "0000"
        finally:
            print(f"bestmove {best_move_text}", flush=True)
            self._clear_search_state()

    def start_search(self, tokens):
        self.stop_search()

        max_depth = self._max_depth_from_go(tokens)
        time_limit = self._time_limit_from_go(tokens)
        if "infinite" in tokens:
            time_limit = float("inf")
        if max_depth is not None:
            time_limit = float("inf")
        elif time_limit is None:
            time_limit = 6.0

        stop_event = threading.Event()
        thread = threading.Thread(
            target=self._search_worker,
            args=(stop_event, max_depth, time_limit),
            daemon=True,
        )

        with self._search_lock:
            self._search_stop_event = stop_event
            self._search_thread = thread

        thread.start()

    def handle_command(self, line):
        tokens = line.split()
        if not tokens:
            return True

        command = tokens[0]

        if command == "uci":
            print("id name K69-CS4 UET", flush=True)
            print("id author K69I-CS4 Do Nam Trung group", flush=True)
            print("uciok", flush=True)
        elif command == "isready":
            print("readyok", flush=True)
        elif command == "ucinewgame":
            self.stop_search()
            self.bot.transposition_table.clear()
            self.state = build_start_state()
        elif command == "position":
            self.set_position(tokens)
        elif command == "go":
            self.start_search(tokens)
        elif command == "stop":
            self.stop_search()
        elif command == "quit":
            self.stop_search()
            return False
        elif command == "d":
            print(state_to_fen(self.state), flush=True)
        return True


def state_to_fen(state):
    rows = []
    for board_rank in range(7, -1, -1):
        empty_count = 0
        row_parts = []
        for file_index in range(8):
            square_index = board_rank * 8 + file_index
            piece_id = state.piece_values[square_index]
            if piece_id == EMPTY:
                empty_count += 1
                continue

            if empty_count:
                row_parts.append(str(empty_count))
                empty_count = 0
            row_parts.append(PIECE_TO_FEN_CHAR[piece_id])

        if empty_count:
            row_parts.append(str(empty_count))
        rows.append("".join(row_parts) or "8")

    board_part = "/".join(rows)
    active_color = "w" if state.turn_color == WHITE else "b"
    castling = []
    if state.castling_rights & WK_RIGHT:
        castling.append("K")
    if state.castling_rights & WQ_RIGHT:
        castling.append("Q")
    if state.castling_rights & BK_RIGHT:
        castling.append("k")
    if state.castling_rights & BQ_RIGHT:
        castling.append("q")

    castling_part = "".join(castling) or "-"
    en_passant_part = "-" if state.en_passant_target is None else index_to_square(state.en_passant_target)
    return f"{board_part} {active_color} {castling_part} {en_passant_part} 0 1"


def run_uci_loop():
    engine = UCIEngine()
    for raw_line in sys.stdin:
        if not engine.handle_command(raw_line.strip()):
            break


if __name__ == "__main__":
    run_uci_loop()
