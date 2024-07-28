function createGameOverUI(winner, eloChange, buttonAction) {
    if (winner == null) {
        return;
    }
    window.removeEventListener('click', onMouseClick);
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseout', onMouseOut);

    let message = 'Game Over! ' + winner + ' wins!';

    // Calculate Elo change display
    let eloChangeMessage = "";
    if (eloChange !== null) {
        const eloChangeText = `Elo: ${eloChange > 0 ? '+' + eloChange : eloChange}`;
        const eloChangeColor = eloChange > 0 ? '#4CAF50' : '#F44336';
        eloChangeMessage = `<div style='color: ${eloChangeColor}; font-size: 18px; margin-top: 10px;'>${eloChangeText}</div>`;
    }

    // Create game over overlay
    const gameOverDiv = document.createElement('div');
    gameOverDiv.style.position = 'fixed';
    gameOverDiv.style.top = '90px';
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

    // Game over message
    const messageDiv = document.createElement('div');
    messageDiv.style.fontSize = '24px';
    messageDiv.style.fontWeight = 'bold';
    messageDiv.style.marginBottom = '15px';
    messageDiv.innerHTML = message;
    gameOverDiv.appendChild(messageDiv);

    // Elo change message
    const eloChangeDiv = document.createElement('div');
    eloChangeDiv.innerHTML = eloChangeMessage;
    gameOverDiv.appendChild(eloChangeDiv);

    // Add a button to start a new game
    const newGameButton = document.createElement('button');
    newGameButton.innerHTML = 'New Game';
    newGameButton.style.marginTop = '20px';
    newGameButton.style.padding = '10px 20px';
    newGameButton.style.fontSize = '16px';
    newGameButton.style.cursor = 'pointer';
    newGameButton.style.backgroundColor = '#3498DB';
    newGameButton.style.color = 'white';
    newGameButton.style.border = 'none';
    newGameButton.style.borderRadius = '5px';
    newGameButton.style.transition = 'background-color 0.3s';
    newGameButton.onmouseover = function() { this.style.backgroundColor = '#2980B9'; }
    newGameButton.onmouseout = function() { this.style.backgroundColor = '#3498DB'; }
    newGameButton.onclick = buttonAction;

    gameOverDiv.appendChild(newGameButton);
    document.body.appendChild(gameOverDiv);
}

function playSound(soundType) {
    const sound = document.getElementById(soundType + "Sound");
    if (sound) {
        sound.play();
    }
}
