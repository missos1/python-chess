from .constants import *
from .precompute import *

# the + rays
def cross_moves(square_index, bitboards, friendly_pieces):
	occupied = bitboards[OCCUPIED]
	legal_moves = 0

	# north (Positive Ray - Index Increases)
	ray = NORTH_RAYS[square_index]
	blockers = ray & occupied
	if blockers:
		# lowest set bit gives us the first blocker in the north direction
		first_blocker_board = blockers & -blockers
		first_blocker_index = first_blocker_board.bit_length() - 1
		# cut the ray off at the blocker (XOR to remove all squares beyond the blocker, including the blocker itself)
		legal_moves |= (ray ^ NORTH_RAYS[first_blocker_index])
	else:
		legal_moves |= ray

	# south (Negative Ray - Index Decreases)
	ray = SOUTH_RAYS[square_index]
	blockers = ray & occupied
	if blockers:
		# Find the HIGHEST set bit using bit_length
		first_blocker_index = blockers.bit_length() - 1
		legal_moves |= (ray ^ SOUTH_RAYS[first_blocker_index])
	else:
		legal_moves |= ray

	# east (Positive Ray - Index Increases)
	ray = EAST_RAYS[square_index]
	blockers = ray & occupied
	if blockers:
		# Lowest set bit
		first_blocker_board = blockers & -blockers
		first_blocker_index = first_blocker_board.bit_length() - 1
		legal_moves |= (ray ^ EAST_RAYS[first_blocker_index])
	else:
		legal_moves |= ray

	# west (Negative Ray - Index Decreases)
	ray = WEST_RAYS[square_index]
	blockers = ray & occupied
	if blockers:
		# Highest set bit
		first_blocker_index = blockers.bit_length() - 1
		legal_moves |= (ray ^ WEST_RAYS[first_blocker_index])
	else:
		legal_moves |= ray

	return legal_moves & ~friendly_pieces

# the "x" rays
def diagonal_moves(square_index, bitboards, friendly_pieces):
    occupied = bitboards[OCCUPIED]
    legal_moves = 0

    # northeast (Positive Ray - Index Increases)
    ray = NORTHEAST_RAYS[square_index]
    blockers = ray & occupied
    if blockers:
        first_blocker_board = blockers & -blockers
        first_blocker_index = first_blocker_board.bit_length() - 1
        legal_moves |= (ray ^ NORTHEAST_RAYS[first_blocker_index])
    else:
        legal_moves |= ray

    # northwest (Positive Ray - Index Increases)
    ray = NORTHWEST_RAYS[square_index]
    blockers = ray & occupied
    if blockers:
        first_blocker_board = blockers & -blockers
        first_blocker_index = first_blocker_board.bit_length() - 1
        legal_moves |= (ray ^ NORTHWEST_RAYS[first_blocker_index])
    else:
        legal_moves |= ray
        
    # southeast (Negative Ray - Index Decreases)
    ray = SOUTHEAST_RAYS[square_index]
    blockers = ray & occupied
    if blockers:
        first_blocker_index = blockers.bit_length() - 1
        legal_moves |= (ray ^ SOUTHEAST_RAYS[first_blocker_index])
    else:   
        legal_moves |= ray
    
    # southwest (Negative Ray - Index Decreases)
    ray = SOUTHWEST_RAYS[square_index]
    blockers = ray & occupied
    if blockers:
        first_blocker_index = blockers.bit_length() - 1
        legal_moves |= (ray ^ SOUTHWEST_RAYS[first_blocker_index])
    else:
        legal_moves |= ray

    return legal_moves & ~friendly_pieces

def queen_moves(square_index, bitboards, friendly_pieces):
	return cross_moves(square_index, bitboards, friendly_pieces) | diagonal_moves(square_index, bitboards, friendly_pieces)