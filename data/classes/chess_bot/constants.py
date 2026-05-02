# Colors
WHITE = 'white'
BLACK = 'black'

W_PAWN   = 'P'
W_KNIGHT = 'N'
W_BISHOP = 'B'
W_ROOK   = 'R'
W_QUEEN  = 'Q'
W_KING   = 'K'

B_PAWN   = 'p'
B_KNIGHT = 'n'
B_BISHOP = 'b'
B_ROOK   = 'r'
B_QUEEN  = 'q'
B_KING   = 'k'

W_PIECES = 'white_pieces'
B_PIECES = 'black_pieces'
OCCUPIED = 'occupied_squares'

# Constants for the exact squares that must be empty
W_KS_EMPTY = (1 << 5) | (1 << 6)                # F1, G1
W_QS_EMPTY = (1 << 1) | (1 << 2) | (1 << 3)     # B1, C1, D1
B_KS_EMPTY = (1 << 61) | (1 << 62)              # F8, G8
B_QS_EMPTY = (1 << 57) | (1 << 58) | (1 << 59)  # B8, C8, D8

# Castling Rights Bits (4 bit flag: 1111)
WK_RIGHT = 8  # 1000
WQ_RIGHT = 4  # 0100
BK_RIGHT = 2  # 0010
BQ_RIGHT = 1  # 0001

# Move Flags
FLAG_QUIET = 0
FLAG_CAPTURE = 1
FLAG_CASTLE_KS = 2
FLAG_CASTLE_QS = 3
FLAG_PROMOTION = 4
FLAG_DOUBLE_PAWN = 5
FLAG_EN_PASSANT = 6

NOT_A_FILE  = 0xFEFEFEFEFEFEFEFE  # A-file bits are 0, everywhere else is 1
NOT_AB_FILE = 0xFCFCFCFCFCFCFCFC  # A and B files are 0
NOT_H_FILE  = 0x7F7F7F7F7F7F7F7F  # H-file bits are 0
NOT_GH_FILE = 0x3F3F3F3F3F3F3F3F  # G and H files are 0
BOARD_MASK = 0xFFFFFFFFFFFFFFFF

# depth
DEPTH = 2