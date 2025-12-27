let replayMoves = [];
let replayInitialState = null;
let currentMoveIndex = -1;
let isInReplayMode = false;
let savedWinningRun = null;
let savedWinner = null;

function createGameOverUI(winner, eloChange, friendRoomCode, buttonAction, isSinglePlayer = false, replayData = null) {
    gameOver = true;
    window.removeEventListener('click', onMouseClick);

    savedWinner = winner;

    let message;
    if (winner === null) {
        message = 'Game Over! It\'s a tie!';
    } else if (isSinglePlayer) {
        message = winner === window.playerColor ? 'Game Over! You Win!' : 'Game Over! You Lose...';
    } else {
        message = 'Game Over! ' + winner + ' wins!';
    }

    const gameOverDiv = document.createElement('div');
    gameOverDiv.id = 'game-over-ui';
    gameOverDiv.style.position = 'fixed';
    gameOverDiv.style.top = '160px';
    gameOverDiv.style.left = '50%';
    gameOverDiv.style.transform = 'translateX(-50%)';
    gameOverDiv.style.backgroundColor = 'rgba(44, 62, 80, 0.9)';
    gameOverDiv.style.color = 'white';
    gameOverDiv.style.padding = '20px';
    gameOverDiv.style.borderRadius = '10px';
    gameOverDiv.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    gameOverDiv.style.zIndex = '1000';
    gameOverDiv.style.maxWidth = '300px';
    gameOverDiv.style.width = '90%';
    gameOverDiv.style.textAlign = 'center';

    const closeButton = document.createElement('button');
    closeButton.style.position = 'absolute';
    closeButton.style.right = '10px';
    closeButton.style.top = '4px';
    closeButton.style.background = 'none';
    closeButton.style.border = 'none';
    closeButton.style.color = '#999';
    closeButton.style.fontSize = '20px';
    closeButton.style.cursor = 'pointer';
    closeButton.innerHTML = '×';
    closeButton.onclick = () => {
        gameOverDiv.remove();
    };
    closeButton.onmouseover = () => {
        closeButton.style.color = '#fff';
    };
    closeButton.onmouseout = () => {
        closeButton.style.color = '#999';
    };
    gameOverDiv.appendChild(closeButton);

    // Game over message and Elo change display
    const messageDiv = document.createElement('div');
    messageDiv.style.fontSize = '24px';
    messageDiv.style.fontWeight = 'bold';
    messageDiv.style.marginBottom = '15px';
    messageDiv.innerHTML = message;
    if (eloChange !== null) {
        const eloChangeText = `Elo: ${eloChange > 0 ? '+' + eloChange : eloChange}`;
        const eloChangeColor = eloChange > 0 ? '#4CAF50' : (eloChange < 0 ? '#F44336' : '#FFD700');
        messageDiv.innerHTML += `<div style='color: ${eloChangeColor}; font-size: 18px; margin-top: 10px;'>${eloChangeText}</div>`;
    }
    gameOverDiv.appendChild(messageDiv);

    const buttonContainer = document.createElement('div');
    buttonContainer.style.display = 'flex';
    buttonContainer.style.flexDirection = 'column';
    buttonContainer.style.alignItems = 'center';
    buttonContainer.style.gap = '10px';
    buttonContainer.style.marginTop = '20px';
    buttonContainer.style.width = '100%';

    const commonButtonStyles = {
        width: '200px',
        padding: '10px 28px',
        fontSize: '16px',
        cursor: 'pointer',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        transition: 'background-color 0.3s'
    };

    if (friendRoomCode) {
        const rematchButton = document.createElement('button');
        rematchButton.innerHTML = 'Rematch';
        Object.assign(rematchButton.style, commonButtonStyles);
        rematchButton.style.padding = '10px 28px';
        rematchButton.style.fontSize = '16px';
        rematchButton.style.cursor = 'pointer';
        rematchButton.style.backgroundColor = '#3498DB';
        rematchButton.style.color = 'white';
        rematchButton.style.border = 'none';
        rematchButton.style.borderRadius = '5px';
        rematchButton.style.transition = 'background-color 0.3s';
        rematchButton.onmouseover = function() { this.style.backgroundColor = '#2980B9'; }
        rematchButton.onmouseout = function() { this.style.backgroundColor = '#3498DB'; }
        rematchButton.onclick = () => handleRematch(friendRoomCode);
        buttonContainer.appendChild(rematchButton);

        const leaveButton = document.createElement('button');
        leaveButton.innerHTML = 'Leave Room';
        Object.assign(leaveButton.style, commonButtonStyles);
        leaveButton.style.padding = '10px 28px';
        leaveButton.style.fontSize = '16px';
        leaveButton.style.cursor = 'pointer';
        leaveButton.style.backgroundColor = '#E74C3C';
        leaveButton.style.color = 'white';
        leaveButton.style.border = 'none';
        leaveButton.style.borderRadius = '5px';
        leaveButton.style.transition = 'background-color 0.3s';
        leaveButton.onmouseover = function() { this.style.backgroundColor = '#C0392B'; }
        leaveButton.onmouseout = function() { this.style.backgroundColor = '#E74C3C'; }
        leaveButton.onclick = () => leaveFriendRoom(friendRoomCode);
        buttonContainer.appendChild(leaveButton);
    } else {
        const playAgainButton = document.createElement('button');
        playAgainButton.innerHTML = 'Play Again';
        Object.assign(playAgainButton.style, commonButtonStyles);
        playAgainButton.style.padding = '10px 28px';
        playAgainButton.style.fontSize = '16px';
        playAgainButton.style.cursor = 'pointer';
        playAgainButton.style.backgroundColor = '#3498DB';
        playAgainButton.style.color = 'white';
        playAgainButton.style.border = 'none';
        playAgainButton.style.borderRadius = '5px';
        playAgainButton.style.transition = 'background-color 0.3s';
        playAgainButton.onmouseover = function() { this.style.backgroundColor = '#2980B9'; }
        playAgainButton.onmouseout = function() { this.style.backgroundColor = '#3498DB'; }
        playAgainButton.onclick = buttonAction;
        buttonContainer.appendChild(playAgainButton);

        if (replayData && replayData.moves && replayData.moves.length > 0) {
            const replayButton = document.createElement('button');
            replayButton.innerHTML = 'Watch Replay';
            Object.assign(replayButton.style, commonButtonStyles);
            replayButton.style.padding = '10px 28px';
            replayButton.style.fontSize = '16px';
            replayButton.style.cursor = 'pointer';
            replayButton.style.backgroundColor = '#9B59B6';
            replayButton.style.color = 'white';
            replayButton.style.border = 'none';
            replayButton.style.borderRadius = '5px';
            replayButton.style.transition = 'background-color 0.3s';
            replayButton.onmouseover = function() { this.style.backgroundColor = '#8E44AD'; }
            replayButton.onmouseout = function() { this.style.backgroundColor = '#9B59B6'; }
            replayButton.onclick = () => enterReplayMode(replayData);
            buttonContainer.appendChild(replayButton);
        }

        const homeButton = document.createElement('button');
        homeButton.innerHTML = 'Home';
        Object.assign(homeButton.style, commonButtonStyles);
        homeButton.style.padding = '10px 28px';
        homeButton.style.fontSize = '16px';
        homeButton.style.cursor = 'pointer';
        homeButton.style.backgroundColor = '#E74C3C';
        homeButton.style.color = 'white';
        homeButton.style.border = 'none';
        homeButton.style.borderRadius = '5px';
        homeButton.style.transition = 'background-color 0.3s';
        homeButton.onmouseover = function() { this.style.backgroundColor = '#C0392B'; }
        homeButton.onmouseout = function() { this.style.backgroundColor = '#E74C3C'; }
        homeButton.onclick = () => window.location.href = '/';
        buttonContainer.appendChild(homeButton);
    }

    gameOverDiv.appendChild(buttonContainer);
    document.body.appendChild(gameOverDiv);
}

function enterReplayMode(replayData) {
    isInReplayMode = true;
    replayMoves = replayData.moves;
    replayInitialState = replayData.initial_state;
    currentMoveIndex = replayMoves.length - 1;

    const gameOverUI = document.getElementById('game-over-ui');
    if (gameOverUI) {
        gameOverUI.style.display = 'none';
    }

    if (window.highlightCubeGroup) {
        while (window.highlightCubeGroup.children.length > 0) {
            window.highlightCubeGroup.remove(window.highlightCubeGroup.children[0]);
        }
    }

    createReplayControls();
    updateReplayDisplay();
}

function exitReplayMode() {
    isInReplayMode = false;

    const replayControls = document.getElementById('replay-controls');
    if (replayControls) {
        replayControls.remove();
    }

    const finalState = reconstructBoardAtMove(replayInitialState, replayMoves, replayMoves.length - 1);
    updatePiecesFromGameState(finalState);

    const gameOverUI = document.getElementById('game-over-ui');
    if (gameOverUI) {
        gameOverUI.style.display = 'block';
    }

    if (savedWinner && savedWinningRun) {
        highlightWinningRun(savedWinner, savedWinningRun);
    }
}

function createReplayControls() {
    const controlsDiv = document.createElement('div');
    controlsDiv.id = 'replay-controls';
    controlsDiv.style.position = 'fixed';
    controlsDiv.style.top = '120px';
    controlsDiv.style.left = '50%';
    controlsDiv.style.transform = 'translateX(-50%)';
    controlsDiv.style.backgroundColor = 'rgba(44, 62, 80, 0.9)';
    controlsDiv.style.color = 'white';
    controlsDiv.style.padding = '15px 20px';
    controlsDiv.style.borderRadius = '10px';
    controlsDiv.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    controlsDiv.style.zIndex = '1001';
    controlsDiv.style.display = 'flex';
    controlsDiv.style.flexDirection = 'column';
    controlsDiv.style.alignItems = 'center';
    controlsDiv.style.gap = '10px';

    const navRow = document.createElement('div');
    navRow.style.display = 'flex';
    navRow.style.alignItems = 'center';
    navRow.style.gap = '10px';

    const buttonStyle = {
        padding: '8px 12px',
        fontSize: '18px',
        cursor: 'pointer',
        backgroundColor: '#3498DB',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        transition: 'background-color 0.3s',
        minWidth: '40px'
    };

    const firstBtn = document.createElement('button');
    firstBtn.innerHTML = '⏮';
    firstBtn.title = 'Go to start';
    Object.assign(firstBtn.style, buttonStyle);
    firstBtn.onmouseover = function() { this.style.backgroundColor = '#2980B9'; }
    firstBtn.onmouseout = function() { this.style.backgroundColor = '#3498DB'; }
    firstBtn.onclick = () => goToMove(-1);
    navRow.appendChild(firstBtn);

    const prevBtn = document.createElement('button');
    prevBtn.innerHTML = '◀';
    prevBtn.title = 'Previous move';
    Object.assign(prevBtn.style, buttonStyle);
    prevBtn.onmouseover = function() { this.style.backgroundColor = '#2980B9'; }
    prevBtn.onmouseout = function() { this.style.backgroundColor = '#3498DB'; }
    prevBtn.onclick = () => goToMove(currentMoveIndex - 1);
    navRow.appendChild(prevBtn);

    const moveCounter = document.createElement('span');
    moveCounter.id = 'replay-move-counter';
    moveCounter.style.padding = '0 10px';
    moveCounter.style.fontSize = '14px';
    moveCounter.style.minWidth = '100px';
    moveCounter.style.textAlign = 'center';
    navRow.appendChild(moveCounter);

    const nextBtn = document.createElement('button');
    nextBtn.innerHTML = '▶';
    nextBtn.title = 'Next move';
    Object.assign(nextBtn.style, buttonStyle);
    nextBtn.onmouseover = function() { this.style.backgroundColor = '#2980B9'; }
    nextBtn.onmouseout = function() { this.style.backgroundColor = '#3498DB'; }
    nextBtn.onclick = () => goToMove(currentMoveIndex + 1);
    navRow.appendChild(nextBtn);

    const lastBtn = document.createElement('button');
    lastBtn.innerHTML = '⏭';
    lastBtn.title = 'Go to end';
    Object.assign(lastBtn.style, buttonStyle);
    lastBtn.onmouseover = function() { this.style.backgroundColor = '#2980B9'; }
    lastBtn.onmouseout = function() { this.style.backgroundColor = '#3498DB'; }
    lastBtn.onclick = () => goToMove(replayMoves.length - 1);
    navRow.appendChild(lastBtn);

    controlsDiv.appendChild(navRow);

    const exitBtn = document.createElement('button');
    exitBtn.innerHTML = 'Exit Replay';
    exitBtn.style.padding = '8px 20px';
    exitBtn.style.fontSize = '14px';
    exitBtn.style.cursor = 'pointer';
    exitBtn.style.backgroundColor = '#E74C3C';
    exitBtn.style.color = 'white';
    exitBtn.style.border = 'none';
    exitBtn.style.borderRadius = '5px';
    exitBtn.style.transition = 'background-color 0.3s';
    exitBtn.onmouseover = function() { this.style.backgroundColor = '#C0392B'; }
    exitBtn.onmouseout = function() { this.style.backgroundColor = '#E74C3C'; }
    exitBtn.onclick = exitReplayMode;
    controlsDiv.appendChild(exitBtn);

    document.body.appendChild(controlsDiv);
}

function goToMove(index) {
    index = Math.max(-1, Math.min(index, replayMoves.length - 1));
    currentMoveIndex = index;

    const state = reconstructBoardAtMove(replayInitialState, replayMoves, index);
    updatePiecesFromGameState(state);
    updateReplayDisplay();
}

function updateReplayDisplay() {
    const counter = document.getElementById('replay-move-counter');
    if (counter) {
        if (currentMoveIndex === -1) {
            counter.textContent = 'Start';
        } else {
            counter.textContent = `Move ${currentMoveIndex + 1} of ${replayMoves.length}`;
        }
    }
}

function reconstructBoardAtMove(initialState, moves, targetIndex) {
    let state = JSON.parse(JSON.stringify(initialState));

    for (let i = 0; i <= targetIndex && i < moves.length; i++) {
        state = applyMoveToState(state, moves[i]);
    }

    return state;
}

function applyMoveToState(state, move) {
    const { x, y, z, direction, is_blocker, player } = move;
    const boardSize = state.length;

    let pieceType;
    if (is_blocker) {
        pieceType = player === 'RED' ? 'RED_BLOCKER' : 'BLUE_BLOCKER';
    } else {
        pieceType = player;
    }

    let row = [];
    switch (direction) {
        case 'BACK':
            for (let yi = 0; yi < boardSize; yi++) row.push({ x, y: yi, z, piece: state[x][yi][z] });
            break;
        case 'FRONT':
            for (let yi = boardSize - 1; yi >= 0; yi--) row.push({ x, y: yi, z, piece: state[x][yi][z] });
            break;
        case 'LEFT':
            for (let xi = boardSize - 1; xi >= 0; xi--) row.push({ x: xi, y, z, piece: state[xi][y][z] });
            break;
        case 'RIGHT':
            for (let xi = 0; xi < boardSize; xi++) row.push({ x: xi, y, z, piece: state[xi][y][z] });
            break;
        case 'UP':
            for (let zi = boardSize - 1; zi >= 0; zi--) row.push({ x, y, z: zi, piece: state[x][y][zi] });
            break;
        case 'DOWN':
            for (let zi = 0; zi < boardSize; zi++) row.push({ x, y, z: zi, piece: state[x][y][zi] });
            break;
    }

    let emptyIndex = row.findIndex(cell => cell.piece === 'EMPTY');
    if (emptyIndex === -1) {
        emptyIndex = row.length - 1;
    }

    for (let i = emptyIndex; i > 0; i--) {
        const curr = row[i];
        const prev = row[i - 1];
        state[curr.x][curr.y][curr.z] = state[prev.x][prev.y][prev.z];
    }

    const entry = row[0];
    state[entry.x][entry.y][entry.z] = pieceType;

    return state;
}