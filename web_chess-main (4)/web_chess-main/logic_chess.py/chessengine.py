class GameState:
    def __init__(self):
        # Bàn cờ 8x8
        # b = black, w = white
        # R = Rook, N = Knight, B = Bishop, Q = Queen, K = King, P = Pawn
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        # True = trắng đi, False = đen đi
        self.whiteToMove = True

        # Lưu lịch sử nước đi để undo
        self.moveLog = []

        # Lưu vị trí vua trắng và vua đen
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        # Trạng thái kết thúc
        self.checkMate = False
        self.staleMate = False

        # Bảng ánh xạ quân cờ -> hàm sinh nước đi
        self.moveFunctions = {
            "P": self.get_pawn_moves,
            "R": self.get_rook_moves,
            "N": self.get_knight_moves,
            "B": self.get_bishop_moves,
            "Q": self.get_queen_moves,
            "K": self.get_king_moves
        }

    # =========================================================
    # 1. THỰC HIỆN NƯỚC ĐI
    # =========================================================
    def make_move(self, move):
        """
        Di chuyển quân cờ trên bàn cờ.
        """
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)

        # Đổi lượt
        self.whiteToMove = not self.whiteToMove

        # Nếu vua di chuyển thì cập nhật vị trí vua
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

    # =========================================================
    # 2. HOÀN TÁC NƯỚC ĐI
    # =========================================================
    def undo_move(self):
        """
        Quay lại nước đi trước đó.
        """
        if len(self.moveLog) == 0:
            return

        move = self.moveLog.pop()

        # Trả quân về vị trí cũ
        self.board[move.startRow][move.startCol] = move.pieceMoved
        self.board[move.endRow][move.endCol] = move.pieceCaptured

        # Đổi lại lượt
        self.whiteToMove = not self.whiteToMove

        # Cập nhật lại vị trí vua nếu vừa undo vua
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.startRow, move.startCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.startRow, move.startCol)

    # =========================================================
    # 3. LẤY TẤT CẢ NƯỚC ĐI HỢP LỆ
    # =========================================================
    def get_valid_moves(self):
        """
        Trả về danh sách các nước đi hợp lệ.
        Nước đi hợp lệ = sau khi đi xong, vua của mình không bị chiếu.
        """
        moves = self.get_all_possible_moves()

        # Duyệt ngược để có thể xóa phần tử an toàn
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])

            # Sau make_move thì lượt đã đổi sang đối phương.
            # Muốn kiểm tra vua của người vừa đi có bị chiếu không,
            # ta đổi lại lượt tạm thời.
            self.whiteToMove = not self.whiteToMove

            if self.in_check():
                moves.remove(moves[i])

            # Trả lại lượt như cũ
            self.whiteToMove = not self.whiteToMove
            self.undo_move()

        # Kiểm tra trạng thái kết thúc
        if len(moves) == 0:
            if self.in_check():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves

    # =========================================================
    # 4. KIỂM TRA BÊN ĐANG ĐI CÓ BỊ CHIẾU KHÔNG
    # =========================================================
    def in_check(self):
        """
        Kiểm tra vua của bên đang đi có bị chiếu không.
        """
        if self.whiteToMove:
            return self.square_under_attack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.square_under_attack(self.blackKingLocation[0], self.blackKingLocation[1])

    # =========================================================
    # 5. KIỂM TRA 1 Ô CÓ BỊ ĐỐI PHƯƠNG TẤN CÔNG KHÔNG
    # =========================================================
    def square_under_attack(self, r, c):
        """
        Kiểm tra ô (r, c) có bị đối phương tấn công không.
        """
        # Đổi lượt sang đối phương để sinh nước đi của đối phương
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove

        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    # =========================================================
    # 6. SINH TẤT CẢ NƯỚC ĐI CÓ THỂ (CHƯA LỌC CHIẾU)
    # =========================================================
    def get_all_possible_moves(self):
        """
        Sinh tất cả nước đi theo luật di chuyển của quân cờ,
        CHƯA xét việc vua có bị chiếu hay không.
        """
        moves = []

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == "--":
                    continue

                color = piece[0]   # 'w' hoặc 'b'
                pieceType = piece[1]  # 'P', 'R', 'N', ...

                # Chỉ sinh nước đi cho bên đang tới lượt
                if (color == "w" and self.whiteToMove) or (color == "b" and not self.whiteToMove):
                    self.moveFunctions[pieceType](r, c, moves)

        return moves

    # =========================================================
    # 7. LOGIC QUÂN TỐT
    # =========================================================
    def get_pawn_moves(self, r, c, moves):
        """
        Sinh nước đi cho quân tốt.
        """
        if self.whiteToMove:
            # Tốt trắng đi lên: r-1

            # Đi 1 ô
            if r - 1 >= 0 and self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))

                # Đi 2 ô nếu ở hàng xuất phát
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))

            # Ăn chéo trái
            if r - 1 >= 0 and c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))

            # Ăn chéo phải
            if r - 1 >= 0 and c + 1 < 8:
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        else:
            # Tốt đen đi xuống: r+1

            # Đi 1 ô
            if r + 1 < 8 and self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))

                # Đi 2 ô nếu ở hàng xuất phát
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))

            # Ăn chéo trái
            if r + 1 < 8 and c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))

            # Ăn chéo phải
            if r + 1 < 8 and c + 1 < 8:
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    # =========================================================
    # 8. LOGIC QUÂN XE
    # =========================================================
    def get_rook_moves(self, r, c, moves):
        """
        Xe đi ngang / dọc.
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        allyColor = "w" if self.whiteToMove else "b"

        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]

                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    # =========================================================
    # 9. LOGIC QUÂN MÃ
    # =========================================================
    def get_knight_moves(self, r, c, moves):
        """
        Mã đi hình chữ L.
        """
        knightMoves = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1)
        ]

        allyColor = "w" if self.whiteToMove else "b"

        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece == "--" or endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    # =========================================================
    # 10. LOGIC QUÂN TƯỢNG
    # =========================================================
    def get_bishop_moves(self, r, c, moves):
        """
        Tượng đi chéo.
        """
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        allyColor = "w" if self.whiteToMove else "b"

        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]

                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    # =========================================================
    # 11. LOGIC QUÂN HẬU
    # =========================================================
    def get_queen_moves(self, r, c, moves):
        """
        Hậu = Xe + Tượng
        """
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    # =========================================================
    # 12. LOGIC QUÂN VUA
    # =========================================================
    def get_king_moves(self, r, c, moves):
        """
        Vua đi 1 ô xung quanh.
        """
        kingMoves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        allyColor = "w" if self.whiteToMove else "b"

        for m in kingMoves:
            endRow = r + m[0]
            endCol = c + m[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece == "--" or endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


# =============================================================
# CLASS MOVE - LƯU THÔNG TIN 1 NƯỚC ĐI
# =============================================================
class Move:
    # ánh xạ chữ <-> số để sau này in nước đi đẹp hơn
    ranksToRows = {
        "1": 7, "2": 6, "3": 5, "4": 4,
        "5": 3, "6": 2, "7": 1, "8": 0
    }
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {
        "a": 0, "b": 1, "c": 2, "d": 3,
        "e": 4, "f": 5, "g": 6, "h": 7
    }
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # ID để so sánh 2 nước đi
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        """
        So sánh 2 đối tượng Move có giống nhau không.
        """
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_notation(self):
        """
        Trả về dạng nước đi kiểu: e2e4
        """
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]