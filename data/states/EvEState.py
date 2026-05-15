import pygame
import random
import threading
import time

from data.states.State import State
from data.classes.Board import Board
from data.classes.Button import Button
from data.classes.chess_bot.GameState import GameState
from data.classes.chess_bot.move_gens import create_piece_array_from_bitboards
from data.classes.chess_bot.constants import WHITE, BLACK
from data.classes.chess_bot.Bot import Bot as NewBot
from data.classes.chess_bot_v1.Bot import Bot as OldBot


class EvEState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.board = None
        self.is_started = False
        self.time_limit = 5.0
        self.tpm_text = "5.0"
        self.tpm_active = False

        self.bot_white = None
        self.bot_black = None
        self.white_bot_name = ""
        self.black_bot_name = ""
        self.bot_thinking = False
        self.bot_move = None
        self.thinking_start_time = 0

        self.custom_selected_piece = None
        self.custom_selected_square = None

        self.sidebar_x = 512
        self.sidebar_width = 88

        self.tpm_rect = pygame.Rect(self.sidebar_x + 4, 60, 80, 26)
        self.start_btn = Button(self.sidebar_x + 4, 110, 80, 36, "Start")
        self.replay_btn = Button(self.sidebar_x + 4, 160, 80, 36, "Replay")

    def on_enter(self) -> None:
        self.reset_board()

    def reset_board(self):
        self.board = Board(512, 512)
        self.board.turn = 'white'
        self.board.selected_piece = None

        self.is_started = False
        self.bot_thinking = False
        self.bot_move = None
        self.custom_selected_piece = None
        self.custom_selected_square = None

        new_bot_white = random.choice([True, False])
        if new_bot_white:
            self.bot_white = NewBot(color=WHITE, time_limit=self.time_limit)
            self.bot_black = OldBot(color=BLACK, time_limit=self.time_limit)
            self.white_bot_name = "New_Bot"
            self.black_bot_name = "Old_Bot"
        else:
            self.bot_white = NewBot(color=WHITE, time_limit=self.time_limit)
            self.bot_black = OldBot(color=BLACK, time_limit=self.time_limit)
            self.white_bot_name = "Old_Bot"
            self.black_bot_name = "New_Bot"

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.change_state('menu')
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if mx >= self.sidebar_x:
                    self._handle_sidebar_click(mx, my)
                elif not self.is_started:
                    self._handle_board_click(mx, my)

            if event.type == pygame.KEYDOWN:
                if not self.is_started:
                    self._handle_text_input(event)
                    if event.key == pygame.K_d:
                        self._delete_selected_piece()

    def _handle_sidebar_click(self, mx, my):
        if self.start_btn.rect.collidepoint(mx, my) and not self.is_started:
            self.is_started = True
            try:
                self.time_limit = float(self.tpm_text)
            except ValueError:
                self.time_limit = 5.0
            self.bot_white.time_limit = self.time_limit
            self.bot_black.time_limit = self.time_limit
            self.tpm_active = False
            return

        if self.replay_btn.rect.collidepoint(mx, my):
            self.reset_board()
            return

        self.tpm_active = self.tpm_rect.collidepoint(mx, my)

    def _handle_board_click(self, mx, my):
        if mx >= self.board.width or my >= self.board.height:
            return

        square_x = mx // self.board.square_width
        square_y = my // self.board.square_height
        square = self.board.get_square_from_pos((square_x, square_y))
        if square is None:
            return

        if self.custom_selected_piece is None:
            if square.occupying_piece:
                self.custom_selected_piece = square.occupying_piece
                self.custom_selected_square = square
                square.occupying_piece = None
                square.highlight = True
        else:
            if square == self.custom_selected_square:
                square.occupying_piece = self.custom_selected_piece
                square.occupying_piece.pos = square.pos
                square.occupying_piece.x = square.x
                square.occupying_piece.y = square.y
            else:
                square.occupying_piece = self.custom_selected_piece
                square.occupying_piece.pos = square.pos
                square.occupying_piece.x = square.x
                square.occupying_piece.y = square.y
                self.custom_selected_square.occupying_piece = None

            self.custom_selected_square.highlight = False
            self.custom_selected_square = None
            self.custom_selected_piece = None

    def _handle_text_input(self, event):
        if not self.tpm_active:
            return

        if event.key == pygame.K_BACKSPACE:
            self.tpm_text = self.tpm_text[:-1]
            return

        if event.unicode.isdigit() or event.unicode == '.':
            if len(self.tpm_text) < 6:
                self.tpm_text += event.unicode

    def _delete_selected_piece(self):
        if self.custom_selected_square and self.custom_selected_piece:
            self.custom_selected_square.highlight = False
            self.custom_selected_square = None
            self.custom_selected_piece = None

    def update(self):
        if not self.is_started:
            return

        if self.board.is_in_checkmate('black') or self.board.is_in_checkmate('white'):
            return

        if not self.bot_thinking:
            self.start_bot_thinking()
        elif self.bot_move is not None:
            self.execute_bot_move(self.bot_move)
            self.bot_move = None
            self.bot_thinking = False

    def start_bot_thinking(self):
        self.bot_thinking = True
        self.thinking_start_time = time.time()

        current_bot = self.bot_white if self.board.turn == 'white' else self.bot_black
        current_bitboards = self.board.get_bitboards()
        pieces_array = create_piece_array_from_bitboards(current_bitboards)

        ep_index = None
        if self.board.en_passant_target:
            x, y = self.board.en_passant_target
            ep_index = (7 - y) * 8 + x

        engine_state = GameState(
            current_bitboards,
            pieces_array,
            self.board.castling_rights,
            en_passant_target=ep_index,
            color=current_bot.color
        )

        def worker(state, bot):
            move = bot.get_best_move(state)
            self.bot_move = move if move is not None else "NO_MOVE"

        thread = threading.Thread(target=worker, args=(engine_state, current_bot))
        thread.start()

    def execute_bot_move(self, best_move_tuple):
        if best_move_tuple != "NO_MOVE":
            source_idx, target_idx, flag = best_move_tuple

            source_x = source_idx % 8
            source_y = 7 - (source_idx // 8)
            target_x = target_idx % 8
            target_y = 7 - (target_idx // 8)

            source_square = self.board.get_square_from_pos((source_x, source_y))
            target_square = self.board.get_square_from_pos((target_x, target_y))
            piece = source_square.occupying_piece

            if piece:
                old_y = piece.y
                if piece.move(self.board, target_square, force=True):
                    self.board.update_en_passant_target(piece, old_y)
                    self.board.turn = 'black' if self.board.turn == 'white' else 'white'

    def draw(self, surface):
        surface.fill((255, 255, 255))

        if not self.is_started:
            for square in self.board.squares:
                if square != self.custom_selected_square:
                    square.highlight = False

        self.board.draw(surface)

        pygame.draw.line(surface, (150, 150, 150), (self.sidebar_x, 0), (self.sidebar_x, 600), 2)

        font = pygame.font.SysFont(None, 20)
        title_lbl = font.render("TPM", True, (0, 0, 0))
        surface.blit(title_lbl, (self.sidebar_x + 8, 35))

        color_box = (200, 255, 200) if self.tpm_active else (220, 220, 220)
        pygame.draw.rect(surface, color_box, self.tpm_rect)
        pygame.draw.rect(surface, (100, 100, 100), self.tpm_rect, 1)
        tpm_surface = font.render(self.tpm_text, True, (0, 0, 0))
        surface.blit(tpm_surface, (self.tpm_rect.x + 6, self.tpm_rect.y + 5))

        self.start_btn.draw(surface)
        self.replay_btn.draw(surface)

        label_font = pygame.font.SysFont(None, 18)
        white_label = label_font.render(f"White: {self.white_bot_name}", True, (0, 0, 0))
        black_label = label_font.render(f"Black: {self.black_bot_name}", True, (0, 0, 0))
        surface.blit(white_label, (self.sidebar_x + 4, 210))
        surface.blit(black_label, (self.sidebar_x + 4, 230))

        if self.custom_selected_piece:
            mx, my = pygame.mouse.get_pos()
            centering_rect = self.custom_selected_piece.img.get_rect()
            centering_rect.center = (mx, my)
            surface.blit(self.custom_selected_piece.img, centering_rect.topleft)

    def get_target_fps(self):
        return 15 if self.bot_thinking else 60
