import pygame

class Piece:
	def __init__(self, pos, color, board):
		self.pos = pos
		self.x = pos[0]
		self.y = pos[1]
		self.color = color
		self.has_moved = False

	def move(self, board, square, game_state, force=False):

		for i in board.squares:
			i.highlight = False

		print(f"Attempting move from {self.get_index_from_pos()} to {square.get_index_from_square()}")
		valid_moves = [move[:2] for move in game_state.get_strictly_legal_moves(board.turn)]
		for move in valid_moves:
			print(f"Valid move: {move}")
		if (self.get_index_from_pos(), square.get_index_from_square()) in valid_moves or force:
			board.selected_piece = None

			return True
		else:
			board.selected_piece = None
			return False

	def moving(self, board, square, force=False):
		for i in board.squares:
			i.highlight = False
		prev_square = board.get_square_from_pos(self.pos)

		# En passant capture
		if self.notation == ' ' and board.en_passant_target is not None:
			if square.pos == board.en_passant_target and square.occupying_piece is None and prev_square.x != square.x:
				capture_y = square.y + (1 if self.color == 'white' else -1)
				if 0 <= capture_y < 8:
					captured_square = board.get_square_from_pos((square.x, capture_y))
					if captured_square.occupying_piece is not None:
						captured_square.occupying_piece = None

		self.pos, self.x, self.y = square.pos, square.x, square.y

		prev_square.occupying_piece = None
		square.occupying_piece = self
		board.selected_piece = None
		self.has_moved = True

		board.en_passant_target = None
		if self.notation == ' ' and abs(prev_square.y - self.y) == 2:
			middle_y = (prev_square.y + self.y) // 2
			board.en_passant_target = (self.x, middle_y)

		# Pawn promotion
		if self.notation == ' ' and not force:
			if self.y == 0 or self.y == 7:
				from data.classes.pieces.Queen import Queen
				square.occupying_piece = Queen(
					(self.x, self.y),
					self.color,
					board
				)

		# Move rook if king castles
		if self.notation == 'K' and not force:
			if prev_square.x - self.x == 2:
				rook = board.get_piece_from_pos((0, self.y))
				rook.moving(board, board.get_square_from_pos((3, self.y)), force=True)
			elif prev_square.x - self.x == -2:
				rook = board.get_piece_from_pos((7, self.y))
				rook.moving(board, board.get_square_from_pos((5, self.y)), force=True)

	def get_moves(self, board):
		output = []
		for direction in self.get_possible_moves(board):
			for square in direction:
				if square.occupying_piece is not None:
					if square.occupying_piece.color == self.color:
						break
					else:
						output.append(square)
						break
				else:
					output.append(square)

		return output


	def get_valid_moves(self, board):
		output = []
		for square in self.get_moves(board):
			if not board.is_in_check(self.color, board_change=[self.pos, square.pos]):
				output.append(square)

		return output


	# True for all pieces except pawn
	def attacking_squares(self, board):
		return self.get_moves(board)
	
	def get_index_from_pos(self):
		return (7 - self.y) * 8 + self.x