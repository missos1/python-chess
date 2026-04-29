from .constants import *

def evaluate(state, current_turn_color):
    white_score = 0
    black_score = 0
    w_bishops = 0
    b_bishops = 0
    
    # Loop through the Hybrid Array exactly once
    for sq in range(64):
        piece = state.piece_values[sq]
        if piece == EMPTY: continue
        
        # Determine color using the integer constants instead of list lookups for extra speed
        is_white = piece <= W_KING_VALUE
        base_value = PIECE_POINT_VALUES.get(piece, 0)
        
        # Track bishops for the valuable Bishop Pair bonus
        if piece == W_BISHOP_VALUE: w_bishops += 1
        elif piece == B_BISHOP_VALUE: b_bishops += 1
        
        # Get PST bonus (Mirror the square if Black!)
        pst = PST_LOOKUP.get(piece, None)
        pst_bonus = 0
        if pst:
            read_sq = sq if is_white else sq ^ 56
            pst_bonus = pst[read_sq]
            
        # Add to total totals
        if is_white:
            white_score += (base_value + pst_bonus)
        else:
            black_score += (base_value + pst_bonus)

    # Apply structural bonuses
    # The Bishop Pair is historically worth about +30 centipawns (almost a third of a pawn advantage)
    if w_bishops >= 2: white_score += 30
    if b_bishops >= 2: black_score += 30
            
    # The absolute evaluation from White's perspective
    evaluation = white_score - black_score
    
    # Negamax perspective shift!
    return evaluation if current_turn_color == WHITE else -evaluation

def score_move(move, state):
    source, target, flag = move
    piece_moving = state.piece_values[source]
    score = 0
    
    # 1. SCORE CAPTURES (Highest Priority)
    if flag == FLAG_CAPTURE or flag == FLAG_PROMOTION or flag == FLAG_EN_PASSANT: # Assuming captures can promote
        victim = state.piece_values[target] if flag != FLAG_EN_PASSANT else (W_PAWN_VALUE if piece_moving == B_PAWN_VALUE else B_PAWN_VALUE)
        attacker = piece_moving
        # MVV-LVA: 1,000,000 ensures captures are ALWAYS searched before quiet moves
        score = 1000000 + (10 * PIECE_POINT_VALUES.get(victim, 0)) - PIECE_POINT_VALUES.get(attacker, 0)
        
    # 2. SCORE QUIET MOVES (Using Heat Maps)
    else:
        # If it's a quiet move, sort it by how "good" the destination square is!
        pst = PST_LOOKUP.get(piece_moving, None)
        if pst:
            # If Black is moving, we flip the board vertically using bitwise XOR 56
            is_black = (piece_moving in [B_PAWN_VALUE, B_KNIGHT_VALUE, B_BISHOP_VALUE, B_ROOK_VALUE, B_QUEEN_VALUE, B_KING_VALUE])
            read_target = target ^ 56 if is_black else target
            
            score = pst[read_target]
            
    return score