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


	def is_in_check(self, color, board_change=None): # board_change = [(x1, y1), (x2, y2)]
     
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


	def get_bitboards(self):
		bitboards = {
			W_PAWN: 0, W_KNIGHT: 0, W_BISHOP: 0, W_ROOK: 0, W_QUEEN: 0, W_KING: 0,
			B_PAWN: 0, B_KNIGHT: 0, B_BISHOP: 0, B_ROOK: 0, B_QUEEN: 0, B_KING: 0,
			W_PIECES: 0, B_PIECES: 0, OCCUPIED: 0
		}

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
					'Pawn': 'P', 'Knight': 'N', 'Bishop': 'B', 
					'Rook': 'R', 'Queen': 'Q', 'King': 'K'
				}
				symbol = symbol_map.get(piece_type)
				
				# Convert to lowercase if the piece is black
				if piece.color == BLACK:
					symbol = symbol.lower()

				# Stamp this piece onto its specific bitboard using Bitwise OR
				# Example: 0001, shift by the lerf index 3 to 1000 and OR 0100 to get 1100
				bitboards[symbol] |= (1 << lerf_index)

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