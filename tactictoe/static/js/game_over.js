function createGameOverUI(winner, eloChange, friendRoomCode, buttonAction, isSinglePlayer = false) {
    gameOver = true;
    window.removeEventListener('click', onMouseClick);

    let message;
    if (winner === null) {
        message = 'Game Over! It\'s a tie!';
    } else if (isSinglePlayer) {
        message = winner === window.playerColor ? 'Game Over! You Win!' : 'Game Over! You Lose...';
    } else {
        message = 'Game Over! ' + winner + ' wins!';
    }

    const gameOverDiv = document.createElement('div');
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
    closeButton.style.top = '10px';
    closeButton.style.background = 'none';
    closeButton.style.border = 'none';
    closeButton.style.color = '#999';
    closeButton.style.fontSize = '20px';
    closeButton.style.cursor = 'pointer';
    closeButton.style.padding = '5px';
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