"""
Tests for the precomputed bitboard tables in chess_bot/precompute.py.

Covers: correct array lengths, boundary values for corner/edge squares,
and basic arithmetic properties of each table.
"""

import pytest
from data.classes.chess_bot.precompute import (
    NORTH_RAYS, SOUTH_RAYS, EAST_RAYS, WEST_RAYS,
    NORTHEAST_RAYS, NORTHWEST_RAYS, SOUTHEAST_RAYS, SOUTHWEST_RAYS,
    KNIGHT_MOVES, KING_MOVES,
    WHITE_PAWN_CAPTURES, BLACK_PAWN_CAPTURES,
)
from data.classes.chess_bot.constants import BOARD_MASK


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def set_bits(bb):
    """Return a sorted list of set bit indices in *bb*."""
    indices = []
    while bb:
        lsb = bb & -bb
        indices.append(lsb.bit_length() - 1)
        bb &= bb - 1
    return indices


# ---------------------------------------------------------------------------
# Array lengths
# ---------------------------------------------------------------------------

class TestArrayLengths:
    @pytest.mark.parametrize("table", [
        NORTH_RAYS, SOUTH_RAYS, EAST_RAYS, WEST_RAYS,
        NORTHEAST_RAYS, NORTHWEST_RAYS, SOUTHEAST_RAYS, SOUTHWEST_RAYS,
        KNIGHT_MOVES, KING_MOVES, WHITE_PAWN_CAPTURES, BLACK_PAWN_CAPTURES,
    ])
    def test_has_64_entries(self, table):
        assert len(table) == 64

    @pytest.mark.parametrize("table", [
        NORTH_RAYS, SOUTH_RAYS, EAST_RAYS, WEST_RAYS,
        NORTHEAST_RAYS, NORTHWEST_RAYS, SOUTHEAST_RAYS, SOUTHWEST_RAYS,
        KNIGHT_MOVES, KING_MOVES, WHITE_PAWN_CAPTURES, BLACK_PAWN_CAPTURES,
    ])
    def test_all_entries_are_non_negative_integers(self, table):
        for val in table:
            assert isinstance(val, int) and val >= 0

    @pytest.mark.parametrize("table", [
        NORTH_RAYS, SOUTH_RAYS, EAST_RAYS, WEST_RAYS,
        NORTHEAST_RAYS, NORTHWEST_RAYS, SOUTHEAST_RAYS, SOUTHWEST_RAYS,
        WHITE_PAWN_CAPTURES, BLACK_PAWN_CAPTURES,
    ])
    def test_values_within_board_mask(self, table):
        """Ray tables and pawn capture tables should never exceed 64 bits."""
        for val in table:
            assert val & BOARD_MASK == val


# ---------------------------------------------------------------------------
# NORTH_RAYS
# ---------------------------------------------------------------------------

class TestNorthRays:
    def test_a1_north_ray(self):
        # From A1 (index 0), north covers A2–A8 (indices 8,16,24,32,40,48,56)
        bits = set_bits(NORTH_RAYS[0])
        assert bits == [8, 16, 24, 32, 40, 48, 56]

    def test_a8_north_ray_is_zero(self):
        # A8 (index 56) has nothing further north
        assert NORTH_RAYS[56] == 0

    def test_ray_does_not_contain_source_square(self):
        for sq in range(64):
            assert NORTH_RAYS[sq] & (1 << sq) == 0

    def test_e4_north_ray(self):
        # E4 = index (3*8)+4 = 28. North: E5=36,E6=44,E7=52,E8=60
        bits = set_bits(NORTH_RAYS[28])
        assert bits == [36, 44, 52, 60]


# ---------------------------------------------------------------------------
# SOUTH_RAYS
# ---------------------------------------------------------------------------

class TestSouthRays:
    def test_a1_south_ray_is_zero(self):
        assert SOUTH_RAYS[0] == 0

    def test_a8_south_ray(self):
        # A8 (index 56) south → A7,A6,...,A1 = (48,40,32,24,16,8,0)
        bits = set_bits(SOUTH_RAYS[56])
        assert bits == [0, 8, 16, 24, 32, 40, 48]

    def test_north_and_south_complement_each_other(self):
        # For any square, NORTH_RAYS + SOUTH_RAYS + source bit = full file mask
        for file in range(8):
            for rank in range(8):
                sq = rank * 8 + file
                full_file = sum(1 << (r * 8 + file) for r in range(8))
                assert (NORTH_RAYS[sq] | SOUTH_RAYS[sq] | (1 << sq)) == full_file


# ---------------------------------------------------------------------------
# EAST_RAYS
# ---------------------------------------------------------------------------

class TestEastRays:
    def test_a1_east_ray(self):
        # From A1 (0), east covers B1–H1 = indices 1–7
        bits = set_bits(EAST_RAYS[0])
        assert bits == [1, 2, 3, 4, 5, 6, 7]

    def test_h1_east_ray_is_zero(self):
        assert EAST_RAYS[7] == 0

    def test_ray_stays_on_same_rank(self):
        for rank in range(8):
            for file in range(8):
                sq = rank * 8 + file
                for target in set_bits(EAST_RAYS[sq]):
                    assert target // 8 == rank


# ---------------------------------------------------------------------------
# WEST_RAYS
# ---------------------------------------------------------------------------

class TestWestRays:
    def test_h1_west_ray(self):
        # H1 = index 7; west covers G1–A1 = indices 6,5,4,3,2,1,0
        bits = set_bits(WEST_RAYS[7])
        assert bits == [0, 1, 2, 3, 4, 5, 6]

    def test_a1_west_ray_is_zero(self):
        assert WEST_RAYS[0] == 0

    def test_east_and_west_complement_on_same_rank(self):
        for rank in range(8):
            for file in range(8):
                sq = rank * 8 + file
                full_rank = sum(1 << (rank * 8 + f) for f in range(8))
                assert (EAST_RAYS[sq] | WEST_RAYS[sq] | (1 << sq)) == full_rank


# ---------------------------------------------------------------------------
# Diagonal rays
# ---------------------------------------------------------------------------

class TestDiagonalRays:
    def test_northeast_from_a1(self):
        # A1 (0) NE: B2=9, C3=18, D4=27, E5=36, F6=45, G7=54, H8=63
        bits = set_bits(NORTHEAST_RAYS[0])
        assert bits == [9, 18, 27, 36, 45, 54, 63]

    def test_northeast_from_h1_is_zero(self):
        # H-file → nothing to the right
        assert NORTHEAST_RAYS[7] == 0

    def test_northwest_from_h1(self):
        # H1 (7) NW: G2=14, F3=21, E4=28, D5=35, C6=42, B7=49, A8=56
        bits = set_bits(NORTHWEST_RAYS[7])
        assert bits == [14, 21, 28, 35, 42, 49, 56]

    def test_northwest_from_a1_is_zero(self):
        assert NORTHWEST_RAYS[0] == 0

    def test_southeast_from_a8(self):
        # A8 (56) SE: B7=49, C6=42, D5=35, E4=28, F3=21, G2=14, H1=7
        bits = set_bits(SOUTHEAST_RAYS[56])
        assert bits == [7, 14, 21, 28, 35, 42, 49]

    def test_southwest_from_h8(self):
        # H8 (63) SW: G7=54, F6=45, E5=36, D4=27, C3=18, B2=9, A1=0
        bits = set_bits(SOUTHWEST_RAYS[63])
        assert bits == [0, 9, 18, 27, 36, 45, 54]


# ---------------------------------------------------------------------------
# KNIGHT_MOVES
# ---------------------------------------------------------------------------

class TestKnightMoves:
    def test_a1_knight(self):
        # From A1 (0): B3=17, C2=10
        bits = set_bits(KNIGHT_MOVES[0])
        assert sorted(bits) == sorted([10, 17])

    def test_center_knight_has_eight_moves(self):
        # E4 = index 28 (rank 3, file 4); in LERF: rank=3, file=4 → 3*8+4=28
        assert bin(KNIGHT_MOVES[28]).count("1") == 8

    def test_knight_moves_do_not_wrap(self):
        """Moves from h-file should not land on a-file (wrapping prevention)."""
        for file in range(8):
            for rank in range(8):
                sq = rank * 8 + file
                for target in set_bits(KNIGHT_MOVES[sq]):
                    t_file = target % 8
                    t_rank = target // 8
                    assert abs(t_file - file) in (1, 2), \
                        f"Unexpected file jump {file} → {t_file}"
                    assert abs(t_rank - rank) in (1, 2), \
                        f"Unexpected rank jump {rank} → {t_rank}"

    def test_h1_knight(self):
        # H1 (7): G3=22, F2=13
        bits = set_bits(KNIGHT_MOVES[7])
        assert sorted(bits) == sorted([13, 22])


# ---------------------------------------------------------------------------
# KING_MOVES
# ---------------------------------------------------------------------------

class TestKingMoves:
    def test_a1_king(self):
        # From A1 (0): A2=8, B1=1, B2=9
        bits = set_bits(KING_MOVES[0])
        assert sorted(bits) == sorted([1, 8, 9])

    def test_e4_king_has_eight_moves(self):
        # Central square
        assert bin(KING_MOVES[28]).count("1") == 8

    def test_king_moves_are_single_step(self):
        for rank in range(8):
            for file in range(8):
                sq = rank * 8 + file
                for target in set_bits(KING_MOVES[sq]):
                    t_file = target % 8
                    t_rank = target // 8
                    assert abs(t_file - file) <= 1, "King moved more than 1 file"
                    assert abs(t_rank - rank) <= 1, "King moved more than 1 rank"

    def test_h8_king(self):
        # H8 (63): G8=62, G7=54, H7=55.
        # Note: upward left/straight shifts from rank 7 produce off-board bits
        # (indices 70 and 71); mask to on-board squares to check valid neighbors.
        on_board = set_bits(KING_MOVES[63] & BOARD_MASK)
        assert sorted(on_board) == sorted([54, 55, 62])


# ---------------------------------------------------------------------------
# Pawn captures
# ---------------------------------------------------------------------------

class TestPawnCaptures:
    def test_white_pawn_a2_captures(self):
        # A2 = LERF 8. White pawn at A2 captures NE → B3=17 only (no NW from A-file)
        bits = set_bits(WHITE_PAWN_CAPTURES[8])
        assert bits == [17]

    def test_white_pawn_e2_captures(self):
        # E2 = LERF 12. Captures D3=19 and F3=21
        bits = set_bits(WHITE_PAWN_CAPTURES[12])
        assert sorted(bits) == sorted([19, 21])

    def test_white_pawn_h2_captures(self):
        # H2 = LERF 15. Only captures G3=22 (no NE past h-file)
        bits = set_bits(WHITE_PAWN_CAPTURES[15])
        assert bits == [22]

    def test_black_pawn_a7_captures(self):
        # A7 = LERF 48. Black captures SE → B6=41 only
        bits = set_bits(BLACK_PAWN_CAPTURES[48])
        assert bits == [41]

    def test_black_pawn_e7_captures(self):
        # E7 = LERF 52. Captures D6=43 and F6=45
        bits = set_bits(BLACK_PAWN_CAPTURES[52])
        assert sorted(bits) == sorted([43, 45])

    def test_black_pawn_h7_captures(self):
        # H7 = LERF 55. Only captures G6=46
        bits = set_bits(BLACK_PAWN_CAPTURES[55])
        assert bits == [46]
