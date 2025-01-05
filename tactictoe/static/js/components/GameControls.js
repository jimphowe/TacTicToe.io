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
    const handleBlockerChange = () => {
      setIsBlockerSelected(window.isBlockerSelected);
    };
    
    window.addEventListener('blockerStateChanged', handleBlockerChange);
    return () => window.removeEventListener('blockerStateChanged', handleBlockerChange);
  }, []);

  React.useEffect(() => {
    window.updateControlPanel = function(gameState, redPower, bluePower) {
      let redBlockers = 0;
      let blueBlockers = 0;
      let moves = 0;

      gameState.forEach(layer => {
        layer.forEach(row => {
          row.forEach(cell => {
            if (cell === 'RED_BLOCKER') redBlockers++;
            if (cell === 'BLUE_BLOCKER') blueBlockers++;
            if (cell === 'RED' || cell === 'BLUE') moves++;
          });
        });
      });

      const movePhase = moves % 4;
      const redHalfPower = movePhase === 1 || movePhase === 2;
      const blueHalfPower = movePhase === 2 || movePhase === 3;
      
      const redValue = redPower + (redHalfPower ? 0.5 : 0);
      const blueValue = bluePower + (blueHalfPower ? 0.5 : 0);

      setRedBlockerCount(redBlockers);
      setBlueBlockerCount(blueBlockers);
      setMyPower(window.playerColor === 'RED' ? redValue : blueValue);
      setOpponentPower(window.playerColor === 'RED' ? blueValue : redValue);
    };

    return () => {
      window.updateControlPanel = undefined;
    };
  }, []);

  const handleBlockerClick = (e) => {
    e.stopPropagation();
    
    const newValue = !window.isBlockerSelected;
    window.isBlockerSelected = newValue;
    setIsBlockerSelected(newValue);
    
    window.dispatchEvent(new Event('blockerStateChanged'));
  };

  const PowerBar = ({ value, color, nextTurnGainsPower }) => {
    const totalBars = 5;
    const bars = [];
    
    for (let i = 0; i < totalBars; i++) {
      const isFullyFilled = i < Math.floor(value);
      const isHalfFilled = i === Math.floor(value) && value % 1 !== 0;
      const showNextTurnIndicator = i === Math.floor(value) && nextTurnGainsPower && i < totalBars;
      
      bars.push(
        React.createElement(
          'div',
          {
            key: i,
            style: {
              width: '20px',
              height: '20px',
              borderRadius: '4px',
              backgroundColor: '#374151',
              position: 'relative',
              overflow: 'hidden'
            }
          },
          [
            // Full or half fill
            React.createElement('div', {
              key: 'fill',
              style: {
                position: 'absolute',
                top: 0,
                left: 0,
                width: isFullyFilled ? '100%' : (isHalfFilled ? '50%' : '0%'),
                height: '100%',
                backgroundColor: color === 'red' ? '#ef4444' : '#3b82f6',
                transition: 'width 300ms, background-color 300ms'
              }
            }),
            // Next turn indicator
            showNextTurnIndicator && React.createElement('div', {
              key: 'indicator',
              style: {
                position: 'absolute',
                top: 0,
                right: 0,
                width: '50%',
                height: '100%',
                backgroundColor: color === 'red' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(59, 130, 246, 0.3)',
                transition: 'background-color 300ms'
              }
            })
          ]
        )
      );
    }
    
    return React.createElement(
      'div',
      {
        style: {
          display: 'flex',
          gap: '4px'
        }
      },
      bars
    );
  };

  const ShieldIcon = ({ filled, color }) => React.createElement(
    'div',
    {
      style: {
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '24px',
        height: '24px',
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
    const rows = [
      { 
        color: 'red', 
        power: window.playerColor === 'RED' ? myPower : opponentPower,
        nextTurnGainsPower: false
      },
      { 
        color: 'blue', 
        power: window.playerColor === 'RED' ? opponentPower : myPower,
        nextTurnGainsPower: false
      }
    ];
  
    return React.createElement(
      'div',
      {
        style: {
          marginBottom: isDesktop ? '40px' : '12px'
        }
      },
      isDesktop ? 
        // Desktop layout
        [
          React.createElement(SectionHeader, { key: 'header', text: 'Pushing Power' }),
          ...rows.map(({ color, power, nextTurnGainsPower }, index) => 
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
                  Math.floor(power)
                ),
                React.createElement(PowerBar, { 
                  key: 'bar', 
                  value: power, 
                  color,
                  nextTurnGainsPower: nextTurnGainsPower
                })
              ]
            )
          )
        ] :
        // Mobile layout
        React.createElement(
          'div',
          {
            style: {
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }
          },
          [
            React.createElement(
              'span',
              {
                key: 'label',
                style: {
                  color: '#d1d5db',
                  fontSize: '14px',
                  lineHeight: '1',
                  marginRight: '12px',
                  display: 'flex',
                  flexDirection: 'column'
                }
              },
              [
                React.createElement('span', { key: 'word1' }, 'Pushing'),
                React.createElement('span', { key: 'word2' }, 'Power')
              ]
            ),
            React.createElement(
              'div',
              { key: 'rows' },
              rows.map(({ color, power, nextTurnGainsPower }, index) => 
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
                    React.createElement(PowerBar, { 
                      key: 'bar', 
                      value: power, 
                      color,
                      nextTurnGainsPower: nextTurnGainsPower
                    })
                  ]
                )
              )
            )
          ]
        )
    );
  };
  
  const BlockerSection = () => {
    const rows = [
      { color: 'red', count: redBlockerCount, isPlayer: window.playerColor === 'RED' },
      { color: 'blue', count: blueBlockerCount, isPlayer: window.playerColor === 'BLUE' }
    ];
  
    const blockerButton = window.playerColor && React.createElement(
      'div',
      {
        style: {
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '4px'
        }
      },
      [
        React.createElement(
          'button',
          {
            onClick: handleBlockerClick,
            style: {
              width: isDesktop ? '80px' : '60px',
              height: isDesktop ? '80px' : '60px',
              backgroundColor: isBlockerSelected ? '#e7e470' : '#1f2937',
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
              transform: isBlockerSelected ? 'scale(1.05)' : 'scale(1)'
            }
          },
          React.createElement('img', {
            src: `/static/images/${window.playerColor.toLowerCase()}_blocker.png`,
            alt: 'Blocker piece',
            style: {
              width: isDesktop ? '60px' : '40px',
              height: isDesktop ? '60px' : '40px'
            }
          })
        ),
        isDesktop && React.createElement(
          'span',
          {
            style: {
              fontSize: '12px',
              color: '#9ca3af',
              textAlign: 'center'
            }
          },
          'Place Blocker'
        )
      ]
    );
  
    return React.createElement(
      'div',
      null,
      isDesktop ?
        // Desktop layout
        [
          React.createElement(SectionHeader, { key: 'header', text: 'Blocker Pieces' }),
          React.createElement(
            'div',
            {
              style: {
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '16px'
              }
            },
            [
              React.createElement(
                'div',
                {
                  key: 'blocker-rows',
                  style: {
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px'
                  }
                },
                rows.map(({ color, count }) =>
                  React.createElement(
                    'div',
                    {
                      key: color,
                      style: {
                        display: 'flex',
                        alignItems: 'center'
                      }
                    },
                    [
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
                        Array(3).fill().map((_, i) => React.createElement(ShieldIcon, {
                          key: i,
                          filled: i < (3 - count),
                          color
                        }))
                      )
                    ]
                  )
                )
              ),
              blockerButton
            ]
          )
        ] :
        // Mobile layout
        React.createElement(
          'div',
          {
            style: {
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }
          },
          [
            React.createElement(
              'span',
              {
                key: 'label',
                style: {
                  color: '#d1d5db',
                  fontSize: '14px',
                  lineHeight: '1',
                  marginRight: '12px',
                  display: 'flex',
                  flexDirection: 'column'
                }
              },
              [
                React.createElement('span', { key: 'word1' }, 'Blocker'),
                React.createElement('span', { key: 'word2' }, 'Pieces')
              ]
            ),
            React.createElement(
              'div',
              {
                style: {
                  display: 'flex',
                  gap: '16px',
                  alignItems: 'center'
                }
              },
              [
                React.createElement(
                  'div',
                  {
                    key: 'blocker-rows',
                    style: {
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px'
                    }
                  },
                  rows.map(({ color, count }) =>
                    React.createElement(
                      'div',
                      {
                        key: color,
                        style: {
                          display: 'flex',
                          gap: '4px'
                        }
                      },
                      Array(3).fill().map((_, i) => React.createElement(ShieldIcon, {
                        key: i,
                        filled: i < (3 - count),
                        color
                      }))
                    )
                  )
                ),
                blockerButton
              ]
            )
          ]
        )
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
          bottom: '4%',
          left: '50%',
          transform: 'translateX(-50%)'
        }),
        backgroundColor: 'rgba(30, 41, 59, 0.9)',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        padding: isDesktop ? '20px 28px' : '16px',
        minWidth: isDesktop ? '300px' : '260px',
        zIndex: 50
      }
    },
    [
      React.createElement(PowerSection, { key: 'power' }),
      React.createElement(BlockerSection, { key: 'blockers' })
    ]
  );
};