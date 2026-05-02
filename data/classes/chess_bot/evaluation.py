def evaluate(state):
    score = 0

    # ✅ FIX: dùng data có sẵn trong state
    pieces = state.piece_values

    values = {
        'P': 100, 'N': 320, 'B': 330,
        'R': 500, 'Q': 900, 'K': 20000
    }

    pawn_table = [
         0,  5,  5,  0,  5, 10, 50,  0,
         0, 10, -5,  0,  5, 10, 50,  0,
         0, 10,-10, 20, 25, 30, 50,  0,
         0,-20,  0, 20, 25, 30, 50,  0,
         0, 10, 10, 20, 25, 30, 50,  0,
         0, 10, 10, 20, 25, 30, 50,  0,
         0, 10, 10,  0,  0,  0, 50,  0,
         0,  5,  5,  0,  5, 10, 50,  0
    ]

    for i, piece in enumerate(pieces):
        if piece is None:
            continue

        base_value = values.get(piece.upper(), 0)

        # material
        if piece.isupper():
            score += base_value
        else:
            score -= base_value

        # position pawn
        if piece.upper() == 'P':
            if piece.isupper():
                score += pawn_table[i]
            else:
                score -= pawn_table[63 - i]

        # center control
        row = i // 8
        col = i % 8
        if 2 <= row <= 5 and 2 <= col <= 5:
            if piece.isupper():
                score += 15
            else:
                score -= 15

    # mobility
    white_moves = len(state.get_strictly_legal_moves('white'))
    black_moves = len(state.get_strictly_legal_moves('black'))

    score += (white_moves - black_moves) * 5

    return score