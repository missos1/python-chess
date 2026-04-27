from data.classes.chess_bot.evaluate import Evaluate

def get_piece_value(piece):
    """Return material value of a piece for move ordering."""
    if piece is None:
        return 0
    
    piece_type = piece.notation
    if piece_type == ' ':
        return 1
    elif piece_type == 'N':
        return 3
    elif piece_type == 'B':
        return 3
    elif piece_type == 'R':
        return 5
    elif piece_type == 'Q':
        return 9
    return 0


def order_moves(board, legal_moves, evaluator=None):
    """Score and sort moves for alpha-beta pruning efficiency.
    
    Scoring heuristic:
    - Captures: value_of_captured_piece * 10 - recapture_penalty
    - Promotions: +8 (pawn promotion is excellent)
    - Checks: +1 (forcing moves)
    - Quiet moves: 0
    
    Args:
        board: Board object.
        legal_moves: List of (piece, move_square) tuples.
        evaluator: Evaluate object (optional).
    
    Returns:
        List of (piece, move_square) tuples sorted by score (descending).
    """
    if evaluator is None:
        evaluator = Evaluate(board)
    
    scored_moves = []
    
    for piece, move_square in legal_moves:
        score = 0
        captured_piece = move_square.occupying_piece
        
        # 1. Capture scoring
        if captured_piece is not None:
            victim_value = get_piece_value(captured_piece)
            attacker_value = get_piece_value(piece)
            
            score += victim_value * 10 - attacker_value
        
        # 2. Promotion scoring
        if piece.notation == ' ' and (move_square.y == 0 or move_square.y == 7):
            score += 8
        
        # 3. Avoid moving to square that opponent team control
        is_capturing, min_recapture_value = board.is_recapturable(piece, move_square)
        if is_capturing and attacker_value > min_recapture_value:
            score -= get_piece_value(piece)
            
        scored_moves.append((piece, move_square, score))
        
    
    # Sort by score descending
    scored_moves.sort(key=lambda x: x[2], reverse=True)
    
    # Return without scores
    return [(piece, move_square) for piece, move_square, score in scored_moves]


def alpha_beta_negamax(board, alpha, beta, depth, evaluator=None):
    """Alpha-beta minimax search with make/unmake move cycle.
    
    Args:
        board: Board object with get_all_valid_moves() and capture_move_state().
        alpha: Alpha cutoff value.
        beta: Beta cutoff value.
        depth: Search depth (0 = leaf node, evaluate position).
        evaluator: Evaluate object. Created if None.
    
    Returns:
        Evaluation score from current position.
    """
    if evaluator is None:
        evaluator = Evaluate(board)
    
    # Leaf node: evaluate position
    if depth == 0:
        return evaluator.evaluate()
    
    # Get all legal moves for current side
    legal_moves = board.get_all_valid_moves()
    
    # Order moves for better alpha-beta pruning
    legal_moves = order_moves(board, legal_moves, evaluator)
    
    # Terminal node: checkmate or stalemate
    if len(legal_moves) == 0:
        if board.is_in_check():
            # Checkmate: losing side to move
            return -10000 - depth  # Penalize distant mates
        else:
            # Stalemate: draw
            return 0
    
    # Alpha-beta minimax loop: make, recurse, unmake for each move
    for piece, move_square in legal_moves:
        # 1. Capture board state before move
        move_state = board.capture_move_state(piece, move_square)
        
        # 2. Execute move
        piece.move(board, move_square, force=True)
        
        # 3. Recurse (negate score for opposite side)
        value = -alpha_beta_negamax(board, -beta, -alpha, depth - 1, evaluator)
        
        # 4. Unmake move (restore board to state before move)
        piece.unmake_move(board, move_state)
        
        # 5. Alpha-beta pruning
        alpha = max(alpha, value)
        if alpha >= beta:
            break  # Beta cutoff: prune remaining moves
    
    return alpha
        

def find_best_move(board, depth, evaluator=None):
    """Find the best move for the current position using alpha-beta negamax search.
    
    Args:
        board: Board object.
        depth: Search depth.
        evaluator: Evaluate object (optional).
    
    Returns:
        Tuple (piece, move_square) of the best move, or None if no legal moves.
    """
    if evaluator is None:
        evaluator = Evaluate(board)
    
    legal_moves = board.get_all_valid_moves()
    if not legal_moves:
        return None
    
    legal_moves = order_moves(board, legal_moves, evaluator)
    
    best_move = None
    best_score = -float('inf')
    
    for piece, move_square in legal_moves:
        move_state = board.capture_move_state(piece, move_square)
        piece.move(board, move_square, force=True)
        
        score = -alpha_beta_negamax(board, -1000000, 1000000, depth - 1, evaluator)
        
        piece.unmake_move(board, move_state)
        
        if score > best_score:
            best_score = score
            best_move = (piece, move_square)
    
    return best_move
    