function findOpponent() {
    return $.ajax({
        url: findOpponentUrl,
        type: 'GET'
    });
}

function setupWebSocket(onGameStart) {
    var socket = new WebSocket(
        'ws://' + window.location.host + '/ws/setup/'
    );

    socket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        if (data.status === 'success') {
            onGameStart(data.game_id);
        }
    };

    socket.onclose = function(e) {
        console.error('Setup socket closed unexpectedly');
    };

    return socket;
}
