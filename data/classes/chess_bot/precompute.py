NOT_A_FILE  = 0xFEFEFEFEFEFEFEFE  # A-file bits are 0, everywhere else is 1
NOT_AB_FILE = 0xFCFCFCFCFCFCFCFC  # A and B files are 0
NOT_H_FILE  = 0x7F7F7F7F7F7F7F7F  # H-file bits are 0
NOT_GH_FILE = 0x3F3F3F3F3F3F3F3F  # G and H files are 0

def precomputed_knight_moves():
    moves = []
    for square in range(64):
        knight = 1 << square
        board = 0
        board |= (knight & NOT_A_FILE) << 15 # Move 2 up, 1 left
        board |= (knight & NOT_H_FILE) << 17 # Move 2 up, 1 right
        board |= (knight & NOT_AB_FILE) << 6 # Move 1 up, 2 left
        board |= (knight & NOT_GH_FILE) << 10 # Move 1 up, 2 right
        board |= (knight & NOT_A_FILE) >> 17 # Move 2 down, 1 left
        board |= (knight & NOT_H_FILE) >> 15 # Move 2 down, 1 right
        board |= (knight & NOT_AB_FILE) >> 10 # Move 1 down, 2 left
        board |= (knight & NOT_GH_FILE) >> 6 # Move 1 down, 2 right
        moves.append(board)
    return moves

def precomputed_king_moves():
    moves = []
    return moves

KNIGHT_MOVES = precomputed_knight_moves()
KING_MOVES = precomputed_king_moves()

