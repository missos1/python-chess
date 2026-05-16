# Colors
WHITE = 'white'
BLACK = 'black'

# don't use float("inf") because for null move pruning 
# we need to add 1 to the score, and float("inf") + 1 
# is still float("inf"), which breaks the logic.
INFINITY = 1000000

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

# Transposition Table Flags
TT_EXACT = 0
TT_UPPER_BOUND = 1
TT_LOWER_BOUND = 2

NOT_A_FILE  = 0xFEFEFEFEFEFEFEFE  # A-file bits are 0, everywhere else is 1
NOT_AB_FILE = 0xFCFCFCFCFCFCFCFC  # A and B files are 0
NOT_H_FILE  = 0x7F7F7F7F7F7F7F7F  # H-file bits are 0
NOT_GH_FILE = 0x3F3F3F3F3F3F3F3F  # G and H files are 0
BOARD_MASK = 0xFFFFFFFFFFFFFFFF

# --- PIECE SQUARE TABLES (White's Perspective) ---
# Note: The evaluation function will automatically mirror these for Black!

# PAWNS (OPENING & MIDDLEGAME)
PAWN_PST_MIDDLEGAME = [
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

# PAWNS (ENDGAME)
PAWN_PST_ENDGAME = [
    # Rank 1
     0,  0,  0,  0,  0,  0,  0,  0,
    # Rank 2
     5, 10, 10,  0,  0, 10, 10,  5,
    # Rank 3
    10, 10, 15, 20, 20, 15, 10, 10,
    # Rank 4
    15, 15, 20, 25, 25, 20, 15, 15,
    # Rank 5
    20, 20, 25, 30, 30, 25, 20, 20,
    # Rank 6
    30, 30, 40, 50, 50, 40, 30, 30,
    # Rank 7
    60, 60, 60, 60, 60, 60, 60, 60,
    # Rank 8 (Indices 56-63)
     0,  0,  0,  0,  0,  0,  0,  0
]

# KNIGHTS (OPENING & MIDDLEGAME)
KNIGHT_PST_MIDDLEGAME = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 10, 10, 10,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -30,  0, 15, 15, 15, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

# KNIGHTS (ENDGAME)
KNIGHT_PST_ENDGAME = [
    -40,-30,-25,-25,-25,-25,-30,-40,
    -30,-15,  0,  5,  5,  0,-15,-30,
    -25,  0, 10, 10, 10, 10,  0,-25,
    -25,  5, 10, 15, 15, 10,  5,-25,
    -25,  5, 10, 15, 15, 10,  5,-25,
    -25,  0, 10, 10, 10, 10,  0,-25,
    -30,-15,  0,  5,  5,  0,-15,-30,
    -40,-30,-25,-25,-25,-25,-30,-40
]

# BISHOPS (OPENING & MIDDLEGAME)
BISHOP_PST_MIDDLEGAME = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

# BISHOPS (ENDGAME)
BISHOP_PST_ENDGAME = [
    -15, -5, -5, -5, -5, -5, -5,-15,
     -5, 10, 10, 10, 10, 10, 10, -5,
     -5, 10, 15, 15, 15, 15, 10, -5,
     -5, 10, 15, 20, 20, 15, 10, -5,
     -5, 10, 15, 20, 20, 15, 10, -5,
     -5, 10, 15, 15, 15, 15, 10, -5,
     -5, 10, 10, 10, 10, 10, 10, -5,
    -15, -5, -5, -5, -5, -5, -5,-15
]

# ROOKS (OPENING & MIDDLEGAME)
ROOK_PST_MIDDLEGAME = [
     0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     5, 10, 10, 10, 10, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

# ROOKS (ENDGAME)
ROOK_PST_ENDGAME = [
     0,  0,  5, 10, 10,  5,  0,  0,
     0,  5,  5, 10, 10,  5,  5,  0,
     0,  5,  5, 10, 10,  5,  5,  0,
     0,  5,  5, 10, 10,  5,  5,  0,
     0,  5,  5, 10, 10,  5,  5,  0,
     5, 10, 10, 15, 15, 10, 10,  5,
    10, 15, 15, 20, 20, 15, 15, 10,
     5, 10, 10, 15, 15, 10, 10,  5
]


# QUEENS (OPENING & MIDDLEGAME)
QUEEN_PST_MIDDLEGAME = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -10,  5,  5,  5,  5,  5,  0,-10,
      0,  0,  5,  5,  5,  5,  0, -5,
     -5,  0,  5,  5,  5,  5,  0, -5,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

# QUEENS (ENDGAME)
QUEEN_PST_ENDGAME = [
    -10, -5, -5,  0,  0, -5, -5,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
     -5,  5, 10, 10, 10, 10,  5, -5,
      0,  5, 10, 15, 15, 10,  5,  0,
      0,  5, 10, 15, 15, 10,  5,  0,
     -5,  5, 10, 10, 10, 10,  5, -5,
     -5,  0,  5,  5,  5,  5,  0, -5,
    -10, -5, -5,  0,  0, -5, -5,-10
]

# KING (OPENING & MIDDLEGAME)
KING_PST_MIDDLEGAME = [
     20, 30, 10,  0,  0, 10, 30, 20,
     20, 20,  0,  0,  0,  0, 20, 20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30
]

# KING (ENDGAME)
KING_PST_ENDGAME = [
    -50,-30,-20,-10,-10,-20,-30,-50,
    -30,-10,  0, 10, 10,  0,-10,-30,
    -20,  0, 20, 30, 30, 20,  0,-20,
    -10, 10, 30, 40, 40, 30, 10,-10,
    -10, 10, 30, 40, 40, 30, 10,-10,
    -20,  0, 20, 30, 30, 20,  0,-20,
    -30,-10,  0, 10, 10,  0,-10,-30,
    -50,-30,-20,-10,-10,-20,-30,-50
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

PHASE_MATERIAL_PIECES = (
    W_KNIGHT, W_BISHOP, W_ROOK, W_QUEEN,
    B_KNIGHT, B_BISHOP, B_ROOK, B_QUEEN
)

# Tapered evaluation phase weights (opening -> endgame)
MAX_PHASE = 24
PHASE_PIECE_WEIGHTS = (
    0,  # EMPTY
    0,  # W_PAWN
    1,  # W_KNIGHT
    1,  # W_BISHOP
    2,  # W_ROOK
    4,  # W_QUEEN
    0,  # W_KING
    0,  # B_PAWN
    1,  # B_KNIGHT
    1,  # B_BISHOP
    2,  # B_ROOK
    4,  # B_QUEEN
    0   # B_KING
)

# Pawn structure evaluation weights
PAWN_DOUBLED_PENALTY = 10
PAWN_ISOLATED_PENALTY = 10
PAWN_CHAIN_BONUS = 10
PAWN_UNPROTECTED_PENALTY = 5
PAWN_PASSED_BONUS_BY_RANK = (
    0, 5, 10, 20, 35, 60, 100, 0
)

# Scale pawn structure impact by phase (Opening, Middlegame, Endgame)
PAWN_PHASE_MULTIPLIER_MG = 100
PAWN_PHASE_MULTIPLIER_EG = 120

PST_LOOKUP_MIDDLEGAME = (
    EMPTY_PST,             # 0: EMPTY
    PAWN_PST_MIDDLEGAME,    # 1: W_PAWN
    KNIGHT_PST_MIDDLEGAME,  # 2: W_KNIGHT
    BISHOP_PST_MIDDLEGAME,  # 3: W_BISHOP
    ROOK_PST_MIDDLEGAME,    # 4: W_ROOK
    QUEEN_PST_MIDDLEGAME,   # 5: W_QUEEN
    KING_PST_MIDDLEGAME,    # 6: W_KING
    PAWN_PST_MIDDLEGAME,    # 7: B_PAWN
    KNIGHT_PST_MIDDLEGAME,  # 8: B_KNIGHT
    BISHOP_PST_MIDDLEGAME,  # 9: B_BISHOP
    ROOK_PST_MIDDLEGAME,    # 10: B_ROOK
    QUEEN_PST_MIDDLEGAME,   # 11: B_QUEEN
    KING_PST_MIDDLEGAME     # 12: B_KING
)

PST_LOOKUP_ENDGAME = (
    EMPTY_PST,           # 0: EMPTY
    PAWN_PST_ENDGAME,     # 1: W_PAWN
    KNIGHT_PST_ENDGAME,   # 2: W_KNIGHT
    BISHOP_PST_ENDGAME,   # 3: W_BISHOP
    ROOK_PST_ENDGAME,     # 4: W_ROOK
    QUEEN_PST_ENDGAME,    # 5: W_QUEEN
    KING_PST_ENDGAME,     # 6: W_KING
    PAWN_PST_ENDGAME,     # 7: B_PAWN
    KNIGHT_PST_ENDGAME,   # 8: B_KNIGHT
    BISHOP_PST_ENDGAME,   # 9: B_BISHOP
    ROOK_PST_ENDGAME,     # 10: B_ROOK
    QUEEN_PST_ENDGAME,    # 11: B_QUEEN
    KING_PST_ENDGAME      # 12: B_KING
)

# Tapered evaluation uses midgame and endgame lookups only.
PST_LOOKUP_MG = PST_LOOKUP_MIDDLEGAME
PST_LOOKUP_EG = PST_LOOKUP_ENDGAME

# Default PST lookup used for move ordering and legacy code
PST_LOOKUP = PST_LOOKUP_MIDDLEGAME

MAX_TT_SIZE = 4000000  # Maximum number of entries in the transposition table before clearing (Reduced from 4 million to save memory)
# It never got so large in testing, but this is a safeguard against memory bloat in long games or repeated positions.

# Syzygy tablebase defaults
SYZYGY_REL_PATH = "data/syzygy"
SYZYGY_MAX_PIECES = 5