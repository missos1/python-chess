import pygame
from data.classes.chess_bot.GameState import GameState
from data.states.State import State
from data.classes.Board import Board
from .debug import bitboard_visualize

class PvPState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.board = None
        self.game_state = None

    def on_enter(self):
        # We start a fresh board whenever we enter PvP mode
        self.board = Board(600, 600)
        self.game_state = GameState(self.board.get_bitboards(), self.board.get_pieces_array())

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                move_tuple = self.board.handle_click(mx, my)
                if move_tuple:
                    self.game_state.make_move(self.board, move_tuple, self.board.turn)
                    self.board.turn = 'white' if self.board.turn == 'black' else 'black'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    # Debug: Visualize bitboard for a piece type
                    bitboard_visualize(self.board.get_bitboards())
                if event.key == pygame.K_z:
                    print(f"the last state: {self.game_state.state_history[-1]['from_sq']} to {self.game_state.state_history[-1]['to_sq'] if self.game_state.state_history else 'No moves made yet.'}")
                    self.game_state.undo_move(self.board)
                    self.board.turn = 'white' if self.board.turn == 'black' else 'black'

    def update(self):
        if self.board.is_in_checkmate('black'):
            print('White wins!')
            self.manager.change_state('menu')
        elif self.board.is_in_checkmate('white'):
            print('Black wins!')
            self.manager.change_state('menu')

    def draw(self, surface):
        surface.fill('white')
        self.board.draw(surface)
