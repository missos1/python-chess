from .constants import *
from .precompute import (
    FILE_MASKS,
    WHITE_PASSED_PAWN_MASKS,
    BLACK_PASSED_PAWN_MASKS,
)

def get_phase_weight(state):
    phase = 0
    for piece_id, weight in enumerate(PHASE_PIECE_WEIGHTS):
        if weight:
            count = state.bitboards[piece_id].bit_count()
            if count:
                phase += count * weight

    return MAX_PHASE if phase > MAX_PHASE else phase

# Legacy compatibility: returns the phase weight used for tapered eval
def get_game_phase(state):
    return get_phase_weight(state)

def evaluate_pawn_structure(state):
    w_pawns = state.bitboards[W_PAWN]
    b_pawns = state.bitboards[B_PAWN]

    if not (w_pawns | b_pawns):
        return 0, 0

    occupied = state.bitboards[OCCUPIED]

    static_score = 0
    dynamic_score = 0

    # Pawn attacks
    w_attacks = ((w_pawns << 7) & NOT_H_FILE) | ((w_pawns << 9) & NOT_A_FILE)
    b_attacks = ((b_pawns >> 7) & NOT_A_FILE) | ((b_pawns >> 9) & NOT_H_FILE)

    #Pawn chain
    w_chain = w_pawns & w_attacks
    b_chain = b_pawns & b_attacks
    static_score += w_chain.bit_count() * PAWN_CHAIN_BONUS
    static_score -= b_chain.bit_count() * PAWN_CHAIN_BONUS

    # Double pawn (trường hợp tĩnh)
    w_file_counts = [0] * 8
    b_file_counts = [0] * 8
    for f in range(8):
        w_count = (w_pawns & FILE_MASKS[f]).bit_count()
        b_count = (b_pawns & FILE_MASKS[f]).bit_count()
        w_file_counts[f] = w_count
        b_file_counts[f] = b_count
        if w_count > 1:
            static_score -= (w_count - 1) * PAWN_DOUBLED_PENALTY
        if b_count > 1:
            static_score += (b_count - 1) * PAWN_DOUBLED_PENALTY

    #Isolated Pawn check
    w_adjacent = [False] * 8
    b_adjacent = [False] * 8
    for f in range(8):
        w_adjacent[f] = ((f > 0 and w_file_counts[f - 1] > 0) or (f < 7 and w_file_counts[f + 1] > 0))
        b_adjacent[f] = ((f > 0 and b_file_counts[f - 1] > 0) or (f < 7 and b_file_counts[f + 1] > 0))

    # Evaluate white pawn
    temp = w_pawns
    while temp:
        lsb = temp & -temp
        temp ^= lsb
        sq = lsb.bit_length() - 1
        file = sq & 7
        rank = sq >> 3

        forward = (lsb << 8) & BOARD_MASK
        is_passed = not (b_pawns & WHITE_PASSED_PAWN_MASKS[sq])

        # Isolated (static, with scaling for doubled pawns)
        if not w_adjacent[file]:
            w_count = w_file_counts[file]
            # If more than one pawn on this isolated file, reduce penalty per pawn
            penalty = PAWN_ISOLATED_PENALTY if w_count == 1 else PAWN_ISOLATED_PENALTY // 2
            static_score -= penalty

        # Passed pawn bonus (dynamic)
        if is_passed:
            bonus = PAWN_PASSED_BONUS_BY_RANK[rank]
            # Blocked passer still has value, but reduced
            if forward & occupied:
                bonus //= 2
            # Extra if protected
            if lsb & w_attacks:
                bonus += PAWN_CHAIN_BONUS // 2
            dynamic_score += bonus

        else:
            # Pawn not protected and blocked
            if (forward & occupied) and not (lsb & w_attacks):
                static_score -= PAWN_UNPROTECTED_PENALTY

    #Evaluate black pawn
    temp = b_pawns
    while temp:
        lsb = temp & -temp
        temp ^= lsb
        sq = lsb.bit_length() - 1
        file = sq & 7
        rank = sq >> 3

        forward = lsb >> 8
        is_passed = not (w_pawns & BLACK_PASSED_PAWN_MASKS[sq])

        # Isolated (static, with scaling)
        if not b_adjacent[file]:
            b_count = b_file_counts[file]
            penalty = PAWN_ISOLATED_PENALTY if b_count == 1 else PAWN_ISOLATED_PENALTY // 2
            static_score += penalty

        # Passed pawn bonus (dynamic)
        if is_passed:
            bonus = PAWN_PASSED_BONUS_BY_RANK[7 - rank]
            if forward & occupied:
                bonus //= 2
            if lsb & b_attacks:
                bonus += PAWN_CHAIN_BONUS // 2
            dynamic_score -= bonus

        else:
            # Pawn blocked and not protected
            if (forward & occupied) and not (lsb & b_attacks):
                static_score += PAWN_UNPROTECTED_PENALTY

    total_score = static_score + dynamic_score
    mg_score = (total_score * PAWN_PHASE_MULTIPLIER_MG) // 100
    eg_score = (total_score * PAWN_PHASE_MULTIPLIER_EG) // 100

    return mg_score, eg_score

def evaluate(state, current_turn_color):
    mg_white = 0
    mg_black = 0
    eg_white = 0
    eg_black = 0
    phase = get_phase_weight(state)
    mg_lookup = PST_LOOKUP_MG
    eg_lookup = PST_LOOKUP_EG
    
    # Loop through the Hybrid Array exactly once
    for piece_id in range(W_PAWN, B_KING + 1):
        piece_bitboard = state.bitboards[piece_id]
        
        if piece_bitboard == 0:
            continue
        
        # Determine color using the integer constants instead of list lookups for extra speed
        is_white = piece_id <= W_KING
        base_value = PIECE_POINT_VALUES[piece_id]
        mg_pst = mg_lookup[piece_id]
        eg_pst = eg_lookup[piece_id]

        # Get PST bonus (Mirror the square if Black!)
        while piece_bitboard:
            lsb = piece_bitboard & -piece_bitboard
            sq = lsb.bit_length() - 1
            piece_bitboard &= piece_bitboard - 1
            
            read_sq = sq if is_white else sq ^ 56  # flip the square vertically for Black pieces
            mg_bonus = mg_pst[read_sq] if mg_pst else 0
            eg_bonus = eg_pst[read_sq] if eg_pst else 0

            if is_white:
                mg_white += (base_value + mg_bonus)
                eg_white += (base_value + eg_bonus)
            else:
                mg_black += (base_value + mg_bonus)
                eg_black += (base_value + eg_bonus)

    if state.bitboards[W_BISHOP].bit_count() >= 2: 
        mg_white += 30
        eg_white += 30
    if state.bitboards[B_BISHOP].bit_count() >= 2: 
        mg_black += 30
        eg_black += 30

    mg_pawn, eg_pawn = evaluate_pawn_structure(state)
    mg_total = (mg_white - mg_black) + mg_pawn
    eg_total = (eg_white - eg_black) + eg_pawn
    evaluation = (mg_total * phase + eg_total * (MAX_PHASE - phase)) // MAX_PHASE
            
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
            phase = get_phase_weight(state)
        mg_pst = PST_LOOKUP_MG[piece_moving]
        eg_pst = PST_LOOKUP_EG[piece_moving]
        if mg_pst or eg_pst:
            # If Black is moving, we flip the board vertically using bitwise XOR 56
            is_black = (piece_moving in [B_PAWN, B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN, B_KING])
            read_target = target ^ 56 if is_black else target
            mg_bonus = mg_pst[read_target] if mg_pst else 0
            eg_bonus = eg_pst[read_target] if eg_pst else 0
            score = (mg_bonus * phase + eg_bonus * (MAX_PHASE - phase)) // MAX_PHASE
            
    return score