window.GameControls = function() {
  const [myPower, setMyPower] = React.useState(window.playerColor === 'RED' ? window.redPower : window.bluePower);
  const [opponentPower, setOpponentPower] = React.useState(window.playerColor === 'RED' ? window.bluePower : window.redPower);
  const [redBlockerCount, setRedBlockerCount] = React.useState(0);
  const [blueBlockerCount, setBlueBlockerCount] = React.useState(0);
  const [isBlockerSelected, setIsBlockerSelected] = React.useState(false);
  const [isDesktop, setIsDesktop] = React.useState(window.innerWidth > 768);
  const [canUndo, setCanUndo] = React.useState(window.canUndo || false);

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
    const handleUndoChange = () => {
      setCanUndo(window.canUndo);
    };
    window.addEventListener('undoStateChanged', handleUndoChange);
    return () => window.removeEventListener('undoStateChanged', handleUndoChange);
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
          { key: i, className: 'power-bar-segment' },
          [
            React.createElement('div', {
              key: 'fill',
              className: 'power-bar-fill',
              style: {
                width: isFullyFilled ? '100%' : (isHalfFilled ? '50%' : '0%'),
                backgroundColor: color === 'red' ? '#ef4444' : '#3b82f6'
              }
            }),
            showNextTurnIndicator && React.createElement('div', {
              key: 'indicator',
              className: 'power-bar-indicator',
              style: {
                backgroundColor: color === 'red' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(59, 130, 246, 0.3)'
              }
            })
          ]
        )
      );
    }

    return React.createElement('div', { className: 'power-bar-container' }, bars);
  };

  const ShieldIcon = ({ filled, color }) => React.createElement(
    'div',
    { className: 'shield-icon' },
    React.createElement('svg', {
      width: '100%',
      height: '100%',
      viewBox: '0 0 24 24',
      fill: filled ? (color === 'red' ? '#ef4444' : '#3b82f6') : '#374151'
    }, React.createElement('path', {
      d: 'M3.783 2.826L12 1l8.217 1.826a1 1 0 0 1 .783.976v9.987a6 6 0 0 1-2.672 4.992L12 23l-6.328-4.219A6 6 0 0 1 3 13.79V3.802a1 1 0 0 1 .783-.976z'
    }))
  );

  const SectionHeader = ({ text }) => React.createElement(
    'h3',
    { className: 'section-header' },
    text
  );

  const PlayerLabel = ({ color }) => React.createElement(
    'span',
    {
      className: `player-label ${isDesktop ? '' : 'mobile'}`,
      style: {
        fontSize: isDesktop ? '16px' : '14px'
      }
    },
    color === 'red' ? 'Red' : 'Blue'
  );

  const PowerSection = () => {
    const rows = [
      { color: 'red', power: window.playerColor === 'RED' ? myPower : opponentPower },
      { color: 'blue', power: window.playerColor === 'RED' ? opponentPower : myPower }
    ];

    return React.createElement(
      'div',
      { style: { marginBottom: isDesktop ? '40px' : '12px' } },
      isDesktop
        ? [
            React.createElement(SectionHeader, { key: 'header', text: 'Pushing Power' }),
            ...rows.map(({ color, power }, index) =>
              React.createElement('div', { key: color, className: 'desktop-row' }, [
                React.createElement(PlayerLabel, { key: 'label', color }),
                React.createElement('span', {
                  key: 'value',
                  style: {
                    color: '#ffffff',
                    fontWeight: 500,
                    minWidth: '12px',
                    textAlign: 'center',
                    marginRight: '8px'
                  }
                }, Math.floor(power)),
                React.createElement(PowerBar, { key: 'bar', value: power, color })
              ])
            )
          ]
        : React.createElement('div', {
            style: { display: 'flex', alignItems: 'center', gap: '12px' }
          }, [
            React.createElement('span', {
              key: 'label',
              style: {
                color: '#d1d5db',
                fontSize: '14px',
                lineHeight: '1',
                marginRight: '12px',
                display: 'flex',
                flexDirection: 'column'
              }
            }, [
              React.createElement('span', { key: 'word1' }, 'Pushing'),
              React.createElement('span', { key: 'word2' }, 'Power')
            ]),
            React.createElement('div', { key: 'rows' },
              rows.map(({ color, power }, index) =>
                React.createElement('div', {
                  key: color,
                  style: {
                    display: 'flex',
                    alignItems: 'center',
                    marginBottom: index === 0 ? '12px' : 0
                  }
                }, [React.createElement(PowerBar, { key: 'bar', value: power, color })])
              )
            )
          ])
    );
  };

  const BlockerSection = () => {
    const rows = [
      { color: 'red', count: redBlockerCount },
      { color: 'blue', count: blueBlockerCount }
    ];

    const blockerButton = window.playerColor && React.createElement('div', { className: 'blocker-button-container' }, [
      React.createElement('button', {
        onClick: handleBlockerClick,
        className: `blocker-button ${isBlockerSelected ? 'active' : 'inactive'}`,
        style: {
          width: isDesktop ? '80px' : '60px',
          height: isDesktop ? '80px' : '60px'
        }
      }, React.createElement('img', {
        src: `/static/images/${window.playerColor.toLowerCase()}_blocker.png`,
        alt: 'Blocker piece',
        style: {
          width: isDesktop ? '60px' : '40px',
          height: isDesktop ? '60px' : '40px'
        }
      })),
      isDesktop && React.createElement('span', { className: 'blocker-caption' }, 'Place Blocker')
    ]);

    return React.createElement('div', null, isDesktop
      ? [
          React.createElement(SectionHeader, { key: 'header', text: 'Blocker Pieces' }),
          React.createElement('div', {
            style: {
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: '16px'
            }
          }, [
            React.createElement('div', { key: 'blocker-rows', className: 'desktop-shield-rows' },
              rows.map(({ color, count }) => React.createElement('div', {
                key: color,
                style: { display: 'flex', alignItems: 'center' }
              }, [
                React.createElement(PlayerLabel, { key: 'label', color }),
                React.createElement('div', { key: 'shields', className: 'desktop-shields' },
                  Array(3).fill().map((_, i) =>
                    React.createElement(ShieldIcon, {
                      key: i,
                      filled: i < (3 - count),
                      color
                    })
                  )
                )
              ]))
            ),
            blockerButton
          ])
        ]
      : React.createElement('div', {
          style: { display: 'flex', alignItems: 'center', gap: '12px' }
        }, [
          React.createElement('span', {
            key: 'label',
            style: {
              color: '#d1d5db',
              fontSize: '14px',
              lineHeight: '1',
              marginRight: '12px',
              display: 'flex',
              flexDirection: 'column'
            }
          }, [
            React.createElement('span', { key: 'word1' }, 'Blocker'),
            React.createElement('span', { key: 'word2' }, 'Pieces')
          ]),
          React.createElement('div', {
            style: { display: 'flex', gap: '16px', alignItems: 'center' }
          }, [
            React.createElement('div', {
              key: 'blocker-rows',
              style: { display: 'flex', flexDirection: 'column', gap: '8px' }
            }, rows.map(({ color, count }) =>
              React.createElement('div', {
                key: color,
                style: { display: 'flex', gap: '4px' }
              }, Array(3).fill().map((_, i) =>
                React.createElement(ShieldIcon, {
                  key: i,
                  filled: i < (3 - count),
                  color
                })
              ))
            )),
            blockerButton
          ])
        ])
    );
  };

  const handleUndoClick = (e) => {
    e.stopPropagation();
    if (window.handleUndo && canUndo) {
      window.handleUndo();
    }
  };

  const UndoSection = () => {
    const undoButton = React.createElement('button', {
      onClick: handleUndoClick,
      disabled: !canUndo,
      className: `undo-button ${canUndo ? 'active' : 'inactive'}`,
      style: {
        padding: isDesktop ? '12px 24px' : '8px 16px',
        fontSize: isDesktop ? '14px' : '12px',
        fontWeight: '500',
        color: canUndo ? '#ffffff' : '#6b7280',
        backgroundColor: canUndo ? '#4b5563' : '#1f2937',
        border: 'none',
        borderRadius: '8px',
        cursor: canUndo ? 'pointer' : 'not-allowed',
        transition: 'all 0.2s ease',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }
    }, [
      React.createElement('i', {
        key: 'icon',
        className: 'fas fa-rotate-left',
        style: { fontSize: isDesktop ? '16px' : '12px' }
      }),
      React.createElement('span', { key: 'text' }, 'Undo')
    ]);

    return React.createElement('div', {
      style: {
        marginTop: isDesktop ? '24px' : '12px',
        display: 'flex',
        justifyContent: 'center'
      }
    }, undoButton);
  };

  const sections = [
    React.createElement(PowerSection, { key: 'power' }),
    React.createElement(BlockerSection, { key: 'blockers' })
  ];

  if (window.undoEnabled) {
    sections.push(React.createElement(UndoSection, { key: 'undo' }));
  }

  return React.createElement(
    'div',
    {
      className: `game-controls-container ${isDesktop ? 'game-controls-desktop' : 'game-controls-mobile'}`
    },
    sections
  );
};
