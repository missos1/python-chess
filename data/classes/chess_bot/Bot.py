from .GameState import *
from.constants import *

class Bot:
    def __init__(self, depth=DEPTH, color=WHITE):
        self.depth = depth
        self.color = color
    
    def get_best_move(self, state: GameState):
        moves = state.get_strictly_legal_moves(self.color)
        
        for move in moves:
            state.make_move(move)
            # TODO: for the move selection logic using Negamax with Alpha-Beta pruning
            state.undo_move(move)
        pass