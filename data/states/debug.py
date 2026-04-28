from data.classes.chess_bot.constants import *
from data.classes.chess_bot.move_gens import *

def bitboard_visualize(bitboards):
        piece_type = input("Enter piece type to visualize moves (P/N/B/R/Q/K): ")
        piece_map = {
            'P': (W_PAWN, get_pawns_moves, WHITE),
            'N': (W_KNIGHT, get_knights_moves, WHITE),
            'B': (W_BISHOP, get_bishops_moves, WHITE),
            'R': (W_ROOK, get_rooks_moves, WHITE),
            'Q': (W_QUEEN, get_queens_moves, WHITE),
            'K': (W_KING, get_king_moves, WHITE, 0),  
            'p': (B_PAWN, get_pawns_moves, BLACK),
            'n': (B_KNIGHT, get_knights_moves, BLACK),
            'b': (B_BISHOP, get_bishops_moves, BLACK),
            'r': (B_ROOK, get_rooks_moves, BLACK),
            'q': (B_QUEEN, get_queens_moves, BLACK),
            'k': (B_KING, get_king_moves, BLACK, 0)
        }
        test_moves = bitboards[piece_map[piece_type][0]]
        
        flag_strings= {
            FLAG_QUIET: "Quiet",
            FLAG_CAPTURE: "Capture",
            FLAG_CASTLE_KS: "Castle Kingside",
            FLAG_CASTLE_QS: "Castle Queenside",
            FLAG_PROMOTION: "Promotion",
            FLAG_DOUBLE_PAWN: "Double Pawn Push"
        }
        squares_string = {
            0: "A1", 1: "B1", 2: "C1", 3: "D1", 4: "E1", 5: "F1", 6: "G1", 7: "H1",
            8: "A2", 9: "B2", 10: "C2", 11: "D2", 12: "E2", 13: "F2", 14: "G2", 15: "H2",
            16: "A3", 17: "B3", 18: "C3", 19: "D3", 20: "E3", 21: "F3", 22: "G3", 23: "H3",
            24: "A4", 25: "B4", 26: "C4", 27: "D4", 28: "E4", 29: "F4", 30: "G4", 31: "H4",
            32: "A5", 33: "B5", 34: "C5", 35: "D5", 36: "E5", 37: "F5", 38: "G5", 39: "H5",
            40: "A6", 41: "B6", 42: "C6", 43: "D6", 44: "E6", 45: "F6", 46: "G6", 47: "H6",
            48: "A7", 49: "B7", 50: "C7", 51: "D7", 52: "E7", 53: "F7", 54: "G7", 55: "H7",
            56: "A8", 57: "B8", 58: "C8", 59: "D8", 60:"E8",61:"F8",62:"G8",63:"H8"
        }
        
        if piece_type not in piece_map:
            print("Invalid piece type. Please enter one of P/N/B/R/Q/K (uppercase for white, lowercase for black).")
            return
        if piece_type != 'K' and piece_type != 'k':
            for move in piece_map[piece_type][1](bitboards, piece_map[piece_type][2],):
                print(f"Move from {squares_string[move[0]]} to {squares_string[move[1]]} with flag {flag_strings[move[2]]}")
                test_moves |= (1 << move[1])
        else:
            for move in piece_map[piece_type][1](bitboards, piece_map[piece_type][2], 15):
                print(f"Move from {squares_string[move[0]]} to {squares_string[move[1]]} with flag {flag_strings[move[2]]}")
                test_moves |= (1 << move[1])
        print_bitboards(test_moves)

# debug function to visualize bitboards in the console
def print_bitboards(bitboard):
    print("\n  A B C D E F G H")
    print("  ---------------")
    
    for rank in range(7, -1, -1):
        row_string = f"{rank + 1}|"
        for file in range(8):
            square_index = (rank * 8) + file
                
            # check if the bit at this index is 1
            # do this by creating a temporary board with a 1 at the target square,
            # using Bitwise AND to see if they overlap.
            if bitboard & (1 << square_index):
                row_string += "1 "  # Piece exists
            else:
                row_string += ". "  # Empty square
                    
        print(row_string)
            
    print("  ---------------\n")