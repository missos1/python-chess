import pygame

from data.classes.Square import Square
from data.classes.pieces.Rook import Rook
from data.classes.pieces.Bishop import Bishop
from data.classes.pieces.Knight import Knight
from data.classes.pieces.Queen import Queen
from data.classes.pieces.King import King
from data.classes.pieces.Pawn import Pawn

class Board:
	def __init__(self, width, height, is_flipped=False):
		self.width = width
		self.height = height
		self.square_width = width // 8
		self.square_height = height // 8
		self.selected_piece = None
		self.turn = 'white'
		self.is_flipped = is_flipped
		self.en_passant_target = None

		self.config = [
			['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
			['b ', 'b ', 'b ', 'b ', 'b ', 'b ', 'b ', 'b '],
			['','','','','','','',''],
			['','','','','','','',''],
			['','','','','','','',''],
			['','','','','','','',''],
			['w ', 'w ', 'w ', 'w ', 'w ', 'w ', 'w ', 'w '],
			['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
		]

		self.squares = self.generate_squares()

		self.setup_board()
		if self.is_flipped:
			self.apply_view(True)

	def generate_squares(self):
		output = []
		for y in range(8):
			for x in range(8):
				output.append(
					Square(
						x,
						y,
						self.square_width,
						self.square_height
					)
				)

		return output


	def setup_board(self):
		for y, row in enumerate(self.config):
			for x, piece in enumerate(row):
				if piece != '':
					square = self.get_square_from_pos((x, y))

					if piece[1] == 'R':
						square.occupying_piece = Rook(
							(x, y),
							'white' if piece[0] == 'w' else 'black',
							self
						)

					elif piece[1] == 'N':
						square.occupying_piece = Knight(
							(x, y),
							'white' if piece[0] == 'w' else 'black',
							self
						)

					elif piece[1] == 'B':
						square.occupying_piece = Bishop(
							(x, y),
							'white' if piece[0] == 'w' else 'black',
							self
						)

					elif piece[1] == 'Q':
						square.occupying_piece = Queen(
							(x, y),
							'white' if piece[0] == 'w' else 'black',
							self
						)

					elif piece[1] == 'K':
						square.occupying_piece = King(
							(x, y),
							'white' if piece[0] == 'w' else 'black',
							self
						)

					elif piece[1] == ' ':
						square.occupying_piece = Pawn(
							(x, y),
							'white' if piece[0] == 'w' else 'black',
							self
						)


	def handle_click(self, mx, my):
		x = mx // self.square_width
		y = my // self.square_height
		if x < 0 or x > 7 or y < 0 or y > 7:
			return
		clicked_square = self.get_square_from_pos((x, y))

		if self.selected_piece is None:
			if clicked_square.occupying_piece is not None:
				if clicked_square.occupying_piece.color == self.turn:
					self.selected_piece = clicked_square.occupying_piece

		elif self.selected_piece.move(self, clicked_square):
			self.turn = 'white' if self.turn == 'black' else 'black'

		elif clicked_square.occupying_piece is not None:
			if clicked_square.occupying_piece.color == self.turn:
				self.selected_piece = clicked_square.occupying_piece

	def handle_click_flipped(self, mx, my):
		x = 7 - (mx // self.square_width)
		y = 7 - (my // self.square_height)
		if x < 0 or x > 7 or y < 0 or y > 7:
			return
		clicked_square = self.get_square_from_pos((x, y))

		if self.selected_piece is None:
			if clicked_square.occupying_piece is not None:
				if clicked_square.occupying_piece.color == self.turn:
					self.selected_piece = clicked_square.occupying_piece

		elif self.selected_piece.move(self, clicked_square):
			self.turn = 'white' if self.turn == 'black' else 'black'

		elif clicked_square.occupying_piece is not None:
			if clicked_square.occupying_piece.color == self.turn:
				self.selected_piece = clicked_square.occupying_piece

	def apply_view(self, is_flipped):
		self.is_flipped = is_flipped
		for square in self.squares:
			square.set_view(self.is_flipped)


	def is_in_check(self, color=None, board_change=None): # board_change = [(x1, y1), (x2, y2)]
		if color == None:
			color = self.turn
		
		output = False
		king_pos = None

		changing_piece = None
		old_square = None
		new_square = None
		new_square_old_piece = None
		en_passant_captured_square = None
		en_passant_captured_piece = None

		if board_change is not None:
			for square in self.squares:
				if square.pos == board_change[0]:
					changing_piece = square.occupying_piece
					old_square = square
					old_square.occupying_piece = None
			for square in self.squares:
				if square.pos == board_change[1]:
					new_square = square
					new_square_old_piece = new_square.occupying_piece
					new_square.occupying_piece = changing_piece

			# Simulate en passant capture by temporarily removing the captured pawn.
			if changing_piece is not None and changing_piece.notation == ' ' and self.en_passant_target is not None:
				if board_change[1] == self.en_passant_target and new_square_old_piece is None and old_square.x != new_square.x:
					capture_y = new_square.y + (1 if changing_piece.color == 'white' else -1)
					if 0 <= capture_y < 8:
						en_passant_captured_square = self.get_square_from_pos((new_square.x, capture_y))
						en_passant_captured_piece = en_passant_captured_square.occupying_piece
						en_passant_captured_square.occupying_piece = None

		pieces = [
			i.occupying_piece for i in self.squares if i.occupying_piece is not None
		]

		if changing_piece is not None:
			if changing_piece.notation == 'K':
				king_pos = new_square.pos
		if king_pos == None:
			for piece in pieces:
				if piece.notation == 'K':
					if piece.color == color:
						king_pos = piece.pos
		for piece in pieces:
			if piece.color != color:
				for square in piece.attacking_squares(self):
					if square.pos == king_pos:
						output = True

		if board_change is not None:
			old_square.occupying_piece = changing_piece
			new_square.occupying_piece = new_square_old_piece
			if en_passant_captured_square is not None:
				en_passant_captured_square.occupying_piece = en_passant_captured_piece
						
		return output


	def is_in_checkmate(self, color):
		output = False

		for piece in [i.occupying_piece for i in self.squares]:
			if piece != None:
				if piece.notation == 'K' and piece.color == color:
					king = piece

		if king.get_valid_moves(self) == []:
			if self.is_in_check(color):
				output = True

		return output


	def get_square_from_pos(self, pos):
		for square in self.squares:
			if (square.x, square.y) == (pos[0], pos[1]):
				return square


	def get_piece_from_pos(self, pos):
		return self.get_square_from_pos(pos).occupying_piece

	def get_all_valid_moves(self, color=None):
		if color == None:
			color = self.turn

		moves = []
		for square in self.squares:
			piece = square.occupying_piece
			if piece and piece.color == color:
				for move_square in piece.get_valid_moves(self):
					moves.append((piece, move_square))
		return moves

	def is_recapturable(self, piece, target_square):
		"""Check if capturing piece can be immediately recaptured by lower-value opponent piece.
		
		Used by move ordering to avoid scoring bad trades (e.g., Qxp when pawn recaptures).
		
		Args:
			piece: The attacking piece about to capture.
			target_square: The destination square (where capture happens).
		
		Returns:
			Tuple (is_recapturable, min_recapture_value):
			- is_recapturable: True if an opponent piece can immediately recapture
			- min_recapture_value: Value of lowest-value piece that can recapture (0 if none)
		"""
		if target_square.occupying_piece is None:
			return False, 0
		
		# Get all opponent pieces that can attack this square
		opponent_color = 'black' if piece.color == 'white' else 'white'
		min_recapture_value = float('inf')
		can_recapture = False
		
		# Check all opponent pieces
		for square in self.squares:
			opponent_piece = square.occupying_piece
			if opponent_piece and opponent_piece.color == opponent_color:
				# Check if this opponent piece can attack target_square
				for attacked_square in opponent_piece.get_moves(self):
					if attacked_square.pos == target_square.pos:
						# This opponent piece can recapture
						can_recapture = True
						# Get piece value
						piece_type = opponent_piece.notation
						value_map = {' ': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 100}
						value = value_map.get(piece_type, 0)
						min_recapture_value = min(min_recapture_value, value)
					break
		
		return can_recapture, min_recapture_value if can_recapture else 0

	def get_bitboards(self):
		bitboards = {
			'P': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0, # White pieces
			'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0  # Black pieces
		}

		for square in self.squares:
			piece = square.occupying_piece
			if piece is not None:
				# Pygame y=0 is Rank 8, y=7 is Rank 1. 
				# Invert y so index 0 is A1 and index 63 is H8 (Little Edian Rank File mapping).
				lerf_index = (7 - square.y) * 8 + square.x

				# Safely get the piece type by its class name
				piece_type = piece.__class__.__name__
				
				# Map the class name to standard FIDE notation
				symbol_map = {
					'Pawn': 'P', 'Knight': 'N', 'Bishop': 'B', 
					'Rook': 'R', 'Queen': 'Q', 'King': 'K'
				}
				symbol = symbol_map.get(piece_type)
				
				# Convert to lowercase if the piece is black
				if piece.color == 'black':
					symbol = symbol.lower()

				# Stamp this piece onto its specific bitboard using Bitwise OR
				# Example: 0001, shift by the lerf index 3 to 1000 and OR 0100 to get 1100
				bitboards[symbol] |= (1 << lerf_index)

		# Generate the summary bitboards for quick AI lookups
		bitboards['white_pieces'] = (bitboards['P'] | bitboards['N'] | bitboards['B'] | 
									 bitboards['R'] | bitboards['Q'] | bitboards['K'])
		
		bitboards['black_pieces'] = (bitboards['p'] | bitboards['n'] | bitboards['b'] | 
									 bitboards['r'] | bitboards['q'] | bitboards['k'])
		
		bitboards['occupied_squares'] = bitboards['white_pieces'] | bitboards['black_pieces']

		return bitboards

	def capture_move_state(self, piece, target_square):
		"""Capture all board state before executing a move.
		
		Used by search algorithms (e.g., alpha-beta minimax) to enable move/unmake cycles.
		Must be called BEFORE piece.move() executes.
		
		Args:
			piece: The piece about to move.
			target_square: The destination square.
		
		Returns:
			dict with keys: from_pos, to_pos, piece_had_moved_before, captured_piece,
			captured_pos, en_passant_target_before, is_promotion, is_castling,
			rook_state (for castling only)
		"""
		from_square = self.get_square_from_pos(piece.pos)
		captured_piece = target_square.occupying_piece
		captured_pos = target_square.pos
		
		# Handle en passant: captured piece is on different square
		if (piece.notation == ' ' and self.en_passant_target is not None and
			target_square.pos == self.en_passant_target and 
			captured_piece is None and from_square.x != target_square.x):
			capture_y = target_square.y + (1 if piece.color == 'white' else -1)
			if 0 <= capture_y < 8:
				en_passant_square = self.get_square_from_pos((target_square.x, capture_y))
				captured_piece = en_passant_square.occupying_piece
				captured_pos = en_passant_square.pos
		
		# Detect if this is a promotion
		is_promotion = (piece.notation == ' ' and (target_square.y == 0 or target_square.y == 7))
		
		# Detect if this is castling and snapshot rook state
		is_castling = (piece.notation == 'K' and abs(from_square.x - target_square.x) == 2)
		rook_state = None
		if is_castling:
			if from_square.x - target_square.x == 2:
				# Queenside castling
				rook = self.get_piece_from_pos((0, piece.y))
				rook_from = (0, piece.y)
				rook_to = (3, piece.y)
			elif from_square.x - target_square.x == -2:
				# Kingside castling
				rook = self.get_piece_from_pos((7, piece.y))
				rook_from = (7, piece.y)
				rook_to = (5, piece.y)
			
			if rook is not None:
				rook_state = {
					'rook': rook,
					'from_pos': rook_from,
					'to_pos': rook_to,
					'rook_had_moved_before': rook.has_moved
				}
		
		return {
			'piece': piece,
			'from_pos': piece.pos,
			'to_pos': target_square.pos,
			'piece_had_moved_before': piece.has_moved,
			'captured_piece': captured_piece,
			'captured_pos': captured_pos,
			'en_passant_target_before': self.en_passant_target,
			'is_promotion': is_promotion,
			'is_castling': is_castling,
			'rook_state': rook_state
		}

	def draw(self, display):
		if self.selected_piece is not None:
			self.get_square_from_pos(self.selected_piece.pos).highlight = True
			for square in self.selected_piece.get_valid_moves(self):
				square.highlight = True

		for square in self.squares:
			square.draw(display)