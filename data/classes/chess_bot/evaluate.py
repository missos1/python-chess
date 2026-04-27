from data.classes.Board import Board

class Evaluate:
    def __init__(self, board):
        self.board = board
        self.pawn_value = 1
        self.knight_value = 3
        self.bishop_value = 3
        self.rook_value = 5
        self.queen_value = 9
    
    # Positional heatmaps for opening play (8x8 arrays, indexed [y][x])
    # y=0 is rank 8 (black's back), y=7 is rank 1 (white's back)
    # Higher value = more preferred square for piece in opening
    
    PAWN_HEATMAP = [
        [0, 0, 0, 0, 0, 0, 0, 0],  # Rank 8: No pawns here
        [0, 0, 0, 0, 0, 0, 0, 0],  # Rank 7: Promotion imminent (not starting)
        [2, 2, 3, 3, 3, 3, 2, 2],  # Rank 6: Advanced pawns good
        [2, 2, 3, 4, 4, 3, 2, 2],  # Rank 5: Pushing forward
        [2, 2, 3, 4, 4, 3, 2, 2],  # Rank 4: Center good
        [1, 1, 2, 3, 3, 2, 1, 1],  # Rank 3: Starting to push
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 2: Starting position
        [0, 0, 0, 0, 0, 0, 0, 0],  # Rank 1: No pawns here
    ]
    
    KNIGHT_HEATMAP = [
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 8: Starting position
        [1, 2, 2, 3, 3, 2, 2, 1],  # Rank 7: Beginning to centralize
        [1, 2, 4, 5, 5, 4, 2, 1],  # Rank 6: Good outposts
        [1, 3, 5, 6, 6, 5, 3, 1],  # Rank 5: Excellent central squares
        [1, 3, 5, 6, 6, 5, 3, 1],  # Rank 4: Excellent central squares
        [1, 2, 4, 5, 5, 4, 2, 1],  # Rank 3: Development squares (Nf3, Nc3)
        [1, 2, 2, 3, 3, 2, 2, 1],  # Rank 2: Development squares
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 1: Starting position
    ]
    
    BISHOP_HEATMAP = [
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 8: Starting position
        [1, 2, 2, 2, 2, 2, 2, 1],  # Rank 7: Developing
        [1, 2, 3, 3, 3, 3, 2, 1],  # Rank 6: Active squares
        [1, 2, 3, 4, 4, 3, 2, 1],  # Rank 5: Long diagonal activation
        [1, 2, 3, 4, 4, 3, 2, 1],  # Rank 4: Long diagonal activation
        [1, 2, 3, 4, 4, 3, 2, 1],  # Rank 3: Development (Bc4, Bf4)
        [1, 2, 3, 3, 3, 3, 2, 1],  # Rank 2: Starting squares
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 1: Starting position
    ]
    
    ROOK_HEATMAP = [
        [2, 2, 2, 3, 3, 2, 2, 2],  # Rank 8: Back rank, central files better
        [2, 2, 2, 3, 3, 2, 2, 2],  # Rank 7
        [1, 2, 3, 3, 3, 3, 2, 1],  # Rank 6: Semi-open files good
        [1, 2, 3, 3, 3, 3, 2, 1],  # Rank 5: Active play
        [1, 2, 3, 3, 3, 3, 2, 1],  # Rank 4: Active play
        [1, 1, 2, 2, 2, 2, 1, 1],  # Rank 3: Still developing
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 2: Back rank
        [2, 2, 2, 3, 3, 2, 2, 2],  # Rank 1: Starting position
    ]
    
    QUEEN_HEATMAP = [
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 8: Starting position
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 7
        [1, 1, 2, 2, 2, 2, 1, 1],  # Rank 6: Moderate activation
        [1, 1, 2, 3, 3, 2, 1, 1],  # Rank 5: Center-biased
        [1, 1, 2, 3, 3, 2, 1, 1],  # Rank 4: Center-biased
        [1, 1, 2, 2, 2, 2, 1, 1],  # Rank 3: Development (Qd3, Qe3 in some lines)
        [1, 1, 1, 2, 2, 1, 1, 1],  # Rank 2: Flexible
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 1: Starting position
    ]
    
    KING_HEATMAP = [
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 8: Starting position
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 7
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 6
        [0, 0, 0, 0, 0, 0, 0, 0],  # Rank 5: Avoid center (exposed)
        [0, 0, 0, 0, 0, 0, 0, 0],  # Rank 4: Avoid center (exposed)
        [0, 0, 0, 0, 0, 0, 0, 0],  # Rank 3: Avoid center (exposed)
        [1, 1, 1, 1, 1, 1, 1, 1],  # Rank 2: Back rank is safe
        [1, 1, 1, 2, 2, 1, 2, 2],  # Rank 1: Kingside castled (g1) better than center
    ]
        
    def countMaterial(self, color):
        material = 0
        if(color == 'w'):
            material = material + bin(self.board.get_bitboards()['P']).count('1')
            material = material + bin(self.board.get_bitboards()['N']).count('1')
            material = material + bin(self.board.get_bitboards()['B']).count('1')
            material = material + bin(self.board.get_bitboards()['R']).count('1')
            material = material + bin(self.board.get_bitboards()['Q']).count('1')
        
        else:
            material = material + bin(self.board.get_bitboards()['p']).count('1')
            material = material + bin(self.board.get_bitboards()['n']).count('1')
            material = material + bin(self.board.get_bitboards()['b']).count('1')
            material = material + bin(self.board.get_bitboards()['r']).count('1')
            material = material + bin(self.board.get_bitboards()['q']).count('1')
        return material
        
        
    def get_positional_score(self):
        """Calculate positional bonuses based on piece placement on preferred squares.
        
        Returns:
            Positional score (positive for white advantage, negative for black).
            Magnitude: 0-500 (doesn't overwhelm material evaluation).
        """
        positional_score = 0
        
        for square in self.board.squares:
            piece = square.occupying_piece
            if piece is None:
                continue
            
            # Get the heatmap for this piece type
            piece_notation = piece.notation
            y, x = square.y, square.x
            
            if piece_notation == ' ':  # Pawn
                heatmap = self.PAWN_HEATMAP
                base_value = 1
            elif piece_notation == 'N':  # Knight
                heatmap = self.KNIGHT_HEATMAP
                base_value = 1
            elif piece_notation == 'B':  # Bishop
                heatmap = self.BISHOP_HEATMAP
                base_value = 1
            elif piece_notation == 'R':  # Rook
                heatmap = self.ROOK_HEATMAP
                base_value = 1
            elif piece_notation == 'Q':  # Queen
                heatmap = self.QUEEN_HEATMAP
                base_value = 1
            elif piece_notation == 'K':  # King
                heatmap = self.KING_HEATMAP
                base_value = 1
            else:
                continue
            
            # Get the positional value for this square
            square_value = heatmap[y][x] * base_value
            
            # Add to score (positive for white, negative for black)
            if piece.color == 'white':
                positional_score += square_value
            else:
                positional_score -= square_value
        
        return positional_score
    
    def evaluate(self):
        black_eval = self.countMaterial('b')
        white_eval = self.countMaterial('w')
        
        material_eval = white_eval - black_eval
        positional_eval = self.get_positional_score()
        
        # Combine material (weighted heavily) and positional evaluation
        # Material: ~30-39 points total, Positional: 0-500 but usually 20-100 in opening
        total_eval = material_eval * 10 + positional_eval
        
        perspective = 1 if self.board.turn == 'white' else -1
        
        return total_eval * perspective
        
    