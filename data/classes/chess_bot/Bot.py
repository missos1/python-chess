import random

from data.classes.chess_bot.constants import *
from data.classes.Move import Move
from data.classes.chess_bot.search import negamax

Depth = 2

class Bot:
    def __init__(self, color='white', depth=Depth):
        self.color = color
        self.depth = depth
    
    # this function calculates and returns the best move (using Negamax with Alpha-Beta pruning)
    def get_best_move(self, board):
        best_move = None
        score, best_move = negamax(board, self.depth, -float('inf'), float('inf'), 1 if board.turn == WHITE else -1)
        return best_move

    def get_random_move(self, board):
        moves = board.generate_moves()
        return moves[random.randint(0, len(moves) - 1)]
        
        
    