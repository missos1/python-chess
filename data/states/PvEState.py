import pygame
import random
import threading
from data.classes.chess_bot.GameState import GameState
from data.classes.chess_bot.Bot import Bot
from data.states.State import State
from data.classes.Board import Board
from data.classes.chess_bot.constants import *
from data.classes.chess_bot.move_gens import *
from .debug import bitboard_visualize

class PvEState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.board = None
        self.bot = None
        self.game_state = None
        self.game_over = False
        self.bot_thread = None
        self.bot_move = None
        self.bot_thinking = False

    def on_enter(self) -> None:
        # Fresh board and random color assignment on load
        self.player_color = random.choice(['white', 'black'])
        self.board = Board(600, 600, is_flipped=(self.player_color == 'black'))
        self.bot = Bot(color='white' if self.player_color == 'black' else 'black')
        self.game_state = GameState(self.board.get_bitboards(), self.board.get_pieces_array())
        self.game_over = False
        print(f"PvE Started! You are playing as {self.player_color}.")
        

    def handle_events(self, events):
        if self.game_over:
            return
            
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Only let player click if it is currently their turn
                if self.board.turn == self.player_color:
                    mx, my = event.pos
                    move_tuple = None
                    move_tuple = self.board.handle_click(mx, my, self.game_state, self.board.is_flipped)

                    if move_tuple:
                        self.game_state.make_move(move_tuple, self.player_color, self.board)
                        self.board.turn = 'white' if self.board.turn == 'black' else 'black'
                        self.board.update_from_bitboards(self.game_state.board)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    # Debug: Visualize bitboard for a piece type
                    bitboard_visualize(self.board.get_bitboards())
                if event.key == pygame.K_z:
                    if not self.game_state.state_history:
                        print("No moves made yet.")
                    else:
                        self.game_state.undo_move(self.board)
                        self.board.turn = 'white' if self.board.turn == 'black' else 'black'
                        self.game_state.undo_move(self.board)
                        self.board.turn = 'white' if self.board.turn == 'black' else 'black'
                        self.board.update_from_bitboards(self.game_state.board)

    def update(self):
        if self.game_over:
            return

        if self.board.is_in_checkmate('black'):
            print('White wins!')
            self.game_over = True
            self.manager.change_state('menu')
            return
        elif self.board.is_in_checkmate('white'):
            print('Black wins!')
            self.game_over = True
            self.manager.change_state('menu')
            return

        # If it is not the player's turn, trigger the bot
        if self.board.turn != self.player_color and not self.game_over:
            # Start bot thinking if not already thinking
            if not self.bot_thinking:
                self.start_bot_move()
            # Check if bot has finished thinking
            elif self.bot_thread and not self.bot_thread.is_alive():
                self.apply_bot_move()

    def start_bot_move(self):
        """Start bot move calculation in a background thread"""
        self.bot_thinking = True
        self.bot_thread = threading.Thread(target=self._bot_search_worker, daemon=True)
        self.bot_thread.start()

    def _bot_search_worker(self):
        """Worker thread that calculates the bot's move"""
        self.bot.color = 'white' if self.player_color == 'black' else 'black'
        # Sync game state with current board state (both bitboards and piece values)
        self.game_state.sync_from_board(self.board)
        # Integrate the AI model to calculate and return the best move on self.board.
        self.bot_move = self.bot.get_best_move(self.board, self.game_state)

    def apply_bot_move(self):
        """Apply the bot's move on the main thread"""
        # Ensure game state is synced with board
        self.game_state.sync_from_board(self.board)
        
        # when the bot fails to find a move (bot prepares to lose), just pick a random move to avoid crashing.
        if self.bot_move is None:
            moves = self.game_state.get_strictly_legal_moves(self.bot.color)
            self.bot_move = random.choice(moves) if moves else None
            # bot is checkmated, just skip its turn and let the player win
            if self.bot_move is None:
                self.board.turn = 'white' if self.board.turn == 'black' else 'black'
                self.bot_thinking = False
                return
        self.game_state.make_move(self.bot_move, self.bot.color, self.board)
        self.board.turn = 'white' if self.board.turn == 'black' else 'black'
        self.board.update_from_bitboards(self.game_state.board)
        self.bot_thinking = False
        self.bot_move = None

    def draw(self, surface):
        surface.fill('white')
        self.board.draw(surface, self.game_state)
    
    