"""
Tests for chess_bot/ray_cast_moves.py.

Covers cross_moves (rook), diagonal_moves (bishop), and queen_moves on
empty boards, boards with friendly blockers, and boards with enemy pieces.
"""

import pytest
from data.classes.chess_bot.ray_cast_moves import cross_moves, diagonal_moves, queen_moves
from data.classes.chess_bot.constants import (
    W_PAWN, W_KNIGHT, W_BISHOP, W_ROOK, W_QUEEN, W_KING,
    B_PAWN, B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN, B_KING,
    W_PIECES, B_PIECES, OCCUPIED,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def empty_bb():
    """Return a bitboards dict with every entry set to zero."""
    return {
        W_PAWN: 0, W_KNIGHT: 0, W_BISHOP: 0, W_ROOK: 0, W_QUEEN: 0, W_KING: 0,
        B_PAWN: 0, B_KNIGHT: 0, B_BISHOP: 0, B_ROOK: 0, B_QUEEN: 0, B_KING: 0,
        W_PIECES: 0, B_PIECES: 0, OCCUPIED: 0,
    }


def bit(index):
    return 1 << index


def set_bits(bb):
    indices = []
    while bb:
        lsb = bb & -bb
        indices.append(lsb.bit_length() - 1)
        bb &= bb - 1
    return sorted(indices)


# ---------------------------------------------------------------------------
# cross_moves – rook-style (rank + file)
# ---------------------------------------------------------------------------

class TestCrossMoves:
    def test_a1_empty_board(self):
        # From A1 (0), N: 8,16,24,32,40,48,56  E: 1,2,3,4,5,6,7
        bb = empty_bb()
        result = set_bits(cross_moves(0, bb, 0))
        expected = sorted([1, 2, 3, 4, 5, 6, 7, 8, 16, 24, 32, 40, 48, 56])
        assert result == expected

    def test_h8_empty_board(self):
        # H8 = index 63. W: 62,61,60,59,58,57,56  S: 55,47,39,31,23,15,7
        bb = empty_bb()
        result = set_bits(cross_moves(63, bb, 0))
        expected = sorted([7, 15, 23, 31, 39, 47, 55, 56, 57, 58, 59, 60, 61, 62])
        assert result == expected

    def test_e4_empty_board_14_squares(self):
        # E4 = index 28 (rank 3, file 4)
        bb = empty_bb()
        result = cross_moves(28, bb, 0)
        assert bin(result).count("1") == 14

    def test_blocked_by_friendly_north(self):
        bb = empty_bb()
        # Rook at A1 (0), friendly piece at A3 (16)
        bb[OCCUPIED] = bit(16)
        bb[W_PIECES] = bit(16)
        result = set_bits(cross_moves(0, bb, bit(16)))
        # North: only A2=8 reachable (A3=16 is friendly – excluded)
        assert 8 in result
        assert 16 not in result
        assert 24 not in result

    def test_enemy_piece_included_ray_stops(self):
        bb = empty_bb()
        # Rook at A1 (0), enemy at A3 (16)
        bb[OCCUPIED] = bit(16)
        bb[B_PIECES] = bit(16)
        result = set_bits(cross_moves(0, bb, 0))  # friendly_pieces=0
        # North: A2=8 and A3=16 (capture), A4+ excluded
        assert 8 in result
        assert 16 in result
        assert 24 not in result

    def test_blocked_east_by_friendly(self):
        bb = empty_bb()
        # Rook at A1 (0), friendly at C1 (2)
        bb[OCCUPIED] = bit(2)
        bb[W_PIECES] = bit(2)
        result = set_bits(cross_moves(0, bb, bit(2)))
        assert 1 in result
        assert 2 not in result
        assert 3 not in result

    def test_returns_correct_rank_and_file_squares(self):
        bb = empty_bb()
        # Rook at E4 (28): verify all 14 squares are on rank 3 or file 4
        result = set_bits(cross_moves(28, bb, 0))
        for sq in result:
            rank = sq // 8
            file = sq % 8
            assert rank == 3 or file == 4, f"Square {sq} not on rook's rank or file"

    def test_result_excludes_source_square(self):
        bb = empty_bb()
        result = cross_moves(28, bb, 0)
        assert result & bit(28) == 0


# ---------------------------------------------------------------------------
# diagonal_moves – bishop-style
# ---------------------------------------------------------------------------

class TestDiagonalMoves:
    def test_a1_empty_board_ne_diagonal_only(self):
        # A1 (0): only the NE diagonal is available
        bb = empty_bb()
        result = set_bits(diagonal_moves(0, bb, 0))
        expected = [9, 18, 27, 36, 45, 54, 63]
        assert result == expected

    def test_h1_empty_board_nw_diagonal_only(self):
        # H1 (7): only the NW diagonal
        bb = empty_bb()
        result = set_bits(diagonal_moves(7, bb, 0))
        expected = [14, 21, 28, 35, 42, 49, 56]
        assert result == expected

    def test_e4_empty_board_13_squares(self):
        # E4 = 28; 4 diagonals, 13 squares total
        bb = empty_bb()
        assert bin(diagonal_moves(28, bb, 0)).count("1") == 13

    def test_blocked_by_friendly_ne(self):
        bb = empty_bb()
        # Bishop at A1 (0), friendly at C3 (18)
        bb[OCCUPIED] = bit(18)
        bb[W_PIECES] = bit(18)
        result = set_bits(diagonal_moves(0, bb, bit(18)))
        assert 9 in result    # B2 reachable
        assert 18 not in result  # C3 blocked by friendly
        assert 27 not in result

    def test_enemy_piece_captured_ray_stops(self):
        bb = empty_bb()
        # Bishop at A1 (0), enemy at C3 (18)
        bb[OCCUPIED] = bit(18)
        bb[B_PIECES] = bit(18)
        result = set_bits(diagonal_moves(0, bb, 0))
        assert 9 in result    # B2
        assert 18 in result   # C3 capture
        assert 27 not in result  # D4 blocked

    def test_result_excludes_source_square(self):
        bb = empty_bb()
        result = diagonal_moves(28, bb, 0)
        assert result & bit(28) == 0

    def test_squares_are_truly_diagonal(self):
        bb = empty_bb()
        result = set_bits(diagonal_moves(28, bb, 0))
        src_rank, src_file = 28 // 8, 28 % 8
        for sq in result:
            t_rank, t_file = sq // 8, sq % 8
            assert abs(t_rank - src_rank) == abs(t_file - src_file), \
                f"Square {sq} is not diagonal from {28}"


# ---------------------------------------------------------------------------
# queen_moves
# ---------------------------------------------------------------------------

class TestQueenMoves:
    def test_e4_empty_board_27_squares(self):
        # Queen at E4 (28): 14 (rook) + 13 (bishop) = 27
        bb = empty_bb()
        assert bin(queen_moves(28, bb, 0)).count("1") == 27

    def test_a1_empty_board(self):
        # A1 (0): N=7, E=7, NE diagonal=7 → 21 total
        bb = empty_bb()
        assert bin(queen_moves(0, bb, 0)).count("1") == 21

    def test_queen_moves_equals_cross_plus_diagonal(self):
        bb = empty_bb()
        for sq in range(64):
            assert queen_moves(sq, bb, 0) == (
                cross_moves(sq, bb, 0) | diagonal_moves(sq, bb, 0)
            )

    def test_blocked_queen(self):
        bb = empty_bb()
        # Queen at E4 (28), friendly piece at E5 (36) blocks north
        bb[OCCUPIED] = bit(36)
        bb[W_PIECES] = bit(36)
        result = queen_moves(28, bb, bit(36))
        assert result & bit(36) == 0   # friendly square excluded
        assert result & bit(44) == 0   # beyond friendly, excluded
