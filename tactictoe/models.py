import random
from enum import Enum

class Piece(Enum):
    EMPTY = "EMPTY"
    BLACK = "BLACK"
    RED = "RED"
    BLUE = "BLUE"
    BLUE_BLOCKER = "BLUE_BLOCKER"
    RED_BLOCKER = "RED_BLOCKER"

class Board:
    def __init__(self):
        # A 3x3x3 grid of pieces (empty, red, black, blue)
        self.setupBoard(11)
        while self.hasSuperCorners() or self.hasSuperFaces():
           self.setupBoard(11)
        self.winningRuns = self.getWinningRuns()
        self.moveHistory = []

    def setupBoard(self,pieces):
        self.pieces = [[[Piece.EMPTY for _ in range(3)] for _ in range(3)] for _ in range(3)]
        for _ in range(pieces):
          x = random.randrange(3)
          y = random.randrange(3)
          z = random.randrange(3)
          while (self.pieces[x][y][z] == Piece.BLACK):
            x = random.randrange(3)
            y = random.randrange(3)
            z = random.randrange(3)
          self.pieces[x][y][z] = Piece.BLACK

    def hasSuperCorners(self):
        superRuns = []
        superRuns.append([(0,0,0),(1,0,0),(2,0,0),(0,1,0),(0,2,0),(0,0,1),(0,0,2)])
        superRuns.append([(2,0,0),(1,0,0),(0,0,0),(2,1,0),(2,2,0),(2,0,1),(2,0,2)])
        superRuns.append([(2,2,0),(2,1,0),(2,0,0),(1,2,0),(0,2,0),(2,2,1),(2,2,2)])
        superRuns.append([(0,2,0),(0,1,0),(0,0,0),(1,2,0),(2,2,0),(0,2,1),(0,2,2)])
        superRuns.append([(0,0,2),(1,0,2),(2,0,2),(0,0,1),(0,0,0),(0,1,2),(0,2,2)])
        superRuns.append([(2,0,2),(2,0,1),(2,0,0),(2,1,2),(2,2,2),(1,0,2),(0,0,2)])
        superRuns.append([(2,2,2),(2,1,2),(2,0,2),(2,2,1),(2,2,0),(1,2,2),(0,2,2)])
        superRuns.append([(0,2,2),(0,1,2),(0,0,2),(1,2,2),(2,2,2),(0,2,1),(0,2,0)])

        for run in superRuns:
            if sum(1 for position in run if self.pieces[position[0]][position[1]][position[2]] == Piece.BLACK) == 6:
                return True
        return False
    
    def hasSuperFaces(self):
        superRuns = []
        superRuns.append(([(1,0,0),(2,0,1),(1,0,2),(0,0,1)],[(1,0,1),(1,1,1),(1,2,1)]))
        superRuns.append(([(1,0,0),(0,1,0),(1,2,0),(2,1,0)],[(1,1,0),(1,1,1),(1,1,2)]))
        superRuns.append(([(0,1,0),(0,0,1),(0,1,2),(0,2,1)],[(0,1,1),(1,1,1),(2,1,1)]))
        superRuns.append(([(1,2,0),(0,2,1),(1,2,2),(2,2,1)],[(1,2,1),(1,1,1),(1,0,1)]))
        superRuns.append(([(2,1,0),(2,2,1),(2,1,2),(2,0,1)],[(2,1,1),(1,1,1),(0,1,1)]))
        superRuns.append(([(1,0,2),(2,1,2),(1,2,2),(0,1,2)],[(1,1,2),(1,1,1),(1,1,0)]))

        for plus, tail in superRuns:
            if not all(self.pieces[position[0]][position[1]][position[2]] == Piece.BLACK for position in tail) and all(self.pieces[position[0]][position[1]][position[2]] == Piece.BLACK for position in plus):
                return True
        return False

    def getState(self):
        # Convert the enum values to their string representations
        return [[[piece.value for piece in row] for row in layer] for layer in self.pieces]
    
    def setState(self, state):
        self.pieces = [[[Piece(piece_string) for piece_string in row] for row in layer] for layer in state]

    # Returns a list of all 3 in a rows in the board, used to check if the game is over
    def getWinningRuns(self):
        runs = []

        runs.append([(0,0,0),(0,0,1),(0,0,2)])
        runs.append([(0,0,0),(0,1,0),(0,2,0)])
        runs.append([(0,0,0),(1,0,0),(2,0,0)])

        runs.append([(2,2,0),(1,2,0),(0,2,0)])
        runs.append([(2,2,0),(2,1,0),(2,0,0)])
        runs.append([(2,2,0),(2,2,1),(2,2,2)])

        runs.append([(0,2,2),(0,1,2),(0,0,2)])
        runs.append([(0,2,2),(1,2,2),(2,2,2)])
        runs.append([(0,2,2),(0,2,1),(0,2,0)])

        runs.append([(2,0,2),(2,0,1),(2,0,0)])
        runs.append([(2,0,2),(1,0,2),(0,0,2)])
        runs.append([(2,0,2),(2,1,2),(2,2,2)])
        # Front
        runs.append([(0,0,0),(1,0,1),(2,0,2)])
        runs.append([(0,0,2),(1,0,1),(2,0,0)])
        runs.append([(1,0,0),(1,0,1),(1,0,2)])
        runs.append([(0,0,1),(1,0,1),(2,0,1)])
        # Top
        runs.append([(0,0,0),(1,1,0),(2,2,0)])
        runs.append([(0,2,0),(1,1,0),(2,0,0)])
        runs.append([(0,1,0),(1,1,0),(2,1,0)])
        runs.append([(1,2,0),(1,1,0),(1,0,0)])
        # Left
        runs.append([(0,0,0),(0,1,1),(0,2,2)])
        runs.append([(0,0,2),(0,1,1),(0,2,0)])
        runs.append([(0,0,1),(0,1,1),(0,2,1)])
        runs.append([(0,1,0),(0,1,1),(0,1,2)])
        # Back
        runs.append([(0,2,2),(1,2,1),(2,2,0)])
        runs.append([(0,2,0),(1,2,1),(2,2,2)])
        runs.append([(1,2,0),(1,2,1),(1,2,2)])
        runs.append([(0,2,1),(1,2,1),(2,2,1)])
        # Right
        runs.append([(2,0,2),(2,1,1),(2,2,0)])
        runs.append([(2,0,0),(2,1,1),(2,2,2)])
        runs.append([(2,0,1),(2,1,1),(2,2,1)])
        runs.append([(2,1,0),(2,1,1),(2,1,2)])
        # Bottom
        runs.append([(2,0,2),(1,1,2),(0,2,2)])
        runs.append([(0,0,2),(1,1,2),(2,2,2)])
        runs.append([(0,1,2),(1,1,2),(2,1,2)])
        runs.append([(1,0,2),(1,1,2),(1,2,2)])
        # Corners
        runs.append([(0,0,0),(1,1,1),(2,2,2)])
        runs.append([(2,0,0),(1,1,1),(0,2,2)])
        runs.append([(2,2,0),(1,1,1),(0,0,2)])
        runs.append([(0,2,0),(1,1,1),(2,0,2)])
        # Edges
        runs.append([(1,0,0),(1,1,1),(1,2,2)])
        runs.append([(2,1,0),(1,1,1),(0,1,2)])
        runs.append([(1,2,0),(1,1,1),(1,0,2)])
        runs.append([(0,1,0),(1,1,1),(2,1,2)])
        runs.append([(0,0,1),(1,1,1),(2,2,1)])
        runs.append([(2,0,1),(1,1,1),(0,2,1)])
        # Middles
        runs.append([(1,1,0),(1,1,1),(1,1,2)])
        runs.append([(1,0,1),(1,1,1),(1,2,1)])
        runs.append([(0,1,1),(1,1,1),(2,1,1)])

        return runs
    
    def validMove(self,x,y,z,dir,isBlocker):
       return self.pieces[x][y][z] == Piece.EMPTY or (not isBlocker and self.valid(x,y,z,dir))

    # Return true if the specified location is empty, or is pieces can be pushed without pushing a piece out of the board"
    def valid(self,x,y,z,dir):
        if not x in range(3) or not y in range(3) or not z in range(3):
              return False
        if x == 1 and y == 1 and z == 1:
              return False
        if dir == 'UP':
              return (z == 2) and (self.pieces[x][y][z] == Piece.EMPTY or self.pieces[x][y][z-1] == Piece.EMPTY or self.pieces[x][y][z-2] == Piece.EMPTY)
        if dir == 'DOWN':
              return (z == 0) and (self.pieces[x][y][z] == Piece.EMPTY or self.pieces[x][y][z+1] == Piece.EMPTY or self.pieces[x][y][z+2] == Piece.EMPTY)
        if dir == 'LEFT':
              return (x == 2) and (self.pieces[x][y][z] == Piece.EMPTY or self.pieces[x-1][y][z] == Piece.EMPTY or self.pieces[x-2][y][z] == Piece.EMPTY)
        if dir == 'RIGHT':
              return (x == 0) and (self.pieces[x][y][z] == Piece.EMPTY or self.pieces[x+1][y][z] == Piece.EMPTY or self.pieces[x+2][y][z] == Piece.EMPTY)
        if dir == 'FRONT':
              return (y == 2) and (self.pieces[x][y][z] == Piece.EMPTY or self.pieces[x][y-1][z] == Piece.EMPTY or self.pieces[x][y-2][z] == Piece.EMPTY)
        if dir == 'BACK':
              return (y == 0) and (self.pieces[x][y][z] == Piece.EMPTY or self.pieces[x][y+1][z] == Piece.EMPTY or self.pieces[x][y+2][z] == Piece.EMPTY)
        else:
              return False
        
    # Returns a list of all valid moves in the current board state
    def getPossibleMoves(self):
        directions = ['UP','DOWN','LEFT','RIGHT','FRONT','BACK']
        moves = []
        for x in range(3):
          for y in range(3):
            for z in range(3):
              for dir in directions:
                if self.valid(x,y,z,dir):
                  moves.append((x,y,z,dir))
        return moves
    
    def spotToValidDir(self,x,y,z):
        directions = ['UP','DOWN','LEFT','RIGHT','FRONT','BACK']
        for dir in directions:
           if self.valid(x,y,z,dir):
              return (x,y,z,dir)
    
    def getPossibleBlockerMoves(self):
        moves = []
        for x in range(3):
          for y in range(3):
            for z in range(3):
              if self.pieces[x][y][z] == Piece.EMPTY:
                if not (x,y,z) == (1,1,1):
                  moves.append((x,y,z))
        return [self.spotToValidDir(x,y,z) for (x,y,z) in moves]

    def undo(self):
      if self.moveHistory == []:
        raise ValueError
      else:
        lastMove = self.moveHistory.pop()
        x, y, z, dir, pushed_pieces = lastMove
        if pushed_pieces == 0:
          self.pieces[x][y][z] = Piece.EMPTY
        else:
          if dir == 'UP':
            if pushed_pieces == 1:
              self.pieces[x][y][z] = self.pieces[x][y][z-1]
              self.pieces[x][y][z-1] = Piece.EMPTY
            else:
              self.pieces[x][y][z] = self.pieces[x][y][z-1]
              self.pieces[x][y][z-1] = self.pieces[x][y][z-2]
              self.pieces[x][y][z-2] = Piece.EMPTY
          elif dir == 'DOWN':
            if pushed_pieces == 1:
              self.pieces[x][y][z] = self.pieces[x][y][z+1]
              self.pieces[x][y][z+1] = Piece.EMPTY
            else:
              self.pieces[x][y][z] = self.pieces[x][y][z+1]
              self.pieces[x][y][z+1] = self.pieces[x][y][z+2]
              self.pieces[x][y][z+2] = Piece.EMPTY
          elif dir == 'LEFT':
            if pushed_pieces == 1:
              self.pieces[x][y][z] = self.pieces[x-1][y][z]
              self.pieces[x-1][y][z] = Piece.EMPTY
            else:
              self.pieces[x][y][z] = self.pieces[x-1][y][z]
              self.pieces[x-1][y][z] = self.pieces[x-2][y][z]
              self.pieces[x-2][y][z] = Piece.EMPTY
          elif dir == 'RIGHT':
            if pushed_pieces == 1:
              self.pieces[x][y][z] = self.pieces[x+1][y][z]
              self.pieces[x+1][y][z] = Piece.EMPTY
            else:
              self.pieces[x][y][z] = self.pieces[x+1][y][z]
              self.pieces[x+1][y][z] = self.pieces[x+2][y][z]
              self.pieces[x+2][y][z] = Piece.EMPTY
          elif dir == 'FRONT':
            if pushed_pieces == 1:
              self.pieces[x][y][z] = self.pieces[x][y-1][z]
              self.pieces[x][y-1][z] = Piece.EMPTY
            else:
              self.pieces[x][y][z] = self.pieces[x][y-1][z]
              self.pieces[x][y-1][z] = self.pieces[x][y-2][z]
              self.pieces[x][y-2][z] = Piece.EMPTY
          elif dir == 'BACK':
            if pushed_pieces == 1:
              self.pieces[x][y][z] = self.pieces[x][y+1][z]
              self.pieces[x][y+1][z] = Piece.EMPTY
            else:
              self.pieces[x][y][z] = self.pieces[x][y+1][z]
              self.pieces[x][y+1][z] = self.pieces[x][y+2][z]
              self.pieces[x][y+2][z] = Piece.EMPTY
            
    def moveAI(self,x,y,z,dir,player):
        if player == "RED":
            player = Piece.RED
        elif player == "BLUE":
            player = Piece.BLUE
        if (self.pieces[x][y][z] == Piece.EMPTY):
                self.pieces[x][y][z] = player
                self.moveHistory.append((x,y,z,dir,0))
        else:
            if dir == 'UP':
                if (self.pieces[x][y][z-1] == Piece.EMPTY):
                    self.pieces[x][y][z-1] = self.pieces[x][y][z]
                    self.pieces[x][y][z] = player
                    self.moveHistory.append((x,y,z,dir,1))
                else:
                    self.pieces[x][y][z-2] = self.pieces[x][y][z-1]
                    self.pieces[x][y][z-1] = self.pieces[x][y][z]
                    self.pieces[x][y][z] = player
                    self.moveHistory.append((x,y,z,dir,2))
            elif dir == 'DOWN':
                  if (self.pieces[x][y][z+1] == Piece.EMPTY):
                      self.pieces[x][y][z+1] = self.pieces[x][y][z]
                      self.pieces[x][y][z] = player
                      self.moveHistory.append((x,y,z,dir,1))
                  else:
                      self.pieces[x][y][z+2] = self.pieces[x][y][z+1]
                      self.pieces[x][y][z+1] = self.pieces[x][y][z]
                      self.pieces[x][y][z] = player
                      self.moveHistory.append((x,y,z,dir,2))
            elif dir == 'LEFT':
                  if (self.pieces[x-1][y][z] == Piece.EMPTY):
                      self.pieces[x-1][y][z] = self.pieces[x][y][z]
                      self.pieces[x][y][z] = player
                      self.moveHistory.append((x,y,z,dir,1))
                  else:
                      self.pieces[x-2][y][z] = self.pieces[x-1][y][z]
                      self.pieces[x-1][y][z] = self.pieces[x][y][z]
                      self.pieces[x][y][z] = player
                      self.moveHistory.append((x,y,z,dir,2))
            elif dir == 'RIGHT':
                  if (self.pieces[x+1][y][z] == Piece.EMPTY):
                      self.pieces[x+1][y][z] = self.pieces[x][y][z]
                      self.pieces[x][y][z] = player
                      self.moveHistory.append((x,y,z,dir,1))
                  else:
                      self.pieces[x+2][y][z] = self.pieces[x+1][y][z]
                      self.pieces[x+1][y][z] = self.pieces[x][y][z]
                      self.pieces[x][y][z] = player
                      self.moveHistory.append((x,y,z,dir,2))
            elif dir == 'FRONT':
                  if (self.pieces[x][y-1][z] == Piece.EMPTY):
                      self.pieces[x][y-1][z] = self.pieces[x][y][z]
                      self.pieces[x][y][z] = player
                      self.moveHistory.append((x,y,z,dir,1))
                  else:
                      self.pieces[x][y-2][z] = self.pieces[x][y-1][z]
                      self.pieces[x][y-1][z] = self.pieces[x][y][z]
                      self.pieces[x][y][z] = player
                      self.moveHistory.append((x,y,z,dir,2))
            elif dir == 'BACK':
                  if (self.pieces[x][y+1][z] == Piece.EMPTY):
                      self.pieces[x][y+1][z] = self.pieces[x][y][z]
                      self.pieces[x][y][z] = player
                      self.moveHistory.append((x,y,z,dir,1))
                  else:
                      self.pieces[x][y+2][z] = self.pieces[x][y+1][z]
                      self.pieces[x][y+1][z] = self.pieces[x][y][z]
                      self.pieces[x][y][z] = player
                      self.moveHistory.append((x,y,z,dir,2))

    # Makes a move after checking if it is valid
    # If there is a piece in the specified location, it is pushed in the specified direction, along with the piece behind it if one exists 
    def move(self,x,y,z,dir,player,isBlocker):
        if isBlocker:
           if player == Piece.RED:
              player = Piece.RED_BLOCKER
           else:
              player = Piece.BLUE_BLOCKER
        elif player == Piece.RED:
            player = Piece.RED
        elif player == Piece.BLUE:
            player = Piece.BLUE
        if (isBlocker and not self.pieces[x][y][z] == Piece.EMPTY) or not self.validMove(x,y,z,dir,isBlocker):
             exc = f'\nAttempted to make move {(x,y,z,dir)}\nOn board:\n{self.getStatePretty()}'
             print(exc)
             raise ValueError(exc)
        else:
            if (self.pieces[x][y][z] == Piece.EMPTY):
                self.pieces[x][y][z] = player
                self.moveHistory.append((x,y,z,dir,0))
            else:
                if dir == 'UP':
                    if (self.pieces[x][y][z-1] == Piece.EMPTY):
                        self.pieces[x][y][z-1] = self.pieces[x][y][z]
                        self.pieces[x][y][z] = player
                        self.moveHistory.append((x,y,z,dir,1))
                    else:
                        self.pieces[x][y][z-2] = self.pieces[x][y][z-1]
                        self.pieces[x][y][z-1] = self.pieces[x][y][z]
                        self.pieces[x][y][z] = player
                        self.moveHistory.append((x,y,z,dir,2))
                elif dir == 'DOWN':
                      if (self.pieces[x][y][z+1] == Piece.EMPTY):
                          self.pieces[x][y][z+1] = self.pieces[x][y][z]
                          self.pieces[x][y][z] = player
                          self.moveHistory.append((x,y,z,dir,1))
                      else:
                          self.pieces[x][y][z+2] = self.pieces[x][y][z+1]
                          self.pieces[x][y][z+1] = self.pieces[x][y][z]
                          self.pieces[x][y][z] = player
                          self.moveHistory.append((x,y,z,dir,2))
                elif dir == 'LEFT':
                      if (self.pieces[x-1][y][z] == Piece.EMPTY):
                          self.pieces[x-1][y][z] = self.pieces[x][y][z]
                          self.pieces[x][y][z] = player
                          self.moveHistory.append((x,y,z,dir,1))
                      else:
                          self.pieces[x-2][y][z] = self.pieces[x-1][y][z]
                          self.pieces[x-1][y][z] = self.pieces[x][y][z]
                          self.pieces[x][y][z] = player
                          self.moveHistory.append((x,y,z,dir,2))
                elif dir == 'RIGHT':
                      if (self.pieces[x+1][y][z] == Piece.EMPTY):
                          self.pieces[x+1][y][z] = self.pieces[x][y][z]
                          self.pieces[x][y][z] = player
                          self.moveHistory.append((x,y,z,dir,1))
                      else:
                          self.pieces[x+2][y][z] = self.pieces[x+1][y][z]
                          self.pieces[x+1][y][z] = self.pieces[x][y][z]
                          self.pieces[x][y][z] = player
                          self.moveHistory.append((x,y,z,dir,2))
                elif dir == 'FRONT':
                      if (self.pieces[x][y-1][z] == Piece.EMPTY):
                          self.pieces[x][y-1][z] = self.pieces[x][y][z]
                          self.pieces[x][y][z] = player
                          self.moveHistory.append((x,y,z,dir,1))
                      else:
                          self.pieces[x][y-2][z] = self.pieces[x][y-1][z]
                          self.pieces[x][y-1][z] = self.pieces[x][y][z]
                          self.pieces[x][y][z] = player
                          self.moveHistory.append((x,y,z,dir,2))
                elif dir == 'BACK':
                      if (self.pieces[x][y+1][z] == Piece.EMPTY):
                          self.pieces[x][y+1][z] = self.pieces[x][y][z]
                          self.pieces[x][y][z] = player
                          self.moveHistory.append((x,y,z,dir,1))
                      else:
                          self.pieces[x][y+2][z] = self.pieces[x][y+1][z]
                          self.pieces[x][y+1][z] = self.pieces[x][y][z]
                          self.pieces[x][y][z] = player
                          self.moveHistory.append((x,y,z,dir,2))

    # Returns a string representation of the gameboard, for debugging purposes
    def getStatePretty(self):
        displayStr = { Piece.RED : " RED ", Piece.BLACK : "BLACK", Piece.BLUE : " BLUE", Piece.EMPTY : "EMPTY"}
        gameState = "+----------------------\n"
        gameState += "| \\ " + displayStr[self.pieces[0][2][0]] + "  " + displayStr[self.pieces[1][2][0]] + "  " + displayStr[self.pieces[2][2][0]] + " \\\n"
        gameState += "|   \\                     \\\n"
        gameState += "|     \\ " + displayStr[self.pieces[0][1][0]] + "  " + displayStr[self.pieces[1][1][0]] + "  " + displayStr[self.pieces[2][1][0]] + " \\\n"
        gameState += "|       \\                     \\\n"
        gameState += "|         \\ " + displayStr[self.pieces[0][0][0]] + "  " + displayStr[self.pieces[1][0][0]] + "  " + displayStr[self.pieces[2][0][0]] + " \\\n"
        gameState += "|          ---------------------|\n"
        gameState += "|   " + displayStr[self.pieces[0][2][1]] + " |" + displayStr[self.pieces[1][2][1]] + "  " + displayStr[self.pieces[2][2][1]] + "         |\n"
        gameState += "|         |                     |\n"
        gameState += "|       " + displayStr[self.pieces[0][1][1]] + "  " + displayStr[self.pieces[1][1][1]] + "  " + displayStr[self.pieces[2][1][1]] + "     |\n"
        gameState += "|         |                     |\n"
        gameState += "|         | " + displayStr[self.pieces[0][0][1]] + "  " + displayStr[self.pieces[1][0][1]] + "  " + displayStr[self.pieces[2][0][1]] + " |\n"
        gameState += "|         |                     |\n"
        gameState += " \\ " + displayStr[self.pieces[0][2][2]] + "  " + displayStr[self.pieces[1][2][2]] + "  " + displayStr[self.pieces[2][2][2]] + "          |\n"
        gameState += "   \\      |                     |\n"
        gameState += "     \\ " + displayStr[self.pieces[0][1][2]] + "  " + displayStr[self.pieces[1][1][2]] + "  " + displayStr[self.pieces[2][1][2]] + "      |\n"
        gameState += "       \\  |                     |\n"
        gameState += "         \\| " + displayStr[self.pieces[0][0][2]] + "  " + displayStr[self.pieces[1][0][2]] + "  " + displayStr[self.pieces[2][0][2]] + " |\n"
        gameState += "           ---------------------+\n\n"
        return gameState

    # Returns a random valid move in the given board
    def getRandomMove(self,player: Piece):
        directions = ['UP','DOWN','LEFT','RIGHT','FRONT','BACK']
        x = random.randint(0,2)
        y = random.randint(0,2)
        z = random.randint(0,2)
        dir = random.choice(directions)
        while not self.validMove(x,y,z,dir,False):
            x = random.randint(0,2)
            y = random.randint(0,2)
            z = random.randint(0,2)
            dir = random.choice(directions)
        return (x,y,z,dir)
    
    # Returns the other player color. Red -> Blue. Blue -> Red
    def otherPlayer(self,player: Piece):
        return Piece.RED if player == Piece.BLUE else Piece.BLUE

    # Loops through possible moves and returns if a move wins the game, else returns None
    def getWinInOne(self,player: Piece):
        for (x,y,z,dir) in self.getPossibleMoves():
          self.moveAI(x,y,z,dir,player)
          if self.hasWon(player):
            self.undo()
            return (x,y,z,dir)
          self.undo()
        return None
    
    # Loops through possible moves and returns a move which prevents the opponent from winning 
    # If there are multiple, picks one at random. If none exist returns None
    def getDefendingMove(self,player: Piece):
        potential_moves = []
        for (x,y,z,dir) in self.getPossibleMoves():
          self.moveAI(x,y,z,dir,player)
          if self.getWinInOne(self.otherPlayer(player)) == None:
            potential_moves.append((x,y,z,dir))
          self.undo()
        if potential_moves:
          return random.choice(potential_moves)
        return None
    
    def getGoodDefendingMove(self, player: Piece):
        potential_moves = []
        for (x, y, z, dir) in self.getPossibleMoves():
            points = 0
            self.moveAI(x, y, z, dir, player)
            if self.getWinInOne(self.otherPlayer(player)) == None:
                points += 100
            points += self.getTwoInARows(player) * 4
            if self.pieces[x][y][z] == self.otherPlayer(player):
               points += 10
            neighbors = self.neighbor_positions(x, y, z)
            for (i,j,k) in neighbors:
               if self.pieces[i][j][k] == self.otherPlayer(player):
                  points += 3
            potential_moves.append(((x, y, z, dir), points))
            self.undo()

        potential_moves.sort(key=lambda move: move[1], reverse=True)

        return potential_moves[0][0]
    
    def getBestDefendingMove(self, player: Piece):
        opponent = self.otherPlayer(player)
        corners = frozenset([(0, 0, 0), (0, 0, 2), (0, 2, 0), (0, 2, 2),
                       (2, 0, 0), (2, 0, 2), (2, 2, 0), (2, 2, 2)])
        middles = frozenset([(1, 0, 1), (2, 1, 1), (1, 2, 2), (0, 1, 1), (1, 1, 0), (1, 1, 2)])
        potential_moves = []
        
        for (x, y, z, dir) in self.getPossibleMoves():
            points = 0
            self.moveAI(x, y, z, dir, player)
            if self.getWinInOne(opponent) == None:
                points += 100
            points += self.getTwoInARows(player) * 5
            neighbors = self.neighbor_positions(x, y, z)
            non_empty_neighbors = sum(1 for i, j, k in neighbors
                                       if self.pieces[i][j][k] != Piece.EMPTY)
            for (i,j,k) in neighbors:
               if self.pieces[i][j][k] == opponent:
                  points += 6
            if self.pieces[x][y][z] == opponent:
               points += 15
            if non_empty_neighbors == 6:
               points += 10
            if (x,y,z) in middles:
               points += 2
            if (x,y,z) in corners:
               points -= 1
            potential_moves.append(((x, y, z, dir), points))
            self.undo()

        potential_moves.sort(key=lambda move: move[1], reverse=True)

        # Check top 5 moves for getWinInTwo condition
        top_moves = potential_moves[:5]
        for move, _ in top_moves:
            x, y, z, dir = move
            self.moveAI(x,y,z,dir,player)
            if self.getWinInTwo(self.otherPlayer(player)) is None:
                self.undo()
                return move
            self.undo()

        if potential_moves:
            return potential_moves[0][0]
        return None

    # Loops through possible moves and for each one examines all possible opponent moves.
    # If there are any moves which allow the given player to win after any opponent move, 
    # return one at random. Otherwise, return None
    def getWinInTwo(self,player: Piece):
        winningMove = self.getWinInOne(player)
        if winningMove:
          return winningMove
        potential_moves = []
        for (x,y,z,dir) in self.getPossibleMoves():
          self.moveAI(x,y,z,dir,player)
          if self.getWinInOne(self.otherPlayer(player)) == None:
            winner = True
            for (x2,y2,z2,dir2) in self.getPossibleMoves():
              self.moveAI(x2,y2,z2,dir2,self.otherPlayer(player))
              if self.getWinInOne(player) == None:
                winner = False
              self.undo()
            if winner:
              potential_moves.append((x,y,z,dir))
          self.undo()
        if potential_moves:
          return random.choice(potential_moves)
        return None
    
    # Returns a random move which is either a middle or edge
    def getGoodStartMove(self):
        # Define corner positions
        corners = [(0, 0, 0), (0, 0, 2), (0, 2, 0), (0, 2, 2),
                  (2, 0, 0), (2, 0, 2), (2, 2, 0), (2, 2, 2)]
        
        # Collect valid moves from middles and edges
        potential_moves = []
        for (x, y, z, dir) in self.getPossibleMoves():
            if not (x, y, z) in corners:
                potential_moves.append((x, y, z, dir))

        # Randomly select one of the valid moves
        if potential_moves:
            return random.choice(potential_moves)
        return None

    def neighbor_positions(self, x, y, z):
        neighbors = []
        for i in range(3):
            if i != x:
                neighbors.append((i, y, z))
        for j in range(3):
            if j != y:
                neighbors.append((x, j, z))
        for k in range(3):
            if k != z:
                neighbors.append((x, y, k))
        return neighbors
    
    def getTwoInARows(self, player: Piece):
        count = 0
        for run in self.winningRuns:
            player_count = sum(1 for x, y, z in run if self.pieces[x][y][z] == player)
            if player_count == 2:
                if (1, 1, 1) in run:
                    count += 0.5
                else:
                    count += 1
        return count

    def numPieces(self,player: Piece):
        count = 0
        for layer in self.pieces:
            for row in layer:
                for piece in row:
                    if piece == player:
                        count += 1
        return count
    
    # Returns true if the given player has won (all locations in a run of three are equal to the player)
    def hasWon(self,player: Piece):
        for run in self.winningRuns:
            if all(self.pieces[x][y][z] == player for (x,y,z) in run):
                return True
        if player == Piece.BLUE and self.numPieces(Piece.EMPTY) == 0:
           return True
        return False
    
    def winningRun(self,player: Piece):
        for run in self.winningRuns:
            if all(self.pieces[x][y][z] == player for (x,y,z) in run):
                return run
        if player == Piece.BLUE and self.hasWon(player):
            return [(x,y,z) for x in range(3) for y in range(3) for z in range(3) if self.pieces[x][y][z] == player]
        return None
    
    def getSimpleDefendingMove(self,player: Piece):
        for (x, y, z, dir) in self.getPossibleMoves():
            if self.pieces[x][y][z] == self.otherPlayer(player):
               return((x,y,z,dir))
            neighbors = self.neighbor_positions(x, y, z)
            for (i,j,k) in neighbors:
              if self.pieces[i][j][k] == self.otherPlayer(player):
                return((x,y,z,dir))
              
    def getRandomBlockerMove(self):
        possibleMoves = self.getPossibleBlockerMoves()
        return random.choice(possibleMoves)
    
    def getMediumBlockerMove(self, player: Piece):
      if player == Piece.BLUE:
         return self.getRandomBlockerMove()
      else:
         if random.random() < 0.5:
            return self.getRandomBlockerMove()
         return None
    
    def getBetterBlockerMove(self, player: Piece):
      if player == Piece.BLUE:
        defending_move = self.getDefendingMove(player)
        if defending_move:
            return self.getRandomBlockerMove()
        for blocker_move in self.getPossibleBlockerMoves():
            (x,y,z,dir) = blocker_move
            self.moveAI(x, y, z, dir, Piece.BLUE_BLOCKER)
            
            defending_move = self.getDefendingMove(player)
            winning_move = self.getWinInOne(player)
            
            if defending_move or winning_move:
                self.undo()
                return blocker_move
            self.undo()
        return self.getRandomBlockerMove()
      else:
        opWinningMove = self.getWinInOne(self.otherPlayer(player))
        defendingMove = self.getDefendingMove(player)
        if opWinningMove:
          for blocker_move in self.getPossibleBlockerMoves():
            (x,y,z,dir) = blocker_move
            self.moveAI(x, y, z, dir, Piece.BLUE_BLOCKER)

            if self.getWinInOne(self.otherPlayer(player)) == None or (defendingMove == None and self.getDefendingMove(player) != None):
              self.undo()
              return blocker_move
            self.undo()
        return None
          
            
               
       
# Returns a winning move if one exists, otherwise picks a random move
class EasyAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num):
        if move_num > 3:
           winningMove = board.getWinInOne(self.player)
           if winningMove:
              return winningMove
        simpleDefendingMove = board.getSimpleDefendingMove(self.player)
        if simpleDefendingMove:
            return simpleDefendingMove
        return board.getRandomMove(self.player)
    
    def getBlockerMove(self, board: Board):
       return None
        
# Returns a winning move if one exists, otherwise a move preventing the opponent from 
# winning if one exists, otherwise a random move
class MediumAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num):
        if move_num == 0:
           return board.getGoodStartMove()
        winningMove = board.getWinInOne(self.player)
        if winningMove:
          return winningMove
        else:
          defendingMove = board.getGoodDefendingMove(self.player)
          if defendingMove:
            return defendingMove
          else:
            return board.getRandomMove(self.player)
          
    def getBlockerMove(self, board: Board):
       return board.getRandomBlockerMove()
          
class HardAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num):  
        if move_num == 0:
           return board.getBestDefendingMove(self.player)
        elif move_num == 1:
          winInTwo = board.getWinInTwo(self.player)
          if winInTwo:
            return winInTwo
          else:
            defendingMove = board.getBestDefendingMove(self.player)
            if defendingMove:
              return defendingMove
            else:
              return board.getRandomMove(self.player)
        else:
          winningMove = board.getWinInOne(self.player)
          if winningMove:
            return winningMove
          else:
            winInTwo = board.getWinInTwo(self.player)
            if winInTwo and (random.random() < 0.5 or self.player == Piece.BLUE):
              return winInTwo
            else:
              defendingMove = board.getGoodDefendingMove(self.player)
              if defendingMove:
                return defendingMove
              else:
                return board.getRandomMove(self.player)
        
    def getBlockerMove(self, board: Board):
       return board.getMediumBlockerMove(self.player)

class ExpertAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num):  
        if move_num == 0:
           return board.getBestDefendingMove(self.player)
        elif move_num == 1:
          winInTwo = board.getWinInTwo(self.player)
          if winInTwo:
            return winInTwo
          else:
            defendingMove = board.getBestDefendingMove(self.player)
            if defendingMove:
              return defendingMove
            else:
              return board.getRandomMove(self.player)
        else:
          winningMove = board.getWinInOne(self.player)
          if winningMove:
            return winningMove
          else:
            winInTwo = board.getWinInTwo(self.player)
            if winInTwo:
              return winInTwo
            else:
              defendingMove = board.getBestDefendingMove(self.player)
              if defendingMove:
                return defendingMove
              else:
                return board.getRandomMove(self.player)
              
    def getBlockerMove(self, board: Board):
       return board.getBetterBlockerMove(self.player)
    
class GamePlayer:
    def __init__(self, difficulty, computerColor):
        self.board = Board()
        self.computer_color = Piece.RED if computerColor == 'RED' else Piece.BLUE
        self.red_blocker_count = 0
        self.blue_blocker_count = 0
        self.last_move_blocker = False
        self.difficulty = difficulty
        match(difficulty):
            case 'easy':
                self.computer = EasyAgent(self.computer_color)
            case 'medium':
                self.computer = MediumAgent(self.computer_color)
            case 'hard':
                self.computer = HardAgent(self.computer_color)
            case 'expert':
                self.computer = ExpertAgent(self.computer_color)

    def serialize(self):
        return json.dumps({
            'board_state': self.board.getState(),
            'computer_color': self.computer_color.value,
            'red_blocker_count': self.red_blocker_count,
            'blue_blocker_count': self.blue_blocker_count,
            'last_move_blocker': self.last_move_blocker,
            'difficulty': self.difficulty
        })
    
    @classmethod
    def deserialize(cls, serialized_data):
        data = json.loads(serialized_data)
        game_player = cls(data['difficulty'], data['computer_color'])
        game_player.board.setState(data['board_state'])
        game_player.red_blocker_count = data['red_blocker_count']
        game_player.blue_blocker_count = data['blue_blocker_count']
        game_player.last_move_blocker = data['last_move_blocker']
        return game_player

    def isOver(self):
        return self.board.hasWon(Piece.RED) or self.board.hasWon(Piece.BLUE)

    def makeComputerMove(self,isBlockerMove):
        if isBlockerMove:
           move = self.computer.getBlockerMove(self.board)
           if move:
            (x,y,z,dir) = move
            if self.computer_color == Piece.RED:
               self.red_blocker_count += 1
               self.board.move(x,y,z,dir,Piece.RED,True)
            else:
               self.blue_blocker_count += 1
               self.board.move(x,y,z,dir,Piece.BLUE,True)
            return move
           else:
              return None
        else:
           (x,y,z,dir) = self.computer.getMove(self.board, self.board.numPieces(self.computer_color))
           self.board.moveAI(x,y,z,dir,self.computer_color)
           return (x,y,z,dir)

    def move(self,x,y,z,dir,player,isBlockerMove):
        if isBlockerMove:
           if self.last_move_blocker:
              raise Exception("last_move_blocker")
           if player == Piece.RED:
              if self.red_blocker_count >= 3:
                 raise Exception("max_blocker_moves")
              self.red_blocker_count += 1
           else:
              if self.blue_blocker_count >= 3:
                 raise Exception("max_blocker_moves")
              self.blue_blocker_count += 1
           self.last_move_blocker = True
        else:
           self.last_move_blocker = False
        if not self.board.validMove(x,y,z,dir,isBlockerMove):
           raise Exception("invalid_move")
        self.board.move(x,y,z,dir,player,isBlockerMove)

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_paid_account = models.BooleanField(default=False)
    background_color = models.CharField(max_length=7, default='#d3d2c0')
    board_color = models.CharField(max_length=7, default='#edd8a8')

    def __str__(self):
        return self.user.username

GAME_TYPES = [
        ('rapid', 'rapid'),
        ('blitz', 'blitz'),
]

class EloRating(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='elo_ratings')
    game_type = models.CharField(max_length=20, choices=GAME_TYPES)
    rating = models.IntegerField(default=1500)

    class Meta:
        unique_together = ('user_profile', 'game_type')

    def __str__(self):
        return f"{self.user_profile.user.username} elo: {self.rating}"

import json
import string
from datetime import timedelta
from django.db import IntegrityError

class Game(models.Model):
    # Player fields
    player_one = models.ForeignKey(User, related_name='games_as_player_one', on_delete=models.CASCADE)
    player_two = models.ForeignKey(User, related_name='games_as_player_two', on_delete=models.CASCADE)

    game_type = models.CharField(max_length=20, choices=GAME_TYPES)
    game_code = models.CharField(max_length=6, unique=True)
    
    # Game state and status
    game_state = models.JSONField(default=list)
    turn = models.ForeignKey(User, on_delete=models.CASCADE)
    move_count = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    winner = models.ForeignKey(User, related_name='winner', on_delete=models.SET_NULL, null=True, blank=True)
    elo_change = models.IntegerField(default=None, null=True)

    player_one_time_left = models.DurationField(default=timedelta(seconds=180))
    player_two_time_left = models.DurationField(default=timedelta(seconds=180))
    last_move_time = models.DateTimeField(auto_now_add=True)

    red_blocker_count = models.IntegerField(default=0)
    blue_blocker_count = models.IntegerField(default=0)
    last_move_blocker = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, **kwargs):
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                kwargs['game_code'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                return cls.objects.create(**kwargs)
            except IntegrityError:
                if attempt == max_attempts - 1:
                    raise

    @classmethod
    def start_new_game(cls, player_one, player_two, game_type):
        board = Board() 
        game = cls.create(
            player_one=player_one,
            player_two=player_two,
            game_type=game_type,
            game_state=json.dumps(board.getState()),  
            turn=player_one,
            completed=False
        )
        game.save()
        return game
    
    def move(self, x, y, z, dir, player, isBlockerMove):
        board = Board()
        board.setState(json.loads(self.game_state))
        if isBlockerMove:
           if self.last_move_blocker:
              raise Exception("last_move_blocker")
           if player == Piece.RED:
                if self.move_count < 1:
                    raise Exception("red_first_move")
                if self.red_blocker_count >= 3:
                    raise Exception("max_blocker_moves")
                self.red_blocker_count += 1
           else:
                if self.blue_blocker_count >= 3:
                    raise Exception("max_blocker_moves")
                self.blue_blocker_count += 1
           self.last_move_blocker = True
        else:
           self.last_move_blocker = False
        if not board.validMove(x,y,z,dir,isBlockerMove):
           raise Exception("invalid_move")
        board.move(x,y,z,dir,player,isBlockerMove)
        self.move_count += 1
        self.game_state = json.dumps(board.getState())

    def __str__(self):
        return f"{self.player_one.username} vs {self.player_two.username} on {self.created_at.strftime('%Y-%m-%d')}"
