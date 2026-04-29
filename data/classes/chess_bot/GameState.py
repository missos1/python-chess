from .move_filter import is_square_attacked
from .move_gens import generate_all_moves
from .constants import *

class GameState:
    def __init__(self, bitboards, pieces_array):
        self.board = bitboards
        self.piece_values = pieces_array
        self.castling_rights = 15
        self.state_history = []
        
    def make_move(self, board, move, color):
        if move is None:
            return

        from_sq, to_sq, flag = move

        from_pos = self.square_index_to_pos(from_sq)
        to_pos = self.square_index_to_pos(to_sq)
        from_square = board.get_square_from_pos(from_pos)
        to_square = board.get_square_from_pos(to_pos)

        moving_piece = from_square.occupying_piece if from_square else None
        captured_piece = to_square.occupying_piece if to_square else None

        rook_snapshot = None
        if flag in (FLAG_CASTLE_KS, FLAG_CASTLE_QS):
            if color == WHITE:
                rook_from_pos = (7, 0) if flag == FLAG_CASTLE_KS else (0, 0)
                rook_to_pos = (5, 0) if flag == FLAG_CASTLE_KS else (3, 0)
            else:
                rook_from_pos = (7, 7) if flag == FLAG_CASTLE_KS else (0, 7)
                rook_to_pos = (5, 7) if flag == FLAG_CASTLE_KS else (3, 7)
            rook_piece = board.get_piece_from_pos(rook_from_pos)
            rook_snapshot = {
                'piece': rook_piece,
                'from_pos': rook_from_pos,
                'to_pos': rook_to_pos,
                'has_moved': rook_piece.has_moved if rook_piece else None
            }

        self.state_history.append({
            'board': self.board.copy(),
            'castling_rights': self.castling_rights,
            'from_sq': from_sq,
            'to_sq': to_sq,
            'flag': flag,
            'moving_piece': moving_piece,
            'captured_piece': captured_piece,
            'moving_piece_has_moved': moving_piece.has_moved if moving_piece else None,
            'rook_snapshot': rook_snapshot
        })

        self.board, self.castling_rights = self._simulate_move(
            self.board,
            move,
            color,
            self.castling_rights
        )

        self._apply_move_to_board(board, from_sq, to_sq, flag)

    def undo_move(self, board):
        if not self.state_history:
            return

        last_state = self.state_history.pop()
        self.board = last_state['board']
        self.castling_rights = last_state['castling_rights']

        from_pos = self.square_index_to_pos(last_state['from_sq'])
        to_pos = self.square_index_to_pos(last_state['to_sq'])
        from_square = board.get_square_from_pos(from_pos)
        to_square = board.get_square_from_pos(to_pos)

        if from_square is None or to_square is None:
            return

        moving_piece = last_state['moving_piece']
        captured_piece = last_state['captured_piece']

        if moving_piece is not None:
            moving_piece.pos = from_pos
            moving_piece.x, moving_piece.y = from_pos
            moving_piece.has_moved = last_state['moving_piece_has_moved']

        to_square.occupying_piece = captured_piece
        from_square.occupying_piece = moving_piece

        if captured_piece is not None:
            captured_piece.pos = to_pos
            captured_piece.x, captured_piece.y = to_pos

        if last_state['flag'] in (FLAG_CASTLE_KS, FLAG_CASTLE_QS):
            rook_snapshot = last_state['rook_snapshot']
            if rook_snapshot and rook_snapshot['piece'] is not None:
                rook_piece = rook_snapshot['piece']
                rook_from_square = board.get_square_from_pos(rook_snapshot['from_pos'])
                rook_to_square = board.get_square_from_pos(rook_snapshot['to_pos'])

                rook_piece.pos = rook_snapshot['from_pos']
                rook_piece.x, rook_piece.y = rook_snapshot['from_pos']
                rook_piece.has_moved = rook_snapshot['has_moved']

                rook_from_square.occupying_piece = rook_piece
                rook_to_square.occupying_piece = None

    def _get_piece_at(self, bitboards, square_index):
        for piece in [W_PAWN, W_KNIGHT, W_BISHOP, W_ROOK, W_QUEEN, W_KING,
                      B_PAWN, B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN, B_KING]:
            if bitboards[piece] & (1 << square_index):
                return piece
        return None

    def _get_king_square(self, bitboards, color):
        king_board = bitboards[W_KING] if color == WHITE else bitboards[B_KING]
        return (king_board & -king_board).bit_length() - 1

    def _update_summary_boards(self, bitboards):
        bitboards[W_PIECES] = (
            bitboards[W_PAWN] | bitboards[W_KNIGHT] | bitboards[W_BISHOP] |
            bitboards[W_ROOK] | bitboards[W_QUEEN] | bitboards[W_KING]
        )
        bitboards[B_PIECES] = (
            bitboards[B_PAWN] | bitboards[B_KNIGHT] | bitboards[B_BISHOP] |
            bitboards[B_ROOK] | bitboards[B_QUEEN] | bitboards[B_KING]
        )
        bitboards[OCCUPIED] = bitboards[W_PIECES] | bitboards[B_PIECES]

    def _simulate_move(self, bitboards, move, color, castling_rights):
        from_sq, to_sq, flag = move
        new_board = bitboards.copy()
        moving_piece = self._get_piece_at(new_board, from_sq)
        if moving_piece is None:
            return new_board, castling_rights

        # Remove the moving piece from its source square
        new_board[moving_piece] &= ~(1 << from_sq)

        # Handle capture
        if flag == FLAG_CAPTURE:
            enemy_piece_types = [W_PAWN, W_KNIGHT, W_BISHOP, W_ROOK, W_QUEEN, W_KING] if color == BLACK else [B_PAWN, B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN, B_KING]
            for piece_type in enemy_piece_types:
                if new_board[piece_type] & (1 << to_sq):
                    new_board[piece_type] &= ~(1 << to_sq)
                    break

        # Place the moving piece on the destination square
        if flag in (FLAG_CASTLE_KS, FLAG_CASTLE_QS):
            new_board[moving_piece] |= (1 << to_sq)
            if color == WHITE:
                if flag == FLAG_CASTLE_KS:
                    rook_from, rook_to = 7, 5
                else:
                    rook_from, rook_to = 0, 3
                rook_piece = W_ROOK
            else:
                if flag == FLAG_CASTLE_KS:
                    rook_from, rook_to = 63, 61
                else:
                    rook_from, rook_to = 56, 59
                rook_piece = B_ROOK
            new_board[rook_piece] &= ~(1 << rook_from)
            new_board[rook_piece] |= (1 << rook_to)
        else:
            new_board[moving_piece] |= (1 << to_sq)

        # Update castling rights
        if moving_piece == W_KING:
            castling_rights &= ~(WK_RIGHT | WQ_RIGHT)
        elif moving_piece == B_KING:
            castling_rights &= ~(BK_RIGHT | BQ_RIGHT)
        elif moving_piece == W_ROOK:
            if from_sq == 7:
                castling_rights &= ~WK_RIGHT
            elif from_sq == 0:
                castling_rights &= ~WQ_RIGHT
        elif moving_piece == B_ROOK:
            if from_sq == 63:
                castling_rights &= ~BK_RIGHT
            elif from_sq == 56:
                castling_rights &= ~BQ_RIGHT

        if flag == FLAG_CAPTURE:
            if color == WHITE and to_sq in {56, 63}:
                if to_sq == 56:
                    castling_rights &= ~BQ_RIGHT
                else:
                    castling_rights &= ~BK_RIGHT
            elif color == BLACK and to_sq in {0, 7}:
                if to_sq == 0:
                    castling_rights &= ~WQ_RIGHT
                else:
                    castling_rights &= ~WK_RIGHT

        self._update_summary_boards(new_board)
        return new_board, castling_rights

    def square_index_to_pos(self, square_index):
        x = square_index % 8
        y = 7 - (square_index // 8)
        return x, y

    def pos_to_square_index(self, pos):
        x, y = pos
        return (7 - y) * 8 + x

    def _apply_move_to_board(self, board, from_sq, to_sq, flag):
        from_pos = self.square_index_to_pos(from_sq)
        to_pos = self.square_index_to_pos(to_sq)

        from_square = board.get_square_from_pos(from_pos)
        to_square = board.get_square_from_pos(to_pos)

        if from_square is None or to_square is None:
            return

        moving_piece = from_square.occupying_piece
        if moving_piece is None:
            return

        # Force the board move so AI and engine state stay in sync.
        moving_piece.moving(board, to_square, force=True)

    def _castle_path_safe(self, color, flag):
        enemy_color = BLACK if color == WHITE else WHITE
        if color == WHITE:
            path = [4, 5, 6] if flag == FLAG_CASTLE_KS else [4, 3, 2]
        else:
            path = [60, 61, 62] if flag == FLAG_CASTLE_KS else [60, 59, 58]
        return not any(is_square_attacked(square, enemy_color, self.board) for square in path)

    def get_strictly_legal_moves(self, color):
        pseudo_legal_moves = generate_all_moves(self.board, color, self.castling_rights)
        strictly_legal = []
        enemy_color = BLACK if color == WHITE else WHITE

        for move in pseudo_legal_moves:
            _, _, flag = move

            if flag in (FLAG_CASTLE_KS, FLAG_CASTLE_QS) and not self._castle_path_safe(color, flag):
                continue

            new_board, new_castling = self._simulate_move(self.board, move, color, self.castling_rights)
            king_square = self._get_king_square(new_board, color)
            if not is_square_attacked(king_square, enemy_color, new_board):
                strictly_legal.append(move)

        return strictly_legal