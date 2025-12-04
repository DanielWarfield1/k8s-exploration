let board = Chessboard('board', {
    draggable: true,
    dropOffBoard: 'trash',
    position: 'start',
    onDrop: async (source, target) => {
        let move = source + target;
        let fen = board.fen();

        let res = await fetch("/move", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                game_id: "local",
                move: move,
                fen: fen
            })
        });

        let data = await res.json();
        board.move(data.best_move);
    }
});
