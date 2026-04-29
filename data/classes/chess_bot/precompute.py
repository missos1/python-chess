import random
from .constants import *

def precompute_zobrist_pieces():
    random.seed(42)
    table = []
    for _ in range(13):
        table.append([random.getrandbits(64) for _ in range(64)])
    return table

def precompute_zobrist_castling():
    random.seed(142)
    return [random.getrandbits(64) for _ in range(16)]

def precompute_zobrist_turn():
    random.seed(242)
    return random.getrandbits(64)

def precompute_zobrist_en_passant():
    random.seed(342)
    return [random.getrandbits(64) for _ in range(8)] 

ZOBRIST_PIECES = precompute_zobrist_pieces()
ZOBRIST_CASTLING = precompute_zobrist_castling()
ZOBRIST_TURN = precompute_zobrist_turn()
ZOBRIST_EN_PASSANT = precompute_zobrist_en_passant()

def precompute_north_rays():
    rays = []
    for square in range(64):
        ray, bit = 0, 1 << square
        while True:
            bit = (bit << 8) & BOARD_MASK  # Shift Up
            if not bit: break
            ray |= bit
        rays.append(ray)
    return rays

def precompute_east_rays():
    rays = []
    for square in range(64):
        ray, bit = 0, 1 << square
        while True:
            bit = (bit << 1) & NOT_A_FILE & BOARD_MASK # Shift Right, kill if it hits A-file
            if not bit: break
            ray |= bit
        rays.append(ray)
    return rays

def precompute_northeast_rays():
    rays = []
    for square in range(64):
        ray, bit = 0, 1 << square
        while True:
            bit = (bit << 9) & NOT_A_FILE & BOARD_MASK
            if not bit: break
            ray |= bit
        rays.append(ray)
    return rays

def precompute_northwest_rays():
    rays = []
    for square in range(64):
        ray, bit = 0, 1 << square
        while True:
            bit = (bit << 7) & NOT_H_FILE & BOARD_MASK
            if not bit: break
            ray |= bit
        rays.append(ray)
    return rays

def precompute_south_rays():
    rays = []
    for square in range(64):
        ray, bit = 0, 1 << square
        while True:
            bit = bit >> 8  # Shift Down
            if not bit: break
            ray |= bit
        rays.append(ray)
    return rays

def precompute_west_rays():
    rays = []
    for square in range(64):
        ray, bit = 0, 1 << square
        while True:
            bit = (bit >> 1) & NOT_H_FILE # Shift Left, kill if it hits H-file
            if not bit: break
            ray |= bit
        rays.append(ray)
    return rays

def precompute_southeast_rays():
    rays = []
    for square in range(64):
        ray, bit = 0, 1 << square
        while True:
            bit = (bit >> 7) & NOT_A_FILE
            if not bit: break
            ray |= bit
        rays.append(ray)
    return rays

def precompute_southwest_rays():
    rays = []
    for square in range(64):
        ray, bit = 0, 1 << square
        while True:
            bit = (bit >> 9) & NOT_H_FILE
            if not bit: break
            ray |= bit
        rays.append(ray)
    return rays

def precompute_white_pawn_captures():
    captures = []
    for square in range(64):
        pawn_bit = 1 << square
        # Shift NorthWest and NorthEast, masking out the files to prevent teleportation
        capture_board = ((pawn_bit << 7) & NOT_H_FILE) | ((pawn_bit << 9) & NOT_A_FILE)
        captures.append(capture_board)
    return captures

def precompute_black_pawn_captures():
    captures = []
    for square in range(64):
        pawn_bit = 1 << square
        # Shift SouthEast and SouthWest
        capture_board = ((pawn_bit >> 7) & NOT_A_FILE) | ((pawn_bit >> 9) & NOT_H_FILE)
        captures.append(capture_board)
    return captures

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
        board &= BOARD_MASK
        moves.append(board)
    return moves

def precomputed_king_moves():
    moves = []
    for square in range(64):
        king = 1 << square
        board = 0
        board |= (king & NOT_A_FILE) << 7 # Move 1 up, 1 left
        board |= king << 8 # Move 1 up
        board |= (king & NOT_H_FILE) << 9 # Move 1 up, 1 right
        board |= (king & NOT_A_FILE) >> 1 # Move 1 left
        board |= (king & NOT_H_FILE) << 1 # Move 1 right
        board |= (king & NOT_A_FILE) >> 9 # Move 1 down, 1 left
        board |= king >> 8 # Move 1 down
        board |= (king & NOT_H_FILE) >> 7 # Move 1 down, 1 right
        board &= BOARD_MASK
        moves.append(board)
    return moves

# Rays for sliding pieces (rook, bishop, queen) - indexed by source square and direction
NORTH_RAYS = precompute_north_rays()
EAST_RAYS = precompute_east_rays()
NORTHEAST_RAYS = precompute_northeast_rays()
NORTHWEST_RAYS = precompute_northwest_rays()
SOUTH_RAYS = precompute_south_rays()
WEST_RAYS = precompute_west_rays()
SOUTHEAST_RAYS = precompute_southeast_rays()
SOUTHWEST_RAYS = precompute_southwest_rays()

KNIGHT_MOVES = precomputed_knight_moves()
KING_MOVES = precomputed_king_moves()
WHITE_PAWN_CAPTURES = precompute_white_pawn_captures()
BLACK_PAWN_CAPTURES = precompute_black_pawn_captures()