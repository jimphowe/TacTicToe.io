window.PlayerGuide = function () {
  const [isOpen, setIsOpen] = React.useState(false);
  const [currentPage, setCurrentPage] = React.useState(0);

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

  const toggleModal = () => {
    setIsOpen(!isOpen);
    if (!isOpen) setCurrentPage(0);
  };

  const totalPages = guidePages.length;

  const BookButton = React.createElement(
    'div',
    { className: 'player-guide-button-container' },
    React.createElement(
      'button',
      { onClick: toggleModal, className: 'player-guide-button' },
      React.createElement('i', { className: 'fas fa-book player-guide-icon' })
    ),
    isOpen &&
      React.createElement(
        'div',
        { className: 'player-guide-modal' },
        [
          React.createElement(
            'button',
            { onClick: toggleModal, className: 'player-guide-close-button' },
            React.createElement('svg', {
              width: '20',
              height: '20',
              viewBox: '0 0 24 24',
              fill: 'none',
              stroke: '#3b82f6',
              strokeWidth: '2',
              strokeLinecap: 'round',
              strokeLinejoin: 'round',
              children: [
                React.createElement('path', { key: 'x1', d: 'M18 6 6 18' }),
                React.createElement('path', { key: 'x2', d: 'm6 6 12 12' })
              ]
            })
          ),
          React.createElement(
            'h2',
            { className: 'player-guide-title' },
            guidePages[currentPage].title
          ),
          React.createElement(
            'p',
            { className: 'player-guide-content' },
            guidePages[currentPage].content
          ),
          React.createElement(
            'div',
            { className: 'player-guide-images' },
            guidePages[currentPage].images.map((src, i) =>
              React.createElement('img', {
                key: i,
                src: src,
                alt: `${guidePages[currentPage].title} illustration ${i + 1}`,
                className: 'player-guide-image',
                style: {
                  width: guidePages[currentPage].images.length > 1 ? '45%' : '80%',
                }
              })
            )
          ),
          React.createElement(
            'div',
            { className: 'player-guide-nav' },
            [
              React.createElement(
                'button',
                {
                  onClick: () => setCurrentPage(currentPage - 1),
                  disabled: currentPage === 0,
                  className: 'player-guide-nav-button'
                },
                'Previous'
              ),
              React.createElement(
                'div',
                { className: 'player-guide-page-indicators' },
                [...Array(totalPages)].map((_, i) =>
                  React.createElement('button', {
                    key: i,
                    onClick: () => setCurrentPage(i),
                    className: `player-guide-indicator-dot ${i === currentPage ? 'active' : ''}`
                  })
                )
              ),
              React.createElement(
                'button',
                {
                  onClick: () => setCurrentPage(currentPage + 1),
                  disabled: currentPage === totalPages - 1,
                  className: 'player-guide-nav-button'
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
