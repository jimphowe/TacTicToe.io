window.PlayerGuide = function () {
  const [isOpen, setIsOpen] = React.useState(false);
  const [currentPage, setCurrentPage] = React.useState(0);

  const guidePages = [
    {
      title: "Objective",
      content: "Get 3 of your pieces in a line anywhere on the 3x3x3 cube. Winning lines can run along any axis, across any face diagonally, or through the cube's center from corner to corner. Players alternate turns until someone completes a line or the cube fills up (a tie).",
      images: ["/static/images/red_wins.png", "/static/images/tie_game.png"]
    },
    {
      title: "The Twist",
      content: "On your turn, place a piece on any empty spot on the cube's outer surface. You can also push: if a spot is occupied, placing there pushes that piece (and any behind it) deeper into the cube, as long as there's an empty space for them to move into. Rotate the cube using the on-screen buttons or W, A, S, D keys to play on any face.",
      images: ["/static/images/before_push.png", "/static/images/after_push.png"]
    },
    {
      title: "Pushing Power",
      content: "Pushing pieces costs \"Pushing Power\" — one power per piece pushed. You gain power as the game progresses: half a power after each of your turns. Red starts with 0 power and Blue starts with 1, which helps balance the first-move advantage.",
      images: ["/static/images/power_controls.png"]
    },
    {
      title: "Blocker Pieces",
      content: "Blockers are neutral pieces you can place in addition to your regular move. Use them strategically to block your opponent or protect key positions. When placing a blocker, you must choose an empty spot — you cannot push when placing a blocker.",
      images: ["/static/images/blocker_controls.png"]
    },
    {
      title: "Game Setup",
      content: "Eight neutral black pieces start on the cube as obstacles, randomly placed each game. This ensures every game is different, so you'll need to adapt your strategy to each new configuration.",
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
