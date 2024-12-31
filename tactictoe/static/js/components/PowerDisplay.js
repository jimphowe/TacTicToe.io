window.PowerDisplay = function() {
    const [myPower, setMyPower] = React.useState(window.playerColor === 'RED' ? window.redPower : window.bluePower);
    const [opponentPower, setOpponentPower] = React.useState(window.playerColor === 'RED' ? window.bluePower : window.redPower);
    
    // Ensure values are between 0-5
    const myPowerValue = Math.min(5, Math.max(0, myPower));
    const opponentPowerValue = Math.min(5, Math.max(0, opponentPower));
    
    window.updatePowerDisplay = function(redPower, bluePower) {
      setMyPower(window.playerColor === 'RED' ? redPower : bluePower);
      setOpponentPower(window.playerColor === 'RED' ? bluePower : redPower);
    };
    
    const style = {
      container: {
        position: 'fixed',
        backgroundColor: 'rgba(30, 41, 59, 0.9)',
        padding: '16px',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        zIndex: 1000,
        ...(window.innerWidth <= 768 ? {
          top: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
        } : {
          top: '50%',
          left: '60px',
          transform: 'translateY(calc(50% + 130px))',
        })
      }
    };
    
    return React.createElement(
      'div',
      { style: style.container },
      [
        // Header
        React.createElement(
          'h3',
          {
            key: 'header',
            style: {
              fontSize: '16px',
              fontWeight: '600',
              margin: '0 0 16px 0',
              textAlign: 'center',
              color: '#ffffff'
            }
          },
          'Pushing Power'
        ),
        // Power Display Container
        React.createElement(
          'div',
          {
            key: 'content',
            style: {
              display: 'flex',
              flexDirection: 'column',
              gap: '12px'
            }
          },
          [
            // Red Power Row
            React.createElement(
              'div',
              {
                key: 'red-row',
                style: {
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }
              },
              [
                React.createElement(
                  'div',
                  {
                    key: 'label',
                    style: {
                      display: 'flex',
                      width: '60px',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }
                  },
                  [
                    React.createElement('span', { 
                      key: 'text',
                      style: { 
                        color: '#ef4444',
                        fontSize: '14px',
                        fontWeight: '500'
                      } 
                    }, 'Red'),
                    React.createElement('span', { 
                      key: 'value',
                      style: { 
                        color: '#ffffff',
                        fontWeight: '500'
                      } 
                    }, window.playerColor === 'RED' ? myPowerValue : opponentPowerValue)
                  ]
                ),
                React.createElement(
                  'div',
                  {
                    key: 'bars',
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
                        backgroundColor: i < (window.playerColor === 'RED' ? myPowerValue : opponentPowerValue) ? '#ef4444' : '#374151',
                        transition: 'background-color 300ms'
                      }
                    }
                  ))
                )
              ]
            ),
            // Blue Power Row
            React.createElement(
              'div',
              {
                key: 'blue-row',
                style: {
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }
              },
              [
                React.createElement(
                  'div',
                  {
                    key: 'label',
                    style: {
                      display: 'flex',
                      width: '60px',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }
                  },
                  [
                    React.createElement('span', { 
                      key: 'text',
                      style: { 
                        color: '#3b82f6',
                        fontSize: '14px',
                        fontWeight: '500'
                      } 
                    }, 'Blue'),
                    React.createElement('span', { 
                      key: 'value',
                      style: { 
                        color: '#ffffff',
                        fontWeight: '500'
                      } 
                    }, window.playerColor === 'BLUE' ? myPowerValue : opponentPowerValue)
                  ]
                ),
                React.createElement(
                  'div',
                  {
                    key: 'bars',
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
                        backgroundColor: i < (window.playerColor === 'BLUE' ? myPowerValue : opponentPowerValue) ? '#3b82f6' : '#374151',
                        transition: 'background-color 300ms'
                      }
                    }
                  ))
                )
              ]
            )
          ]
        )
      ]
    );
  };