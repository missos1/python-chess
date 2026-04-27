from .constants import *
from .precompute import *
from .ray_cast_moves import *

# Returns the indices of the set bits in a bitboard
# Example: 0b1010 -> yields 1 and 3 (0-indexed from the right)
def get_set_bits(bitboard):
	while bitboard: 
		lsb = bitboard & -bitboard
		yield lsb.bit_length() - 1
		bitboard &= bitboard - 1
  
def get_pawns_moves(bitboards, color):
    moves = []
    
    occupied = bitboards[OCCUPIED]
    
    empty = ~occupied & BOARD_MASK

    if color == WHITE:
        pawns = bitboards[W_PAWN]
        enemies = bitboards[B_PIECES]

        for pawn in get_set_bits(pawns):
            single_push = pawn + 8
            
            if (1 << single_push) & empty:
                moves.append((pawn, single_push, FLAG_QUIET))
                
                if pawn // 8 == 1: 				# Only pawns on the 2nd rank can do a double push
                    double_push = pawn + 16 	# Only possible from the 2nd rank (indices 8-15)
                    if (1 << double_push) & empty:
                        moves.append((pawn, double_push, FLAG_DOUBLE_PAWN))

            captures_board = WHITE_PAWN_CAPTURES[pawn] & enemies
            
            for target in get_set_bits(captures_board):
                moves.append((pawn, target, FLAG_CAPTURE))

    else:
        pawns = bitboards[B_PAWN]
        enemies = bitboards[W_PIECES]

        for pawn in get_set_bits(pawns):
            single_push = pawn - 8
            
            if (1 << single_push) & empty:
                moves.append((pawn, single_push, FLAG_QUIET))
                
                if pawn // 8 == 6:
                    double_push = pawn - 16
                    if (1 << double_push) & empty:
                        moves.append((pawn, double_push, FLAG_DOUBLE_PAWN))

            captures_board = BLACK_PAWN_CAPTURES[pawn] & enemies
            
            for target in get_set_bits(captures_board):
                moves.append((pawn, target, FLAG_CAPTURE))

    return moves

def get_knights_moves(bitboards, color):
	moves = []
	if color == WHITE:
		knights = bitboards[W_KNIGHT]
		friendly_pieces = bitboards[W_PIECES]
		enemy_pieces = bitboards[B_PIECES]
	else:
		knights = bitboards[B_KNIGHT]
		friendly_pieces = bitboards[B_PIECES]
		enemy_pieces = bitboards[W_PIECES]
	
	for knight in get_set_bits(knights):
		raw_moves = KNIGHT_MOVES[knight]
		legal_moves = raw_moves & ~friendly_pieces
  
		captures_board = legal_moves & enemy_pieces
		quiets_board = legal_moves & ~enemy_pieces
  
		for target in get_set_bits(captures_board):
			moves.append((knight, target, FLAG_CAPTURE))
   
		for target in get_set_bits(quiets_board):
			moves.append((knight, target, FLAG_QUIET))
   
	return moves

def get_king_moves(bitboards, color, castling_rights):
    moves = []
    occupied = bitboards[OCCUPIED]

    if color == WHITE:
        king_board = bitboards[W_KING]
        friendly_pieces = bitboards[W_PIECES]
        enemies = bitboards[B_PIECES]
        
        king = (king_board & -king_board).bit_length() - 1
        
        raw_moves = KING_MOVES[king]
        legal_moves = raw_moves & ~friendly_pieces

        for target in get_set_bits(legal_moves):
            if (1 << target) & enemies:
                moves.append((king, target, FLAG_CAPTURE))
            else:
                moves.append((king, target, FLAG_QUIET))
                
        if castling_rights & WK_RIGHT:
            if (occupied & W_KS_EMPTY) == 0:
                moves.append((king, 6, FLAG_CASTLE_KS))
                
        # Queenside Castling (O-O-O)
        if castling_rights & WQ_RIGHT:
            if (occupied & W_QS_EMPTY) == 0:
                moves.append((king, 2, FLAG_CASTLE_QS))

    else:
        king_board = bitboards[B_KING]
        friendly_pieces = bitboards[B_PIECES]
        enemies = bitboards[W_PIECES]
        
        king = (king_board & -king_board).bit_length() - 1
        
        raw_moves = KING_MOVES[king]
        legal_moves = raw_moves & ~friendly_pieces

        for target in get_set_bits(legal_moves):
            if (1 << target) & enemies:
                moves.append((king, target, FLAG_CAPTURE))
            else:
                moves.append((king, target, FLAG_QUIET))
                
        if castling_rights & BK_RIGHT:
            if (occupied & B_KS_EMPTY) == 0:
                moves.append((king, 62, FLAG_CASTLE_KS))
                
        if castling_rights & BQ_RIGHT:
            if (occupied & B_QS_EMPTY) == 0:
                moves.append((king, 58, FLAG_CASTLE_QS))

    return moves

def _get_sliding_pieces_moves(bitboards, color, white_piece, black_piece, move_func):
	moves = []
	
	pieces = bitboards[white_piece] if color == WHITE else bitboards[black_piece]
	friendly_pieces = bitboards[W_PIECES] if color == WHITE else bitboards[B_PIECES]
	enemy_pieces = bitboards[B_PIECES] if color == WHITE else bitboards[W_PIECES]
		
	for piece in get_set_bits(pieces):
		legal_moves = move_func(piece, bitboards, friendly_pieces)
		
		captures_board = legal_moves & enemy_pieces
		quiets_board = legal_moves & ~enemy_pieces
		
		for target in get_set_bits(captures_board):
			moves.append((piece, target, FLAG_CAPTURE))
			
		for target in get_set_bits(quiets_board):
			moves.append((piece, target, FLAG_QUIET))
			
	return moves

def get_rooks_moves(bitboards, color):
	return _get_sliding_pieces_moves(bitboards, color, W_ROOK, B_ROOK, cross_moves)

def get_bishops_moves(bitboards, color):
	return _get_sliding_pieces_moves(bitboards, color, W_BISHOP, B_BISHOP, diagonal_moves)

def get_queens_moves(bitboards, color):
	return _get_sliding_pieces_moves(bitboards, color, W_QUEEN, B_QUEEN, queen_moves)

def generate_all_moves(bitboards, color, castling_rights):
	moves = []
	moves.extend(get_pawns_moves(bitboards, color))
	moves.extend(get_knights_moves(bitboards, color))
	moves.extend(get_king_moves(bitboards, color, castling_rights))
	moves.extend(get_rooks_moves(bitboards, color))
	moves.extend(get_bishops_moves(bitboards, color))
	moves.extend(get_queens_moves(bitboards, color))
	return moves