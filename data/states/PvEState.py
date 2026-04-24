import pygame
import random
from data.classes.chess_bot.Bot import *
from data.classes.chess_bot.constants import *
from data.states.State import State
from data.classes.Board import Board

class PvEState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.board = None
        self.player_color = None
        self.game_over = False
        self.bot = None

    def on_enter(self):
        # Fresh board and random color assignment on load
        self.player_color = random.choice(['white', 'black'])
        self.board = Board(600, 600, is_flipped=(self.player_color == 'black'))
        self.bot = Bot(BLACK if self.player_color == WHITE else WHITE)
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
                    if self.board.is_flipped:
                        self.board.handle_click_flipped(mx, my)
                    else:
                        self.board.handle_click(mx, my)
            
            elif event.type == pygame.KEYDOWN:
                # press z to undo
                if event.key == pygame.K_z:
                    self.board.undo_move()
                    self.board.undo_move()

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
        if self.board.turn != self.player_color and not self.game_over:
            self.run_bot_move()

    def run_bot_move(self):
        AImove = self.bot.get_best_move(self.board)
        if AImove is None:
            AImove = self.bot.get_random_move(self.board)
        self.board.AI_move(AImove)
        # debug
        print(f"Move {len(self.board.move_history)}: {self.board.move_history[len(self.board.move_history) - 1].from_pos} to {self.board.move_history[len(self.board.move_history) - 1].to_pos}")
        
    def draw(self, surface):
        surface.fill('white')
        self.board.draw(surface)
