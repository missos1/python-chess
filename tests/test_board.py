"""
Tests for the Board class.

Covers: square generation, piece setup, square/piece lookup, check detection,
checkmate detection, bitboard generation, click handlers, and board flipping.
"""

import pytest
from data.classes.Board import Board
from data.classes.pieces.King import King
from data.classes.pieces.Queen import Queen
from data.classes.pieces.Rook import Rook
from data.classes.pieces.Bishop import Bishop
from data.classes.pieces.Knight import Knight
from data.classes.pieces.Pawn import Pawn


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def place(board, cls, pos, color):
    """Place a piece of *cls* at *pos* and return it."""
    piece = cls(pos, color, board)
    board.get_square_from_pos(pos).occupying_piece = piece
    return piece


# ---------------------------------------------------------------------------
# generate_squares
# ---------------------------------------------------------------------------

class TestGenerateSquares:
    def test_square_count(self, board):
        assert len(board.squares) == 64

    def test_all_positions_unique(self, board):
        positions = {(s.x, s.y) for s in board.squares}
        assert len(positions) == 64

    def test_positions_cover_full_grid(self, board):
        positions = {(s.x, s.y) for s in board.squares}
        for x in range(8):
            for y in range(8):
                assert (x, y) in positions

    def test_square_dimensions(self, board):
        for sq in board.squares:
            assert sq.width == board.square_width
            assert sq.height == board.square_height


# ---------------------------------------------------------------------------
# setup_board – initial piece placement
# ---------------------------------------------------------------------------

class TestInitialSetup:
    def test_initial_turn_is_white(self, board):
        assert board.turn == "white"

    def test_white_pawns_on_rank6(self, board):
        for x in range(8):
            piece = board.get_piece_from_pos((x, 6))
            assert piece is not None
            assert piece.color == "white"
            assert piece.notation == " "

    def test_black_pawns_on_rank1(self, board):
        for x in range(8):
            piece = board.get_piece_from_pos((x, 1))
            assert piece is not None
            assert piece.color == "black"
            assert piece.notation == " "

    def test_empty_middle_rows(self, board):
        for y in range(2, 6):
            for x in range(8):
                assert board.get_piece_from_pos((x, y)) is None

    def test_white_back_rank_pieces(self, board):
        expected = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        for x, notation in enumerate(expected):
            piece = board.get_piece_from_pos((x, 7))
            assert piece is not None
            assert piece.notation == notation
            assert piece.color == "white"

    def test_black_back_rank_pieces(self, board):
        expected = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        for x, notation in enumerate(expected):
            piece = board.get_piece_from_pos((x, 0))
            assert piece is not None
            assert piece.notation == notation
            assert piece.color == "black"


# ---------------------------------------------------------------------------
# get_square_from_pos / get_piece_from_pos
# ---------------------------------------------------------------------------

class TestSquareLookup:
    def test_get_square_from_pos_returns_correct_square(self, board):
        sq = board.get_square_from_pos((3, 5))
        assert sq.x == 3
        assert sq.y == 5

    def test_get_square_from_pos_all_corners(self, board):
        for x, y in [(0, 0), (7, 0), (0, 7), (7, 7)]:
            sq = board.get_square_from_pos((x, y))
            assert sq.pos == (x, y)

    def test_get_piece_from_pos_occupied(self, board):
        piece = board.get_piece_from_pos((4, 7))  # white king
        assert piece is not None
        assert piece.notation == "K"

    def test_get_piece_from_pos_empty(self, board):
        assert board.get_piece_from_pos((4, 4)) is None


# ---------------------------------------------------------------------------
# is_in_check
# ---------------------------------------------------------------------------

class TestIsInCheck:
    def test_no_check_at_start(self, board):
        assert board.is_in_check("white") is False
        assert board.is_in_check("black") is False

    def test_king_in_check_from_rook(self, empty_board):
        b = empty_board
        place(b, King, (4, 7), "white")
        place(b, Rook, (4, 0), "black")  # attacks white king via the same file
        assert b.is_in_check("white") is True

    def test_king_not_in_check_rook_different_file(self, empty_board):
        b = empty_board
        place(b, King, (4, 7), "white")
        place(b, Rook, (5, 0), "black")
        assert b.is_in_check("white") is False

    def test_king_in_check_from_bishop(self, empty_board):
        b = empty_board
        place(b, King, (4, 7), "white")
        place(b, Bishop, (7, 4), "black")  # diagonal: (4,7)→(5,6)→(6,5)→(7,4)
        assert b.is_in_check("white") is True

    def test_king_not_in_check_blocked_by_own_piece(self, empty_board):
        b = empty_board
        place(b, King, (4, 7), "white")
        place(b, Rook, (4, 4), "white")  # friendly piece blocks the enemy rook
        place(b, Rook, (4, 0), "black")
        assert b.is_in_check("white") is False

    def test_board_change_exposes_check(self, empty_board):
        """Moving a friendly piece out of the way reveals a check."""
        b = empty_board
        wk = place(b, King, (7, 7), "white")
        place(b, Rook, (7, 5), "white")  # shields the king
        place(b, Rook, (7, 0), "black")
        # Not in check now (white rook blocks)
        assert b.is_in_check("white") is False
        # Simulate moving the white rook away → exposes the king
        assert b.is_in_check("white", board_change=[(7, 5), (6, 5)]) is True

    def test_board_change_king_moves_to_safe_square(self, empty_board):
        b = empty_board
        place(b, King, (4, 7), "white")
        place(b, Rook, (4, 0), "black")
        # King is in check; moving to (5,7) escapes the rook's file
        assert b.is_in_check("white", board_change=[(4, 7), (5, 7)]) is False

    def test_king_in_check_from_queen(self, empty_board):
        b = empty_board
        place(b, King, (0, 7), "white")
        place(b, Queen, (7, 7), "black")  # same rank
        assert b.is_in_check("white") is True

    def test_king_in_check_from_knight(self, empty_board):
        b = empty_board
        place(b, King, (4, 7), "white")
        # Knight at (3,5): moves (+1,+2)→(4,7) → attacks white king
        place(b, Knight, (3, 5), "black")
        assert b.is_in_check("white") is True


# ---------------------------------------------------------------------------
# is_in_checkmate
# ---------------------------------------------------------------------------

class TestIsInCheckmate:
    def _setup_checkmate(self, empty_board):
        """
        White king at corner (0,7), attacked by black rook at (0,5).
        All three escape squares covered:
          (0,6) by the rook continuing south,
          (1,6) by black queen at (2,6) going west,
          (1,7) by black queen going south-west.
        """
        b = empty_board
        wk = place(b, King, (0, 7), "white")
        wk.has_moved = True  # disable castling look-up
        place(b, Rook, (0, 5), "black")
        place(b, Queen, (2, 6), "black")
        return b

    def test_is_in_checkmate_true(self, empty_board):
        b = self._setup_checkmate(empty_board)
        assert b.is_in_checkmate("white") is True

    def test_not_in_checkmate_when_escape_exists(self, empty_board):
        b = empty_board
        wk = place(b, King, (0, 7), "white")
        wk.has_moved = True
        place(b, Rook, (0, 5), "black")
        # No queen – king can escape to (1,6) or (1,7)
        assert b.is_in_checkmate("white") is False

    def test_not_in_checkmate_when_not_in_check(self, empty_board):
        b = empty_board
        wk = place(b, King, (4, 4), "white")
        wk.has_moved = True
        assert b.is_in_checkmate("white") is False


# ---------------------------------------------------------------------------
# get_bitboards
# ---------------------------------------------------------------------------

class TestGetBitboards:
    """
    LERF index = (7 - square.y) * 8 + square.x.
    Initial white back rank: y=7  → LERF rank 0  (indices 0–7).
    Initial white pawns:      y=6  → LERF rank 1  (indices 8–15).
    Initial black pawns:      y=1  → LERF rank 6  (indices 48–55).
    Initial black back rank:  y=0  → LERF rank 7  (indices 56–63).
    """

    def test_white_pawns(self, board):
        bb = board.get_bitboards()
        assert bb["P"] == 0xFF00  # bits 8–15

    def test_black_pawns(self, board):
        bb = board.get_bitboards()
        assert bb["p"] == 0x00FF000000000000  # bits 48–55

    def test_white_rooks(self, board):
        bb = board.get_bitboards()
        assert bb["R"] == (1 << 0) | (1 << 7)  # A1=0, H1=7

    def test_black_rooks(self, board):
        bb = board.get_bitboards()
        assert bb["r"] == (1 << 56) | (1 << 63)  # A8=56, H8=63

    def test_white_knights(self, board):
        bb = board.get_bitboards()
        assert bb["N"] == (1 << 1) | (1 << 6)  # B1=1, G1=6

    def test_black_knights(self, board):
        bb = board.get_bitboards()
        assert bb["n"] == (1 << 57) | (1 << 62)

    def test_white_bishops(self, board):
        bb = board.get_bitboards()
        assert bb["B"] == (1 << 2) | (1 << 5)

    def test_black_bishops(self, board):
        bb = board.get_bitboards()
        assert bb["b"] == (1 << 58) | (1 << 61)

    def test_white_queen(self, board):
        bb = board.get_bitboards()
        assert bb["Q"] == (1 << 3)

    def test_black_queen(self, board):
        bb = board.get_bitboards()
        assert bb["q"] == (1 << 59)

    def test_white_king(self, board):
        bb = board.get_bitboards()
        assert bb["K"] == (1 << 4)

    def test_black_king(self, board):
        bb = board.get_bitboards()
        assert bb["k"] == (1 << 60)

    def test_white_pieces_summary(self, board):
        bb = board.get_bitboards()
        expected = bb["P"] | bb["N"] | bb["B"] | bb["R"] | bb["Q"] | bb["K"]
        assert bb["white_pieces"] == expected

    def test_black_pieces_summary(self, board):
        bb = board.get_bitboards()
        expected = bb["p"] | bb["n"] | bb["b"] | bb["r"] | bb["q"] | bb["k"]
        assert bb["black_pieces"] == expected

    def test_occupied_summary(self, board):
        bb = board.get_bitboards()
        assert bb["occupied_squares"] == (bb["white_pieces"] | bb["black_pieces"])

    def test_empty_board_all_zeros(self, empty_board):
        bb = empty_board.get_bitboards()
        for key in ["P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k",
                    "white_pieces", "black_pieces", "occupied_squares"]:
            assert bb[key] == 0, f"{key} should be 0 on empty board"


# ---------------------------------------------------------------------------
# handle_click
# ---------------------------------------------------------------------------

class TestHandleClick:
    """
    Board is 800×800, so each square is 100×100 pixels.
    Pixel (mx, my) → square (mx//100, my//100).
    """

    def test_click_selects_white_piece_on_whites_turn(self, board):
        # e2 pawn is at logical (4,6); centre pixel ≈ (450, 650)
        board.handle_click(450, 650)
        assert board.selected_piece is not None
        assert board.selected_piece.pos == (4, 6)

    def test_click_does_not_select_black_piece_on_whites_turn(self, board):
        board.handle_click(450, 150)  # e7 black pawn
        assert board.selected_piece is None

    def test_click_does_not_select_empty_square(self, board):
        board.handle_click(450, 450)  # e5 – empty
        assert board.selected_piece is None

    def test_click_moves_pawn_forward(self, board):
        board.handle_click(450, 650)  # select e2 pawn
        board.handle_click(450, 550)  # move to e3 (4,5)
        assert board.get_piece_from_pos((4, 5)) is not None
        assert board.get_piece_from_pos((4, 6)) is None

    def test_click_move_switches_turn(self, board):
        board.handle_click(450, 650)
        board.handle_click(450, 550)
        assert board.turn == "black"

    def test_click_invalid_move_deselects(self, board):
        board.handle_click(450, 650)  # select e2 pawn
        board.handle_click(450, 350)  # click e6 – not a valid pawn move
        assert board.selected_piece is None

    def test_click_out_of_bounds_ignored(self, board):
        board.handle_click(-10, 50)
        assert board.selected_piece is None

    def test_reselect_another_piece(self, board):
        board.handle_click(350, 650)  # select d2 pawn
        board.handle_click(450, 650)  # click e2 pawn (reselect)
        assert board.selected_piece is not None
        assert board.selected_piece.pos == (4, 6)


# ---------------------------------------------------------------------------
# handle_click_flipped
# ---------------------------------------------------------------------------

class TestHandleClickFlipped:
    """
    Flipped board: x = 7 – (mx // 100), y = 7 – (my // 100).
    Click (350, 150) → x=7–3=4, y=7–1=6 → logical (4,6) = e2 white pawn.
    """

    def test_click_selects_piece_on_flipped_board(self):
        b = Board(800, 800, is_flipped=True)
        b.handle_click_flipped(350, 150)
        assert b.selected_piece is not None
        assert b.selected_piece.pos == (4, 6)

    def test_click_moves_piece_on_flipped_board(self):
        b = Board(800, 800, is_flipped=True)
        b.handle_click_flipped(350, 150)  # select e2 pawn
        b.handle_click_flipped(350, 250)  # move to (4,5): x=7-3=4, y=7-2=5
        assert b.get_piece_from_pos((4, 5)) is not None
        assert b.turn == "black"


# ---------------------------------------------------------------------------
# apply_view
# ---------------------------------------------------------------------------

class TestApplyView:
    def test_apply_view_sets_is_flipped(self, board):
        board.apply_view(True)
        assert board.is_flipped is True

    def test_apply_view_false(self, board):
        board.apply_view(True)
        board.apply_view(False)
        assert board.is_flipped is False

    def test_apply_view_updates_squares(self, board):
        sq = board.get_square_from_pos((0, 0))
        board.apply_view(True)
        # a1 flipped → draw position becomes h8 pixel coords
        assert sq.abs_x == 7 * board.square_width
        assert sq.abs_y == 7 * board.square_height
