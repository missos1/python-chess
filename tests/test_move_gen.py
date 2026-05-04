import unittest
from data.classes.chess_bot.GameState import GameState
from data.classes.chess_bot.constants import *
from data.classes.Board import Board

DEPTH_5_STOCKFISH = {
    "a2a3": 181046,
    "b2b3": 215255,
    "c2c3": 222861,
    "d2d3": 328511,
    "e2e3": 402988,
    "f2f3": 178889,
    "g2g3": 217210,
    "h2h3": 181044,
    "a2a4": 217832,
    "b2b4": 216145,
    "c2c4": 240082,
    "d2d4": 361790,
    "e2e4": 405385,
    "f2f4": 198473,
    "g2g4": 214048,
    "h2h4": 218829,
    "b1a3": 198572,
    "b1c3": 234656,
    "g1f3": 233491,
    "g1h3": 198502
}

def run_perft(state, depth, current_color):
    if depth == 0:
        return 1
    
    nodes = 0
    # USE STRICTLY LEGAL MOVES HERE just to prove the math works!
    legal_moves = state.get_strictly_legal_moves(current_color)
    enemy_color = BLACK if current_color == WHITE else WHITE
    
    for move in legal_moves:
        state.make_move(move, current_color)
        nodes += run_perft(state, depth - 1, enemy_color)
        state.undo_move()
        
    return nodes

def index_to_algebraic(index):
    # Get the file (a-h)
    file_char = chr((index % 8) + ord('a'))
    # Get the rank (1-8)
    rank_char = str((index // 8) + 1)
    return file_char + rank_char

def divide(state, depth, current_color, dictionary):
    print(f"go perft {depth}")
    
    if depth == 0:
        return
        
    total_nodes = 0
    legal_moves = state.get_strictly_legal_moves(current_color)
    enemy_color = BLACK if current_color == WHITE else WHITE
    
    for move in legal_moves:
        source, target, flag = move
        
        # 1. Make the top-level move
        state.make_move(move, current_color)
        
        # 2. Count all nodes branching off from here
        branch_nodes = run_perft(state, depth - 1, enemy_color)
        
        # 3. Undo the move
        state.undo_move()
        
        # 4. Format and print
        move_str = index_to_algebraic(source) + index_to_algebraic(target)
        
        # If it was a promotion, you might want to add the piece letter (e.g. e7e8q)
        if flag == FLAG_PROMOTION:
            move_str += "q" # Simplified for printing
            
        dictionary[move_str] = branch_nodes
        total_nodes += branch_nodes
        
    print(f"\nNodes searched: {total_nodes}")

class TestMoveGeneration(unittest.TestCase):
    def build_test_state(self):
        # 1. Initialize a dummy GUI board (dimensions don't matter for the logic)
        board = Board(800, 800)
        
        # 3. Reset the squares and set up the pieces based on the new config
        board.squares = board.generate_squares()
        board.setup_board()
        
        # 4. Extract the bitboards and castling rights from the GUI board
        bitboards = board.get_bitboards()
        
        # 5. Get the 1D pieces array (See note below!)
        pieces_array = board.get_pieces_array()
        
        # 6. Create and return the GameState engine object
        state = GameState(bitboards, pieces_array)
        return state
    
    def test_startpos(self):
        # Build your state from the starting position here
        state = self.build_test_state()
        dict = {}
        
        divide(state, depth=5, current_color=WHITE, dictionary=dict)
        # lack of en passant made the test failed.
        for move, _ in dict.items():
            self.assertEqual(dict[move], DEPTH_5_STOCKFISH[move], f"Move {move} has incorrect node count. Expected {DEPTH_5_STOCKFISH[move]}, got {dict[move]}.")
        print(f"If you see a mismatch, the bug is likely in move generation or make/undo move logic.")
        self.assertEqual(run_perft(state, depth=1, current_color=WHITE), 20)
        self.assertEqual(run_perft(state, depth=2, current_color=WHITE), 400)
        self.assertEqual(run_perft(state, depth=3, current_color=WHITE), 8902)
        self.assertEqual(run_perft(state, depth=4, current_color=WHITE), 197281)