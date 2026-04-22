from .constants import *
from .precompute import KNIGHT_MOVES, KING_MOVES

# Returns the indices of the set bits in a bitboard
# Example: 0b1010 -> yields 1 and 3 (0-indexed from the right)
def get_set_bits(bitboard):
	while bitboard: 
		lsb = bitboard & -bitboard
		yield lsb.bit_length() - 1
		bitboard &= bitboard - 1

def get_knights_moves(bitboards, color):
	moves = []
	if color == WHITE:
		knights = bitboards[W_KNIGHT]
		friendly_pieces = bitboards[W_PIECES]
	else:
		knights = bitboards[B_KNIGHT]
		friendly_pieces = bitboards[B_PIECES]
	
	for knight in get_set_bits(knights):
		raw_moves = KNIGHT_MOVES[knight]
		legal_moves = raw_moves & ~friendly_pieces

		for target in get_set_bits(legal_moves):
			moves.append((knight, target))
	return moves