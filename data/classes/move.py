class Move:
	def __init__(self, piece, from_pos, to_pos,
				 captured=None,
				 piece_has_moved=False,
				 is_castling=False,
				 rook=None, rook_from=None, rook_to=None,
				 promotion=None):
		
		self.piece = piece
		self.from_pos = from_pos
		self.to_pos = to_pos
		self.captured = captured
		
		self.piece_has_moved = piece_has_moved
		
		# Castling
		self.is_castling = is_castling
		self.rook = rook
		self.rook_from = rook_from
		self.rook_to = rook_to
		
		# Promotion
		self.promotion = promotion