const gameCode = JSON.parse(document.getElementById('game-code').textContent);
const playerName = JSON.parse(document.getElementById('player-name').textContent);
const iHaveGameCode = JSON.parse(document.getElementById('i-have-game-code').textContent);
const gameMatrixId = JSON.parse(document.getElementById('game-matrix-id').textContent);

let mySymbol = 'X';
if (iHaveGameCode === 'on') {
    mySymbol = 'O';
}

let ws = null;
let isMyTurn = false;

function initWebSocket() {
    const wsUrl =
        'ws://' +
        window.location.host +
        '/ws/asc/pg/' +
        gameCode +
        '/' +
        gameMatrixId +
        '/' +
        playerName +
        '/' +
        iHaveGameCode +
        '/';

    console.log('Connecting to:', wsUrl);
    ws = new WebSocket(wsUrl);

    ws.onopen = function () {
        console.log('WebSocket: connection established ✅');
    };

    ws.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.msg_type === 'state') {
            // Initial state from server
            if (data.your_symbol) {
                mySymbol = data.your_symbol;
                console.log('You are:', mySymbol);
            }

            // Board sync (agar already koi moves ho chuke ho)
            if (data.board) {
                Object.keys(data.board).forEach((pos) => {
                    const cell = document.getElementById(pos);
                    if (cell && data.board[pos]) {
                        cell.textContent = data.board[pos];
                    }
                });
            }

            // Turn set
            isMyTurn = data.current_symbol === mySymbol;
            console.log('Is my turn?', isMyTurn);
        } else if (data.msg_type === 'chance') {
            // Ek move hua, board update karo
            const cell = document.getElementById(data.position);
            if (cell) {
                cell.textContent = data.symbol; // X or O
            }

            // Ab turn dusre symbol ka hai
            isMyTurn = data.symbol !== mySymbol;
            console.log('Is my turn now?', isMyTurn);
        } else if (data.msg_type === 'result') {
            const result =
                data.msg === 'game drawn'
                    ? 'Game Drawn 😄😄'
                    : data.msg + ' Wins... 🥳🥳';

            document.getElementsByClassName('modal-body')[0].textContent = result;
            document.getElementById('result').click();
            console.log('Result:', data.msg);

            // Game over → further moves disable
            isMyTurn = false;
        } else if (data.msg_type === 'info') {
            console.log('Info from server:', data.msg);
        }
    };

    ws.onerror = function (event) {
        console.error('WebSocket: error ❌ connection aborted...', event);
    };

    ws.onclose = function (event) {
        console.log('WebSocket: connection closed ❌', event);
        isMyTurn = false;
    };
}

// page load pe ek baar hi
initWebSocket();

function func(box_id) {
    const box = document.getElementById(box_id.toString());
    if (!box) {
        console.error('No element found for box_id:', box_id);
        return;
    }

    const box_content = box.textContent;

    if (!isMyTurn) {
        console.log('Not your turn, wait for opponent.');
        return;
    }

    if (box_content === '') {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(box_id.toString());
        } else {
            console.error(
                'WebSocket is not OPEN. State =',
                ws ? ws.readyState : 'no socket'
            );
        }
    }
}
