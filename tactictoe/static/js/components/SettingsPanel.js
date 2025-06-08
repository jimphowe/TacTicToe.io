window.SettingsPanel = function () {
  const [isOpen, setIsOpen] = React.useState(false);
  const [neutralPiecesHidden, setNeutralPiecesHidden] = React.useState(false);
  const [soundsMuted, setSoundsMuted] = React.useState(false);
  const [isMultiplayer, setIsMultiplayer] = React.useState(false);

  React.useEffect(() => {
    const topBar = document.querySelector('.top-bar');
    setIsMultiplayer(!!topBar);
  }, []);

  const togglePanel = () => {
    setIsOpen(!isOpen);
  };

  const toggleNeutralPieces = () => {
    setNeutralPiecesHidden(!neutralPiecesHidden);
    window.toggleNeutralPiecesVisibility();
  };

  const toggleSounds = () => {
    setSoundsMuted(!soundsMuted);
    window.toggleSoundsMuted(!soundsMuted);
  };

  return React.createElement(
    'div',
    { className: 'settings-toggle-container' },
    React.createElement(
      'button',
      {
        onClick: togglePanel,
        className: 'settings-toggle-button',
        style: {
          top: isMultiplayer ? '98px' : '28px',
          right: '36px',
        }
      },
      React.createElement(window.Icons.Settings, {
        className: 'text-white hover:text-gray-300 transition-colors'
      })
    ),
    isOpen && React.createElement(
      'div',
      {
        className: 'settings-panel',
        style: {
          top: isMultiplayer ? '90px' : '20px',
          right: '20px',
        }
      },
      React.createElement(
        'div',
        { className: 'settings-header' },
        React.createElement('h2', { className: 'settings-title' }, 'Settings'),
        React.createElement(
          'button',
          { onClick: togglePanel, className: 'settings-close-button' },
          React.createElement(window.Icons.X, {
            className: 'text-gray-700 w-8 h-8 hover:text-gray-900'
          })
        )
      ),
      React.createElement(
        'div',
        { className: 'settings-content' },
        React.createElement(
          'label',
          { className: 'checkbox-label' },
          React.createElement(
            'button',
            {
              onClick: toggleNeutralPieces,
              className: `custom-checkbox ${neutralPiecesHidden ? 'checked' : ''}`
            },
            neutralPiecesHidden && React.createElement(
              'svg',
              { viewBox: '0 0 24 24' },
              React.createElement('path', {
                d: 'M20 6L9 17L4 12',
                stroke: '#ef4444',
                strokeWidth: '4',
                strokeLinecap: 'round',
                strokeLinejoin: 'round',
                fill: 'none'
              })
            )
          ),
          React.createElement('span', null, 'Hide neutral pieces')
        ),
        React.createElement(
          'div',
          { className: 'sounds-toggle-container' },
          React.createElement(
            'button',
            { onClick: toggleSounds, className: 'sound-button' },
            React.createElement(window.Icons.Volume, {
              className: 'text-gray-700',
              width: '32',
              height: '32'
            }),
            soundsMuted && React.createElement('div', {
              className: 'sound-muted-indicator'
            })
          )
        )
      )
    )
  );
};
