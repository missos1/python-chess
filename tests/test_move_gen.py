import unittest
from data.classes.chess_bot.GameState import GameState
from data.classes.chess_bot.constants import *
from data.classes.Board import Board
from data.classes.chess_bot.move_gens import create_piece_array_from_bitboards
from tests.constants_for_tests import *
from tests.utils_for_test import run_perft, divide

class TestMoveGeneration(unittest.TestCase):
    def build_test_state(self):
        # 1. Initialize a dummy GUI board (dimensions don't matter for the logic)
        board = Board(800, 800)
        
        # 3. Reset the squares and set up the pieces based on the new config
        board.squares = board.generate_squares()
        board.setup_board()
        
        # 4. Extract the bitboards and castling rights from the GUI board
        bitboards = board.get_bitboards()
        castling_rights = board.castling_rights
        
        # 5. Get the 1D pieces array (See note below!)
        pieces_array = create_piece_array_from_bitboards(bitboards)
        
        # 6. Create and return the GameState engine object
        state = GameState(bitboards, pieces_array, castling_rights, en_passant_target=None)
        state.castling_rights = castling_rights
        return state
    
    def test_startpos(self):
        state = self.build_test_state()
        
        self.assertEqual(run_perft(state, depth=1, current_color=WHITE), 20)
        self.assertEqual(run_perft(state, depth=2, current_color=WHITE), 400)
        self.assertEqual(run_perft(state, depth=3, current_color=WHITE), 8902)
        self.assertEqual(run_perft(state, depth=4, current_color=WHITE), 197281)
        
    def test_startpos_divide(self):
        state = self.build_test_state()
        dict = {}

        divide(state, depth=5, current_color=WHITE, dictionary=dict)
        # lack of en passant made the test failed in the pass.
        for move, _ in dict.items():
            self.assertEqual(
                dict[move], DEPTH_5_STOCKFISH[move], 
                f"Move {move} has incorrect node count. Expected {DEPTH_5_STOCKFISH[move]}, got {dict[move]}."
                )
            
        print(f"If you see a mismatch, the bug is likely in move generation or make/undo move logic.")