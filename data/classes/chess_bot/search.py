import time
from .constants import *
from .evaluate import evaluate, score_move, get_game_phase
from .move_filter import is_square_attacked
from .move_gens import generate_all_moves
from .GameState import GameState

class TimeOutException(Exception):
    pass

def quiescence_search(state: GameState, alpha, beta, current_color, search_params) -> float:
    # search_params = [nodes_searched, start_time, time_limit]
    search_params[0] += 1
    if search_params[0] & 4095 == 0:
        if time.time() - search_params[1] > search_params[2]:
            raise TimeOutException()
    
    # if our king has been captured, this is a losing position
    king_board = state.bitboards[W_KING] if current_color == WHITE else state.bitboards[B_KING]
    if king_board == 0:
        return -99999
    
    moves_to_search = []
    
        # evaluate current position
    stand_pat = evaluate(state, current_color)
        
        # alpha-beta pruning on the quiet evaluation of the position before we start looking at captures
    if stand_pat >= beta:
            return beta
    if alpha < stand_pat:
            alpha = stand_pat
        
    raw_moves = generate_all_moves(state.bitboards, current_color, state.castling_rights, state.en_passant_target)
    moves_to_search = [move for move in raw_moves if move[2] in (FLAG_CAPTURE, FLAG_PROMOTION, FLAG_EN_PASSANT)]
    
    phase = get_game_phase(state)
    moves_to_search.sort(key=lambda m: score_move(m, state, phase), reverse=True)
    
    next_color = BLACK if current_color == WHITE else WHITE
    make_move = state.make_move
    undo_move = state.undo_move
    
    for move in moves_to_search:
        
        make_move(move)
        try:
            score = -quiescence_search(state, -beta, -alpha, next_color, search_params)
        finally:
            undo_move(move)
        
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
            
    return alpha

def negamax(depth, state: GameState, alpha, beta, current_color, search_params, tt, killer_moves, ply) -> float:
    """ Search the game tree to a certain depth using negamax with alpha-beta pruning, 
    along with quiescence search at the leaf nodes, and a transposition table to store
    previously evaluated positions."""
    search_params[0] += 1                                           # Increment nodes searched
    if search_params[0] & 4095 == 0:                                # Check time every 4095 nodes
        if time.time() - search_params[1] > search_params[2]:       # If we've exceeded our time limit, raise an exception to stop the search
            raise TimeOutException()                                

    # Check for terminal states (Checkmate or Stalemate)
    king_board = state.bitboards[W_KING] if current_color == WHITE else state.bitboards[B_KING]
    enemy_king_board = state.bitboards[B_KING] if current_color == WHITE else state.bitboards[W_KING]
    if king_board == 0:
        return -99999 - depth 
    
    king_sq = (king_board & -king_board).bit_length() - 1
    enemy_king_sq = (enemy_king_board & -enemy_king_board).bit_length() - 1
    
    next_color = BLACK if current_color == WHITE else WHITE
    enemy_color = next_color
    alpha_orig = alpha
    zobrist_hash = state.zobrist_hash

    tt_entry = tt.get(zobrist_hash)
    
    tt_move = None
    
    if tt_entry is not None and tt_entry[0] >= depth:
        if len(tt_entry) == 4:
            tt_move = tt_entry[3]
            # print(f"tuple with length 4 confirmed")
        tt_flag = tt_entry[2]
        tt_score = tt_entry[1]
        
        if tt_flag == TT_EXACT:
            return tt_score
        elif tt_flag == TT_UPPER_BOUND:
            if tt_score <= alpha:
                return alpha
        elif tt_flag == TT_LOWER_BOUND:
            if tt_score >= beta:
                return beta
                
    # Null Move Pruning: If we are not in a quiet position 
    # (i.e. there is significant material on the board), we can try skipping our move and see if the opponent has a strong response. If they do, then we know we need to search this position more deeply. If they don't, we can safely assume this position is good for us and cut off the search.
    not_zugzwang = True if state.get_non_pawn_materials() > 0 else False
    is_in_check = is_square_attacked(king_sq, enemy_color, state.bitboards)
    can_capture_enemy_king = is_square_attacked(enemy_king_sq, current_color, state.bitboards)
    
    if depth > 2 and not_zugzwang and not (is_in_check or can_capture_enemy_king):
        state.make_null_move()
        try:
            null_move_score = -negamax(
                    depth - 3, 
                    state, 
                    -beta, 
                    -beta + 1, 
                    enemy_color, 
                    search_params, 
                    tt,
                    killer_moves,
                    ply + 1
            )
            if null_move_score >= beta:
                search_params[3] += 1  # Increment null prune count for stats
                return beta
        finally:
            state.undo_null_move()  # Ensure we always undo the null move even if we time out
            
    if depth <= 0:
        return quiescence_search(state, alpha, beta, current_color, search_params)
        
    moves = generate_all_moves(
        state.bitboards, 
        current_color, 
        state.castling_rights, 
        state.en_passant_target
    )
    
    # moves = state.get_strictly_legal_moves(current_color)
    
    phase = get_game_phase(state)

    def move_order_score(move):

        if move == tt_move:
            return 10_000_000

        if move == killer_moves[ply][0]:
            return 9_000_000

        if move == killer_moves[ply][1]:
            return 8_000_000

        return score_move(move, state, phase)

    moves.sort(key=move_order_score, reverse=True)
    
    make_move = state.make_move
    undo_move = state.undo_move
    
    best_score = -float('inf')
    best_move_found = None
    move_index = 0
    
    for move in moves:
        flag = move[2]
        
        # skip illegal castling moves where the king would pass through or end up on an attacked square
        if flag in (FLAG_CASTLE_KS, FLAG_CASTLE_QS):
            if current_color == WHITE:
                if flag == FLAG_CASTLE_KS and (is_square_attacked(4, enemy_color, state.bitboards) or is_square_attacked(5, enemy_color, state.bitboards)):
                    continue
                elif flag == FLAG_CASTLE_QS and (is_square_attacked(4, enemy_color, state.bitboards) or is_square_attacked(3, enemy_color, state.bitboards)):
                    continue
            else:
                if flag == FLAG_CASTLE_KS and (is_square_attacked(60, enemy_color, state.bitboards) or is_square_attacked(61, enemy_color, state.bitboards)):
                    continue
                elif flag == FLAG_CASTLE_QS and (is_square_attacked(60, enemy_color, state.bitboards) or is_square_attacked(59, enemy_color, state.bitboards)):
                    continue

        make_move(move)
        try:
            reduction = 0

            is_quiet = flag not in (
                FLAG_CAPTURE,
                FLAG_PROMOTION,
                FLAG_EN_PASSANT
            )

            is_tt_move = (move == tt_move)
            is_killer = (
                move == killer_moves[ply][0] or
                move == killer_moves[ply][1]
            )

            # LMR conditions
            if (
                depth >= 3 and
                move_index >= 4 and
                is_quiet and
                not is_in_check and
                not is_tt_move and
                not is_killer
            ):
                enemy_king_board_after = (
                    state.bitboards[B_KING]
                    if current_color == WHITE
                    else state.bitboards[W_KING]
                )

                enemy_king_sq_after = (
                    enemy_king_board_after & -enemy_king_board_after
                ).bit_length() - 1

                if not is_square_attacked(enemy_king_sq_after, current_color, state.bitboards):
                    reduction = 1

            # reduced search
            if reduction:
                score = -negamax(
                    depth - 1 - reduction,
                    state,
                    -alpha - 1,
                    -alpha,
                    enemy_color,
                    search_params,
                    tt,
                    killer_moves,
                    ply + 1
                )

                # re-search if move looks good
                if score > alpha:
                    score = -negamax(
                        depth - 1,
                        state,
                        -beta,
                        -alpha,
                        enemy_color,
                        search_params,
                        tt,
                        killer_moves,
                        ply + 1
                    )
            else:
                score = -negamax(
                    depth - 1, 
                    state, 
                    -beta, 
                    -alpha, 
                    enemy_color, 
                    search_params, 
                    tt,
                    killer_moves,
                    ply + 1
                )
        finally:
            undo_move(move)

        move_index += 1
        
        if score > best_score:
            best_score = score
            best_move_found = move
            
        if score >= beta:
            # store killer move
            if flag not in (
                FLAG_CAPTURE,
                FLAG_PROMOTION,
                FLAG_EN_PASSANT
            ):
                if move != killer_moves[ply][0]:
                    killer_moves[ply][1] = killer_moves[ply][0]
                    killer_moves[ply][0] = move
            if score < 90000 and score > -90000:
                tt[zobrist_hash] = (depth, beta, TT_LOWER_BOUND, move)
            return beta
            
        if score > alpha:
            alpha = score
            
    # mate or stalemate detection: 
    # If we have no legal moves, and our king is attacked, it's checkmate. 
    # If we have no legal moves and our king is not attacked, it's stalemate.
    # If all pseudo-legal moves resulted in our King getting captured, 
    # the best_score will be heavily negative.
    if best_score <= -90000:
        if not is_in_check:
            return 0 # We are not in check, so it's a Stalemate (Draw)
        return best_score # We are in check, Checkmate!
            
    flag = TT_UPPER_BOUND if alpha <= alpha_orig else TT_EXACT
    tt[zobrist_hash] = (depth, alpha, flag, best_move_found)
    
    return alpha
