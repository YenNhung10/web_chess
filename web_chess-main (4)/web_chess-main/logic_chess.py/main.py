from chessengine import GameState, Move
import chessAI

def print_board(board):
    print("\n   a    b    c    d    e    f    g    h")
    for r in range(8):
        print(8 - r, end=" ")
        for c in range(8):
            print(board[r][c], end="  ")
        print()
    print()

def parse_move(move_str):
    """
    Chuyển chuỗi như 'e2e4' thành tọa độ:
    start = (6,4), end = (4,4)
    """
    if len(move_str) != 4:
        return None

    start_file = move_str[0]
    start_rank = move_str[1]
    end_file = move_str[2]
    end_rank = move_str[3]

    if start_file not in "abcdefgh" or end_file not in "abcdefgh":
        return None
    if start_rank not in "12345678" or end_rank not in "12345678":
        return None

    start_col = Move.filesToCols[start_file]
    start_row = Move.ranksToRows[start_rank]
    end_col = Move.filesToCols[end_file]
    end_row = Move.ranksToRows[end_rank]

    return (start_row, start_col), (end_row, end_col)

def main():
    gs = GameState()

    while True:
        valid_moves = gs.get_valid_moves()

        # kiểm tra kết thúc game
        if gs.checkMate:
            print_board(gs.board)
            if gs.whiteToMove:
                print("Checkmate! Den thang!")
            else:
                print("Checkmate! Trang thang!")
            break

        if gs.staleMate:
            print_board(gs.board)
            print("Hoa co (Stalemate)!")
            break

        print_board(gs.board)

        # =========================
        # LƯỢT NGƯỜI CHƠI (TRẮNG)
        # =========================
        if gs.whiteToMove:
            move_input = input("Nhap nuoc di cua ban (vd: e2e4), hoặc 'q' để thoat: ").strip()

            if move_input.lower() == "q":
                print("Da thoat game.")
                break

            parsed = parse_move(move_input)
            if parsed is None:
                print("Nhap sai dinh dang! Hay nhap kiểu e2e4.\n")
                continue

            startSq, endSq = parsed
            move = Move(startSq, endSq, gs.board)

            if move in valid_moves:
                gs.make_move(move)
            else:
                print("Nuoc di khong hop le!\n")
                continue

        # =========================
        # LƯỢT AI (ĐEN)
        # =========================
        else:
            print("AI dang suy nghi...")
            best_move = chessAI.find_best_move(gs, valid_moves)

            if best_move is None:
                print("AI khong tim thay nuoc di.")
                break

            print("AI di:", best_move.get_chess_notation())
            gs.make_move(best_move)

if __name__ == "__main__":
    main()