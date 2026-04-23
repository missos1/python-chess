import pygame

from data.classes.Square import Square
from data.classes.move import Move
from data.classes.pieces.Rook import Rook
from data.classes.pieces.Bishop import Bishop
from data.classes.pieces.Knight import Knight
from data.classes.pieces.Queen import Queen
from data.classes.pieces.King import King
from data.classes.pieces.Pawn import Pawn

class Board:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.square_width = width // 8
		self.square_height = height // 8
		self.selected_piece = None
		self.turn = 'white'
		self.move_history = []

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
		clicked_square = self.get_square_from_pos((x, y))

		if self.selected_piece is None:
			if clicked_square.occupying_piece is not None:
				if clicked_square.occupying_piece.color == self.turn:
					self.selected_piece = clicked_square.occupying_piece
					print(self.selected_piece.has_moved)

		elif self.selected_piece.move(self, clicked_square):
			self.turn = 'white' if self.turn == 'black' else 'black'

		elif clicked_square.occupying_piece is not None:
			if clicked_square.occupying_piece.color == self.turn:
				self.selected_piece = clicked_square.occupying_piece
				print(self.selected_piece.has_moved)


	def is_in_check(self, color, board_change=None): # board_change = [(x1, y1), (x2, y2)]
		output = False
		king_pos = None

		changing_piece = None
		old_square = None
		new_square = None
		new_square_old_piece = None

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
	
	# def make_move(self, move):
	# 	from_square = self.get_square_from_pos(move.from_pos)
	# 	to_square = self.get_square_from_pos(move.to_pos)
	# 	new_move = Move(piece=move.piece,
	# 		  		from_pos=move.from_pos,
	# 				to_pos=move.to_pos,
	# 				captured=to_square.occupying_piece,
	# 				piece_has_moved=move.piece.has_moved)
	# 	move.piece.pos, move.piece.x, move.piece.y = to_square.pos, to_square.x, to_square.y
	# 	from_square.occupying_piece = None
	# 	to_square.occupying_piece = move.piece
	# 	self.selected_piece = None
	# 	move.piece.has_moved = True

	# 	# Pawn promotion
	# 	if move.piece.notation == ' ':
	# 		if to_square.y == 0 or to_square.y == 7:
	# 			from data.classes.pieces.Queen import Queen
	# 			to_square.occupying_piece = Queen(
	# 				(to_square.x, to_square.y),
	# 				move.piece.color,
	# 				self
	# 			)
	# 			new_move.promotion = to_square.occupying_piece

	# 	# Move rook if king castles
	# 	if move.piece.notation == 'K':
	# 		if from_square.x - to_square.x == 2:
	# 			rook = self.get_piece_from_pos((0, to_square.y))
	# 			new_move.is_castling = True
	# 			new_move.rook = rook
	# 			new_move.rook_from = (0, to_square.y)
	# 			new_move.rook_to = (3, to_square.y)
	# 			rook.move(self, new_move.rook_to, force=True)
	# 		elif from_square.x - to_square.x == -2:
	# 			rook = self.get_piece_from_pos((7, to_square.y))
	# 			new_move.is_castling = True
	# 			new_move.rook = rook
	# 			new_move.rook_from = (7, to_square.y)
	# 			new_move.rook_to = (5, to_square.y)
	# 			rook.move(self, new_move.rook_to, force=True)
	# 	self.save_move(new_move)
	# 	self.turn = 'white' if self.turn == 'black' else 'black'

	def AI_move(self, move):
		current_piece = move.piece
		square = self.get_square_from_pos(move.to_pos)
		current_piece.make_move(self, square, True, move)
		self.turn = 'white'
	
	def save_move(self, move):
		self.move_history.append(move)

	def undo_move(self):
		if not self.move_history:
			return
		
		move = self.move_history.pop()

		piece = move.piece

		from_square = self.get_square_from_pos(move.from_pos)
		to_square = self.get_square_from_pos(move.to_pos)

		# Undo promotion
		if move.promotion is not None:
			from_square.occupying_piece = piece
		else:
			from_square.occupying_piece = piece

		piece.pos = move.from_pos
		piece.x, piece.y = move.from_pos

		# Restore captured piece
		to_square.occupying_piece = move.captured

		# Restore has_moved
		piece.has_moved = move.piece_has_moved

		# Undo castling
		if move.is_castling:
			rook = move.rook
			rook.has_moved = False
			rook_from_square = self.get_square_from_pos(move.rook_from)
			rook_to_square = self.get_square_from_pos(move.rook_to)

			rook_from_square.occupying_piece = rook
			rook_to_square.occupying_piece = None

			rook.pos = move.rook_from
			rook.x, rook.y = move.rook_from

		self.turn = 'black' if self.turn == 'white' else 'white'



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

	def draw(self, display):
		if self.selected_piece is not None:
			self.get_square_from_pos(self.selected_piece.pos).highlight = True
			for square in self.selected_piece.get_valid_moves(self):
				square.highlight = True

		for square in self.squares:
			square.draw(display)