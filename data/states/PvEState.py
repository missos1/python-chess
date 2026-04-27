import pygame
import random
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

    def on_enter(self) -> None:
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
            self.run_bot_move()

    def run_bot_move(self):
        # TODO: Add Model prediction here. 
        # Integrate the AI model to calculate and return the best move on self.board. 
        
        bot_color = 'white' if self.player_color == 'black' else 'black'
        
        # --- Temporarily use a random move to prevent soft locks during testing ---
        # NOTE: Remove this stubbed logic once the model provides a move!
        valid_moves = []
        for square in self.board.squares:
            piece = square.occupying_piece
            if piece and piece.color == bot_color:
                moves = piece.get_valid_moves(self.board)
                for move_square in moves:
                    valid_moves.append((piece, move_square))
                    
        if valid_moves:
            piece, move_square = random.choice(valid_moves)
            # The .move() function returns True if valid execution
            if piece.move(self.board, move_square):
                # Switch turn back to the player manually after bot hits move
                self.board.turn = self.player_color
        else:
            # No valid moves edge case (Should be covered by checkmate checks normally)
            pass

    def draw(self, surface):
        surface.fill('white')
        self.board.draw(surface)
    
    