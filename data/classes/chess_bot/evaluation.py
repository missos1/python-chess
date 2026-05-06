def evaluate(state):
    score = 0
    pieces = state.piece_values  # board 64 ô

    values = {
        'P': 100, 'N': 320, 'B': 330,
        'R': 500, 'Q': 900, 'K': 20000
    }

    # PIECE-SQUARE TABLES
    pawn_table = [
         0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
         5,  5, 10, 25, 25, 10,  5,  5,
         0,  0,  0, 20, 20,  0,  0,  0,
         5, -5,-10,  0,  0,-10, -5,  5,
         5, 10, 10,-20,-20, 10, 10,  5,
         0,  0,  0,  0,  0,  0,  0,  0
    ]

    knight_table = [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ]

    bishop_table = [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ]

    rook_table = [
         0,  0,  5, 10, 10,  5,  0,  0,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
         5, 10, 10, 10, 10, 10, 10,  5,
         0,  0,  0,  0,  0,  0,  0,  0
    ]

    queen_table = [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
         -5,  0,  5,  5,  5,  5,  0, -5,
          0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ]

    king_mid = [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
         20, 20,  0,  0,  0,  0, 20, 20,
         20, 30, 10,  0,  0, 10, 30, 20
    ]

    king_end = [
        -50,-40,-30,-20,-20,-30,-40,-50,
        -30,-20,-10,  0,  0,-10,-20,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-30,  0,  0,  0,  0,-30,-30,
        -50,-30,-30,-30,-30,-30,-30,-50
    ]

    # GAME PHASE
    total_material = 0
    for p in pieces:
        if p:
            total_material += values.get(p.upper(), 0)
    endgame = total_material < 2000


    # MAIN LOOP
    white_bishops = 0
    black_bishops = 0
    for i, piece in enumerate(pieces):
        if piece is None:
            continue
        is_white = piece.isupper()
        p = piece.upper()
        val = values[p]

        # MATERIAL
        score += val if is_white else -val

        # POSITION
        table = 0
        idx = i if is_white else 63 - i
        if p == 'P':
            table = pawn_table[idx]
        elif p == 'N':
            table = knight_table[idx]
        elif p == 'B':
            table = bishop_table[idx]
            if is_white:
                white_bishops += 1
            else:
                black_bishops += 1
        elif p == 'R':
            table = rook_table[idx]
        elif p == 'Q':
            table = queen_table[idx]
        elif p == 'K':
            table = king_end[idx] if endgame else king_mid[idx]
        score += table if is_white else -table

        # CENTER CONTROL
        row, col = i // 8, i % 8
        if 2 <= row <= 5 and 2 <= col <= 5:
            score += 10 if is_white else -10


    # BISHOP PAIR
    if white_bishops >= 2:
        score += 30
    if black_bishops >= 2:
        score -= 30

    # MOBILITY
    try:
        white_moves = len(state.get_strictly_legal_moves('white'))
        black_moves = len(state.get_strictly_legal_moves('black'))
        score += (white_moves - black_moves) * 3
    except:
        pass


    # KING SAFETY (simple)
    for i, piece in enumerate(pieces):
        if piece is None:
            continue

        if piece == 'K':
            row = i // 8
            if row < 2:
                score += 20  # an toàn
        elif piece == 'k':
            row = i // 8
            if row > 5:
                score -= 20
    return score