pieceScore = {
    "K": 0,
    "Q": 9,
    "R": 5,
    "B": 3,
    "N": 3,
    "P": 1
}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2   # độ sâu minimax, có thể tăng lên 3 nếu máy chạy ổn


def score_board(gs):
    """
    Tính điểm bàn cờ:
    + điểm dương -> trắng lợi
    + điểm âm   -> đen lợi
    """
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE   # tới lượt trắng mà bị chiếu bí -> trắng thua
        else:
            return CHECKMATE    # tới lượt đen mà bị chiếu bí -> đen thua

    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for piece in row:
            if piece == "--":
                continue

            value = pieceScore[piece[1]]

            if piece[0] == "w":
                score += value
            else:
                score -= value

    return score


def find_best_move(gs, validMoves):
    """
    Hàm gọi từ main.py để AI chọn nước đi tốt nhất.
    """
    bestMove = None

    if gs.whiteToMove:
        bestScore = -CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            score = minimax(gs, DEPTH - 1, False)
            gs.undo_move()

            if score > bestScore:
                bestScore = score
                bestMove = move
    else:
        bestScore = CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            score = minimax(gs, DEPTH - 1, True)
            gs.undo_move()

            if score < bestScore:
                bestScore = score
                bestMove = move

    return bestMove


def minimax(gs, depth, whiteToMove):
    """
    Thuật toán Minimax:
    - whiteToMove = True  -> lượt tối đa hóa điểm
    - whiteToMove = False -> lượt tối thiểu hóa điểm
    """
    if depth == 0:
        return score_board(gs)

    validMoves = gs.get_valid_moves()

    # nếu không còn nước đi thì score_board sẽ xử lý checkmate/stalemate
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            score = minimax(gs, depth - 1, False)
            gs.undo_move()
            if score > maxScore:
                maxScore = score
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            score = minimax(gs, depth - 1, True)
            gs.undo_move()
            if score < minScore:
                minScore = score
        return minScore