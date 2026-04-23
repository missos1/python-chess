import random

from data.classes.chess_bot.constants import BLACK
from data.classes.move import Move

Depth = 2

class Bot:
    def __init__(self, color='white', depth=Depth):
        pass
    
    def get_best_move():
        pass

    def get_random_move(self, board):
        moves = []
        for square in board.squares:
            if square.occupying_piece is not None:
                if square.occupying_piece.color == BLACK:
                    piece = square.occupying_piece
                    for to_square in piece.get_valid_moves(board):
                        moves.append(Move(piece=piece, 
                                          from_pos=square.pos, 
                                          to_pos=to_square.pos, 
                                          captured=to_square.occupying_piece, 
                                          piece_has_moved=piece.has_moved))
                        
        return moves[random.randint(0, len(moves) - 1)]
        
        
    