// boardSize is optional, defaults to 3 for backwards compatibility
function findOpponent(boardSize) {
    boardSize = boardSize || 3;
    return $.ajax({
        url: findOpponentUrl + '?board_size=' + boardSize,
        type: 'GET'
    });
}

// boardSize is optional, defaults to 3 for backwards compatibility
function cancelSearch(boardSize) {
    boardSize = boardSize || 3;
    return $.ajax({
        url: '/cancel-search/?board_size=' + boardSize,
        type: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });
}

let setupSocket;

function startWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    setupSocket = new WebSocket(
        protocol + window.location.host + '/ws/setup/'
    );

    setupSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        if (data.status === 'success') {
            playSound("start");
            window.location.href = '/game/' + data.game_code;
        } else if (data.status === 'cancelled') {
            const waitingModal = document.querySelector('.waiting-modal');
            if (waitingModal) {
                waitingModal.remove();
            }
            alert('Other player cancelled the rematch');
            window.location.href = '/';
        }
    };

    setupSocket.onclose = function(e) {
        console.error('Setup socket closed unexpectedly');
    };
}

window.setupSocket = setupSocket;