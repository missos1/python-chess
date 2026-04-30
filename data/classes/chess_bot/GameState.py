from .move_filter import is_square_attacked
from .move_gens import generate_all_moves
from .constants import *

class GameState:
    def __init__(self, bitboards, pieces_array):
        self.board = bitboards
        self.piece_values = pieces_array
        self.castling_rights = 15
        self.en_passant_sq = None
        self.state_history = []
        
        # Reference table for quickly checking castling rights
        self.castling_update_table = [15] * 64  # 1111

        # White
        self.castling_update_table[7] &= ~WK_RIGHT
        self.castling_update_table[0] &= ~WQ_RIGHT
        self.castling_update_table[4] &= ~(WK_RIGHT | WQ_RIGHT)

        # Black
        self.castling_update_table[63] &= ~BK_RIGHT
        self.castling_update_table[56] &= ~BQ_RIGHT
        self.castling_update_table[60] &= ~(BK_RIGHT | BQ_RIGHT)
        
    def sync_from_board(self, board):
        self.board = board.get_bitboards()
        self.piece_values = board.get_pieces_array()

    def make_move(self, move, color, board=None):
        if board is not None:
            self.sync_from_board(board)

        from_sq, to_sq, flag = move
        moving_piece = self.piece_values[from_sq]
        captured_piece = self.piece_values[to_sq]
        promoted_symbol = None

        # Moving pieces on the Bitboard
        move_mask = (1 << from_sq) | (1 << to_sq)
        self.board[moving_piece] ^= move_mask
        
        # Handling a capture
        if flag == FLAG_CAPTURE:
            self.board[captured_piece] &= ~(1 << to_sq)
        
        # update Piece Array
        self.piece_values[to_sq] = moving_piece
        self.piece_values[from_sq] = None

        # Pawn promotion: convert pawn to queen on the promotion rank
        if moving_piece in (W_PAWN, B_PAWN):
            if (color == WHITE and to_sq >= 56) or (color == BLACK and to_sq < 8):
                promoted_symbol = W_QUEEN if color == WHITE else B_QUEEN
                self.piece_values[to_sq] = promoted_symbol
                self.board[moving_piece] &= ~(1 << to_sq)
                self.board[promoted_symbol] |= (1 << to_sq)

        self.state_history.append({
            'move': move,
            'color': color,
            'captured': captured_piece,
            'castling': self.castling_rights,
            'en_passant': self.en_passant_sq,
            'moved_piece': moving_piece,
            'promoted_symbol': promoted_symbol
        })

        # Handling Castling (Move the rook as well)
        if flag in (FLAG_CASTLE_KS, FLAG_CASTLE_QS):
            r_from, r_to = self.get_rook_castle_sq(color, flag)
            rook_piece = W_ROOK if color == WHITE else B_ROOK
            rook_mask = (1 << r_from) | (1 << r_to)
            self.board[rook_piece] ^= rook_mask
            self.piece_values[r_to] = rook_piece
            self.piece_values[r_from] = None

        # Update Castling Rights
        self.castling_rights &= self.castling_update_table[from_sq]
        self.castling_rights &= self.castling_update_table[to_sq]

        # Update Bitboard (Incremental)
        self.update_summary_boards_incrementally(from_sq, to_sq, moving_piece, captured_piece, color, flag)
        if board is not None:
            board.update_piece_positions(self.piece_values) # update board to draw correctly after move

    def undo_move(self, board=None):
        if not self.state_history:
            return

        state = self.state_history.pop()
        from_sq, to_sq, flag = state['move']
        captured_piece = state['captured']
        moved_piece = state['moved_piece']
        promoted_symbol = state.get('promoted_symbol')
        color = WHITE if moved_piece.isupper() else BLACK

        # Reverse the move on the Bitboard
        if promoted_symbol is None:
            self.board[moved_piece] ^= (1 << from_sq) | (1 << to_sq)
        else:
            self.board[promoted_symbol] &= ~(1 << to_sq)
            self.board[moved_piece] |= (1 << from_sq)

        # Restore captured piece if there was one
        if captured_piece is not None:
            self.board[captured_piece] |= (1 << to_sq)
            self.piece_values[to_sq] = captured_piece
        else:
            self.piece_values[to_sq] = None
        
        self.piece_values[from_sq] = moved_piece

        # Reverse the castling move
        if flag in (FLAG_CASTLE_KS, FLAG_CASTLE_QS):
            r_from, r_to = self.get_rook_castle_sq(color, flag)
            rook_piece = W_ROOK if color == WHITE else B_ROOK
            self.board[rook_piece] ^= (1 << r_from) | (1 << r_to)
            self.piece_values[r_from] = rook_piece
            self.piece_values[r_to] = None

        # Restrore castling rights and en passant square
        self.castling_rights = state['castling']
        self.en_passant_sq = state['en_passant']
        self.full_update_summary_boards()
        if board is not None:
            board.update_piece_positions(self.piece_values) # update board to draw correctly after undo

    def update_summary_boards_incrementally(self, f, t, p, cap, color, flag):
        """Update the summary bitboards (W_PIECES, B_PIECES, OCCUPIED) based on a single move without needing to recalculate everything."""
        side_board = W_PIECES if color == WHITE else B_PIECES
        enemy_board = B_PIECES if color == WHITE else W_PIECES
        
        mask = (1 << f) | (1 << t)
        if flag in (FLAG_CASTLE_KS, FLAG_CASTLE_QS):
            r_from, r_to = self.get_rook_castle_sq(color, flag)
            mask |= (1 << r_from) | (1 << r_to)

        self.board[side_board] ^= mask
        
        if cap is not None:
            self.board[enemy_board] &= ~(1 << t)
            
        self.board[OCCUPIED] = self.board[W_PIECES] | self.board[B_PIECES]

    def get_rook_castle_sq(self, color, flag):
        if color == WHITE:
            return (7, 5) if flag == FLAG_CASTLE_KS else (0, 3)
        return (63, 61) if flag == FLAG_CASTLE_KS else (56, 59)

    def castle_path_safe(self, color, flag):
        enemy_color = BLACK if color == WHITE else WHITE
        if color == WHITE:
            if flag == FLAG_CASTLE_KS:
                path_squares = (4, 5, 6)
            else:
                path_squares = (4, 3, 2)
        else:
            if flag == FLAG_CASTLE_KS:
                path_squares = (60, 61, 62)
            else:
                path_squares = (60, 59, 58)

        for sq in path_squares:
            if is_square_attacked(sq, enemy_color, self.board):
                return False
        return True

    def get_strictly_legal_moves(self, color):
        pseudo_moves = generate_all_moves(self.board, color, self.castling_rights)
        legal_moves = []
        enemy_color = BLACK if color == WHITE else WHITE
        
        king_bitboard = self.board[W_KING] if color == WHITE else self.board[B_KING]
        king_sq = (king_bitboard & -king_bitboard).bit_length() - 1

        for move in pseudo_moves:
            from_sq, to_sq, flag = move
            
            # Check castling legality before trying the move
            if flag in (FLAG_CASTLE_KS, FLAG_CASTLE_QS):
                if not self.castle_path_safe(color, flag):
                    continue

            self.make_move(move, color)
            
            new_king_sq = to_sq if from_sq == king_sq else king_sq
            
            if not is_square_attacked(new_king_sq, enemy_color, self.board):
                legal_moves.append(move)
            
            self.undo_move(None)
            
        return legal_moves

    def full_update_summary_boards(self):
        # Only use when really need to recalculate everything
        self.board[W_PIECES] = (self.board[W_PAWN] | self.board[W_KNIGHT] | self.board[W_BISHOP] |
                                self.board[W_ROOK] | self.board[W_QUEEN] | self.board[W_KING])
        self.board[B_PIECES] = (self.board[B_PAWN] | self.board[B_KNIGHT] | self.board[B_BISHOP] |
                                self.board[B_ROOK] | self.board[B_QUEEN] | self.board[B_KING])
        self.board[OCCUPIED] = self.board[W_PIECES] | self.board[B_PIECES]