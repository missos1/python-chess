from data.classes.chess_bot.evaluation import evaluate

def negamax_alphabeta(state, depth, alpha, beta, turn_multiplier, color):

    # ===== STOP CONDITION =====
    if depth == 0:
        return evaluate(state) * turn_multiplier, None

    moves = state.get_strictly_legal_moves(color)

    # ===== CHECKMATE / STALEMATE =====
    if len(moves) == 0:
        return -999999 * turn_multiplier, None

    max_score = -float('inf')
    best_move = None

    next_color = 'white' if color == 'black' else 'black'

    for move in moves:
        state.make_move(move, color)

        score, _ = negamax_alphabeta(
            state,
            depth - 1,
            -beta,
            -alpha,
            -turn_multiplier,
            next_color
        )

        score = -score
        state.undo_move()

        if score > max_score:
            max_score = score
            best_move = move

        alpha = max(alpha, score)

        if alpha >= beta:
            break  # cắt tỉa

    return max_score, best_move