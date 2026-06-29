from flask import Flask, render_template, request, jsonify, send_from_directory
import chess

app = Flask(__name__)

board = chess.Board()

player_color = 'w'

def evaluate_board(board):
    if board.is_checkmate():
        return -9999 if board.turn == chess.WHITE else 9999
    if board.is_stalemate():
        return 0

    piece_values = {
        chess.PAWN: 10,
        chess.KNIGHT: 30,
        chess.BISHOP: 30,
        chess.ROOK: 50,
        chess.QUEEN: 90,
        chess.KING: 900
    }

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
    return score


def minimax(board, depth, alpha, beta, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)

    if is_maximizing:
        max_eval = -99999
        for move in legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = 99999
        for move in legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


def get_best_ai_move(board_obj, depth=2):
    import chess
    # Tự động xác định AI cần tối ưu theo hướng Max (Trắng) hay Min (Đen) dựa vào board_obj.turn
    is_ai_white = (board_obj.turn == chess.WHITE)
    best_move = None
    
    if is_ai_white:
        best_value = -99999
    else:
        best_value = 99999

    legal_moves = list(board_obj.legal_moves)
    if not legal_moves:
        return None

    for move in legal_moves:
        board_obj.push(move)
        # Giả định hàm minimax() của bạn đã được khai báo sẵn trong dự án
        # next_is_max sẽ đảo ngược lại với phe hiện tại của AI sau khi push
        try:
            value = minimax(board_obj, depth - 1, -99999, 99999, not is_ai_white)
        except NameError:
            # Phòng hờ nếu bạn chưa link hàm minimax, AI sẽ chạy random không bị crash
            value = random.randint(-10, 10)
            
        board_obj.pop()

        if is_ai_white:
            if value > best_value:
                best_value = value
                best_move = move
        else:
            if value < best_value:
                best_value = value
                best_move = move
                
    if best_move is None and legal_moves:
        best_move = random.choice(legal_moves)
        
    return best_move


def board_to_matrix(board):
    matrix = [["--" for _ in range(8)] for _ in range(8)]

    piece_map = {
        "P": "wP", "N": "wN", "B": "wB", "R": "wR", "Q": "wQ", "K": "wK",
        "p": "bP", "n": "bN", "b": "bB", "r": "bR", "q": "bQ", "k": "bK"
    }

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            matrix[row][col] = piece_map[piece.symbol()]

    return matrix

def reset_board_for_black_player():
    """
    Người chơi cầm đen.
    AI (trắng) sẽ đi trước 1 nước ngay khi bắt đầu ván.
    """
    global board
    board = chess.Board()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_board", methods=["GET"])
def get_board():
    return jsonify({
        "success": True,
        "fen": board.fen(),
        "turn": "white" if board.turn == chess.WHITE else "black",
        "game_over": board.is_game_over(),
        "result": board.result() if board.is_game_over() else None
    })


@app.route('/legal_moves_from', methods=['POST'])
def legal_moves_from():
    global board
    data = request.get_json() or {}
    square_str = data.get('square')
    
    try:
        square = chess.parse_square(square_str)
        
        # --- ĐOẠN SỬA QUAN TRỌNG ---
        # Kiểm tra xem quân cờ tại ô đó có trùng với lượt đi hiện tại của bàn cờ (board.turn) không.
        # Nếu AI Trắng vừa đi xong, board.turn sẽ tự động chuyển sang chess.BLACK.
        piece = board.piece_at(square)
        if piece is None or piece.color != board.turn:
            return jsonify({"success": True, "moves": []}) # Trả về mảng rỗng nếu chọn sai quân/sai lượt
        # ---------------------------

        moves = [chess.square_name(m.to_square) for m in board.legal_moves if m.from_square == square]
        return jsonify({"success": True, "moves": moves})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/chess_peices/<path:filename>')
def chess_pieces(filename):
    return send_from_directory('chess_peices', filename)


@app.route('/move', methods=['POST'])
def make_move():
    global board, player_color
    data = request.get_json() or {}
    move_str = data.get('move')
    
    try:
        move = chess.Move.from_uci(move_str)
        if move in board.legal_moves:
            board.push(move)  # Người chơi thực hiện nước đi của họ
            
            is_game_over_after_player = board.is_game_over()
            ai_move_str = None
            
            # Nếu trận đấu chưa kết thúc, kích hoạt AI phản công nước tiếp theo
            if not is_game_over_after_player:
                ai_move = get_best_ai_move(board)
                if ai_move:
                    board.push(ai_move)
                    ai_move_str = ai_move.uci()
            
            final_game_over = board.is_game_over()
            # Xác định lượt đi tiếp theo trên hệ thống thuộc về ai ('w' hoặc 'b')
            next_turn = 'w' if board.turn == chess.WHITE else 'b'
            
            # Tính toán kết quả chuỗi trận đấu nếu kết thúc
            result_str = ""
            if final_game_over:
                result_str = board.result()

            response = {
                "success": True,
                "fen": board.fen(),
                "game_over": final_game_over,
                "result": result_str,
                "turn": next_turn
            }
            if ai_move_str:
                response["ai_move"] = ai_move_str
                
            return jsonify(response)
        else:
            return jsonify({"success": False, "error": "Nước đi không hợp lệ!"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/reset', methods=['POST'])
def reset_game():
    global board, player_color
    data = request.get_json() or {}
    player_color = data.get('color', 'w')  # Nhận 'w' hoặc 'b' từ giao diện
    
    board = chess.Board()  # Khởi tạo lại bàn cờ mới 100%
    
    response = {
        "success": True,
        "fen": board.fen(),
        "ai_move": None
    }
    
    # NẾU NGƯỜI CHƠI CHỌN ĐEN (b) -> AI mang quân Trắng (WHITE) sẽ tự động đi trước nước đầu tiên
    if player_color == 'b':
        ai_move = get_best_ai_move(board)
        if ai_move:
            board.push(ai_move)
            response["fen"] = board.fen()
            response["ai_move"] = ai_move.uci()
        
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)