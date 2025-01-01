window.GameControls = function() {
  const [myPower, setMyPower] = React.useState(window.playerColor === 'RED' ? window.redPower : window.bluePower);
  const [opponentPower, setOpponentPower] = React.useState(window.playerColor === 'RED' ? window.bluePower : window.redPower);
  const [redBlockerCount, setRedBlockerCount] = React.useState(0);
  const [blueBlockerCount, setBlueBlockerCount] = React.useState(0);
  const [isBlockerSelected, setIsBlockerSelected] = React.useState(false);
  const [isDesktop, setIsDesktop] = React.useState(window.innerWidth > 768);
  
  React.useEffect(() => {
    const handleResize = () => {
      setIsDesktop(window.innerWidth > 768);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  React.useEffect(() => {
    // Keep React state in sync with global state
    const handleBlockerChange = () => {
      setIsBlockerSelected(window.isBlockerSelected);
    };
    
    window.addEventListener('blockerStateChanged', handleBlockerChange);
    return () => window.removeEventListener('blockerStateChanged', handleBlockerChange);
  }, []);

  const myPowerValue = Math.min(5, Math.max(0, myPower));
  const opponentPowerValue = Math.min(5, Math.max(0, opponentPower));
  
  window.updatePowerDisplay = function(redPower, bluePower) {
    setMyPower(window.playerColor === 'RED' ? redPower : bluePower);
    setOpponentPower(window.playerColor === 'RED' ? bluePower : redPower);
  };

  React.useEffect(() => {
    window.updateBlockerDisplay = function(gameState) {
      let redCount = 0;
      let blueCount = 0;
      let moveCount = 0;

      gameState.forEach(layer => {
        layer.forEach(row => {
          row.forEach(cell => {
            if (cell === 'RED_BLOCKER') redCount++;
            if (cell === 'BLUE_BLOCKER') blueCount++;
            if (cell === 'RED' || cell === 'BLUE') moveCount++;
          });
        });
      });

      setRedBlockerCount(redCount);
      setBlueBlockerCount(blueCount);
      window.moveCount = moveCount;
    };
  }, []);

  const handleBlockerClick = (e) => {
    e.stopPropagation();
    
    const newValue = !window.isBlockerSelected;
    window.isBlockerSelected = newValue;
    setIsBlockerSelected(newValue);
    
    // Dispatch event for any other components that need to know
    window.dispatchEvent(new Event('blockerStateChanged'));
  };

  const ShieldIcon = ({ filled, color }) => React.createElement(
    'div',
    {
      style: {
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '20px',
        height: '20px',
        flexShrink: 0
      }
    },
    React.createElement(
      'svg',
      {
        width: '100%',
        height: '100%',
        viewBox: '0 0 24 24',
        fill: filled ? (color === 'red' ? '#ef4444' : '#3b82f6') : '#374151'
      },
      React.createElement('path', {
        d: 'M3.783 2.826L12 1l8.217 1.826a1 1 0 0 1 .783.976v9.987a6 6 0 0 1-2.672 4.992L12 23l-6.328-4.219A6 6 0 0 1 3 13.79V3.802a1 1 0 0 1 .783-.976z'
      })
    )
  );

  const PowerBar = ({ value, color }) => React.createElement(
    'div',
    {
      style: {
        display: 'flex',
        gap: '4px'
      }
    },
    Array(5).fill().map((_, i) => React.createElement(
      'div',
      {
        key: i,
        style: {
          width: '20px',
          height: '20px',
          borderRadius: '4px',
          backgroundColor: i < value ? (color === 'red' ? '#ef4444' : '#3b82f6') : '#374151',
          transition: 'background-color 300ms'
        }
      }
    ))
  );

  const SectionHeader = ({ text }) => React.createElement(
    'h3',
    {
      style: {
        fontSize: '22px',
        fontWeight: '600',
        marginBottom: '28px',
        textAlign: 'center',
        color: '#ffffff'
      }
    },
    text
  );

  const ColorDot = ({ color }) => React.createElement(
    'div',
    {
      style: {
        width: isDesktop ? '16px' : '12px',
        height: isDesktop ? '16px' : '12px',
        borderRadius: '50%',
        backgroundColor: color === 'red' ? '#ef4444' : '#3b82f6',
        marginRight: isDesktop ? '12px' : '8px'
      }
    }
  );

  const PlayerLabel = ({ color }) => React.createElement(
    'span',
    {
      style: {
        color: '#d1d5db',
        fontSize: isDesktop ? '16px' : '14px',
        minWidth: '50px',
        display: isDesktop ? 'block' : 'none'
      }
    },
    color === 'red' ? 'Red' : 'Blue'
  );

  const PowerSection = () => {
    const redFirst = window.playerColor === 'RED';
    const rows = [
      { color: redFirst ? 'red' : 'blue', power: redFirst ? myPowerValue : opponentPowerValue },
      { color: redFirst ? 'blue' : 'red', power: redFirst ? opponentPowerValue : myPowerValue }
    ];

    return React.createElement(
      'div',
      {
        style: {
          marginBottom: isDesktop ? '40px' : '12px'
        }
      },
      [
        isDesktop && React.createElement(SectionHeader, { key: 'header', text: 'Pushing Power' }),
        ...rows.map(({ color, power }, index) => 
          React.createElement(
            'div',
            {
              key: color,
              style: {
                display: 'flex',
                alignItems: 'center',
                marginBottom: index === 0 ? '12px' : 0
              }
            },
            [
              React.createElement(ColorDot, { key: 'dot', color }),
              React.createElement(PlayerLabel, { key: 'label', color }),
              React.createElement(
                'span',
                {
                  key: 'value',
                  style: {
                    color: '#ffffff',
                    fontWeight: 500,
                    minWidth: '12px',
                    textAlign: 'center',
                    marginRight: '8px'
                  }
                },
                power
              ),
              React.createElement(PowerBar, { key: 'bar', value: power, color })
            ]
          )
        )
      ]
    );
  };

  const BlockerSection = () => {
    const redFirst = window.playerColor === 'RED';
    const rows = [
      { color: redFirst ? 'red' : 'blue', count: redFirst ? redBlockerCount : blueBlockerCount, isPlayer: true },
      { color: redFirst ? 'blue' : 'red', count: redFirst ? blueBlockerCount : redBlockerCount, isPlayer: false }
    ];

    return React.createElement(
      'div',
      null,
      [
        isDesktop && React.createElement(SectionHeader, { key: 'header', text: 'Blocker Pieces' }),
        ...rows.map(({ color, count, isPlayer }, index) =>
          React.createElement(
            'div',
            {
              key: color,
              style: {
                display: 'flex',
                alignItems: 'center',
                marginBottom: index === 0 ? '12px' : 0
              }
            },
            [
              React.createElement(ColorDot, { key: 'dot', color }),
              React.createElement(PlayerLabel, { key: 'label', color }),
              React.createElement(
                'div',
                {
                  key: 'shields',
                  style: {
                    display: 'flex',
                    gap: '4px'
                  }
                },
                // Now showing remaining blockers (3 - count)
                Array(3).fill().map((_, i) => React.createElement(ShieldIcon, {
                  key: i,
                  filled: i < (3 - count), // This is the key change
                  color
                }))
              ),
              isPlayer && React.createElement(
                'div',  // Wrapper div for button and label
                {
                  key: 'blocker-container',
                  style: {
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    marginLeft: '12px',
                    gap: '4px'
                  }
                },
                [
                  React.createElement(
                    'button',
                    {
                      key: 'blocker-button',
                      onClick: handleBlockerClick,
                      style: {
                        width: isDesktop ? '80px' : '28px',
                        height: isDesktop ? '80px' : '28px',
                        backgroundColor: isBlockerSelected ? '#FFD700' : '#1f2937',
                        borderRadius: '12px',
                        transition: 'all 300ms',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: '2px solid #4a5568',
                        boxShadow: isBlockerSelected ? 
                          '0 0 10px rgba(255, 215, 0, 0.3)' : 
                          '0 2px 4px rgba(0, 0, 0, 0.2)',
                        transform: isBlockerSelected ? 'scale(1.05)' : 'scale(1)',
                        ':hover': {
                          border: '2px solid #718096',
                          transform: 'scale(1.05)',
                          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)'
                        }
                      }
                    },
                    React.createElement('img', {
                      src: `/static/images/${window.playerColor.toLowerCase()}_blocker.png`,
                      alt: 'Blocker piece',
                      style: {
                        width: isDesktop ? '60px' : '24px',
                        height: isDesktop ? '60px' : '24px'
                      }
                    })
                  ),
                  React.createElement(
                    'span',
                    {
                      key: 'button-label',
                      style: {
                        fontSize: isDesktop ? '12px' : '10px',
                        color: '#9ca3af',
                        textAlign: 'center'
                      }
                    },
                    'Place Blocker'
                  )
                ]
              )
            ]
          )
        )
      ]
    );
  };

  return React.createElement(
    'div',
    {
      style: {
        position: 'fixed',
        ...(isDesktop ? {
          top: '50%',
          left: '60px',
          transform: 'translateY(-50%)',
          maxHeight: '90vh',
          overflowY: 'auto'
        } : {
          top: '96px',
          left: '50%',
          transform: 'translateX(-50%)'
        }),
        backgroundColor: 'rgba(30, 41, 59, 0.9)',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        padding: isDesktop ? '32px 40px' : '16px',
        minWidth: isDesktop ? '400px' : '280px',
        zIndex: 50
      }
    },
    [
      React.createElement(PowerSection, { key: 'power' }),
      React.createElement(BlockerSection, { key: 'blockers' })
    ]
  );
};