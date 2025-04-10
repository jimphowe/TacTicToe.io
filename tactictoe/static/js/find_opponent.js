function findOpponent() {
    return $.ajax({
        url: findOpponentUrl,
        type: 'GET'
    });
}

function cancelSearch() {
    return $.ajax({
        url: '/cancel-search/',
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