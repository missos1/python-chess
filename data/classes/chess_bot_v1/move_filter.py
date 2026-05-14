from .constants import *
from .precompute import *
from .ray_cast_moves import *

def is_square_attacked(square_index, attacker_color, bitboards):
    # Setup the pieces based on who is attacking
    if attacker_color == WHITE:
        enemy_pawns   = bitboards[W_PAWN]
        enemy_knights = bitboards[W_KNIGHT]
        enemy_bishops = bitboards[W_BISHOP]
        enemy_rooks   = bitboards[W_ROOK]
        enemy_queens  = bitboards[W_QUEEN]
        enemy_king    = bitboards[W_KING]
        
        friendly_for_radar = bitboards[B_PIECES] 
    else:
        enemy_pawns   = bitboards[B_PAWN]
        enemy_knights = bitboards[B_KNIGHT]
        enemy_bishops = bitboards[B_BISHOP]
        enemy_rooks   = bitboards[B_ROOK]
        enemy_queens  = bitboards[B_QUEEN]
        enemy_king    = bitboards[B_KING]
        
        friendly_for_radar = bitboards[W_PIECES]
    
    # check if the square_index is attacked by sliding pieces by firing rays from the target square_index outwards 
    # and seeing if they hit an enemy piece before hitting a friendly piece or the edge of the board
    bishop_radar = diagonal_moves(square_index, bitboards, friendly_for_radar)
    if bishop_radar & (enemy_bishops | enemy_queens): 
        return True
        
    rook_radar = cross_moves(square_index, bitboards, friendly_for_radar)
    if rook_radar & (enemy_rooks | enemy_queens): 
        return True

    # check if the square_index is attacked by knights or king using precomputed move boards
    if KNIGHT_MOVES[square_index] & enemy_knights: return True
    if KING_MOVES[square_index] & enemy_king: return True

    # check if the square_index is attacked by pawns using precomputed capture boards
    if attacker_color == WHITE:
        if BLACK_PAWN_CAPTURES[square_index] & enemy_pawns: return True
    else:
        if WHITE_PAWN_CAPTURES[square_index] & enemy_pawns: return True

    return False