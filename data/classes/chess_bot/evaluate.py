from .constants import *
from .move_gens import get_set_bits

def get_game_phase(state):
    material = 0
    for piece_id in PHASE_MATERIAL_PIECES:
        count = state.bitboards[piece_id].bit_count()
        if count:
            material += count * PIECE_POINT_VALUES[piece_id]

    if material >= PHASE_OPENING_MIN_MATERIAL:
        return PHASE_OPENING
    if material <= PHASE_ENDGAME_MAX_MATERIAL:
        return PHASE_ENDGAME
    return PHASE_MIDDLEGAME

def evaluate(state, current_turn_color):
    white_score = 0
    black_score = 0
    phase = get_game_phase(state)
    pst_lookup = PST_LOOKUP_BY_PHASE[phase]
    
    # Loop through the Hybrid Array exactly once
    for piece_id in range(W_PAWN, B_KING + 1):
        piece_bitboard = state.bitboards[piece_id]
        
        if piece_bitboard == 0:
            continue
        
        # Determine color using the integer constants instead of list lookups for extra speed
        is_white = piece_id <= W_KING
        base_value = PIECE_POINT_VALUES[piece_id]
        pst = pst_lookup[piece_id]

        # Get PST bonus (Mirror the square if Black!)
        while piece_bitboard:
            lsb = piece_bitboard & -piece_bitboard
            sq = lsb.bit_length() - 1
            piece_bitboard &= piece_bitboard - 1
            
            pst_bonus = 0
            if pst:
                read_sq = sq if is_white else sq ^ 56  # flip the square vertically for Black pieces
                pst_bonus = pst[read_sq]
            
            if is_white:
                white_score += (base_value + pst_bonus)
            else:
                black_score += (base_value + pst_bonus)

    if state.bitboards[W_BISHOP].bit_count() >= 2: 
        white_score += 30
    if state.bitboards[B_BISHOP].bit_count() >= 2: 
        black_score += 30
            
    # The absolute evaluation from White's perspective
    evaluation = white_score - black_score
    
    # Negamax perspective shift!
    return evaluation if current_turn_color == WHITE else -evaluation

def score_move(move, state, phase=None):
    source, target, flag = move
    piece_moving = state.piece_values[source]
    score = 0
    
    # 1. SCORE CAPTURES (Highest Priority)
    if flag == FLAG_CAPTURE or flag == FLAG_PROMOTION or flag == FLAG_EN_PASSANT: # Assuming captures can promote
        victim = state.piece_values[target] if flag != FLAG_EN_PASSANT else (W_PAWN if piece_moving == B_PAWN else B_PAWN)
        attacker = piece_moving
        # MVV-LVA: 1,000,000 ensures captures are ALWAYS searched before quiet moves but behind tt move
        score = 1000000 + (10 * PIECE_POINT_VALUES[victim]) - PIECE_POINT_VALUES[attacker]
        
    # 2. SCORE QUIET MOVES (Using Heat Maps)
    else:
        # If it's a quiet move, sort it by how "good" the destination square is!
        if phase is None:
            phase = get_game_phase(state)
        pst_lookup = PST_LOOKUP_BY_PHASE[phase]
        pst = pst_lookup[piece_moving]
        if pst:
            # If Black is moving, we flip the board vertically using bitwise XOR 56
            is_black = (piece_moving in [B_PAWN, B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN, B_KING])
            read_target = target ^ 56 if is_black else target
            
            score = pst[read_target]
            
    return score