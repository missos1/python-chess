import unittest
from data.classes.chess_bot.constants import *
from data.classes.chess_bot.GameState import GameState
from data.classes.chess_bot.Bot import Bot
from data.classes.Board import Board
from data.classes.chess_bot.move_gens import *
from tests.constants_for_tests import *

class TestMoveScenarios(unittest.TestCase):
    def build_test_state(self, custom_config=STARTING_POSITION):
        # 1. Initialize a dummy GUI board (dimensions don't matter for the logic)
        board = Board(800, 800)
        
        # 2. Overwrite the config with your custom puzzle
        board.config = custom_config
        
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

    def test_mate_in_one(self):
        # A simple Mate in 1 scenario: Two White Rooks vs Black King
        
        
        state = self.build_test_state(custom_config=MATE_CONFIG)
        
        bot = Bot(color=WHITE)
        best_move = bot.get_best_move(state)
        
        # In this config, moving the Rook from B2 (index 9) to B8 (index 57) is mate.
        # Assuming your move tuple is (source, target, flag)
        if best_move is not None:
            self.assertEqual(best_move[0], 51)   # Source square
            self.assertEqual(best_move[1], 59)  # Target square
    
