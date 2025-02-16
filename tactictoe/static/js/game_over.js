function createGameOverUI(winner, eloChange, friendRoomCode, buttonAction) {
    gameOver = true;
    window.removeEventListener('click', onMouseClick);

    let message = winner === null ? 'Game Over! It\'s a tie!' : 'Game Over! ' + winner + ' wins!';

    // Create game over overlay
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

function handleRematch(friendRoomCode) {
    const waitingModal = showWaitingForRematch();
    
    fetch('/handle-rematch/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            friend_room_code: friendRoomCode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.game_created) {
            waitingModal.remove();
            window.location.href = '/game/' + data.game_code;
        } else if (data.status === 'waiting') {
            // Keep waiting modal visible
        } else {
            waitingModal.remove();
            showToast(data.message || 'Error starting rematch');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        waitingModal.remove();
        showToast('Unexpected error occurred');
    });
}

function showWaitingForRematch(friendRoomCode) {
    // Initialize WebSocket if not already connected
    if (!window.setupSocket || window.setupSocket.readyState !== WebSocket.OPEN) {
        startWebSocket();
    }

    const modalDiv = document.createElement('div');
    modalDiv.className = 'waiting-modal';
    modalDiv.style.position = 'fixed';
    modalDiv.style.top = '50%';
    modalDiv.style.left = '50%';
    modalDiv.style.transform = 'translate(-50%, -50%)';
    modalDiv.style.backgroundColor = 'rgba(30, 41, 59, 0.9)';
    modalDiv.style.padding = '24px';
    modalDiv.style.borderRadius = '10px';
    modalDiv.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    modalDiv.style.zIndex = '1000';
    modalDiv.style.minWidth = '300px';
    modalDiv.style.textAlign = 'center';
    modalDiv.style.color = 'white';

    const spinnerDiv = document.createElement('div');
    spinnerDiv.style.width = '48px';
    spinnerDiv.style.height = '48px';
    spinnerDiv.style.border = '4px solid #f3f3f3';
    spinnerDiv.style.borderTop = '4px solid #3498db';
    spinnerDiv.style.borderRadius = '50%';
    spinnerDiv.style.animation = 'spin 1s linear infinite';
    spinnerDiv.style.margin = '0 auto 20px auto';

    // Add the spin animation if it doesn't exist
    if (!document.querySelector('#spin-animation')) {
        const style = document.createElement('style');
        style.id = 'spin-animation';
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    const messageDiv = document.createElement('div');
    messageDiv.style.marginBottom = '20px';
    messageDiv.style.fontSize = '18px';
    messageDiv.textContent = 'Waiting for opponent to accept rematch...';

    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.style.padding = '10px 20px';
    cancelButton.style.fontSize = '16px';
    cancelButton.style.cursor = 'pointer';
    cancelButton.style.backgroundColor = '#E74C3C';  // Red color
    cancelButton.style.color = 'white';
    cancelButton.style.border = 'none';
    cancelButton.style.borderRadius = '5px';
    cancelButton.style.transition = 'background-color 0.3s';
    
    cancelButton.onmouseover = () => {
        cancelButton.style.backgroundColor = '#C0392B';
    };
    cancelButton.onmouseout = () => {
        cancelButton.style.backgroundColor = '#E74C3C';
    };

    cancelButton.onclick = () => {
        fetch('/cancel-rematch/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                friend_room_code: friendRoomCode
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (window.setupSocket) {
                    window.setupSocket.close();
                }
                modalDiv.remove();
                window.location.href = '/';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error canceling rematch');
        });
    };

    modalDiv.appendChild(spinnerDiv);
    modalDiv.appendChild(messageDiv);
    modalDiv.appendChild(cancelButton);
    document.body.appendChild(modalDiv);

    return modalDiv;
}

function cancelRematch(friendRoomCode) {
    fetch('/cancel-rematch/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            friend_room_code: friendRoomCode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Hide waiting UI and show regular game over UI
            hideRematchWaitingUI();
            showRegularGameOverUI();
        }
    });
}

function leaveFriendRoom(friendRoomCode) {
    fetch('/leave-friend-room/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            friend_room_code: friendRoomCode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = '/';
        }
    });
}
