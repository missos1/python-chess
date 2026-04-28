from .move_filter import is_square_attacked

class GameState:
    def __init__(self, bitboards, pieces_array):
        self.board = bitboards
        self.piece_values = pieces_array
        self.castling_rights = 15
        self.state_history = []
        
    def make_move(self, move):
        # Placeholder for move execution logic
        # TODO: Remember to teleport the rooks when castling and update castling rights accordingly
        pass
    
    def undo_move(self, move):
        # Placeholder for undoing a move
        pass
    
    def get_strictly_legal_moves(self, color):
        # Placeholder for move filtering logic to ensure moves don't leave king in check or castle through check or move into check
        return []