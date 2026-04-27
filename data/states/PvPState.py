import pygame
from data.states.State import State
from data.classes.Board import Board
from .debug import bitboard_visualize

class PvPState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.board = None

    def on_enter(self):
        # We start a fresh board whenever we enter PvP mode
        self.board = Board(600, 600)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                self.board.handle_click(mx, my)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    # Debug: Visualize bitboard for a piece type
                    bitboard_visualize(self.board.get_bitboards())

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
