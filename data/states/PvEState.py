import pygame
import random
from data.states.State import State
from data.classes.Board import Board
from data.classes.chess_bot.search import find_best_move
from data.classes.chess_bot.evaluate import Evaluate

class PvEState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.board = None
        self.player_color = None
        self.game_over = False

    def on_enter(self):
        # Fresh board and random color assignment on load
        self.player_color = random.choice(['white', 'black'])
        self.board = Board(600, 600, is_flipped=(self.player_color == 'black'))
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
            self.run_bot_move()

    def run_bot_move(self):
        """Execute bot move using alpha-beta negamax search."""
        bot_color = 'white' if self.player_color == 'black' else 'black'
        
        # Temporarily set turn to bot so search works correctly
        self.board.turn = bot_color
        
        # Find best move using alpha-beta search with depth 2
        evaluator = Evaluate(self.board)
        best_move = find_best_move(self.board, depth=2, evaluator=evaluator)
        
        if best_move:
            piece, move_square = best_move
            piece.move(self.board, move_square, force=True)
            # Switch turn back to player
            self.board.turn = self.player_color

    def draw(self, surface):
        surface.fill('white')
        self.board.draw(surface)
