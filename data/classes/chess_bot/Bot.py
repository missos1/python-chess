from data.classes.chess_bot.search import negamax_alphabeta

from .GameState import *
from.constants import *

class Bot:
    def __init__(self, depth=DEPTH, color=WHITE):
        self.depth = depth
        self.color = color
    
    def get_best_move(self, board, state: GameState):
        score, best_move = negamax_alphabeta(state,self.depth, -float('inf'), float('inf'), 1 if board.turn == WHITE else -1, board.turn)
        return best_move