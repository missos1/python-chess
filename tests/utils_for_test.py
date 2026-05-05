from data.classes.chess_bot.constants import *

def run_perft(state, depth, current_color):
    if depth == 0:
        return 1
    
    nodes = 0
    # USE STRICTLY LEGAL MOVES HERE just to prove the math works!
    legal_moves = state.get_strictly_legal_moves(current_color)
    enemy_color = BLACK if current_color == WHITE else WHITE
    
    for move in legal_moves:
        state.make_move(move)
        nodes += run_perft(state, depth - 1, enemy_color)
        state.undo_move(move)
        
    return nodes

def index_to_algebraic(index):
    # Get the file (a-h)
    file_char = chr((index % 8) + ord('a'))
    # Get the rank (1-8)
    rank_char = str((index // 8) + 1)
    return file_char + rank_char

def divide(state, depth, current_color, dictionary):
    print(f"go perft {depth}")
    
    if depth == 0:
        return
        
    total_nodes = 0
    legal_moves = state.get_strictly_legal_moves(current_color)
    enemy_color = BLACK if current_color == WHITE else WHITE
    
    for move in legal_moves:
        source, target, flag = move
        
        # 1. Make the top-level move
        state.make_move(move)
        
        # 2. Count all nodes branching off from here
        branch_nodes = run_perft(state, depth - 1, enemy_color)
        
        # 3. Undo the move
        state.undo_move(move)
        
        # 4. Format and print
        move_str = index_to_algebraic(source) + index_to_algebraic(target)
        
        # If it was a promotion, you might want to add the piece letter (e.g. e7e8q)
        if flag == FLAG_PROMOTION:
            move_str += "q" # Simplified for printing
            
        dictionary[move_str] = branch_nodes
        total_nodes += branch_nodes
        
    print(f"\nNodes searched: {total_nodes}")