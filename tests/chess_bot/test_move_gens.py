"""
Tests for chess_bot/move_gens.py.

Covers: get_set_bits, get_pawns_moves, get_knights_moves, get_king_moves,
get_rooks_moves, get_bishops_moves, get_queens_moves, and generate_all_moves.
"""

import pytest
from data.classes.chess_bot.move_gens import (
    get_set_bits,
    get_pawns_moves,
    get_knights_moves,
    get_king_moves,
    get_rooks_moves,
    get_bishops_moves,
    get_queens_moves,
    generate_all_moves,
)
from data.classes.chess_bot.constants import (
    WHITE, BLACK,
    W_PAWN, W_KNIGHT, W_BISHOP, W_ROOK, W_QUEEN, W_KING,
    B_PAWN, B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN, B_KING,
    W_PIECES, B_PIECES, OCCUPIED,
    FLAG_QUIET, FLAG_CAPTURE, FLAG_DOUBLE_PAWN, FLAG_CASTLE_KS, FLAG_CASTLE_QS,
    WK_RIGHT, WQ_RIGHT, BK_RIGHT, BQ_RIGHT,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def bit(index):
    return 1 << index


def empty_bb():
    return {
        W_PAWN: 0, W_KNIGHT: 0, W_BISHOP: 0, W_ROOK: 0, W_QUEEN: 0, W_KING: 0,
        B_PAWN: 0, B_KNIGHT: 0, B_BISHOP: 0, B_ROOK: 0, B_QUEEN: 0, B_KING: 0,
        W_PIECES: 0, B_PIECES: 0, OCCUPIED: 0,
    }


def set_bb(bb, piece_key, color_key, squares):
    """Stamp *squares* (list of bit indices) into bb for a given piece."""
    mask = 0
    for sq in squares:
        mask |= bit(sq)
    bb[piece_key] = mask
    bb[color_key] |= mask
    bb[OCCUPIED] |= mask
    return bb


# ---------------------------------------------------------------------------
# get_set_bits
# ---------------------------------------------------------------------------

class TestGetSetBits:
    def test_empty_bitboard_yields_nothing(self):
        assert list(get_set_bits(0)) == []

    def test_single_bit(self):
        assert list(get_set_bits(1)) == [0]

    def test_multiple_bits(self):
        # bits 0, 3, 7 → 0b10001001 = 137
        result = sorted(get_set_bits(0b10001001))
        assert result == [0, 3, 7]

    def test_full_rank(self):
        # Bits 0–7 all set
        result = sorted(get_set_bits(0xFF))
        assert result == list(range(8))

    def test_high_bit(self):
        result = list(get_set_bits(1 << 63))
        assert result == [63]


# ---------------------------------------------------------------------------
# get_pawns_moves
# ---------------------------------------------------------------------------

class TestGetPawnsMoves:
    def test_white_pawn_single_push(self):
        bb = empty_bb()
        set_bb(bb, W_PAWN, W_PIECES, [12])  # E2 = LERF 12
        moves = get_pawns_moves(bb, WHITE)
        assert (12, 20, FLAG_QUIET) in moves

    def test_white_pawn_double_push_from_rank_1(self):
        bb = empty_bb()
        set_bb(bb, W_PAWN, W_PIECES, [12])  # E2 on rank 1 (12 // 8 == 1)
        moves = get_pawns_moves(bb, WHITE)
        assert (12, 28, FLAG_DOUBLE_PAWN) in moves

    def test_white_pawn_no_double_push_from_rank_2(self):
        bb = empty_bb()
        set_bb(bb, W_PAWN, W_PIECES, [20])  # E3 = LERF 20, rank 2 (20//8==2)
        moves = get_pawns_moves(bb, WHITE)
        froms = [m[0] for m in moves]
        assert 20 in froms
        assert not any(m[2] == FLAG_DOUBLE_PAWN for m in moves)

    def test_white_pawn_blocked_no_push(self):
        bb = empty_bb()
        set_bb(bb, W_PAWN, W_PIECES, [12])  # E2
        # Place a black piece at E3 (20) blocking the path
        bb[B_PIECES] = bit(20)
        bb[OCCUPIED] |= bit(20)
        moves = get_pawns_moves(bb, WHITE)
        assert not any(m[0] == 12 for m in moves)

    def test_white_pawn_capture(self):
        bb = empty_bb()
        set_bb(bb, W_PAWN, W_PIECES, [12])  # E2
        # Enemy at D3 (19)
        bb[B_PIECES] = bit(19)
        bb[OCCUPIED] |= bit(19)
        moves = get_pawns_moves(bb, WHITE)
        assert (12, 19, FLAG_CAPTURE) in moves

    def test_white_pawn_no_capture_own_piece(self):
        bb = empty_bb()
        set_bb(bb, W_PAWN, W_PIECES, [12])  # E2
        # Friendly at D3 (19)
        bb[W_PIECES] |= bit(19)
        bb[OCCUPIED] |= bit(19)
        moves = get_pawns_moves(bb, WHITE)
        assert not any(m[1] == 19 for m in moves)

    def test_black_pawn_single_push(self):
        bb = empty_bb()
        set_bb(bb, B_PAWN, B_PIECES, [52])  # E7 = LERF 52
        moves = get_pawns_moves(bb, BLACK)
        assert (52, 44, FLAG_QUIET) in moves

    def test_black_pawn_double_push_from_rank_6(self):
        bb = empty_bb()
        set_bb(bb, B_PAWN, B_PIECES, [52])  # 52 // 8 == 6
        moves = get_pawns_moves(bb, BLACK)
        assert (52, 36, FLAG_DOUBLE_PAWN) in moves

    def test_black_pawn_capture(self):
        bb = empty_bb()
        set_bb(bb, B_PAWN, B_PIECES, [52])  # E7
        # White piece at F6 (45)
        bb[W_PIECES] = bit(45)
        bb[OCCUPIED] |= bit(45)
        moves = get_pawns_moves(bb, BLACK)
        assert (52, 45, FLAG_CAPTURE) in moves

    def test_multiple_white_pawns(self):
        bb = empty_bb()
        set_bb(bb, W_PAWN, W_PIECES, [8, 9, 10])  # A2, B2, C2
        moves = get_pawns_moves(bb, WHITE)
        srcs = {m[0] for m in moves}
        assert 8 in srcs
        assert 9 in srcs
        assert 10 in srcs


# ---------------------------------------------------------------------------
# get_knights_moves
# ---------------------------------------------------------------------------

class TestGetKnightsMoves:
    def test_white_knight_at_b1(self):
        bb = empty_bb()
        set_bb(bb, W_KNIGHT, W_PIECES, [1])  # B1
        moves = get_knights_moves(bb, WHITE)
        targets = {m[1] for m in moves}
        # B1 knight → A3=16, C3=18, D2=11
        assert 16 in targets
        assert 18 in targets

    def test_knight_cannot_capture_friendly(self):
        bb = empty_bb()
        set_bb(bb, W_KNIGHT, W_PIECES, [28])  # E4
        # Friendly piece at one of the target squares
        target = 28 + 17  # F6
        bb[W_PIECES] |= bit(target)
        bb[OCCUPIED] |= bit(target)
        moves = get_knights_moves(bb, WHITE)
        assert not any(m[1] == target for m in moves)

    def test_knight_capture_flag(self):
        bb = empty_bb()
        set_bb(bb, W_KNIGHT, W_PIECES, [28])  # E4
        enemy_sq = 45  # F6
        bb[B_PIECES] = bit(enemy_sq)
        bb[OCCUPIED] |= bit(enemy_sq)
        moves = get_knights_moves(bb, WHITE)
        capture_moves = [m for m in moves if m[1] == enemy_sq]
        assert len(capture_moves) == 1
        assert capture_moves[0][2] == FLAG_CAPTURE

    def test_black_knight_moves(self):
        bb = empty_bb()
        set_bb(bb, B_KNIGHT, B_PIECES, [62])  # G8
        moves = get_knights_moves(bb, BLACK)
        targets = {m[1] for m in moves}
        assert len(targets) > 0

    def test_no_knights_returns_empty(self):
        bb = empty_bb()
        assert get_knights_moves(bb, WHITE) == []


# ---------------------------------------------------------------------------
# get_king_moves
# ---------------------------------------------------------------------------

class TestGetKingMoves:
    def test_white_king_at_e1_open_board(self):
        bb = empty_bb()
        set_bb(bb, W_KING, W_PIECES, [4])  # E1
        moves = get_king_moves(bb, WHITE, 0)
        targets = {m[1] for m in moves}
        # E1 king can go to D1(3), D2(11), E2(12), F2(13), F1(5)
        assert 3 in targets
        assert 5 in targets
        assert 12 in targets

    def test_king_cannot_move_to_friendly_square(self):
        bb = empty_bb()
        set_bb(bb, W_KING, W_PIECES, [4])  # E1
        # Place a friendly at D1 (3)
        bb[W_PIECES] |= bit(3)
        bb[OCCUPIED] |= bit(3)
        moves = get_king_moves(bb, WHITE, 0)
        assert not any(m[1] == 3 for m in moves)

    def test_king_capture_flag(self):
        bb = empty_bb()
        set_bb(bb, W_KING, W_PIECES, [4])  # E1
        bb[B_PIECES] = bit(5)   # F1 – enemy
        bb[OCCUPIED] |= bit(5)
        moves = get_king_moves(bb, WHITE, 0)
        capture_moves = [m for m in moves if m[1] == 5]
        assert capture_moves[0][2] == FLAG_CAPTURE

    def test_white_king_kingside_castling(self):
        bb = empty_bb()
        set_bb(bb, W_KING, W_PIECES, [4])  # E1
        # No pieces on F1(5) or G1(6)
        moves = get_king_moves(bb, WHITE, WK_RIGHT)
        assert (4, 6, FLAG_CASTLE_KS) in moves

    def test_white_king_no_castling_path_blocked(self):
        bb = empty_bb()
        set_bb(bb, W_KING, W_PIECES, [4])  # E1
        # Block F1 (5)
        bb[OCCUPIED] = bit(5)
        moves = get_king_moves(bb, WHITE, WK_RIGHT)
        assert not any(m[2] == FLAG_CASTLE_KS for m in moves)

    def test_white_king_queenside_castling(self):
        bb = empty_bb()
        set_bb(bb, W_KING, W_PIECES, [4])  # E1
        # Clear B1(1), C1(2), D1(3)
        moves = get_king_moves(bb, WHITE, WQ_RIGHT)
        assert (4, 2, FLAG_CASTLE_QS) in moves

    def test_black_king_kingside_castling(self):
        bb = empty_bb()
        set_bb(bb, B_KING, B_PIECES, [60])  # E8
        moves = get_king_moves(bb, BLACK, BK_RIGHT)
        assert (60, 62, FLAG_CASTLE_KS) in moves

    def test_black_king_queenside_castling(self):
        bb = empty_bb()
        set_bb(bb, B_KING, B_PIECES, [60])  # E8
        moves = get_king_moves(bb, BLACK, BQ_RIGHT)
        assert (60, 58, FLAG_CASTLE_QS) in moves


# ---------------------------------------------------------------------------
# get_rooks_moves
# ---------------------------------------------------------------------------

class TestGetRooksMoves:
    def test_white_rook_open_file(self):
        bb = empty_bb()
        set_bb(bb, W_ROOK, W_PIECES, [0])  # A1
        moves = get_rooks_moves(bb, WHITE)
        assert len(moves) > 0

    def test_rook_capture_flag(self):
        bb = empty_bb()
        set_bb(bb, W_ROOK, W_PIECES, [0])  # A1
        bb[B_PIECES] = bit(8)   # A2 – enemy
        bb[OCCUPIED] |= bit(8)
        moves = get_rooks_moves(bb, WHITE)
        capture_moves = [m for m in moves if m[1] == 8]
        assert capture_moves[0][2] == FLAG_CAPTURE


# ---------------------------------------------------------------------------
# get_bishops_moves
# ---------------------------------------------------------------------------

class TestGetBishopsMoves:
    def test_white_bishop_open_diagonal(self):
        bb = empty_bb()
        set_bb(bb, W_BISHOP, W_PIECES, [0])  # A1
        moves = get_bishops_moves(bb, WHITE)
        targets = {m[1] for m in moves}
        assert 9 in targets   # B2
        assert 63 in targets  # H8

    def test_black_bishop(self):
        bb = empty_bb()
        set_bb(bb, B_BISHOP, B_PIECES, [63])  # H8
        moves = get_bishops_moves(bb, BLACK)
        targets = {m[1] for m in moves}
        assert 54 in targets  # G7


# ---------------------------------------------------------------------------
# get_queens_moves
# ---------------------------------------------------------------------------

class TestGetQueensMoves:
    def test_white_queen_open_board(self):
        bb = empty_bb()
        set_bb(bb, W_QUEEN, W_PIECES, [28])  # E4
        moves = get_queens_moves(bb, WHITE)
        assert len(moves) == 27

    def test_black_queen(self):
        bb = empty_bb()
        set_bb(bb, B_QUEEN, B_PIECES, [28])  # E4
        moves = get_queens_moves(bb, BLACK)
        assert len(moves) == 27


# ---------------------------------------------------------------------------
# generate_all_moves – integration
# ---------------------------------------------------------------------------

class TestGenerateAllMoves:
    def test_white_starting_position_20_pseudo_legal_moves(self):
        """
        From the initial position, white has exactly 20 pseudo-legal moves:
        8 single-pawn pushes + 8 double-pawn pushes + 4 knight moves.
        """
        bb = empty_bb()
        # White pawns on rank 1 (LERF indices 8–15)
        for sq in range(8, 16):
            bb[W_PAWN] |= bit(sq)
        bb[W_PIECES] = bb[W_PAWN]
        # White knights at B1 (1) and G1 (6)
        bb[W_KNIGHT] = bit(1) | bit(6)
        bb[W_PIECES] |= bb[W_KNIGHT]
        # Remaining white pieces (not adding kings/bishops/rooks/queens here for
        # simplicity – we only need occupied squares to block pawns)
        bb[W_ROOK] = bit(0) | bit(7)
        bb[W_BISHOP] = bit(2) | bit(5)
        bb[W_QUEEN] = bit(3)
        bb[W_KING] = bit(4)
        bb[W_PIECES] |= bb[W_ROOK] | bb[W_BISHOP] | bb[W_QUEEN] | bb[W_KING]
        # Black pawns on rank 6 (LERF 48–55) and black back rank (56–63)
        for sq in range(48, 64):
            bb[B_PIECES] |= bit(sq)
        bb[OCCUPIED] = bb[W_PIECES] | bb[B_PIECES]

        moves = generate_all_moves(bb, WHITE, 0)
        assert len(moves) == 20

    def test_returns_list_of_3_tuples(self):
        bb = empty_bb()
        set_bb(bb, W_PAWN, W_PIECES, [12])  # E2
        set_bb(bb, W_KING, W_PIECES, [4])   # E1
        moves = generate_all_moves(bb, WHITE, 0)
        for move in moves:
            assert isinstance(move, tuple) and len(move) == 3

    def test_no_pieces_of_type_returns_no_moves_for_that_type(self):
        """Individual piece generators return empty lists when no pieces present."""
        bb = empty_bb()
        assert get_pawns_moves(bb, WHITE) == []
        assert get_knights_moves(bb, WHITE) == []
        assert get_rooks_moves(bb, WHITE) == []
        assert get_bishops_moves(bb, WHITE) == []
        assert get_queens_moves(bb, WHITE) == []

    def test_all_move_sources_are_occupied(self):
        """Every move's source square should be a set bit in OCCUPIED."""
        bb = empty_bb()
        set_bb(bb, W_PAWN, W_PIECES, [12])
        set_bb(bb, W_KNIGHT, W_PIECES, [1])
        set_bb(bb, W_KING, W_PIECES, [4])   # include a real king to avoid edge case
        moves = generate_all_moves(bb, WHITE, 0)
        for src, dst, flag in moves:
            assert src >= 0, f"Source index {src} is negative (invalid)"
            assert bb[OCCUPIED] & bit(src), f"Source {src} not occupied"
