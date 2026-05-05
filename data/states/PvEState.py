import pygame
import random
import threading
import time
from data.classes.chess_bot.Bot import Bot
from data.classes.chess_bot.GameState import GameState
from data.states.State import State
from data.classes.Board import Board
from data.classes.chess_bot.constants import *
from data.classes.chess_bot.move_gens import *
from .debug import bitboard_visualize

class PvEState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.board = None
        self.player_color = None
        self.game_over = False
        self.bot_thinking = False
        self.bot_move = None
        self.bot_thread = None
        self.bot = None
        self.thinking_start_time = 0

    def on_enter(self) -> None:
        # Fresh board and random color assignment on load
        self.player_color = random.choice(['white', 'black'])
        self.board = Board(600, 600, is_flipped=(self.player_color == 'black'))
        self.game_over = False
        self.bot = Bot(depth=5, color=BLACK if self.player_color == 'white' else WHITE)
        print(f"PvE Started! You are playing as {self.player_color}.")
        

    def handle_events(self, events):
        if self.game_over:
            return
            
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Only let player click if it is currently their turn
                if self.board.turn == self.player_color:
                    mx, my = event.pos

                    self.board.handle_click(mx, my, self.board.is_flipped)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    # Debug: Visualize bitboard for a piece type
                    bitboard_visualize(self.board.get_bitboards())
                    

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

        # If it is not the player's turn, instantly trigger the bot
        if self.board.turn != self.player_color:
            if not self.bot_thinking:
                self.start_bot_thinking()
            elif self.bot_move is not None:
                elapsed = time.time() - self.thinking_start_time
                print(f"Bot finished thinking in {elapsed:.2f} seconds.")
                self.execute_bot_move(self.bot_move)
                self.bot_move = None
                self.bot_thinking = False

    def start_bot_thinking(self):
        self.bot_thinking = True
        self.thinking_start_time = time.time()
        print("Bot is thinking...")
        
        current_bitboards = self.board.get_bitboards()
        pieces_array = create_piece_array_from_bitboards(current_bitboards)
        
        if self.board.en_passant_target is None:
            ep_index = None
        else:
            x, y = self.board.en_passant_target
            ep_index = (7 - y) * 8 + x

        engine_state = GameState(current_bitboards, pieces_array, en_passant_target=ep_index)
        # Using the property we defined in the Board class
        engine_state.castling_rights = self.board.castling_rights 
        
        def worker(state):
            ai = self.bot
            # Store the computed move so the main loop can pick it up
            self.bot_move = ai.get_best_move(state) 
            
            # Failsafe if it returns nothing (checkmate)
            if self.bot_move is None:
                self.bot_move = "NO_MOVE"

        self.bot_thread = threading.Thread(target=worker, args=(engine_state,))
        self.bot_thread.start()
        
    def execute_bot_move(self, best_move_tuple):
        if best_move_tuple and best_move_tuple != "NO_MOVE":
            source_idx, target_idx, flag = best_move_tuple
            
            # Reverse the bitboard index back to Pygame (x, y) coordinates
            source_x = source_idx % 8
            source_y = 7 - (source_idx // 8)
            
            target_x = target_idx % 8
            target_y = 7 - (target_idx // 8)
            
            # Grab the physical Pygame objects
            source_square = self.board.get_square_from_pos((source_x, source_y))
            target_square = self.board.get_square_from_pos((target_x, target_y))
            
            piece = source_square.occupying_piece
            
            if piece:
                # We use force=True because our mathematical Bot already verified 
                # this move is 100% strictly legal!
                if piece.move(self.board, target_square, force=True):
                    self.board.turn = self.player_color
                    
        else:
            # If get_best_move returns None, the Bot is in Checkmate or Stalemate.
            pass

    def draw(self, surface):
        surface.fill('white')
        self.board.draw(surface)

    def get_target_fps(self):
        return 15 if self.bot_thinking else 60
    
    