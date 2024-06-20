function createGameOverUI(winner, eloChange, buttonAction) {
    console.log("GAME OVER")
    console.log(winner);
    console.log(eloChange);
    if (winner == null) {
        return;
    }

    window.removeEventListener('click', onMouseClick);
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseout', onMouseOut);

    let message = 'Game Over! ' + winner + ' wins!';

    // Calculate Elo change display
    let eloChangeMessage = "";

    if (eloChange !== undefined) {
        const eloChangeText = `Elo: ${eloChange > 0 ? '+' + eloChange : eloChange}`;
        const eloChangeColor = eloChange > 0 ? 'green' : 'red';
        eloChangeMessage = `<br><span style='color: ${eloChangeColor};'>${eloChangeText}</span>`;
    }

    // Display game over message
    const gameOverDiv = document.createElement('div');
    gameOverDiv.style.position = 'absolute';
    gameOverDiv.style.top = '50%';
    gameOverDiv.style.left = '50%';
    gameOverDiv.style.transform = 'translate(-50%, -50%)';
    gameOverDiv.style.fontSize = '24px';
    gameOverDiv.style.color = 'white';
    gameOverDiv.style.textAlign = 'center';
    gameOverDiv.style.padding = '20px';
    gameOverDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    gameOverDiv.style.borderRadius = '10px';
    gameOverDiv.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    gameOverDiv.innerHTML = message + eloChangeMessage;

    // Add a button to restart the game
    const restartButton = document.createElement('button');
    restartButton.innerHTML = 'New Game';
    restartButton.style.marginTop = '20px';
    restartButton.style.padding = '10px 20px';
    restartButton.style.fontSize = '16px';
    restartButton.style.cursor = 'pointer';
    restartButton.onclick = buttonAction;

    gameOverDiv.appendChild(restartButton);
    document.body.appendChild(gameOverDiv);
}

function playSound(soundType) {
    const sound = document.getElementById(soundType + "Sound");
    if (sound) {
        sound.play();
    }
}
