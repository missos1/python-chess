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

# --- PIECE SQUARE TABLES (White's Perspective) ---
# Note: The evaluation function will automatically mirror these for Black!

# PAWNS: Encourage controlling the center and pushing toward promotion.
PAWN_PST = [
    # Rank 1 (Indices 0-7)
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

W_PAWN_VALUE = 1
W_KNIGHT_VALUE = 2
W_BISHOP_VALUE = 3
W_ROOK_VALUE = 4
W_QUEEN_VALUE = 5
W_KING_VALUE = 6

B_PAWN_VALUE = 7
B_KNIGHT_VALUE = 8
B_BISHOP_VALUE = 9
B_ROOK_VALUE = 10
B_QUEEN_VALUE = 11
B_KING_VALUE = 12


# --- PIECE POINT VALUES (For Evaluation & MVV-LVA Sorter) ---
# Scores are in "Centipawns" (100 points = 1 Pawn).
# Notice how Bishops (330) are valued slightly higher than Knights (320). 
# This teaches your Bot the "Bishop Pair" advantage!
PIECE_POINT_VALUES = {
    EMPTY: 0,
    
    W_PAWN_VALUE: 100,   
    B_PAWN_VALUE: 100,
    
    W_KNIGHT_VALUE: 320, 
    B_KNIGHT_VALUE: 320,
    
    W_BISHOP_VALUE: 330, 
    B_BISHOP_VALUE: 330,
    
    W_ROOK_VALUE: 500,   
    B_ROOK_VALUE: 500,
    
    W_QUEEN_VALUE: 900,  
    B_QUEEN_VALUE: 900,
    
    # The King is given an absurdly high value so the MVV-LVA sorter 
    # knows that capturing it (or checking it) is the ultimate priority.
    W_KING_VALUE: 20000, 
    B_KING_VALUE: 20000 
}

# The Master Lookup Dictionary (Allows instant O(1) access by piece ID)
PST_LOOKUP = {
    W_PAWN_VALUE: PAWN_PST,     B_PAWN_VALUE: PAWN_PST,
    W_KNIGHT_VALUE: KNIGHT_PST, B_KNIGHT_VALUE: KNIGHT_PST,
    W_BISHOP_VALUE: BISHOP_PST, B_BISHOP_VALUE: BISHOP_PST,
    W_ROOK_VALUE: ROOK_PST,     B_ROOK_VALUE: ROOK_PST,
    W_QUEEN_VALUE: QUEEN_PST,   B_QUEEN_VALUE: QUEEN_PST,
    W_KING_VALUE: KING_PST,     B_KING_VALUE: KING_PST
}

