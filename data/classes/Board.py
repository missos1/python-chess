import pygame

from data.classes.chess_bot.constants import *

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


	def handle_click(self, mx, my, is_flipped=False):
		x = mx // self.square_width if not is_flipped else 7 - (mx // self.square_width)
		y = my // self.square_height if not is_flipped else 7 - (my // self.square_height)
		if x < 0 or x > 7 or y < 0 or y > 7:
			return
		clicked_square = self.get_square_from_pos((x, y))

		if self.selected_piece is None:
			if clicked_square.occupying_piece is not None:
				if clicked_square.occupying_piece.color == self.turn:
					self.selected_piece = clicked_square.occupying_piece

		else:
			moving_piece = self.selected_piece
			old_y = self.selected_piece.y
			if moving_piece.move(self, clicked_square):
				if moving_piece.notation == ' ' and abs(moving_piece.y - old_y) == 2:
					self.en_passant_target = (moving_piece.x, (moving_piece.y + old_y) // 2)
				else:
					self.en_passant_target = None
				self.turn = 'white' if self.turn == 'black' else 'black'
			elif clicked_square.occupying_piece is not None:
				if clicked_square.occupying_piece.color == self.turn:
					self.selected_piece = clicked_square.occupying_piece



	def apply_view(self, is_flipped):
		self.is_flipped = is_flipped
		for square in self.squares:
			square.set_view(self.is_flipped)


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
		for piece in [i.occupying_piece for i in self.squares]:
			if piece != None and piece.color == color:
				if piece.get_valid_moves(self) != []:
					return False

		return self.is_in_check(color)


	def get_square_from_pos(self, pos):
		for square in self.squares:
			if (square.x, square.y) == (pos[0], pos[1]):
				return square


	def get_piece_from_pos(self, pos):
		return self.get_square_from_pos(pos).occupying_piece


	def get_bitboards(self) -> list:
		bitboards = [0] * 16

		for square in self.squares:
			piece = square.occupying_piece
			if piece is not None:
				# Pygame y=0 is Rank 8, y=7 is Rank 1. 
				# Invert y so index 0 is A1 and index 63 is H8 (Little Edian Rank File mapping).
				lerf_index = (7 - square.y) * 8 + square.x

				# Safely get the piece type by its class name
				piece_type = piece.__class__.__name__
				
				# Map the class name
				symbol_map = {
					'Pawn': W_PAWN, 'Knight': W_KNIGHT, 'Bishop': W_BISHOP, 
					'Rook': W_ROOK, 'Queen': W_QUEEN, 'King': W_KING
				}

				piece_index = symbol_map.get(piece_type)
 
				# If the piece is black, just add 6 to the index!
				if piece.color == BLACK: # Make sure BLACK is defined, usually 'black' in Pygame
					piece_index = piece_index + 6

				# Stamp this piece onto its specific bitboard using Bitwise OR
				# bitboards is now a List, so this is an instant O(1) memory pointer update
				bitboards[piece_index] |= (1 << lerf_index)

		# Generate the summary bitboards for quick AI lookups
		bitboards[W_PIECES] = (bitboards[W_PAWN] | bitboards[W_KNIGHT] | bitboards[W_BISHOP] | 
									 bitboards[W_ROOK] | bitboards[W_QUEEN] | bitboards[W_KING])
		
		bitboards[B_PIECES] = (bitboards[B_PAWN] | bitboards[B_KNIGHT] | bitboards[B_BISHOP] | 
									 bitboards[B_ROOK] | bitboards[B_QUEEN] | bitboards[B_KING])
		
		bitboards[OCCUPIED] = bitboards[W_PIECES] |bitboards[B_PIECES]

		return bitboards

	# This function will be for the evaluation function to quickly access piece values without bitboard manipulation during capturing or evaluation
 	# It will be a 64-length array with the value of the piece on each square, or 0 if it's empty
	# TODO: Implement piece values
	def get_pieces_array(self):
		pass

	def draw(self, display):
		if self.selected_piece is not None:
			self.get_square_from_pos(self.selected_piece.pos).highlight = True
			for square in self.selected_piece.get_valid_moves(self):
				square.highlight = True

		for square in self.squares:
			square.draw(display)
   
	@property
	def castling_rights(self):
		rights = 0
		
		# Determine White's rights (Rank 1 -> y = 7 in Pygame coords)
		white_king = self.get_piece_from_pos((4, 7))
		if white_king is not None and white_king.notation == 'K' and not white_king.has_moved:
			# Kingside Rook at H1 (7, 7)
			w_kingside_rook = self.get_piece_from_pos((7, 7))
			if w_kingside_rook is not None and w_kingside_rook.notation == 'R' and not w_kingside_rook.has_moved:
				rights |= WK_RIGHT  # 8
				
			# Queenside Rook at A1 (0, 7)
			w_queenside_rook = self.get_piece_from_pos((0, 7))
			if w_queenside_rook is not None and w_queenside_rook.notation == 'R' and not w_queenside_rook.has_moved:
				rights |= WQ_RIGHT  # 4
				
		# Determine Black's rights (Rank 8 -> y = 0 in Pygame coords)
		black_king = self.get_piece_from_pos((4, 0))
		if black_king is not None and black_king.notation == 'K' and not black_king.has_moved:
			# Kingside Rook at H8 (7, 0)
			b_kingside_rook = self.get_piece_from_pos((7, 0))
			if b_kingside_rook is not None and b_kingside_rook.notation == 'R' and not b_kingside_rook.has_moved:
				rights |= BK_RIGHT  # 2
				
			# Queenside Rook at A8 (0, 0)
			b_queenside_rook = self.get_piece_from_pos((0, 0))
			if b_queenside_rook is not None and b_queenside_rook.notation == 'R' and not b_queenside_rook.has_moved:
				rights |= BQ_RIGHT  # 1
				
		return rights