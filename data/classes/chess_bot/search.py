def negamax_alphabeta(state, depth, alpha, beta, turn_multiplier, color):
    if depth == 0:
        # TODO: Implement a proper evaluation function here that considers material, piece activity, king safety,...
        return 100 * turn_multiplier, None # fake evaluate
    
    max_score = -float('inf')
    best_move = None
    moves = state.get_strictly_legal_moves(color)
    next_color = 'white' if color == 'black' else 'black'

    for move in moves:
        state.make_move(move, color)
        score, _ = negamax_alphabeta(state, depth - 1, -beta, -alpha, -turn_multiplier, next_color)
        score = -score
        state.undo_move()

        if score > max_score:
            max_score = score
            best_move = move

        alpha = max(alpha, score)

        if alpha >= beta:
            break  # pruning

    return max_score, best_move
