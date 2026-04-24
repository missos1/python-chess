import random

from data.classes.chess_bot import evaluate


def negamax(board, depth, alpha, beta, turn_multiplier):
    if depth == 0:
        # return turn_multiplier * evaluate(), None
        return random.randint(-100, 100), None # fake evaluate, it should return turn_multiplier * evaluate(), None
    
    max_score = -float('inf')
    best_move = None
    moves = board.generate_moves()

    for move in moves:
        board.AI_move(move)
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
