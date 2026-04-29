import time
from .constants import *
from .evaluate import evaluate, score_move
from .move_filter import is_square_attacked

class TimeOutException(Exception):
    pass

def quiescence_search(state, alpha, beta, current_color, search_params):
    # search_params = [nodes_searched, start_time, time_limit]
    search_params[0] += 1
    if search_params[0] & 2047 == 0:
        if time.time() - search_params[1] > search_params[2]:
            raise TimeOutException()
    
    stand_pat = evaluate(state, current_color)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat
        
    capture_moves = state.get_capture_moves_only(current_color)
    capture_moves.sort(key=lambda m: score_move(m, state), reverse=True)
    
    next_color = BLACK if current_color == WHITE else WHITE
    make_move = state.make_move
    undo_move = state.undo_move
    
    for move in capture_moves:
        make_move(move)
        score = -quiescence_search(state, -beta, -alpha, next_color, search_params)
        undo_move(move)
        
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
            
    return alpha

def negamax(depth, state, alpha, beta, current_color, search_params, tt):
    search_params[0] += 1
    if search_params[0] & 2047 == 0:
        if time.time() - search_params[1] > search_params[2]:
            raise TimeOutException()
            
    alpha_orig = alpha
    zobrist_hash = state.zobrist_hash
    tt_entry = tt.get(zobrist_hash)
    
    if tt_entry is not None and tt_entry[0] >= depth:
        tt_flag = tt_entry[2]
        tt_score = tt_entry[1]
        
        if tt_flag == 0:
            return tt_score
        elif tt_flag == 1:
            if tt_score <= alpha:
                return alpha
        elif tt_flag == 2:
            if tt_score >= beta:
                return beta
                
    if depth <= 0:
        return quiescence_search(state, alpha, beta, current_color, search_params)
        
    legal_moves = state.get_strictly_legal_moves(current_color)
    
    if not legal_moves:
        bitboards = state.bitboards
        king_board = bitboards[W_KING] if current_color == WHITE else bitboards[B_KING]
        king_sq = (king_board & -king_board).bit_length() - 1
        enemy_color = BLACK if current_color == WHITE else WHITE
        
        if is_square_attacked(king_sq, enemy_color, bitboards):
            return -99999 - depth
        return 0
        
    legal_moves.sort(key=lambda m: score_move(m, state), reverse=True)
    
    next_color = BLACK if current_color == WHITE else WHITE
    make_move = state.make_move
    undo_move = state.undo_move
    
    for move in legal_moves:
        make_move(move)
        score = -negamax(depth - 1, state, -beta, -alpha, next_color, search_params, tt)
        undo_move(move)
        
        if score >= beta:
            tt[zobrist_hash] = (depth, beta, 2)
            return beta
        if score > alpha:
            alpha = score
            
    flag = 1 if alpha <= alpha_orig else 0
    tt[zobrist_hash] = (depth, alpha, flag)
    return alpha
