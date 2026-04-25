import random

from data.classes.chess_bot import evaluate


def negamax(board, depth, alpha, beta, turn_multiplier):
    if depth == 0:
        # if evaluate works, change this line below to 'return turn_multiplier * evaluate()'
        return random.randint(0, 100) * turn_multiplier, None
    
    max_score = -float('inf')
    best_move = None
    moves = board.generate_moves()

    for move in moves:
        board.make_move(move)
        score, _ = negamax(board, depth - 1, -beta, -alpha, -turn_multiplier)
        score = -score
        board.undo_move()

        if score > max_score:
            max_score = score
            best_move = move

        alpha = max(alpha, score)

        if alpha >= beta:
            break  # prunning

    return max_score, best_move
