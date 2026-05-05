import unittest
from data.classes.chess_bot.constants import *
from data.classes.chess_bot.GameState import GameState
from data.classes.chess_bot.Bot import Bot
from data.classes.Board import Board
from data.classes.chess_bot.move_gens import *
from tests.constants_for_tests import *

class TestZobristHashing(unittest.TestCase):
    def build_test_state(self, custom_config=STARTING_POSITION, color='white'):
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
        state = GameState(bitboards, pieces_array, castling_rights, en_passant_target=None, color=color)
        state.castling_rights = castling_rights
        return state
    
    def test_zobrist_transposition(self):
        # Setup the standard starting board
        state = self.build_test_state() 
        
        move_e4 = (12, 28, FLAG_QUIET) # e2 to e4
        move_e5 = (52, 36, FLAG_QUIET) # e7 to e5
        move_Nf3 = (6, 21, FLAG_QUIET) # g1 to f3
        move_Nc6 = (57, 42, FLAG_QUIET) # b8 to c6
        
        # Path 1: e4, e5, Nf3, Nc6
        state.make_move(move_e4)
        state.make_move(move_e5)
        state.make_move(move_Nf3)
        state.make_move(move_Nc6)
        hash_path_1 = state.zobrist_hash
        
        state.undo_move(move_Nc6)
        state.undo_move(move_Nf3)
        state.undo_move(move_e5)
        state.undo_move(move_e4)
        
        state.make_move(move_Nf3)
        state.make_move(move_Nc6)
        state.make_move(move_e4)
        state.make_move(move_e5)
        hash_path_2 = state.zobrist_hash
        
        self.assertEqual(hash_path_1, hash_path_2, "Zobrist hash failed transposition test!")
        
    def test_initial_hash(self):
        black_go_1st_state = self.build_test_state(color='black')
        expected_initial_hash = self.build_test_state(color='white').zobrist_hash ^ ZOBRIST_TURN
        
        self.assertEqual(
            black_go_1st_state.zobrist_hash, 
            expected_initial_hash, 
            "Initial Zobrist hash does not match expected value!"
        )
    
    def test_board_hash_consistency(self):
        # Create two identical states and check their hashes based on whose turn it is
        state1 = self.build_test_state(custom_config=MATE_CONFIG, color='white')
        state2 = self.build_test_state(custom_config=MATE_CONFIG, color='black')
        
        self.assertNotEqual(
            state1.zobrist_hash, 
            state2.zobrist_hash, 
            "Identical board states have different Zobrist hashes!"
            )