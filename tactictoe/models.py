import random
from enum import Enum

class Piece(Enum):
    EMPTY = "EMPTY"
    BLACK = "BLACK"
    RED = "RED"
    BLUE = "BLUE"
    BLOCKER = "BLOCKER"

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
        
    # Returns a liist of all valid moves in the current board state
    def getPossibleMoves(self):
        directions = ['UP','DOWN','LEFT','RIGHT','FRONT','BACK']
        moves = []
        for x in range(3):
          for y in range(3):
            for z in range(3):
              for dir in directions:
                if self.validMove(x,y,z,dir,False):
                  moves.append((x,y,z,dir))
        return moves

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
            
    # Makes a move after checking if it is valid
    # If there is a piece in the specified location, it is pushed in the specified direction, along with the piece behind it if one exists 
    def move(self,x,y,z,dir,player,isBlocker):
        if isBlocker:
           player = Piece.BLOCKER
        elif player == "RED":
            player = Piece.RED
        elif player == "BLUE":
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
          self.move(x,y,z,dir,player,False)
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
          self.move(x,y,z,dir,player)
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
            self.move(x, y, z, dir, player)
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
        corners = [(0, 0, 0), (0, 0, 2), (0, 2, 0), (0, 2, 2),
                  (2, 0, 0), (2, 0, 2), (2, 2, 0), (2, 2, 2)]
        middles = [(1, 0, 1), (2, 1, 1), (1, 2, 2), (0, 1, 1), (1, 1, 0), (1, 1, 2)]
        potential_moves = []
        
        for (x, y, z, dir) in self.getPossibleMoves():
            points = 0
            self.move(x, y, z, dir, player, False)
            if self.getWinInOne(self.otherPlayer(player)) == None:
                points += 100
            points += self.getTwoInARows(player) * 5
            neighbors = self.neighbor_positions(x, y, z)
            non_empty_neighbors = sum(1 for i, j, k in neighbors
                                       if self.pieces[i][j][k] != Piece.EMPTY)
            for (i,j,k) in neighbors:
               if self.pieces[i][j][k] == self.otherPlayer(player):
                  points += 6
            if self.pieces[x][y][z] == self.otherPlayer(player):
               points += 15
            if non_empty_neighbors == 6:
               points += 10
            if (x,y,z) in corners:
               points += 2
            if (x,y,z) in middles:
               points += 1
            potential_moves.append(((x, y, z, dir), points))
            self.undo()

        potential_moves.sort(key=lambda move: move[1], reverse=True)

        # Check top 5 moves for getWinInTwo condition
        top_moves = potential_moves[:5]
        for move, _ in top_moves:
            x, y, z, dir = move
            self.move(x, y, z, dir, player, False)
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
          self.move(x,y,z,dir,player,False)
          if self.getWinInOne(self.otherPlayer(player)) == None:
            winner = True
            for (x2,y2,z2,dir2) in self.getPossibleMoves():
              self.move(x2,y2,z2,dir2,self.otherPlayer(player),False)
              if self.getWinInOne(player) == None:
                winner = False
              self.undo()
            if winner:
              potential_moves.append((x,y,z,dir))
          self.undo()
        if potential_moves:
          return random.choice(potential_moves)
        return None
    
    # Returns a random move which is either a corner or middle (not along the edge)
    def getGoodStartMove(self,player: Piece):
        # Define corners and middle positions
        corners = [(0, 0, 0), (0, 0, 2), (0, 2, 0), (0, 2, 2),
                  (2, 0, 0), (2, 0, 2), (2, 2, 0), (2, 2, 2)]
        middles = [(1, 0, 1), (2, 1, 1), (1, 2, 2), (0, 1, 1), (1, 1, 0), (1, 1, 2)]
        
        # Collect valid moves from corners and middles
        potential_moves = []
        for (x, y, z, dir) in self.getPossibleMoves():
            if (x, y, z) in corners or (x, y, z) in middles:
                potential_moves.append((x, y, z, dir))

        # Randomly select one of the valid moves if any
        if potential_moves:
            return random.choice(potential_moves)
        return None

    # If there is a corner move which would 'lock' the piece in place (two pieces on every side), make it
    # Otherwise, if there is a corner move which would leave 5 of 7 spaces of the 3 edges going through the corner, make it
    # Otherwise, if there is a middle move which would 'lock' the piece in place (two pieces behind it, none directly next to it), make it
    # Otherwise, return getGoodStartMove
    def getBestStartMove(self,player: Piece):
        corners = [(0, 0, 0), (0, 0, 2), (0, 2, 0), (0, 2, 2),
               (2, 0, 0), (2, 0, 2), (2, 2, 0), (2, 2, 2)]
        
        best_moves = []
        best_so_far = 4
        for (x, y, z, dir) in self.getPossibleMoves():
            if (x, y, z) in corners:
                self.move(x,y,z,dir,player)
                non_empty_neighbors = sum(1 for i, j, k in self.neighbor_positions(x, y, z)
                                       if self.pieces[i][j][k] != Piece.EMPTY)
                if (non_empty_neighbors > best_so_far) and (non_empty_neighbors % 2 == 0):
                    best_so_far = non_empty_neighbors
                    best_moves = [(x, y, z, dir)]
                elif non_empty_neighbors == best_so_far:
                    best_moves.append((x, y, z, dir))
                self.undo()

        # Randomly select one of the best moves if any
        if best_moves:
            return random.choice(best_moves)
        return self.getGoodStartMove(player)

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
        return None
    
    def getSimpleDefendingMove(self,player: Piece):
        for (x, y, z, dir) in self.getPossibleMoves():
            if self.pieces[x][y][z] == self.otherPlayer(player):
               return((x,y,z,dir))
            neighbors = self.neighbor_positions(x, y, z)
            for (i,j,k) in neighbors:
              if self.pieces[i][j][k] == self.otherPlayer(player):
                return((x,y,z,dir))
       
    
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
        
# Returns a winning move if one exists, otherwise a move preventing the opponent from 
# winning if one exists, otherwise a random move
class MediumAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num):
        if move_num == 0:
           return board.getGoodStartMove(self.player)
        winningMove = board.getWinInOne(self.player)
        if winningMove:
          return winningMove
        else:
          defendingMove = board.getGoodDefendingMove(self.player)
          if defendingMove:
            return defendingMove
          else:
            return board.getRandomMove(self.player)
          
class HardAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num):  
        if move_num == 0:
           return board.getGoodStartMove(self.player)
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
              defendingMove = board.getGoodDefendingMove(self.player)
              if defendingMove:
                return defendingMove
              else:
                return board.getRandomMove(self.player)

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
    
class GamePlayer:
    def __init__(self, difficulty, computerColor):
        self.board = Board()
        self.computerColor = Piece.RED if computerColor == 'RED' else Piece.BLUE
        self.blockerMoveCount = 0
        self.lastMoveBlocker = False
        self.difficulty = difficulty
        match(difficulty):
            case 'easy':
                self.computer = EasyAgent(self.computerColor)
            case 'medium':
                self.computer = MediumAgent(self.computerColor)
            case 'hard':
                self.computer = HardAgent(self.computerColor)
            case 'expert':
                self.computer = ExpertAgent(self.computerColor)

    def serialize(self):
        return json.dumps({
            'board_state': self.board.getState(),
            'computer_color': self.computerColor.value,
            'blocker_move_count': self.blockerMoveCount,
            'last_move_blocker': self.lastMoveBlocker,
            'difficulty': self.difficulty
        })
    
    @classmethod
    def deserialize(cls, serialized_data):
        data = json.loads(serialized_data)
        game_player = cls(data['difficulty'], data['computer_color'])
        game_player.board.setState(data['board_state'])
        game_player.blockerMoveCount = data['blocker_move_count']
        game_player.lastMoveBlocker = data['last_move_blocker']
        return game_player

    def isOver(self):
        return self.board.hasWon(Piece.RED) or self.board.hasWon(Piece.BLUE)

    def makeComputerMove(self):
        (x,y,z,dir) = self.computer.getMove(self.board, self.board.numPieces(self.computerColor))
        self.board.move(x,y,z,dir,self.computerColor,False)

    def move(self,x,y,z,dir,player,isBlockerMove):
        if isBlockerMove:
           if self.lastMoveBlocker:
              raise Exception("last_move_blocker")
           elif self.blockerMoveCount >= 2:
              raise Exception("max_blocker_moves")
           self.lastMoveBlocker = True
           self.blockerMoveCount += 1
        else:
           self.lastMoveBlocker = False
        if not self.board.validMove(x,y,z,dir,isBlockerMove):
           raise Exception("invalid_move")
        self.board.move(x,y,z,dir,player,isBlockerMove)

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_paid_account = models.BooleanField(default=False)

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
    completed = models.BooleanField(default=False)
    winner = models.ForeignKey(User, related_name='winner', on_delete=models.SET_NULL, null=True, blank=True)
    elo_change = models.IntegerField(default=None, null=True)

    player_one_time_left = models.DurationField(default=timedelta(seconds=180))
    player_two_time_left = models.DurationField(default=timedelta(seconds=180))
    last_move_time = models.DateTimeField(auto_now_add=True)

    blocker_move_count = models.IntegerField(default=0)
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
           elif self.blocker_move_count >= 2:
              raise Exception("max_blocker_moves")
           self.last_move_blocker = True
           self.blocker_move_count += 1
        else:
           self.last_move_blocker = False
        if not board.validMove(x,y,z,dir,isBlockerMove):
           raise Exception("invalid_move")
        board.move(x,y,z,dir,player,isBlockerMove)
        self.game_state = json.dumps(board.getState())

    def __str__(self):
        return f"{self.player_one.username} vs {self.player_two.username} on {self.created_at.strftime('%Y-%m-%d')}"
