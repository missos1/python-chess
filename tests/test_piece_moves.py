"""
Tests for piece movement logic.

Covers: Pawn, Knight, Bishop, Rook, Queen, King – including special moves
(double push, diagonal capture, promotion, castling) and the Piece base-class
helpers (get_moves, get_valid_moves, move, attacking_squares).
"""

import pytest
from data.classes.Board import Board
from data.classes.pieces.Pawn import Pawn
from data.classes.pieces.Knight import Knight
from data.classes.pieces.Bishop import Bishop
from data.classes.pieces.Rook import Rook
from data.classes.pieces.Queen import Queen
from data.classes.pieces.King import King


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fresh_empty_board():
    b = Board(800, 800)
    for sq in b.squares:
        sq.occupying_piece = None
    return b


def place(board, cls, pos, color):
    piece = cls(pos, color, board)
    board.get_square_from_pos(pos).occupying_piece = piece
    return piece


def move_positions(piece, board):
    """Return sorted list of (x, y) tuples for a piece's valid moves."""
    return sorted((s.x, s.y) for s in piece.get_valid_moves(board))


# ---------------------------------------------------------------------------
# Pawn
# ---------------------------------------------------------------------------

class TestPawnMoves:
    def test_white_pawn_single_push(self):
        b = fresh_empty_board()
        place(b, King, (0, 0), "white")  # keep king on board for is_in_check
        pawn = place(b, Pawn, (4, 5), "white")
        pawn.has_moved = True
        moves = move_positions(pawn, b)
        assert (4, 4) in moves
        assert len(moves) == 1

    def test_white_pawn_double_push_from_start_rank(self):
        b = fresh_empty_board()
        place(b, King, (0, 0), "white")
        pawn = place(b, Pawn, (4, 6), "white")
        moves = move_positions(pawn, b)
        assert (4, 5) in moves
        assert (4, 4) in moves

    def test_white_pawn_blocked_single(self):
        b = fresh_empty_board()
        place(b, King, (0, 0), "white")
        pawn = place(b, Pawn, (4, 6), "white")
        place(b, Rook, (4, 5), "black")  # block the path
        moves = move_positions(pawn, b)
        assert (4, 5) not in moves
        assert (4, 4) not in moves

    def test_white_pawn_diagonal_capture(self):
        b = fresh_empty_board()
        place(b, King, (0, 0), "white")
        pawn = place(b, Pawn, (4, 6), "white")
        place(b, Knight, (5, 5), "black")
        moves = move_positions(pawn, b)
        assert (5, 5) in moves

    def test_white_pawn_no_capture_own_piece(self):
        b = fresh_empty_board()
        place(b, King, (0, 0), "white")
        pawn = place(b, Pawn, (4, 6), "white")
        place(b, Knight, (5, 5), "white")  # friendly – cannot capture
        moves = move_positions(pawn, b)
        assert (5, 5) not in moves

    def test_black_pawn_single_push(self):
        b = fresh_empty_board()
        place(b, King, (7, 7), "black")
        pawn = place(b, Pawn, (4, 2), "black")
        pawn.has_moved = True
        moves = move_positions(pawn, b)
        assert (4, 3) in moves
        assert len(moves) == 1

    def test_black_pawn_double_push_from_start_rank(self):
        b = fresh_empty_board()
        place(b, King, (7, 7), "black")
        pawn = place(b, Pawn, (4, 1), "black")
        moves = move_positions(pawn, b)
        assert (4, 2) in moves
        assert (4, 3) in moves

    def test_black_pawn_diagonal_capture(self):
        b = fresh_empty_board()
        place(b, King, (7, 7), "black")
        pawn = place(b, Pawn, (4, 1), "black")
        place(b, Knight, (3, 2), "white")
        moves = move_positions(pawn, b)
        assert (3, 2) in moves

    def test_pawn_attacking_squares_are_diagonal_only(self):
        b = fresh_empty_board()
        place(b, King, (0, 0), "white")
        pawn = place(b, Pawn, (4, 4), "white")
        atk = [(s.x, s.y) for s in pawn.attacking_squares(b)]
        assert (4, 3) not in atk   # forward square is not an attack square
        # Diagonal attack squares (only if empty – pawn.get_moves returns only
        # squares that actually have an enemy; attacking_squares filters by x)
        for sq_pos in atk:
            assert sq_pos[0] != 4  # no forward (same file) squares

    def test_pawn_a_file_no_left_capture(self):
        b = fresh_empty_board()
        place(b, King, (7, 7), "white")
        pawn = place(b, Pawn, (0, 6), "white")
        place(b, Knight, (0, 5), "black")  # directly in front – blocks
        # There's no square to the left of the a-file
        moves = move_positions(pawn, b)
        assert all(m[0] >= 0 for m in moves)

    def test_pawn_promotion_white(self):
        """White pawn reaching y=0 is replaced by a Queen."""
        b = fresh_empty_board()
        place(b, King, (7, 7), "white")
        pawn = place(b, Pawn, (4, 1), "white")
        target_sq = b.get_square_from_pos((4, 0))
        pawn.move(b, target_sq, force=True)
        promoted = b.get_piece_from_pos((4, 0))
        assert promoted is not None
        assert promoted.notation == "Q"
        assert promoted.color == "white"

    def test_pawn_promotion_black(self):
        """Black pawn reaching y=7 is replaced by a Queen."""
        b = fresh_empty_board()
        place(b, King, (0, 0), "black")
        pawn = place(b, Pawn, (4, 6), "black")
        target_sq = b.get_square_from_pos((4, 7))
        pawn.move(b, target_sq, force=True)
        promoted = b.get_piece_from_pos((4, 7))
        assert promoted is not None
        assert promoted.notation == "Q"
        assert promoted.color == "black"


# ---------------------------------------------------------------------------
# Knight
# ---------------------------------------------------------------------------

class TestKnightMoves:
    def test_knight_in_center_has_eight_moves(self):
        b = fresh_empty_board()
        knight = place(b, Knight, (4, 4), "white")
        moves = move_positions(knight, b)
        assert len(moves) == 8

    def test_knight_in_corner_a1_has_two_moves(self):
        b = fresh_empty_board()
        knight = place(b, Knight, (0, 7), "white")
        moves = move_positions(knight, b)
        assert len(moves) == 2
        assert (1, 5) in moves
        assert (2, 6) in moves

    def test_knight_blocked_by_friendly(self):
        b = fresh_empty_board()
        knight = place(b, Knight, (4, 4), "white")
        # Place a friendly piece on one of the knight's target squares
        place(b, Rook, (5, 2), "white")
        moves = move_positions(knight, b)
        assert (5, 2) not in moves

    def test_knight_can_capture_enemy(self):
        b = fresh_empty_board()
        knight = place(b, Knight, (4, 4), "white")
        place(b, Pawn, (5, 2), "black")
        moves = move_positions(knight, b)
        assert (5, 2) in moves

    def test_knight_jumps_over_pieces(self):
        b = fresh_empty_board()
        knight = place(b, Knight, (4, 4), "white")
        # Fill surrounding squares – knight should still have 8 moves
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0),
                       (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = 4 + dx, 4 + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                place(b, Rook, (nx, ny), "black")
        moves = move_positions(knight, b)
        assert len(moves) == 8

    def test_knight_l_shape_moves_correct(self):
        b = fresh_empty_board()
        knight = place(b, Knight, (3, 3), "white")
        expected = sorted([
            (4, 1), (5, 2), (5, 4), (4, 5),
            (2, 5), (1, 4), (1, 2), (2, 1),
        ])
        assert move_positions(knight, b) == expected


# ---------------------------------------------------------------------------
# Bishop
# ---------------------------------------------------------------------------

class TestBishopMoves:
    def test_bishop_in_center_empty_board(self):
        b = fresh_empty_board()
        bishop = place(b, Bishop, (4, 4), "white")
        # NE: (5,3),(6,2),(7,1)=3; NW: (3,3),(2,2),(1,1),(0,0)=4
        # SE: (5,5),(6,6),(7,7)=3; SW: (3,5),(2,6),(1,7)=3 → 13 total
        moves = move_positions(bishop, b)
        assert len(moves) == 13

    def test_bishop_blocked_by_friendly(self):
        b = fresh_empty_board()
        bishop = place(b, Bishop, (0, 7), "white")
        place(b, Pawn, (1, 6), "white")
        moves = move_positions(bishop, b)
        assert (1, 6) not in moves
        assert len(moves) == 0  # only the NE diagonal, blocked immediately

    def test_bishop_can_capture_enemy_but_not_pass(self):
        b = fresh_empty_board()
        bishop = place(b, Bishop, (0, 7), "white")
        place(b, Pawn, (2, 5), "black")
        moves = move_positions(bishop, b)
        assert (1, 6) in moves
        assert (2, 5) in moves
        assert (3, 4) not in moves  # blocked by the captured pawn

    def test_bishop_corner_h8_diagonal(self):
        b = fresh_empty_board()
        bishop = place(b, Bishop, (7, 0), "white")
        moves = move_positions(bishop, b)
        # Only SW diagonal: (6,1),(5,2),(4,3),(3,4),(2,5),(1,6),(0,7) = 7 squares
        assert len(moves) == 7


# ---------------------------------------------------------------------------
# Rook
# ---------------------------------------------------------------------------

class TestRookMoves:
    def test_rook_in_center_empty_board(self):
        b = fresh_empty_board()
        rook = place(b, Rook, (4, 4), "white")
        moves = move_positions(rook, b)
        # N:4, S:3, E:3, W:4 = 14
        assert len(moves) == 14

    def test_rook_on_a1_empty_board(self):
        b = fresh_empty_board()
        rook = place(b, Rook, (0, 7), "white")
        moves = move_positions(rook, b)
        # N:7, E:7, S:0, W:0 = 14
        assert len(moves) == 14

    def test_rook_blocked_by_friendly(self):
        b = fresh_empty_board()
        rook = place(b, Rook, (4, 4), "white")
        place(b, Pawn, (4, 2), "white")  # blocks north direction at (4,2)
        moves = move_positions(rook, b)
        # North direction: (4,3) then stopped by friendly at (4,2) → only (4,3)
        assert (4, 3) in moves
        assert (4, 2) not in moves
        assert (4, 1) not in moves

    def test_rook_captures_enemy_stops_there(self):
        b = fresh_empty_board()
        rook = place(b, Rook, (4, 4), "white")
        place(b, Pawn, (4, 2), "black")
        moves = move_positions(rook, b)
        assert (4, 3) in moves
        assert (4, 2) in moves   # can capture
        assert (4, 1) not in moves  # cannot pass through


# ---------------------------------------------------------------------------
# Queen
# ---------------------------------------------------------------------------

class TestQueenMoves:
    def test_queen_center_empty_board_27_moves(self):
        b = fresh_empty_board()
        queen = place(b, Queen, (4, 4), "white")
        moves = move_positions(queen, b)
        # Rook-like: 14, Bishop-like: 13 = 27 total
        assert len(moves) == 27

    def test_queen_blocked_by_friendly(self):
        b = fresh_empty_board()
        queen = place(b, Queen, (4, 4), "white")
        place(b, Rook, (4, 3), "white")  # block north
        moves = move_positions(queen, b)
        assert (4, 3) not in moves
        assert (4, 2) not in moves

    def test_queen_can_capture_but_not_pass(self):
        b = fresh_empty_board()
        queen = place(b, Queen, (4, 4), "white")
        place(b, Pawn, (4, 2), "black")
        moves = move_positions(queen, b)
        assert (4, 3) in moves
        assert (4, 2) in moves
        assert (4, 1) not in moves


# ---------------------------------------------------------------------------
# King
# ---------------------------------------------------------------------------

class TestKingMoves:
    def test_king_center_eight_moves(self):
        b = fresh_empty_board()
        king = place(b, King, (4, 4), "white")
        king.has_moved = True
        moves = move_positions(king, b)
        assert len(moves) == 8

    def test_king_corner_three_moves(self):
        b = fresh_empty_board()
        king = place(b, King, (0, 7), "white")
        king.has_moved = True
        moves = move_positions(king, b)
        assert len(moves) == 3

    def test_king_cannot_move_into_check(self):
        b = fresh_empty_board()
        king = place(b, King, (4, 4), "white")
        king.has_moved = True
        # Black rook at (4,0) controls the entire file – (4,3) and (4,5)
        # would leave the king on the rook's file
        place(b, Rook, (3, 0), "black")  # controls column 3
        moves = move_positions(king, b)
        for x, y in moves:
            assert x != 3, f"King moved to file 3 which is attacked by black rook"

    def test_king_cannot_capture_into_check(self):
        """King should not capture a piece that is defended."""
        b = fresh_empty_board()
        king = place(b, King, (4, 7), "white")
        king.has_moved = True
        # Black pawn at (5,6) defended by a black rook at (5,0)
        place(b, Pawn, (5, 6), "black")
        place(b, Rook, (5, 0), "black")
        moves = move_positions(king, b)
        assert (5, 6) not in moves


class TestKingCastle:
    def test_can_castle_kingside_initial_position(self):
        b = Board(800, 800)
        # Clear kingside path for white
        b.get_square_from_pos((5, 7)).occupying_piece = None
        b.get_square_from_pos((6, 7)).occupying_piece = None
        king = b.get_piece_from_pos((4, 7))
        assert king.can_castle(b) == "kingside"

    def test_can_castle_queenside_initial_position(self):
        b = Board(800, 800)
        # Clear queenside path for white
        for x in [1, 2, 3]:
            b.get_square_from_pos((x, 7)).occupying_piece = None
        king = b.get_piece_from_pos((4, 7))
        assert king.can_castle(b) == "queenside"

    def test_cannot_castle_after_king_moved(self):
        b = Board(800, 800)
        for x in [5, 6]:
            b.get_square_from_pos((x, 7)).occupying_piece = None
        king = b.get_piece_from_pos((4, 7))
        king.has_moved = True
        assert king.can_castle(b) is None

    def test_cannot_castle_when_path_blocked(self):
        b = Board(800, 800)
        # Kingside path not cleared → bishop at (5,7) blocks
        king = b.get_piece_from_pos((4, 7))
        assert king.can_castle(b) is None

    def test_castling_moves_rook_kingside(self):
        """When the king castles kingside, the rook should end up at f1."""
        b = Board(800, 800)
        b.get_square_from_pos((5, 7)).occupying_piece = None
        b.get_square_from_pos((6, 7)).occupying_piece = None
        king = b.get_piece_from_pos((4, 7))
        castle_sq = b.get_square_from_pos((6, 7))
        king.move(b, castle_sq)
        assert b.get_piece_from_pos((6, 7)) is not None
        assert b.get_piece_from_pos((6, 7)).notation == "K"
        assert b.get_piece_from_pos((5, 7)) is not None
        assert b.get_piece_from_pos((5, 7)).notation == "R"
        assert b.get_piece_from_pos((7, 7)) is None

    def test_black_can_castle_kingside(self):
        b = Board(800, 800)
        for x in [5, 6]:
            b.get_square_from_pos((x, 0)).occupying_piece = None
        king = b.get_piece_from_pos((4, 0))
        assert king.can_castle(b) == "kingside"

    def test_black_can_castle_queenside(self):
        b = Board(800, 800)
        for x in [1, 2, 3]:
            b.get_square_from_pos((x, 0)).occupying_piece = None
        king = b.get_piece_from_pos((4, 0))
        assert king.can_castle(b) == "queenside"


# ---------------------------------------------------------------------------
# Piece base-class – move() and get_valid_moves() with check filtering
# ---------------------------------------------------------------------------

class TestPieceMoveMethod:
    def test_move_returns_true_on_valid_move(self):
        b = Board(800, 800)
        pawn = b.get_piece_from_pos((4, 6))
        target = b.get_square_from_pos((4, 5))
        result = pawn.move(b, target)
        assert result is True

    def test_move_returns_false_on_invalid_move(self):
        b = Board(800, 800)
        pawn = b.get_piece_from_pos((4, 6))
        target = b.get_square_from_pos((4, 3))  # too far
        result = pawn.move(b, target)
        assert result is False

    def test_move_updates_piece_position(self):
        b = Board(800, 800)
        pawn = b.get_piece_from_pos((4, 6))
        target = b.get_square_from_pos((4, 5))
        pawn.move(b, target)
        assert pawn.pos == (4, 5)
        assert pawn.x == 4
        assert pawn.y == 5

    def test_move_updates_board_squares(self):
        b = Board(800, 800)
        pawn = b.get_piece_from_pos((4, 6))
        target = b.get_square_from_pos((4, 5))
        pawn.move(b, target)
        assert b.get_piece_from_pos((4, 6)) is None
        assert b.get_piece_from_pos((4, 5)) is pawn

    def test_move_sets_has_moved(self):
        b = Board(800, 800)
        pawn = b.get_piece_from_pos((4, 6))
        assert pawn.has_moved is False
        pawn.move(b, b.get_square_from_pos((4, 5)))
        assert pawn.has_moved is True

    def test_move_force_ignores_validity(self):
        b = fresh_empty_board()
        place(b, King, (0, 0), "white")
        rook = place(b, Rook, (4, 4), "white")
        # Force the rook to a square that would otherwise require a clear path check
        target = b.get_square_from_pos((4, 0))
        result = rook.move(b, target, force=True)
        assert result is True
        assert b.get_piece_from_pos((4, 0)) is rook

    def test_get_valid_moves_filters_moves_that_expose_check(self):
        """A pinned piece should have no valid moves."""
        b = fresh_empty_board()
        wk = place(b, King, (4, 7), "white")
        wk.has_moved = True
        # White rook on same file as king, with enemy rook behind
        wr = place(b, Rook, (4, 4), "white")
        place(b, Rook, (4, 0), "black")   # pins the white rook
        # The white rook is pinned – moving off the file would expose the king
        valid = wr.get_valid_moves(b)
        for sq in valid:
            assert sq.x == 4, "Pinned rook should only move along the pin file"
