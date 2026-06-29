let currentFen = 'start';
let highlightedSquares = [];
let selectedSquare = null;
const statusDiv = document.getElementById("status");

function clearHighlights() {
    highlightedSquares.forEach(square => {
        $('#myBoard .square-' + square).removeClass('highlight-square');
    });

    if (selectedSquare) {
        $('#myBoard .square-' + selectedSquare).removeClass('highlight-selected');
    }

    highlightedSquares = [];
    selectedSquare = null;
}

function highlightSquares(fromSquare, moves) {
    clearHighlights();

    selectedSquare = fromSquare;
    $('#myBoard .square-' + fromSquare).addClass('highlight-selected');

    moves.forEach(square => {
        $('#myBoard .square-' + square).addClass('highlight-square');
        highlightedSquares.push(square);
    });
}

// ===================================
// HÀM CHẶN KHÔNG CHO BỐC NHẦM QUÂN AI
// ===================================
function onDragStart(source, piece, position, orientation) {
    const playerColor = $('#colorSelect').val() || 'w';

    // Nếu chọn Trắng (w) mà cố tình bốc quân Đen (b), hoặc ngược lại thì không cho nhấc quân
    if ((playerColor === 'w' && piece.search(/^b/) !== -1) ||
        (playerColor === 'b' && piece.search(/^w/) !== -1)) {
        return false;
    }
}

function onMouseoverSquare(square, piece) {
    const playerColor = $('#colorSelect').val() || 'w'; 

    // Chỉ highlight nước đi hợp lệ khi rê chuột vào đúng quân của mình chọn
    if (!piece || piece[0] !== playerColor) return;

    $.ajax({
        url: '/legal_moves_from',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ square: square }),
        success: function(data) {
            if (data.success) {
                highlightSquares(square, data.moves);
            }
        }
    });
}

function onMouseoutSquare(square, piece) {
    // clearHighlights();
}

// ===================================
// XỬ LÝ KÉO THẢ QUÂN CỜ
// ===================================
function onDrop(source, target) {
    if (source === target) return;

    const playerColor = $('#colorSelect').val() || 'w';
    const colorName = (playerColor === 'b') ? "Đen" : "Trắng";

    clearHighlights();

    // Gửi trực tiếp chuỗi uci (ví dụ: g8f6) lên server
    $.ajax({
        url: '/move',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ move: source + target }),
        success: function(data) {
            if (!data.success) {
                // Nếu không hợp lệ, chessboard.js cần return 'snapback' để quân cờ nảy về chỗ cũ
                board.position(currentFen);
                return 'snapback';
            }

            currentFen = data.fen;
            board.position(currentFen);

            if (data.game_over) {
                if (statusDiv) statusDiv.innerText = "Ván cờ kết thúc: " + (data.result || "");
            } else if (data.ai_move) {
                if (statusDiv) statusDiv.innerText = "AI vừa đi: " + data.ai_move + " | Lượt của bạn (" + colorName + ")";
            } else {
                if (statusDiv) statusDiv.innerText = "Lượt của bạn (" + colorName + ")";
            }
        },
        error: function() {
            alert("Không kết nối được tới server!");
            board.position(currentFen);
        }
    });
}

// ===================================
// SỬA ĐỒNG BỘ ĐỂ ĐIỀU KHIỂN ĐƯỢC QUÂN ĐEN
// ===================================
function resetGame() {
    const playerColor = $('#colorSelect').val() || 'w';

    if (playerColor === 'b') {
        board.orientation('black');
        if (statusDiv) statusDiv.innerText = "Đang đợi AI đi nước đầu tiên...";
    } else {
        board.orientation('white');
        if (statusDiv) statusDiv.innerText = "Lượt của bạn (Trắng)";
    }

    $.ajax({
        url: '/reset',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ color: playerColor }),
        success: function(data) {
            // QUAN TRỌNG: Cập nhật FEN ngay lập tức bao gồm cả nước đi đầu tiên của AI Trắng
            currentFen = data.fen; 
            board.position(currentFen);
            clearHighlights();
            
            if (playerColor === 'b' && data.ai_move) {
                if (statusDiv) statusDiv.innerText = "AI (Trắng) vừa đi: " + data.ai_move + " | Lượt của bạn (Đen)";
            }
        },
        error: function() {
            alert("Reset thất bại!");
        }
    });
}

// Khởi tạo bàn cờ tích hợp cả onDragStart
var board = Chessboard('myBoard', {
    draggable: true,
    position: 'start',
    pieceTheme: 'https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/img/chesspieces/wikipedia/{piece}.png',
    onDragStart: onDragStart, // Kích hoạt bộ lọc chặn bốc nhầm quân
    onDrop: onDrop,
    onMouseoverSquare: onMouseoverSquare,
    onMouseoutSquare: onMouseoutSquare
});

$(document).ready(function() {
    resetGame();
});