window.PlayerGuide = function() {
    const [isOpen, setIsOpen] = React.useState(false);
    const [currentPage, setCurrentPage] = React.useState(0);
    
    // Guide content pages
    const guidePages = [
      {
        title: "Objective",
        content: "Position 3 of your pieces in a row anywhere on the three-dimensional 3x3x3 game board. Players alternate turns placing their pieces until one achieves a run of 3 or the board fills up without a winner. If the board fills up, it's a tie!",
        images: ["/static/images/red_wins.png", "/static/images/tie_game.png"]
      },
      {
        title: "The Twist",
        content: "You can either place a new piece in an empty square, or push existing pieces toward the back of the cube, as long as the row you push isn't full. Rotate the board using the buttons on screen or W, A, S, D to play on any side of the board.",
        images: ["/static/images/before_push.png", "/static/images/after_push.png"]
      },
      {
        title: "Pushing Power",
        content: "Pushing existing pieces in the cube costs \"Pushing Power\" for each piece you push. Throughout the game you will gain half a power per turn after you make your move. To start the game, Red has 0 power and Blue has 1. This serves to even out the first player advantage.",
        images: ["/static/images/power_controls.png"]
      },
      {
        title: "Blocker Pieces",
        content: "Blocker pieces are neutral pieces you can place in addition to your regular move. Use them strategically to prevent your opponent from winning or to secure your pieces in advantageous positions. Blockers must be placed on empty squares and cannot push other pieces.",
        images: ["/static/images/blocker_controls.png"]
      },
      {
        title: "Game Setup",
        content: "Eight \"neutral\" black pieces start on the board as obstacles, placed in a random pattern generated each time you play. This makes every game unique, so your strategies need to be adaptable.",
        images: ["/static/images/start_1.png", "/static/images/start_2.png"]
      }
    ];
  
    const totalPages = guidePages.length;
  
    const toggleModal = () => {
      setIsOpen(!isOpen);
      if (!isOpen) {
        setCurrentPage(0); // Reset to first page when opening
      }
    };
  
    const nextPage = () => {
      if (currentPage < totalPages - 1) {
        setCurrentPage(currentPage + 1);
      }
    };
  
    const prevPage = () => {
      if (currentPage > 0) {
        setCurrentPage(currentPage - 1);
      }
    };
  
    const goToPage = (index) => {
      setCurrentPage(index);
    };
  
    // Custom book icon button
    const BookButton = React.createElement(
      'div',
      {
        style: {
          position: 'fixed',
          top: 0,
          right: '40px',
          zIndex: 1000,
          pointerEvents: 'none'
        }
      },
      React.createElement(
        'button',
        {
          onClick: toggleModal,
          style: {
            position: 'absolute',
            top: '84px',
            right: '0',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: 0,
            pointerEvents: 'auto'
          }
        },
        React.createElement('i', {
          className: 'fas fa-book',
          style: {
            fontSize: '32px',
            color: 'white'
          }
        })
      ),
      isOpen && React.createElement(
        'div',
        {
          style: {
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            backgroundColor: 'rgba(20, 30, 40, 0.95)',
            borderRadius: '8px',
            width: '90%',
            maxWidth: '600px',
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: '24px',
            pointerEvents: 'auto',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            color: 'white',
            zIndex: 1001
          }
        },
        [
          // Close button
          React.createElement(
            'button',
            {
              onClick: toggleModal,
              style: {
                position: 'absolute',
                top: '12px',
                right: '12px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '4px'
              }
            },
            React.createElement('svg', {
                width: '20',
                height: '20',
                viewBox: '0 0 24 24',
                fill: 'none',
                stroke: '#3b82f6',
                strokeWidth: '2',
                strokeLinecap: 'round',
                strokeLinejoin: 'round'
              }, [
                React.createElement('path', {
                  key: 'x1',
                  d: 'M18 6 6 18'
                }),
                React.createElement('path', {
                  key: 'x2',
                  d: 'm6 6 12 12'
                })
              ])
          ),
          
          // Title
          React.createElement(
            'h2',
            { 
              style: {
                fontSize: '24px',
                fontWeight: 'bold',
                marginBottom: '16px',
                textAlign: 'center'
              }
            },
            guidePages[currentPage].title
          ),
          
          // Content
          React.createElement(
            'p',
            {
              style: {
                fontSize: '16px',
                lineHeight: '1.6',
                marginBottom: '20px'
              }
            },
            guidePages[currentPage].content
          ),
          
          // Images container
          React.createElement(
            'div',
            {
              style: {
                display: 'flex',
                justifyContent: 'center',
                gap: '16px',
                marginBottom: '24px',
                flexWrap: 'wrap'
              }
            },
            guidePages[currentPage].images.map((src, i) => 
              React.createElement(
                'img',
                {
                  key: i,
                  src: src,
                  alt: `${guidePages[currentPage].title} illustration ${i+1}`,
                  style: {
                    width: guidePages[currentPage].images.length > 1 ? '45%' : '80%',
                    maxHeight: '200px',
                    objectFit: 'contain',
                    borderRadius: '4px'
                  }
                }
              )
            )
          ),
          
          // Navigation buttons
          React.createElement(
            'div',
            {
              style: {
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginTop: '16px'
              }
            },
            [
              // Prev button
              React.createElement(
                'button',
                {
                  onClick: prevPage,
                  disabled: currentPage === 0,
                  style: {
                    padding: '8px 16px',
                    background: currentPage === 0 ? '#4a5568' : '#2d3748',
                    color: currentPage === 0 ? '#a0aec0' : 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: currentPage === 0 ? 'not-allowed' : 'pointer'
                  }
                },
                'Previous'
              ),
              
              // Page indicator
              React.createElement(
                'div',
                {
                  style: {
                    display: 'flex',
                    gap: '8px'
                  }
                },
                [...Array(totalPages)].map((_, i) => 
                  React.createElement(
                    'button',
                    {
                      key: i,
                      onClick: () => goToPage(i),
                      style: {
                        width: '10px',
                        height: '10px',
                        borderRadius: '50%',
                        background: i === currentPage ? 'white' : '#4a5568',
                        border: 'none',
                        padding: 0,
                        cursor: 'pointer'
                      }
                    }
                  )
                )
              ),
              
              // Next button
              React.createElement(
                'button',
                {
                  onClick: nextPage,
                  disabled: currentPage === totalPages - 1,
                  style: {
                    padding: '8px 16px',
                    background: currentPage === totalPages - 1 ? '#4a5568' : '#2d3748',
                    color: currentPage === totalPages - 1 ? '#a0aec0' : 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: currentPage === totalPages - 1 ? 'not-allowed' : 'pointer'
                  }
                },
                'Next'
              )
            ]
          )
        ]
      )
    );
  
    return BookButton;
  };