"""
Tests for the Square class.

Covers: coordinate notation, color assignment, absolute pixel positions,
and the set_view() flip behaviour.
"""

import pytest
from data.classes.Square import Square


SQUARE_W = 100
SQUARE_H = 100


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_square(x, y):
    return Square(x, y, SQUARE_W, SQUARE_H)


# ---------------------------------------------------------------------------
# get_coord()
# ---------------------------------------------------------------------------

class TestGetCoord:
    def test_a1(self):
        assert make_square(0, 0).get_coord() == "a1"

    def test_h1(self):
        assert make_square(7, 0).get_coord() == "h1"

    def test_a8(self):
        assert make_square(0, 7).get_coord() == "a8"

    def test_h8(self):
        assert make_square(7, 7).get_coord() == "h8"

    def test_e4(self):
        # file e = index 4, rank 4 = y+1 = 4 → y=3
        assert make_square(4, 3).get_coord() == "e4"

    def test_d5(self):
        assert make_square(3, 4).get_coord() == "d5"


# ---------------------------------------------------------------------------
# Square color
# ---------------------------------------------------------------------------

class TestSquareColor:
    def test_a1_is_light(self):
        # (0+0) % 2 == 0 → light
        sq = make_square(0, 0)
        assert sq.color == "light"

    def test_b1_is_dark(self):
        # (1+0) % 2 == 1 → dark
        sq = make_square(1, 0)
        assert sq.color == "dark"

    def test_h8_is_light(self):
        # (7+7) % 2 == 0 → light
        sq = make_square(7, 7)
        assert sq.color == "light"

    def test_a8_is_dark(self):
        # (0+7) % 2 == 1 → dark
        sq = make_square(0, 7)
        assert sq.color == "dark"

    def test_checkerboard_pattern(self):
        for x in range(8):
            for y in range(8):
                sq = make_square(x, y)
                expected = "light" if (x + y) % 2 == 0 else "dark"
                assert sq.color == expected, f"({x},{y}) expected {expected}"


# ---------------------------------------------------------------------------
# Absolute pixel position
# ---------------------------------------------------------------------------

class TestAbsolutePosition:
    def test_origin(self):
        sq = make_square(0, 0)
        assert sq.abs_x == 0
        assert sq.abs_y == 0
        assert sq.abs_pos == (0, 0)

    def test_arbitrary_square(self):
        sq = make_square(3, 5)
        assert sq.abs_x == 300
        assert sq.abs_y == 500
        assert sq.abs_pos == (300, 500)

    def test_bottom_right(self):
        sq = make_square(7, 7)
        assert sq.abs_x == 700
        assert sq.abs_y == 700


# ---------------------------------------------------------------------------
# pos and rect
# ---------------------------------------------------------------------------

class TestPosAndRect:
    def test_pos_tuple(self):
        sq = make_square(2, 4)
        assert sq.pos == (2, 4)

    def test_rect_origin(self):
        sq = make_square(0, 0)
        assert sq.rect.x == 0
        assert sq.rect.y == 0
        assert sq.rect.width == SQUARE_W
        assert sq.rect.height == SQUARE_H

    def test_rect_offset(self):
        sq = make_square(3, 2)
        assert sq.rect.x == 300
        assert sq.rect.y == 200


# ---------------------------------------------------------------------------
# set_view()
# ---------------------------------------------------------------------------

class TestSetView:
    def test_no_flip(self):
        sq = make_square(2, 3)
        sq.set_view(False)
        assert sq.abs_x == 2 * SQUARE_W
        assert sq.abs_y == 3 * SQUARE_H
        assert sq.abs_pos == (200, 300)

    def test_flip(self):
        sq = make_square(2, 3)
        sq.set_view(True)
        # flipped: draw_x = 7-2=5, draw_y = 7-3=4
        assert sq.abs_x == 5 * SQUARE_W
        assert sq.abs_y == 4 * SQUARE_H
        assert sq.abs_pos == (500, 400)

    def test_flip_corner_a1(self):
        sq = make_square(0, 0)
        sq.set_view(True)
        # draw_x = 7, draw_y = 7
        assert sq.abs_x == 7 * SQUARE_W
        assert sq.abs_y == 7 * SQUARE_H

    def test_flip_corner_h8(self):
        sq = make_square(7, 7)
        sq.set_view(True)
        # draw_x = 0, draw_y = 0
        assert sq.abs_x == 0
        assert sq.abs_y == 0

    def test_flip_rect_updated(self):
        sq = make_square(1, 2)
        sq.set_view(True)
        assert sq.rect.x == sq.abs_x
        assert sq.rect.y == sq.abs_y

    def test_no_flip_does_not_change_rect(self):
        sq = make_square(4, 5)
        original_x = sq.abs_x
        sq.set_view(False)
        assert sq.abs_x == original_x


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

class TestInitialState:
    def test_no_piece_initially(self):
        sq = make_square(3, 3)
        assert sq.occupying_piece is None

    def test_highlight_false_initially(self):
        sq = make_square(3, 3)
        assert sq.highlight is False
