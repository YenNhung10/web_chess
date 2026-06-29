currentFen = 'start'
highlightedSquares = []
selectedSquare = null

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

function onMouseoverSquare(square, piece) {
    // chỉ highlight quân trắng của người chơi
    if (!piece || piece[0] !== 'w') return;

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
    // nếu muốn rê chuột ra là tắt highlight thì bỏ comment dòng dưới
    // clearHighlights();
}

function onDrop(source, target) {
    if (source === target) return;

    clearHighlights();

    $.ajax({
        url: '/move',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ move: source + target }),

        success: function(data) {
            if (!data.success) {
                alert(data.error || "Nước đi không hợp lệ!");
                board.position(currentFen);
                return;
            }

            currentFen = data.fen;
            board.position(currentFen);
        },

        error: function() {
            alert("Không kết nối được tới server!");
            board.position(currentFen);
        }
    });
}

function resetGame() {
    $.ajax({
        url: '/reset',
        type: 'POST',
        success: function(data) {
            currentFen = 'start';
            board.start();
            clearHighlights();
        },
        error: function() {
            alert("Reset thất bại!");
        }
    });
}

var board = Chessboard('myBoard', {
    draggable: true,
    position: 'start',
    pieceTheme: 'https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/img/chesspieces/wikipedia/{piece}.png',
    onDrop: onDrop,
    onMouseoverSquare: onMouseoverSquare,
    onMouseoutSquare: onMouseoutSquare
});
