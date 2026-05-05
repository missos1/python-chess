# Colors
WHITE = 'white'
BLACK = 'black'

W_PAWN   = 1
W_KNIGHT = 2
W_BISHOP = 3
W_ROOK   = 4
W_QUEEN  = 5
W_KING   = 6

B_PAWN   = 7
B_KNIGHT = 8
B_BISHOP = 9
B_ROOK   = 10
B_QUEEN  = 11
B_KING   = 12

W_PIECES = 13
B_PIECES = 14
OCCUPIED = 15

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

# --- PIECE SQUARE TABLES (White's Perspective) ---
# Note: The evaluation function will automatically mirror these for Black!

# PAWNS: Encourage controlling the center and pushing toward promotion.
PAWN_PST = [
    # Rank 1 
     0,  0,  0,  0,  0,  0,  0,  0, 
    # Rank 2
     5, 10, 10,-20,-20, 10, 10,  5, 
    # Rank 3
     5, -5,-10,  0,  0,-10, -5,  5, 
    # Rank 4
     0,  0,  0, 20, 20,  0,  0,  0, 
    # Rank 5
     5,  5, 10, 25, 25, 10,  5,  5, 
    # Rank 6
    10, 10, 20, 30, 30, 20, 10, 10, 
    # Rank 7
    50, 50, 50, 50, 50, 50, 50, 50, 
    # Rank 8 (Indices 56-63)
     0,  0,  0,  0,  0,  0,  0,  0  
]

# KNIGHTS: Heavily punish the edges and corners, reward the dead center.
# Tweaked slightly downward so knights don't sacrifice themselves just to stand in the center.
KNIGHT_PST = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 10, 10, 10,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -30,  0, 15, 15, 15, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

# BISHOPS: Reward controlling the long diagonals and staying active.
BISHOP_PST = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

# ROOKS: Huge bonus for reaching the 7th rank (attacking enemy pawns). Minor centralization.
ROOK_PST = [
     0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     5, 10, 10, 10, 10, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

# QUEENS: Very slight positional bonuses to prevent early queen blunders.
QUEEN_PST = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -10,  5,  5,  5,  5,  5,  0,-10,
      0,  0,  5,  5,  5,  5,  0, -5,
     -5,  0,  5,  5,  5,  5,  0, -5,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

# KING (MIDDLEGAME): Heavy bonuses for castling squares (C1, G1). Punish moving out early.
KING_PST = [
     20, 30, 10,  0,  0, 10, 30, 20,  # Huge bonus for C1 (2) and G1 (6)
     20, 20,  0,  0,  0,  0, 20, 20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30
]

# --- PIECE IDs (For the 1D Hybrid piece_array) ---
# These are just simple integer IDs so the engine can instantly identify pieces.
EMPTY = 0


# --- PIECE POINT VALUES (For Evaluation & MVV-LVA Sorter) ---
PIECE_POINT_VALUES = (
    0,      # 0: EMPTY
    100,    # 1: W_PAWN
    280,    # 2: W_KNIGHT
    320,    # 3: W_BISHOP
    479,    # 4: W_ROOK
    929,    # 5: W_QUEEN
    60000,  # 6: W_KING
    100,    # 7: B_PAWN
    280,    # 8: B_KNIGHT
    320,    # 9: B_BISHOP
    479,    # 10: B_ROOK
    929,    # 11: B_QUEEN
    60000   # 12: B_KING
)

# Dummy table for EMPTY squares (Index 0)
EMPTY_PST = [0] * 64

# Replace PST_LOOKUP dictionary with a Tuple
PST_LOOKUP = (
    EMPTY_PST,   # 0: EMPTY
    PAWN_PST,    # 1: W_PAWN
    KNIGHT_PST,  # 2: W_KNIGHT
    BISHOP_PST,  # 3: W_BISHOP
    ROOK_PST,    # 4: W_ROOK
    QUEEN_PST,   # 5: W_QUEEN
    KING_PST,    # 6: W_KING
    PAWN_PST,    # 7: B_PAWN
    KNIGHT_PST,  # 8: B_KNIGHT
    BISHOP_PST,  # 9: B_BISHOP
    ROOK_PST,    # 10: B_ROOK
    QUEEN_PST,   # 11: B_QUEEN
    KING_PST     # 12: B_KING
)

MAX_TT_SIZE = 4000000  # Maximum number of entries in the transposition table before clearing (Reduced from 4 million to save memory)
# It never got so large in testing, but this is a safeguard against memory bloat in long games or repeated positions.