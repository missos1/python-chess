import pygame

class Piece:
	def __init__(self, pos, color, board):
		self.pos = pos
		self.x = pos[0]
		self.y = pos[1]
		self.color = color
		self.has_moved = False

	def move(self, board, square, force=False):

		for i in board.squares:
			i.highlight = False

		if square in self.get_valid_moves(board) or force:
			prev_square = board.get_square_from_pos(self.pos)

			if self.notation == ' ' and board.en_passant_target is not None:
				if square.pos == board.en_passant_target and square.occupying_piece is None and prev_square.x != square.x:
					capture_y = square.y + (1 if self.color == 'white' else -1)
					if 0 <= capture_y < 8:
						captured_square = board.get_square_from_pos((square.x, capture_y))
						captured_piece = captured_square.occupying_piece
						if captured_piece is not None and captured_piece.notation == ' ' and captured_piece.color != self.color:
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
			if self.notation == ' ':
				if self.y == 0 or self.y == 7:
					from data.classes.pieces.Queen import Queen
					square.occupying_piece = Queen(
						(self.x, self.y),
						self.color,
						board
					)

			# Move rook if king castles
			if self.notation == 'K':
				if prev_square.x - self.x == 2:
					rook = board.get_piece_from_pos((0, self.y))
					rook.move(board, board.get_square_from_pos((3, self.y)), force=True)
				elif prev_square.x - self.x == -2:
					rook = board.get_piece_from_pos((7, self.y))
					rook.move(board, board.get_square_from_pos((5, self.y)), force=True)

			return True
		else:
			board.selected_piece = None
			return False


	def unmake_move(self, board, move_state):
		"""Reverse all state changes from a move.
		
		Used by search algorithms to explore move trees via make/unmake cycles.
		Restores: piece position, has_moved flag, captures, en passant, promotion, castling.
		
		Args:
			board: The board object.
			move_state: Dict returned by board.capture_move_state() before the move.
		"""
		# Restore piece position
		self.pos = move_state['from_pos']
		self.x = move_state['from_pos'][0]
		self.y = move_state['from_pos'][1]
		
		# Restore has_moved flag (critical for castling/pawn legality)
		self.has_moved = move_state['piece_had_moved_before']
		
		# Restore source and destination squares
		from_square = board.get_square_from_pos(move_state['from_pos'])
		to_square = board.get_square_from_pos(move_state['to_pos'])
		
		# Remove piece from destination
		to_square.occupying_piece = None
		
		# Place piece back on source square
		from_square.occupying_piece = self
		
		# Restore captured piece (if any)
		if move_state['captured_piece'] is not None:
			captured_square = board.get_square_from_pos(move_state['captured_pos'])
			captured_square.occupying_piece = move_state['captured_piece']
		
		# Restore en passant target state
		board.en_passant_target = move_state['en_passant_target_before']
		
		# Handle promotion: replace promoted piece back with original pawn
		if move_state['is_promotion']:
			from_square.occupying_piece = self
		
		# Handle castling: recursively unmake rook's move
		if move_state['is_castling'] and move_state['rook_state'] is not None:
			rook_state = move_state['rook_state']
			rook = rook_state['rook']
			rook.unmake_move(board, {
				'piece': rook,
				'from_pos': rook_state['from_pos'],
				'to_pos': rook_state['to_pos'],
				'piece_had_moved_before': rook_state['rook_had_moved_before'],
				'captured_piece': None,
				'captured_pos': None,
				'en_passant_target_before': board.en_passant_target,
				'is_promotion': False,
				'is_castling': False,
				'rook_state': None
			})


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