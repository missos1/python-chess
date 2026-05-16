from .constants import *
from .move_filter import is_square_attacked
from .move_gens import *
from .precompute import ZOBRIST_PIECES, ZOBRIST_CASTLING, ZOBRIST_TURN, ZOBRIST_EN_PASSANT

class GameState:
    def __init__(self, bitboards: list, pieces_array: list, castling_rights: int, en_passant_target=None, color = WHITE):
        self.bitboards = bitboards
        self.piece_values = pieces_array
        self.castling_rights = castling_rights
        self.en_passant_target = en_passant_target
        self.state_history = []
        self.turn_color = color
        self.zobrist_hash = self._compute_initial_hash()

    def _compute_initial_hash(self):
        h = 0
        for sq in range(64):
            piece = self.piece_values[sq]
            if piece != EMPTY:
                h ^= ZOBRIST_PIECES[piece][sq]
        h ^= ZOBRIST_CASTLING[self.castling_rights]
        if self.en_passant_target is not None:
            h ^= ZOBRIST_EN_PASSANT[self.en_passant_target % 8]
        h ^= ZOBRIST_TURN if self.turn_color == BLACK else 0
        return h
        
    def make_move(self, move):
        """This function use history stack and Zobrist hashing 
        (utilizing the xor operation attribute a ^ b ^ b = a) 
        to efficiently make a move on the board and update 
        all relevant state variables. It also handles all special 
        move types (castling, en passant, promotion) 
        and updates castling rights accordingly. """
        source, target, flag = move
        
        piece_moved = self.piece_values[source]
        captured_piece = self.piece_values[target]
        
        # 1. SAVE THE HISTORY
        # Push castling rights and the victim so we can restore them later
        self.state_history.append((self.castling_rights, captured_piece, self.zobrist_hash, self.en_passant_target))
        
        # Remove old castling rights from hash
        self.zobrist_hash ^= ZOBRIST_CASTLING[self.castling_rights]
        
        # Remove old en passant target from hash
        if self.en_passant_target is not None:
            self.zobrist_hash ^= ZOBRIST_EN_PASSANT[self.en_passant_target % 8]
        self.en_passant_target = None
        
        # Remove the moving piece from its original square in hash
        self.zobrist_hash ^= ZOBRIST_PIECES[piece_moved][source]
        if captured_piece != EMPTY:
            self.zobrist_hash ^= ZOBRIST_PIECES[captured_piece][target]
        self.zobrist_hash ^= ZOBRIST_PIECES[piece_moved][target]
        
        self.piece_values[target] = piece_moved
        self.piece_values[source] = EMPTY
        
        # 3. STANDARD BITBOARD TELEPORTATION (XOR)
        # Move the attacker
        
        self.bitboards[piece_moved] ^= (1 << source) | (1 << target)
        
        # If it was a capture, delete the victim from its bitboard
        if captured_piece != EMPTY and flag != FLAG_EN_PASSANT:
            self.bitboards[captured_piece] ^= (1 << target)

        # 4. HANDLE SPECIAL FLAGS
        if flag == FLAG_DOUBLE_PAWN:
            if piece_moved == W_PAWN:
                self.en_passant_target = target - 8
            else:
                self.en_passant_target = target + 8
            self.zobrist_hash ^= ZOBRIST_EN_PASSANT[self.en_passant_target % 8]
                
        elif flag == FLAG_EN_PASSANT:
            victim_sq = target - 8 if piece_moved == W_PAWN else target + 8
            victim_piece = self.piece_values[victim_sq]
            
            # Remove victim from bitboard, history and hash
            self.bitboards[victim_piece] ^= (1 << victim_sq)
            self.piece_values[victim_sq] = EMPTY
            self.zobrist_hash ^= ZOBRIST_PIECES[victim_piece][victim_sq]
            
        elif flag == FLAG_PROMOTION:
            # Delete the Pawn we just moved to the 8th/1st rank
            self.bitboards[piece_moved] ^= (1 << target) 
            self.zobrist_hash ^= ZOBRIST_PIECES[piece_moved][target] # Remove Pawn from hatch
            
            # Spawn the Queen and update the piece array
            if piece_moved == W_PAWN:
                self.bitboards[W_QUEEN] ^= (1 << target)
                self.piece_values[target] = W_QUEEN
                self.zobrist_hash ^= ZOBRIST_PIECES[W_QUEEN][target] # Add Queen
            else:
                self.bitboards[B_QUEEN] ^= (1 << target)
                self.piece_values[target] = B_QUEEN
                self.zobrist_hash ^= ZOBRIST_PIECES[B_QUEEN][target] # Add Queen

        elif flag == FLAG_CASTLE_KS:
            if target == 6: # White O-O
                self.bitboards[W_ROOK] ^= (1 << 7) | (1 << 5)
                self.piece_values[7] = EMPTY
                self.piece_values[5] = W_ROOK
                self.zobrist_hash ^= ZOBRIST_PIECES[W_ROOK][7] # Remove rook on h1
                self.zobrist_hash ^= ZOBRIST_PIECES[W_ROOK][5] # Add rook on f1
            elif target == 62: # Black O-O
                self.bitboards[B_ROOK] ^= (1 << 63) | (1 << 61)
                self.piece_values[63] = EMPTY
                self.piece_values[61] = B_ROOK
                self.zobrist_hash ^= ZOBRIST_PIECES[B_ROOK][63]
                self.zobrist_hash ^= ZOBRIST_PIECES[B_ROOK][61]

        elif flag == FLAG_CASTLE_QS:
            if target == 2: # White O-O-O
                self.bitboards[W_ROOK] ^= (1 << 0) | (1 << 3)
                self.piece_values[0] = EMPTY
                self.piece_values[3] = W_ROOK
                self.zobrist_hash ^= ZOBRIST_PIECES[W_ROOK][0]
                self.zobrist_hash ^= ZOBRIST_PIECES[W_ROOK][3]
            elif target == 58: # Black O-O-O
                self.bitboards[B_ROOK] ^= (1 << 56) | (1 << 59)
                self.piece_values[56] = EMPTY
                self.piece_values[59] = B_ROOK
                self.zobrist_hash ^= ZOBRIST_PIECES[B_ROOK][56]
                self.zobrist_hash ^= ZOBRIST_PIECES[B_ROOK][59]

        # King moves: lose both rights
        if piece_moved == W_KING:
            self.castling_rights &= ~(WK_RIGHT | WQ_RIGHT)
        elif piece_moved == B_KING:
            self.castling_rights &= ~(BK_RIGHT | BQ_RIGHT)
            
        # Rook moves or is captured on its starting square: lose that specific right
        if source == 0 or target == 0: self.castling_rights &= ~WQ_RIGHT
        if source == 7 or target == 7: self.castling_rights &= ~WK_RIGHT
        if source == 56 or target == 56: self.castling_rights &= ~BQ_RIGHT
        if source == 63 or target == 63: self.castling_rights &= ~BK_RIGHT
        
        # Add new castling rights into hash
        self.zobrist_hash ^= ZOBRIST_CASTLING[self.castling_rights]
        self.zobrist_hash ^= ZOBRIST_TURN
        self.turn_color = BLACK if self.turn_color == WHITE else WHITE
        
        self._update_composites()

    def _update_composites(self):
        # Dynamically recalculate team and occupied bitboards so the move-generator never uses stale data in deep searches!
        self.bitboards[W_PIECES] = (
            self.bitboards[W_PAWN] | self.bitboards[W_KNIGHT] | self.bitboards[W_BISHOP] |
            self.bitboards[W_ROOK] | self.bitboards[W_QUEEN] | self.bitboards[W_KING]
        )
        self.bitboards[B_PIECES] = (
            self.bitboards[B_PAWN] | self.bitboards[B_KNIGHT] | self.bitboards[B_BISHOP] |
            self.bitboards[B_ROOK] | self.bitboards[B_QUEEN] | self.bitboards[B_KING]
        )
        self.bitboards[OCCUPIED] = self.bitboards[W_PIECES] | self.bitboards[B_PIECES]
    
    def undo_move(self, move):
        """This function uses the history stack and Zobrist hashing 
        to efficiently undo a move, including all special move types and
        restoring castling rights. By popping the last state from the 
        history stack, we can revert to the previous position without needing 
        to recompute everything from scratch. The use of XOR with Zobrist hashing 
        allows us to quickly update the hash back to its previous value.
        """
        source, target, flag = move
        
        # 1. POP THE HISTORY
        old_castling_rights, captured_piece, old_zobrist_hash, old_en_passant = self.state_history.pop()
        
        # Instantly restore old castling rights, hash, and en passant!
        self.castling_rights = old_castling_rights
        self.zobrist_hash = old_zobrist_hash
        self.en_passant_target = old_en_passant
        
        # Identify the piece currently sitting on the target square
        piece_moved = self.piece_values[target]
        
        # 2. REVERT SPECIAL FLAGS (Before standard reversion)
        if flag == FLAG_PROMOTION:
            # Kill the Queen we spawned
            
            self.bitboards[piece_moved] ^= (1 << target) 
            
            # Re-assign piece_moved to be a Pawn
            if target >= 56: # White
                piece_moved = W_PAWN
            else:            # Black
                piece_moved = B_PAWN
                
            # Spawn the Pawn back on the target square temporarily
            self.bitboards[piece_moved] ^= (1 << target)
            
        elif flag == FLAG_CASTLE_KS:
            if target == 6: # White
                self.bitboards[W_ROOK] ^= (1 << 5) | (1 << 7) # F1 back to H1
                self.piece_values[5] = EMPTY
                self.piece_values[7] = W_ROOK
            elif target == 62: # Black
                self.bitboards[B_ROOK] ^= (1 << 61) | (1 << 63) # F8 back to H8
                self.piece_values[61] = EMPTY
                self.piece_values[63] = B_ROOK

        elif flag == FLAG_CASTLE_QS:
            if target == 2: # White
                self.bitboards[W_ROOK] ^= (1 << 3) | (1 << 0) # D1 back to A1
                self.piece_values[3] = EMPTY
                self.piece_values[0] = W_ROOK
            elif target == 58: # Black
                self.bitboards[B_ROOK] ^= (1 << 59) | (1 << 56) # D8 back to A8
                self.piece_values[59] = EMPTY
                self.piece_values[56] = B_ROOK

        elif flag == FLAG_EN_PASSANT:
            victim_sq = target - 8 if piece_moved == W_PAWN else target + 8
            # The victim wasn't stored at 'target', so we manually put it back
            victim_piece = B_PAWN if piece_moved == W_PAWN else W_PAWN
            self.piece_values[victim_sq] = victim_piece
            self.bitboards[victim_piece] ^= (1 << victim_sq)
            captured_piece = EMPTY # Prevent the lower capture logic from restoring a piece at 'target'

        # 3. REVERT STANDARD BITBOARD TELEPORTATION (XOR)
        # Move the piece backwards from target to source
        self.bitboards[piece_moved] ^= (1 << target) | (1 << source)
        
        # If there was a capture, resurrect the victim!
        if captured_piece != EMPTY:
            self.bitboards[captured_piece] ^= (1 << target)

        # 4. REVERT THE PIECE ARRAY
        self.piece_values[source] = piece_moved
        self.piece_values[target] = captured_piece
        self.turn_color = BLACK if self.turn_color == WHITE else WHITE
        
        self._update_composites()
        
    def make_null_move(self):
        """This function is used for Null Move Pruning in the search
        algorithm. By making a "null move" (i.e., skipping our turn), we can test 
        if the opponent has any strong responses. If they do, it indicates that we need 
        to search this position more deeply. If they don't, we can safely assume this position 
        is good for us and cut off the search. The history stack and Zobrist hash are updated accordingly 
        to allow for an efficient undo of the null move.
        """
        self.state_history.append((self.castling_rights, None, self.zobrist_hash, self.en_passant_target))
        
        # self.castling_rights ^= ZOBRIST_CASTLING[self.castling_rights]
        
        if self.en_passant_target is not None:
            self.zobrist_hash ^= ZOBRIST_EN_PASSANT[self.en_passant_target % 8]
        self.en_passant_target = None
        
        self.zobrist_hash ^= ZOBRIST_TURN
        self.turn_color = BLACK if self.turn_color == WHITE else WHITE
        
    def undo_null_move(self):
        old_castling_rights, _, old_zobrist_hash, old_en_passant = self.state_history.pop()
        
        self.castling_rights = old_castling_rights
        self.zobrist_hash = old_zobrist_hash
        self.en_passant_target = old_en_passant
        self.turn_color = BLACK if self.turn_color == WHITE else WHITE
    
    def get_strictly_legal_moves(self, color):
        raw_moves = generate_all_moves(self.bitboards, color, self.castling_rights, self.en_passant_target)
        
        legal_moves = []
        enemy_color = BLACK if color == WHITE else WHITE
        
        for move in raw_moves:
            source, target, flag = move
            is_castling_illegal = False
            
            if flag == FLAG_CASTLE_KS:
                if color == WHITE:
                    if is_square_attacked(4, enemy_color, self.bitboards) or \
                    is_square_attacked(5, enemy_color, self.bitboards):
                        is_castling_illegal = True  
                else:
                    if is_square_attacked(60, enemy_color, self.bitboards) or \
                    is_square_attacked(61, enemy_color, self.bitboards):
                        is_castling_illegal = True        
            elif flag == FLAG_CASTLE_QS:
                if color == WHITE:
                    if is_square_attacked(4, enemy_color, self.bitboards) or \
                    is_square_attacked(3, enemy_color, self.bitboards):
                        is_castling_illegal = True
                else:
                    if is_square_attacked(60, enemy_color, self.bitboards) or \
                    is_square_attacked(59, enemy_color, self.bitboards):
                        is_castling_illegal = True
            if is_castling_illegal:
                continue
            
            self.make_move(move)
            
            king_board = self.bitboards[W_KING] if color == WHITE else self.bitboards[B_KING]
            
            if king_board != 0:
                king_sq = (king_board & -king_board).bit_length() - 1
                
                # if the king is not in check after the move, it's a legal move
                if not is_square_attacked(king_sq, enemy_color, self.bitboards):
                    legal_moves.append(move)
                    
            self.undo_move(move)    
            
        return legal_moves

    def get_capture_moves_only(self, color):
        raw_moves = generate_all_moves(self.bitboards, color, self.castling_rights, self.en_passant_target)
        capture_moves = []
        enemy_color = BLACK if color == WHITE else WHITE
        
        make_move = self.make_move
        undo_move = self.undo_move
        bitboards = self.bitboards
        
        for move in raw_moves:
            _, _, flag = move
            if flag == FLAG_CAPTURE or flag == FLAG_PROMOTION or flag == FLAG_EN_PASSANT:
                make_move(move)
                
                king_board = bitboards[W_KING] if color == WHITE else bitboards[B_KING]
                
                if king_board != 0:
                    king_sq = (king_board & -king_board).bit_length() - 1
                    if not is_square_attacked(king_sq, enemy_color, bitboards):
                        capture_moves.append(move)
                        
                undo_move(move)
                
        return capture_moves
    
    def get_non_pawn_materials(self):
        total_mat = 0
        heavy_pieces = [W_QUEEN, W_ROOK, W_BISHOP, W_KNIGHT, B_QUEEN, B_ROOK, B_BISHOP, B_KNIGHT]
        for piece in heavy_pieces:
            count = (self.bitboards[piece]).bit_count()
            total_mat += PIECE_POINT_VALUES[piece] * count
            
        return total_mat