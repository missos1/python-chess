"""
Tests for chess_bot/move_filter.py – is_square_attacked().

Covers attacks by pawns, knights, bishops, rooks, queens, and kings from
both colors, as well as multi-piece scenarios.
"""

import pytest
from data.classes.chess_bot.move_filter import is_square_attacked
from data.classes.chess_bot.constants import (
    WHITE, BLACK,
    W_PAWN, W_KNIGHT, W_BISHOP, W_ROOK, W_QUEEN, W_KING,
    B_PAWN, B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN, B_KING,
    W_PIECES, B_PIECES, OCCUPIED,
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


def place_white(bb, piece_key, sq):
    bb[piece_key] |= bit(sq)
    bb[W_PIECES] |= bit(sq)
    bb[OCCUPIED] |= bit(sq)


def place_black(bb, piece_key, sq):
    bb[piece_key] |= bit(sq)
    bb[B_PIECES] |= bit(sq)
    bb[OCCUPIED] |= bit(sq)


# ---------------------------------------------------------------------------
# Rook attacks
# ---------------------------------------------------------------------------

class TestRookAttacks:
    def test_white_rook_attacks_square_on_same_rank(self):
        bb = empty_bb()
        place_white(bb, W_ROOK, 0)  # A1
        assert is_square_attacked(7, WHITE, bb) is True  # H1 same rank

    def test_white_rook_attacks_square_on_same_file(self):
        bb = empty_bb()
        place_white(bb, W_ROOK, 0)  # A1
        assert is_square_attacked(56, WHITE, bb) is True  # A8 same file

    def test_white_rook_does_not_attack_diagonal(self):
        bb = empty_bb()
        place_white(bb, W_ROOK, 0)  # A1
        assert is_square_attacked(9, WHITE, bb) is False  # B2 diagonal

    def test_rook_attack_blocked_by_piece(self):
        bb = empty_bb()
        place_white(bb, W_ROOK, 0)   # A1
        place_white(bb, W_PAWN, 8)   # A2 blocks the north ray
        # A8 (56) should not be attacked because A2 is in the way
        assert is_square_attacked(56, WHITE, bb) is False

    def test_black_rook_attacks_square(self):
        bb = empty_bb()
        place_black(bb, B_ROOK, 56)  # A8
        assert is_square_attacked(0, BLACK, bb) is True   # A1

    def test_rook_does_not_attack_own_color(self):
        """is_square_attacked checks if *attacker_color* attacks the square."""
        bb = empty_bb()
        place_white(bb, W_ROOK, 0)
        # White rook at A1 should NOT register as attacking A1 itself
        # (the rook's own square is not in any ray)
        assert is_square_attacked(0, WHITE, bb) is False


# ---------------------------------------------------------------------------
# Bishop / Queen diagonal attacks
# ---------------------------------------------------------------------------

class TestBishopAttacks:
    def test_white_bishop_attacks_diagonal(self):
        bb = empty_bb()
        place_white(bb, W_BISHOP, 0)  # A1
        assert is_square_attacked(63, WHITE, bb) is True  # H8 same diagonal

    def test_white_bishop_does_not_attack_same_file(self):
        bb = empty_bb()
        place_white(bb, W_BISHOP, 0)  # A1
        assert is_square_attacked(8, WHITE, bb) is False  # A2

    def test_queen_attacks_diagonal_and_rank(self):
        bb = empty_bb()
        place_white(bb, W_QUEEN, 28)  # E4
        # E4 NE diagonal: F5(37)→G6(46)→H7(55)
        assert is_square_attacked(55, WHITE, bb) is True  # H7 via NE diagonal
        assert is_square_attacked(24, WHITE, bb) is True  # A4 via west rank


# ---------------------------------------------------------------------------
# Knight attacks
# ---------------------------------------------------------------------------

class TestKnightAttacks:
    def test_white_knight_attacks_l_shape(self):
        bb = empty_bb()
        place_white(bb, W_KNIGHT, 28)  # E4
        # E4 knight attacks: D6=43, F6=45, C5=34, G5=38, etc.
        assert is_square_attacked(45, WHITE, bb) is True   # F6
        assert is_square_attacked(43, WHITE, bb) is True   # D6

    def test_knight_does_not_attack_adjacent(self):
        bb = empty_bb()
        place_white(bb, W_KNIGHT, 28)  # E4
        assert is_square_attacked(29, WHITE, bb) is False  # F4 adjacent

    def test_black_knight_attacks(self):
        bb = empty_bb()
        place_black(bb, B_KNIGHT, 0)  # A1
        # A1 knight: C2=10, B3=17
        assert is_square_attacked(10, BLACK, bb) is True
        assert is_square_attacked(17, BLACK, bb) is True


# ---------------------------------------------------------------------------
# King attacks
# ---------------------------------------------------------------------------

class TestKingAttacks:
    def test_white_king_attacks_adjacent(self):
        bb = empty_bb()
        place_white(bb, W_KING, 28)  # E4
        # Surroundings: D3=19, E3=20, F3=21, D4=27, F4=29, D5=35, E5=36, F5=37
        assert is_square_attacked(36, WHITE, bb) is True
        assert is_square_attacked(27, WHITE, bb) is True

    def test_king_does_not_attack_two_squares_away(self):
        bb = empty_bb()
        place_white(bb, W_KING, 28)  # E4
        assert is_square_attacked(44, WHITE, bb) is False  # E6 two squares north


# ---------------------------------------------------------------------------
# Pawn attacks
# ---------------------------------------------------------------------------

class TestPawnAttacks:
    def test_white_pawn_attacks_diagonals(self):
        """
        is_square_attacked uses BLACK_PAWN_CAPTURES to detect white pawns
        (the function fires pawn-capture rays outward from the target square).
        """
        bb = empty_bb()
        place_white(bb, W_PAWN, 12)  # E2 (LERF 12)
        # E2 white pawn attacks D3 (19) and F3 (21)
        assert is_square_attacked(19, WHITE, bb) is True
        assert is_square_attacked(21, WHITE, bb) is True

    def test_white_pawn_does_not_attack_forward(self):
        bb = empty_bb()
        place_white(bb, W_PAWN, 12)  # E2
        assert is_square_attacked(20, WHITE, bb) is False  # E3 forward

    def test_black_pawn_attacks_diagonals(self):
        bb = empty_bb()
        place_black(bb, B_PAWN, 52)  # E7 (LERF 52)
        # E7 black pawn attacks D6 (43) and F6 (45)
        assert is_square_attacked(43, BLACK, bb) is True
        assert is_square_attacked(45, BLACK, bb) is True

    def test_black_pawn_does_not_attack_forward(self):
        bb = empty_bb()
        place_black(bb, B_PAWN, 52)  # E7
        assert is_square_attacked(44, BLACK, bb) is False  # E6 forward


# ---------------------------------------------------------------------------
# No attacker
# ---------------------------------------------------------------------------

class TestNoAttacker:
    def test_empty_board_no_attacks(self):
        bb = empty_bb()
        for sq in range(64):
            assert is_square_attacked(sq, WHITE, bb) is False
            assert is_square_attacked(sq, BLACK, bb) is False


# ---------------------------------------------------------------------------
# Mixed-piece scenarios
# ---------------------------------------------------------------------------

class TestMixedAttacks:
    def test_multiple_white_pieces_attack_same_square(self):
        bb = empty_bb()
        place_white(bb, W_ROOK, 4)    # E1 rook attacks E4 via north
        place_white(bb, W_BISHOP, 0)  # A1 bishop attacks E5 via NE... not E4
        # E4 = 28; E1 rook on file E (file 4): attacks E4 via north
        assert is_square_attacked(28, WHITE, bb) is True

    def test_white_does_not_see_black_pieces(self):
        """White attack check should not be triggered by black pieces."""
        bb = empty_bb()
        place_black(bb, B_ROOK, 0)    # Black rook at A1
        assert is_square_attacked(56, WHITE, bb) is False  # A8 not attacked by white
        assert is_square_attacked(56, BLACK, bb) is True   # A8 attacked by black
