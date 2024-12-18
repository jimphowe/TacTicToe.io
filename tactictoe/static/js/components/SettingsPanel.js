window.SettingsPanel = function() {
  const [isOpen, setIsOpen] = React.useState(false);
  const [neutralPiecesHidden, setNeutralPiecesHidden] = React.useState(false);
  const [soundsMuted, setSoundsMuted] = React.useState(false);

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

  // Custom checkbox button with larger, higher checkmark
  const CustomCheckbox = React.createElement(
    'div',
    {
      style: {
        position: 'fixed',
        top: 0,
        right: 0,
        zIndex: 1000,
        pointerEvents: 'none'
      }
    },
    React.createElement(
      'button',
      {
        onClick: togglePanel,
        style: {
          position: 'absolute',
          top: '28px',
          right: '36px',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: 0,
          pointerEvents: 'auto'
        }
      },
      React.createElement(window.Icons.Settings, {
        className: 'text-white hover:text-gray-300 transition-colors'
      })
    ),
    isOpen && React.createElement(
      'div',
      {
        style: {
          position: 'absolute',
          top: '20px',
          right: '20px',
          backgroundColor: '#d1d5db',
          padding: '24px',
          borderRadius: '8px',
          width: '250px',
          pointerEvents: 'auto',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          color: '#1f2937'
        }
      },
      React.createElement(
        'div',
        {
          style: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
            position: 'relative'
          }
        },
        React.createElement('h2', { 
          style: {
            fontSize: '18px',
            fontWeight: 'bold',
            margin: 0
          }
        }, 'Settings'),
        React.createElement(
          'button',
          {
            onClick: togglePanel,
            style: {
              position: 'absolute',
              top: '-8px',
              right: '-8px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '4px'
            }
          },
          React.createElement(window.Icons.X, {
            className: 'text-gray-700 w-8 h-8 hover:text-gray-900'
          })
        )
      ),
      React.createElement(
        'div',
        {
          style: {
            display: 'flex',
            flexDirection: 'column',
            gap: '16px'
          }
        },
        React.createElement(
          'label',
          { 
            style: {
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              cursor: 'pointer'
            }
          },
          React.createElement(
            'button',
            {
              onClick: toggleNeutralPieces,
              style: {
                position: 'relative',
                width: '24px',
                height: '24px',
                border: '2px solid #4b5563',
                backgroundColor: neutralPiecesHidden ? '#e5e7eb' : 'white',
                borderRadius: '4px',
                cursor: 'pointer',
                padding: 0,
                marginRight: '4px'
              }
            },
            neutralPiecesHidden && React.createElement(
              'svg',
              {
                viewBox: '0 0 24 24',
                style: {
                  position: 'absolute',
                  left: '-8px',
                  top: '-14px',
                  width: '40px',
                  height: '40px',
                  pointerEvents: 'none'
                }
              },
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
          {
            style: {
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              justifyContent: 'center',
              marginTop: '12px',
              marginBottom: '4px',
            }
          },
          React.createElement(
            'button',
            {
              onClick: toggleSounds,
              style: {
                position: 'relative',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '8px',
                borderRadius: '4px',
                backgroundColor: '#e5e7eb'
              }
            },
            React.createElement(window.Icons.Volume, {
              className: 'text-gray-700',
              width: '32',
              height: '32',
            }),
            soundsMuted && React.createElement(
              'div',
              {
                style: {
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%) rotate(-45deg)',
                  width: '100%',
                  height: '4px',
                  backgroundColor: '#ef4444'
                }
              }
            )
          ),
        )
      )
    )
  );

  return CustomCheckbox;
};