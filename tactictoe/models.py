import random
from enum import Enum

class Piece(Enum):
    EMPTY = "EMPTY"
    BLACK = "BLACK"
    RED = "RED"
    BLUE = "BLUE"
    BLUE_BLOCKER = "BLUE_BLOCKER"
    RED_BLOCKER = "RED_BLOCKER"

# Board size configuration: 3 for 3x3x3, 4 for 4x4x4
DEFAULT_BOARD_SIZE = 3

# Zobrist hashing tables for efficient board state hashing
# Initialized lazily per board size
_zobrist_tables = {}

def _init_zobrist_table(size):
    """Initialize Zobrist hash table for a given board size."""
    if size in _zobrist_tables:
        return _zobrist_tables[size]

    random.seed(42)  # Fixed seed for reproducibility
    table = {}
    pieces = list(Piece)
    for x in range(size):
        for y in range(size):
            for z in range(size):
                for piece in pieces:
                    table[(x, y, z, piece)] = random.getrandbits(64)
    random.seed()  # Reset to random seed
    _zobrist_tables[size] = table
    return table

class Board:
    def __init__(self, board_size=DEFAULT_BOARD_SIZE):
        self.size = board_size
        self.max_coord = board_size - 1  # 2 for 3x3x3, 3 for 4x4x4
        # Number of starting neutral pieces scales with board size
        starting_pieces = 8 if board_size == 3 else 16
        self.setupBoard(starting_pieces)
        while self.hasSuperCorners() or self.hasSuperFaces():
           self.setupBoard(starting_pieces)
        self.winningRuns = self.getWinningRuns()
        self.moveHistory = []
        # Build index: for each position, which runs contain it
        self._runsByPosition = {}
        for run in self.winningRuns:
            for pos in run:
                if pos not in self._runsByPosition:
                    self._runsByPosition[pos] = []
                self._runsByPosition[pos].append(run)

        # Initialize Zobrist hashing for efficient state caching
        self._zobrist_table = _init_zobrist_table(board_size)
        self._zobrist_hash = self._compute_full_hash()

        # Transposition table for caching evaluated positions
        # Key: (zobrist_hash, player, depth) -> result
        self._win_in_one_cache = {}
        self._win_in_two_cache = {}

        # Cache for run statistics (invalidated on moves)
        self._run_stats_cache = {}

    def setupBoard(self,pieces):
        self.pieces = [[[Piece.EMPTY for _ in range(self.size)] for _ in range(self.size)] for _ in range(self.size)]
        for _ in range(pieces):
          x = random.randrange(self.size)
          y = random.randrange(self.size)
          z = random.randrange(self.size)
          while (self.pieces[x][y][z] == Piece.BLACK):
            x = random.randrange(self.size)
            y = random.randrange(self.size)
            z = random.randrange(self.size)
          self.pieces[x][y][z] = Piece.BLACK

    def _compute_full_hash(self):
        """Compute the full Zobrist hash of the current board state."""
        h = 0
        table = self._zobrist_table
        pieces = self.pieces
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    piece = pieces[x][y][z]
                    h ^= table[(x, y, z, piece)]
        return h

    def _update_hash(self, x, y, z, old_piece, new_piece):
        """Incrementally update the Zobrist hash after a piece change."""
        table = self._zobrist_table
        self._zobrist_hash ^= table[(x, y, z, old_piece)]
        self._zobrist_hash ^= table[(x, y, z, new_piece)]

    def _invalidate_caches(self):
        """Invalidate position-dependent caches after a move."""
        self._win_in_one_cache.clear()
        self._win_in_two_cache.clear()
        self._run_stats_cache.clear()

    def hasSuperCorners(self):
        # Super corner detection only applies to 3x3x3 boards
        if self.size != 3:
            return False
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
        # Super face detection only applies to 3x3x3 boards
        if self.size != 3:
            return False
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
        # Recompute hash and clear caches after state change
        self._zobrist_hash = self._compute_full_hash()
        self._invalidate_caches()
        self.moveHistory = []  # Clear move history since we can't undo past state loads

    # Returns a list of all N-in-a-row lines in the board (N = board size)
    # Used to check if the game is over
    def getWinningRuns(self):
        runs = []
        n = self.size
        max_c = self.max_coord

        # Generate all straight lines along each axis
        for i in range(n):
            for j in range(n):
                # Lines along x-axis
                runs.append([(k, i, j) for k in range(n)])
                # Lines along y-axis
                runs.append([(i, k, j) for k in range(n)])
                # Lines along z-axis
                runs.append([(i, j, k) for k in range(n)])

        # Generate face diagonals (diagonals on each 2D face)
        for i in range(n):
            # XY plane diagonals (for each z)
            runs.append([(k, k, i) for k in range(n)])
            runs.append([(k, max_c - k, i) for k in range(n)])
            # XZ plane diagonals (for each y)
            runs.append([(k, i, k) for k in range(n)])
            runs.append([(k, i, max_c - k) for k in range(n)])
            # YZ plane diagonals (for each x)
            runs.append([(i, k, k) for k in range(n)])
            runs.append([(i, k, max_c - k) for k in range(n)])

        # Generate space diagonals (4 body diagonals through the cube)
        runs.append([(k, k, k) for k in range(n)])
        runs.append([(k, k, max_c - k) for k in range(n)])
        runs.append([(k, max_c - k, k) for k in range(n)])
        runs.append([(max_c - k, k, k) for k in range(n)])

        # Remove duplicates (some lines may be generated multiple times)
        unique_runs = []
        seen = set()
        for run in runs:
            # Normalize: sort the tuple representation
            key = tuple(sorted(run))
            if key not in seen:
                seen.add(key)
                unique_runs.append(run)

        return unique_runs
    
    # Assumes that the move is valid
    def count_pieces_pushed(self, x, y, z, dir):
      if self.pieces[x][y][z] == Piece.EMPTY:
          return 0

      count = 0
      # Define direction deltas
      deltas = {
          'UP': (0, 0, -1),
          'DOWN': (0, 0, 1),
          'LEFT': (-1, 0, 0),
          'RIGHT': (1, 0, 0),
          'FRONT': (0, -1, 0),
          'BACK': (0, 1, 0)
      }
      dx, dy, dz = deltas[dir]

      # Count consecutive non-empty pieces in the push direction
      cx, cy, cz = x, y, z
      while 0 <= cx < self.size and 0 <= cy < self.size and 0 <= cz < self.size:
          if self.pieces[cx][cy][cz] == Piece.EMPTY:
              break
          count += 1
          cx += dx
          cy += dy
          cz += dz

      return count
    
    def validMove(self,x,y,z,dir,isBlocker):
       return self.pieces[x][y][z] == Piece.EMPTY or (not isBlocker and self.valid(x,y,z,dir))

    def isCenter(self, x, y, z):
        """Check if position is in the center (excluded from blocker placement).
        For 3x3x3: single center at (1,1,1)
        For 4x4x4: 2x2x2 center cube at (1,1,1), (1,1,2), (1,2,1), (1,2,2), (2,1,1), (2,1,2), (2,2,1), (2,2,2)
        """
        if self.size == 3:
            return x == 1 and y == 1 and z == 1
        else:  # size == 4
            return (x in [1, 2]) and (y in [1, 2]) and (z in [1, 2])

    # Return true if the specified location is empty, or if pieces can be pushed without pushing a piece out of the board
    def valid(self,x,y,z,dir):
        if not x in range(self.size) or not y in range(self.size) or not z in range(self.size):
              return False
        if self.isCenter(x, y, z):
              return False
        # Check if position is on the correct boundary face and there's room to push
        max_c = self.max_coord
        if dir == 'UP':
              if z != max_c:
                  return False
              # Check if there's an empty spot along the push path
              return any(self.pieces[x][y][z-i] == Piece.EMPTY for i in range(self.size))
        if dir == 'DOWN':
              if z != 0:
                  return False
              return any(self.pieces[x][y][z+i] == Piece.EMPTY for i in range(self.size))
        if dir == 'LEFT':
              if x != max_c:
                  return False
              return any(self.pieces[x-i][y][z] == Piece.EMPTY for i in range(self.size))
        if dir == 'RIGHT':
              if x != 0:
                  return False
              return any(self.pieces[x+i][y][z] == Piece.EMPTY for i in range(self.size))
        if dir == 'FRONT':
              if y != max_c:
                  return False
              return any(self.pieces[x][y-i][z] == Piece.EMPTY for i in range(self.size))
        if dir == 'BACK':
              if y != 0:
                  return False
              return any(self.pieces[x][y+i][z] == Piece.EMPTY for i in range(self.size))
        else:
              return False
        
    # Returns a list of all valid moves in the current board state
    def getPossibleMoves(self,available_power):
        directions = ['UP','DOWN','LEFT','RIGHT','FRONT','BACK']
        moves = []
        for x in range(self.size):
          for y in range(self.size):
            for z in range(self.size):
              for dir in directions:
                if self.valid(x,y,z,dir):
                  pieces_pushed = self.count_pieces_pushed(x,y,z,dir)
                  if pieces_pushed > available_power:
                      continue
                  moves.append((x,y,z,dir))
        return moves

    def spotToValidDir(self,x,y,z):
        directions = ['UP','DOWN','LEFT','RIGHT','FRONT','BACK']
        for dir in directions:
           if self.valid(x,y,z,dir):
              return (x,y,z,dir)

    def getPossibleBlockerMoves(self):
        moves = []
        for x in range(self.size):
          for y in range(self.size):
            for z in range(self.size):
              if self.pieces[x][y][z] == Piece.EMPTY:
                if not self.isCenter(x, y, z):
                  moves.append((x,y,z))
        return [self.spotToValidDir(x,y,z) for (x,y,z) in moves]

    def undo(self):
      if self.moveHistory == []:
        raise ValueError
      else:
        lastMove = self.moveHistory.pop()
        x, y, z, dir, pushed_pieces, old_hash = lastMove
        self._invalidate_caches()

        if pushed_pieces == 0:
          self.pieces[x][y][z] = Piece.EMPTY
        else:
          # Define direction deltas for the original push direction
          deltas = {
              'UP': (0, 0, -1),
              'DOWN': (0, 0, 1),
              'LEFT': (-1, 0, 0),
              'RIGHT': (1, 0, 0),
              'FRONT': (0, -1, 0),
              'BACK': (0, 1, 0)
          }
          dx, dy, dz = deltas[dir]

          # To undo a push, we need to shift pieces back in reverse order
          # Move started at (x,y,z) and pushed pieces in direction (dx,dy,dz)
          # After move: [NEW_PIECE, old_piece_0, old_piece_1, ..., old_piece_n-1]
          # We need to restore: [old_piece_0, old_piece_1, ..., old_piece_n-1, EMPTY]

          # Shift pieces back from position 0 outward (nearest to furthest)
          for i in range(1, pushed_pieces + 1):
            # Source is where the piece ended up (i positions from start)
            src_x, src_y, src_z = x + dx * i, y + dy * i, z + dz * i
            # Destination is one position back toward start
            dst_x, dst_y, dst_z = x + dx * (i - 1), y + dy * (i - 1), z + dz * (i - 1)
            self.pieces[dst_x][dst_y][dst_z] = self.pieces[src_x][src_y][src_z]

          # Clear the furthest position (where the last piece was pushed to)
          self.pieces[x + dx * pushed_pieces][y + dy * pushed_pieces][z + dz * pushed_pieces] = Piece.EMPTY

        # Restore the hash directly (must be after piece restoration)
        self._zobrist_hash = old_hash
            
    def moveAI(self,x,y,z,dir,player):
        if player == "RED":
            player = Piece.RED
        elif player == "BLUE":
            player = Piece.BLUE

        # Save hash before move for undo
        old_hash = self._zobrist_hash
        self._invalidate_caches()

        if (self.pieces[x][y][z] == Piece.EMPTY):
                old_piece = self.pieces[x][y][z]
                self.pieces[x][y][z] = player
                self._update_hash(x, y, z, old_piece, player)
                self.moveHistory.append((x,y,z,dir,0,old_hash))
        else:
            # Define direction deltas
            deltas = {
                'UP': (0, 0, -1),
                'DOWN': (0, 0, 1),
                'LEFT': (-1, 0, 0),
                'RIGHT': (1, 0, 0),
                'FRONT': (0, -1, 0),
                'BACK': (0, 1, 0)
            }
            dx, dy, dz = deltas[dir]

            # Find how many pieces to push (count until we hit empty)
            pushed_pieces = 0
            cx, cy, cz = x, y, z
            while 0 <= cx < self.size and 0 <= cy < self.size and 0 <= cz < self.size:
                if self.pieces[cx][cy][cz] == Piece.EMPTY:
                    break
                pushed_pieces += 1
                cx += dx
                cy += dy
                cz += dz

            # Shift pieces from furthest to nearest, updating hash incrementally
            for i in range(pushed_pieces, 0, -1):
                src_x, src_y, src_z = x + dx * (i - 1), y + dy * (i - 1), z + dz * (i - 1)
                dst_x, dst_y, dst_z = x + dx * i, y + dy * i, z + dz * i
                old_dst = self.pieces[dst_x][dst_y][dst_z]
                src_piece = self.pieces[src_x][src_y][src_z]
                self._update_hash(dst_x, dst_y, dst_z, old_dst, src_piece)
                self.pieces[dst_x][dst_y][dst_z] = src_piece

            # Place the new piece
            old_piece = self.pieces[x][y][z]
            self._update_hash(x, y, z, old_piece, player)
            self.pieces[x][y][z] = player
            self.moveHistory.append((x,y,z,dir,pushed_pieces,old_hash))

    # Makes a move after checking if it is valid
    # If there is a piece in the specified location, it is pushed in the specified direction, along with any pieces behind it
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
            # Save hash before move for undo
            old_hash = self._zobrist_hash
            self._invalidate_caches()

            if (self.pieces[x][y][z] == Piece.EMPTY):
                old_piece = self.pieces[x][y][z]
                self.pieces[x][y][z] = player
                self._update_hash(x, y, z, old_piece, player)
                self.moveHistory.append((x,y,z,dir,0,old_hash))
            else:
                # Define direction deltas
                deltas = {
                    'UP': (0, 0, -1),
                    'DOWN': (0, 0, 1),
                    'LEFT': (-1, 0, 0),
                    'RIGHT': (1, 0, 0),
                    'FRONT': (0, -1, 0),
                    'BACK': (0, 1, 0)
                }
                dx, dy, dz = deltas[dir]

                # Find how many pieces to push (count until we hit empty)
                pushed_pieces = 0
                cx, cy, cz = x, y, z
                while 0 <= cx < self.size and 0 <= cy < self.size and 0 <= cz < self.size:
                    if self.pieces[cx][cy][cz] == Piece.EMPTY:
                        break
                    pushed_pieces += 1
                    cx += dx
                    cy += dy
                    cz += dz

                # Shift pieces from furthest to nearest, updating hash incrementally
                for i in range(pushed_pieces, 0, -1):
                    src_x, src_y, src_z = x + dx * (i - 1), y + dy * (i - 1), z + dz * (i - 1)
                    dst_x, dst_y, dst_z = x + dx * i, y + dy * i, z + dz * i
                    old_dst = self.pieces[dst_x][dst_y][dst_z]
                    src_piece = self.pieces[src_x][src_y][src_z]
                    self._update_hash(dst_x, dst_y, dst_z, old_dst, src_piece)
                    self.pieces[dst_x][dst_y][dst_z] = src_piece

                # Place the new piece
                old_piece = self.pieces[x][y][z]
                self._update_hash(x, y, z, old_piece, player)
                self.pieces[x][y][z] = player
                self.moveHistory.append((x,y,z,dir,pushed_pieces,old_hash))

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
    
    # Returns the other player color. Red -> Blue. Blue -> Red
    def otherPlayer(self,player: Piece):
        return Piece.RED if player == Piece.BLUE else Piece.BLUE
    
    def neighbor_positions(self, x, y, z):
        neighbors = []
        for i in range(self.size):
            if i != x:
                neighbors.append((i, y, z))
        for j in range(self.size):
            if j != y:
                neighbors.append((x, j, z))
        for k in range(self.size):
            if k != z:
                neighbors.append((x, y, k))
        return neighbors
    
    def getTwoInARows(self, player: Piece):
        """Count near-complete runs. For 3x3x3: 2-in-a-row, for 4x4x4: 3-in-a-row."""
        count = 0.0
        target = self.size - 1  # 2 for 3x3x3, 3 for 4x4x4
        pieces = self.pieces  # Local lookup
        for run in self.winningRuns:
            player_count = 0
            has_empty = False
            blocked = False
            for pos in run:
                piece = pieces[pos[0]][pos[1]][pos[2]]
                if piece == player:
                    player_count += 1
                elif piece == Piece.EMPTY:
                    has_empty = True
                else:
                    blocked = True
                    break  # Opponent or blocker in the way
            if not blocked and player_count == target:
                count += 1.0 if has_empty else 0.5
        return count

    def numPieces(self, player: Piece):
        # Flattened sum is faster than triple nested loop
        return sum(piece == player for layer in self.pieces for row in layer for piece in row)

    def hasWon(self, player: Piece):
        pieces = self.pieces  # Local variable lookup is faster
        for run in self.winningRuns:
            won = True
            for pos in run:
                if pieces[pos[0]][pos[1]][pos[2]] != player:
                    won = False
                    break
            if won:
                return True
        return False

    def hasWonAt(self, player: Piece, x: int, y: int, z: int):
        """Check if player has won, only checking runs that contain position (x,y,z).
        Much faster than hasWon() when we know which position just changed."""
        pieces = self.pieces
        runs = self._runsByPosition.get((x, y, z), [])
        for run in runs:
            won = True
            for pos in run:
                if pieces[pos[0]][pos[1]][pos[2]] != player:
                    won = False
                    break
            if won:
                return True
        return False
    
    def isTie(self):
        if self.numPieces(Piece.EMPTY) > 0:
            return False
        return not (self.hasWon(Piece.RED) or self.hasWon(Piece.BLUE))
    
    def winningRun(self,player: Piece):
        for run in self.winningRuns:
            if all(self.pieces[x][y][z] == player for (x,y,z) in run):
                return run
        return None
    
    # Returns a random valid move in the given board
    def getRandomMove(self, player: Piece, power_dict):
      possible_moves = self.getPossibleMoves(power_dict[player.value])
      return random.choice(possible_moves)

    def _get_near_complete_runs(self, player: Piece):
        """Find runs where player has N-1 pieces and 1 empty spot (can win in one move)."""
        cache_key = ('near_complete', player)
        if cache_key in self._run_stats_cache:
            return self._run_stats_cache[cache_key]

        near_complete = []
        pieces = self.pieces
        target = self.size - 1  # Need N-1 pieces to win in one

        for run in self.winningRuns:
            player_count = 0
            empty_pos = None
            blocked = False
            for pos in run:
                piece = pieces[pos[0]][pos[1]][pos[2]]
                if piece == player:
                    player_count += 1
                elif piece == Piece.EMPTY:
                    if empty_pos is None:
                        empty_pos = pos
                    else:
                        blocked = True  # More than one empty
                        break
                else:
                    blocked = True  # Opponent or blocker
                    break
            if not blocked and player_count == target and empty_pos is not None:
                near_complete.append((run, empty_pos))

        self._run_stats_cache[cache_key] = near_complete
        return near_complete

    # Loops through possible moves and returns if a move wins the game, else returns None
    def getWinInOne(self, player: Piece, power_dict):
        # Check cache first
        cache_key = (self._zobrist_hash, player, power_dict[player.value])
        if cache_key in self._win_in_one_cache:
            return self._win_in_one_cache[cache_key]

        available_power = power_dict[player.value]

        # Fast path: check near-complete runs first (most likely to have winning moves)
        near_complete = self._get_near_complete_runs(player)
        for _run, empty_pos in near_complete:
            x, y, z = empty_pos
            # Check if we can place at this empty position
            for dir in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'FRONT', 'BACK']:
                if self.valid(x, y, z, dir):
                    cost = self.count_pieces_pushed(x, y, z, dir)
                    if cost <= available_power:
                        # This move should win - verify
                        self.moveAI(x, y, z, dir, player)
                        if self.hasWonAt(player, x, y, z):
                            self.undo()
                            self._win_in_one_cache[cache_key] = (x, y, z, dir)
                            return (x, y, z, dir)
                        self.undo()
                    break  # Only need one valid direction per position

        # Also check push-based wins (where pushing creates a line)
        for (x, y, z, dir) in self.getPossibleMoves(available_power):
            # Skip empty positions (already checked above)
            if self.pieces[x][y][z] == Piece.EMPTY:
                continue

            self.moveAI(x, y, z, dir, player)
            # Push moves need full check since pushed pieces can form wins
            if self.hasWon(player):
                self.undo()
                self._win_in_one_cache[cache_key] = (x, y, z, dir)
                return (x, y, z, dir)
            self.undo()

        self._win_in_one_cache[cache_key] = None
        return None
    
    # Loops through possible moves and returns a move which prevents the opponent from winning 
    # If there are multiple, picks one at random. If none exist returns None
    def getDefendingMove(self,player: Piece, power_dict):
        potential_moves = []
        for (x,y,z,dir) in self.getPossibleMoves(power_dict[player.value]):
          self.moveAI(x,y,z,dir,player)
          opponent = self.otherPlayer(player)
          if self.getWinInOne(opponent, power_dict) == None:
            potential_moves.append((x,y,z,dir))
          self.undo()
        if potential_moves:
          return random.choice(potential_moves)
        return None
    
    def getGoodDefendingMove(self, player: Piece, power_dict):
        potential_moves = []
        for (x, y, z, dir) in self.getPossibleMoves(power_dict[player.value]):
            points = 0
            self.moveAI(x, y, z, dir, player)
            opponent = self.otherPlayer(player)
            if self.getWinInOne(opponent, power_dict) == None:
                points += 100
            points += self.getTwoInARows(player) * 4
            if self.pieces[x][y][z] == opponent:
               points += 10
            neighbors = self.neighbor_positions(x, y, z)
            for (i,j,k) in neighbors:
               if self.pieces[i][j][k] == opponent:
                  points += 3
            potential_moves.append(((x, y, z, dir), points))
            self.undo()

        potential_moves.sort(key=lambda move: move[1], reverse=True)

        return potential_moves[0][0]
    
    def getCorners(self):
        """Get all corner positions for the current board size."""
        m = self.max_coord
        return frozenset([
            (0, 0, 0), (0, 0, m), (0, m, 0), (0, m, m),
            (m, 0, 0), (m, 0, m), (m, m, 0), (m, m, m)
        ])

    def getMiddles(self):
        """Get middle/edge positions for the current board size.
        For 3x3x3: face centers
        For 4x4x4: similar strategic positions on faces
        """
        if self.size == 3:
            return frozenset([(1, 0, 1), (2, 1, 1), (1, 2, 2), (0, 1, 1), (1, 1, 0), (1, 1, 2)])
        else:  # size == 4
            # Face center positions for 4x4x4 (positions on faces that aren't corners or edges)
            middles = set()
            m = self.max_coord
            # For each face, add the inner 2x2 positions
            for i in [1, 2]:
                for j in [1, 2]:
                    middles.add((0, i, j))  # left face
                    middles.add((m, i, j))  # right face
                    middles.add((i, 0, j))  # front face
                    middles.add((i, m, j))  # back face
                    middles.add((i, j, 0))  # top face
                    middles.add((i, j, m))  # bottom face
            return frozenset(middles)

    def getBestDefendingMove(self, player: Piece, power_dict):
        opponent = self.otherPlayer(player)
        corners = self.getCorners()
        middles = self.getMiddles()
        potential_moves = []
        available_power = power_dict[player.value]

        all_moves = self.getPossibleMoves(available_power)

        # For 4x4x4, limit initial move evaluation to avoid slowdown
        if self.size == 4 and len(all_moves) > 40:
            all_moves = random.sample(all_moves, 40)

        for (x, y, z, dir) in all_moves:
            points = 0
            power_cost = self.count_pieces_pushed(x, y, z, dir)

            if available_power > 0:
                power_efficiency = 15 * (1 - power_cost / available_power)
                points += power_efficiency
            self.moveAI(x, y, z, dir, player)
            if self.getWinInOne(opponent, power_dict) == None:
                points += 100
            points += self.getTwoInARows(player) * 5
            neighbors = self.neighbor_positions(x, y, z)
            non_empty_neighbors = sum(1 for i, j, k in neighbors
                                      if self.pieces[i][j][k] != Piece.EMPTY)
            for (i, j, k) in neighbors:
                if self.pieces[i][j][k] == opponent:
                    points += 6
            if self.pieces[x][y][z] == opponent:
                points += 15
            if non_empty_neighbors == 6:
                points += 10
            if (x, y, z) in middles:
                points += 2
            if (x, y, z) in corners:
                points -= 1
            potential_moves.append(((x, y, z, dir), points))
            self.undo()

        potential_moves.sort(key=lambda move: move[1], reverse=True)

        # Check top moves for getWinInTwo condition
        # For 4x4x4, check fewer moves and skip this expensive check early game
        num_to_check = 3 if self.size == 4 else 5
        top_moves = potential_moves[:num_to_check]

        # Skip getWinInTwo check for 4x4x4 in early game (too slow, less critical)
        if self.size == 4 and self.numPieces(player) < 3:
            if potential_moves:
                return potential_moves[0][0]
            return None

        for move, _ in top_moves:
            x, y, z, dir = move
            self.moveAI(x, y, z, dir, player)
            if self.getWinInTwo(opponent, power_dict) is None:
                self.undo()
                return move
            self.undo()

        if potential_moves:
            return potential_moves[0][0]
        return None

    def _score_move_for_ordering(self, x, y, z, _dir, player: Piece):
        """Quick heuristic score for move ordering - higher is better."""
        score = 0
        pieces = self.pieces

        # Prefer moves that place near our pieces
        for run in self._runsByPosition.get((x, y, z), []):
            player_count = sum(1 for pos in run if pieces[pos[0]][pos[1]][pos[2]] == player)
            score += player_count * 10

        # Prefer empty positions (cheaper)
        if pieces[x][y][z] == Piece.EMPTY:
            score += 5

        # Prefer strategic positions
        if self.size == 3 and (x, y, z) == (1, 1, 1):
            score += 15
        elif self.size == 4 and x in [1, 2] and y in [1, 2] and z in [1, 2]:
            score += 10

        return score

    # Loops through possible moves and for each one examines all possible opponent moves.
    # If there are any moves which allow the given player to win after any opponent move,
    # return one at random. Otherwise, return None
    def getWinInTwo(self, player: Piece, power_dict):
        # Check cache first
        cache_key = (self._zobrist_hash, player, power_dict[player.value])
        if cache_key in self._win_in_two_cache:
            return self._win_in_two_cache[cache_key]

        winningMove = self.getWinInOne(player, power_dict)
        if winningMove:
            self._win_in_two_cache[cache_key] = winningMove
            return winningMove

        potential_moves = []
        opponent = self.otherPlayer(player)
        moves_made = self.numPieces(Piece.RED) + self.numPieces(Piece.BLUE)

        all_moves = self.getPossibleMoves(power_dict[player.value])

        # Move ordering: score moves and sort best-first for faster pruning
        scored_moves = [(m, self._score_move_for_ordering(m[0], m[1], m[2], m[3], player)) for m in all_moves]
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        all_moves = [m for m, _ in scored_moves]

        # For 4x4x4, limit search but take best moves, not random
        max_moves = 40 if self.size == 4 else len(all_moves)
        all_moves = all_moves[:max_moves]

        for (x, y, z, dir) in all_moves:
            first_move_cost = self.count_pieces_pushed(x, y, z, dir)
            remaining_power = power_dict[player.value] - first_move_cost + GamePlayer.get_power_gain(moves_made)
            self.moveAI(x, y, z, dir, player)

            if self.getWinInOne(opponent, power_dict) is None:
                winner = True
                opponent_moves = self.getPossibleMoves(power_dict[opponent.value])

                # Order opponent moves too - check their best moves first
                opp_scored = [(m, self._score_move_for_ordering(m[0], m[1], m[2], m[3], opponent)) for m in opponent_moves]
                opp_scored.sort(key=lambda x: x[1], reverse=True)
                opponent_moves = [m for m, _ in opp_scored]

                # For 4x4x4, limit opponent moves but take best, not random
                max_opp_moves = 30 if self.size == 4 else len(opponent_moves)
                opponent_moves = opponent_moves[:max_opp_moves]

                for (x2, y2, z2, dir2) in opponent_moves:
                    self.moveAI(x2, y2, z2, dir2, opponent)
                    if self.getWinInOne(player, {player.value: remaining_power, opponent.value: power_dict[opponent.value]}) is None:
                        winner = False
                        self.undo()
                        break  # Early termination
                    self.undo()

                if winner:
                    potential_moves.append((x, y, z, dir))
                    # Early exit: found a winning move
                    self.undo()
                    result = (x, y, z, dir)
                    self._win_in_two_cache[cache_key] = result
                    return result

            self.undo()

        self._win_in_two_cache[cache_key] = None
        return None
    
    # Returns a random move which is either a middle or edge
    def getGoodStartMove(self, player: Piece, power_dict):
        corners = self.getCorners()

        # Collect valid moves from middles and edges
        potential_moves = []
        for (x, y, z, dir) in self.getPossibleMoves(power_dict[player.value]):
            if not (x, y, z) in corners:
                potential_moves.append((x, y, z, dir))

        # Randomly select one of the valid moves
        if potential_moves:
            return random.choice(potential_moves)
        return None
    
    def getSimpleDefendingMove(self,player: Piece, power_dict):
        opponent = self.otherPlayer(player)
        for (x, y, z, dir) in self.getPossibleMoves(power_dict[player.value]):
            if self.pieces[x][y][z] == opponent:
               return((x,y,z,dir))
            neighbors = self.neighbor_positions(x, y, z)
            for (i,j,k) in neighbors:
              if self.pieces[i][j][k] == opponent:
                return((x,y,z,dir))
              
    def getRandomBlockerMove(self):
        possibleMoves = self.getPossibleBlockerMoves()
        return random.choice(possibleMoves)

    def getGoodIntermediateBlockerMove(self, player: Piece):
      opponent = self.otherPlayer(player)
      potential_positions = []
      max_c = self.max_coord
      # For 4x4x4, look for N-1 pieces in a row instead of just 2
      target_count = self.size - 1

      # Look through all winning runs
      for run in self.winningRuns:
          # Check if opponent has target_count pieces in this run
          opponent_pieces = [(x,y,z) for (x,y,z) in run if self.pieces[x][y][z] == opponent]
          if len(opponent_pieces) == target_count:
              # Get the remaining positions in the run
              remaining_pos = [pos for pos in run if pos not in opponent_pieces][0]
              x, y, z = remaining_pos

              if self.pieces[x][y][z] == Piece.EMPTY:
                  # Case 1: Remaining spot is empty - highest priority
                  if not self.isCenter(x, y, z):
                      potential_positions.append((remaining_pos, 15))  # Highest priority

                  # Also consider positions where pieces could be pushed to this empty spot
                  for piece_pos in opponent_pieces:
                      push_positions = self.getPushablePositions(piece_pos, remaining_pos)
                      for pos in push_positions:
                          if self.pieces[pos[0]][pos[1]][pos[2]] == Piece.EMPTY:
                              if not self.isCenter(pos[0], pos[1], pos[2]):
                                  potential_positions.append((pos, 10))

              else:
                  # Case 2: Remaining spot is filled - check if it's pushable
                  pushable = False
                  directions = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'FRONT', 'BACK']
                  for dir in directions:
                      if self.valid(x, y, z, dir):
                          pushable = True
                          # Get positions where the filled piece could be pushed to
                          if dir == 'UP' and z > 0:
                              block_pos = (x, y, z-1)
                          elif dir == 'DOWN' and z < max_c:
                              block_pos = (x, y, z+1)
                          elif dir == 'LEFT' and x > 0:
                              block_pos = (x-1, y, z)
                          elif dir == 'RIGHT' and x < max_c:
                              block_pos = (x+1, y, z)
                          elif dir == 'FRONT' and y > 0:
                              block_pos = (x, y-1, z)
                          elif dir == 'BACK' and y < max_c:
                              block_pos = (x, y+1, z)
                          else:
                              continue

                          if self.pieces[block_pos[0]][block_pos[1]][block_pos[2]] == Piece.EMPTY:
                              if not self.isCenter(block_pos[0], block_pos[1], block_pos[2]):
                                  potential_positions.append((block_pos, 8))  # Medium priority

                  if pushable:
                      # Also look for positions to block the push path
                      for piece_pos in opponent_pieces:
                          push_positions = self.getPushablePositions(piece_pos, remaining_pos)
                          for pos in push_positions:
                              if self.pieces[pos[0]][pos[1]][pos[2]] == Piece.EMPTY:
                                  if not self.isCenter(pos[0], pos[1], pos[2]):
                                      potential_positions.append((pos, 5))  # Lower priority

      if not potential_positions:
          return self.getRandomBlockerMove()

      # Sort by priority and pick highest priority position
      potential_positions.sort(key=lambda x: x[1], reverse=True)
      for pos, _ in potential_positions:
          blocker_move = self.spotToValidDir(pos[0], pos[1], pos[2])
          if blocker_move:
              return blocker_move

      return self.getRandomBlockerMove()

    # Find positions where pieces could be pushed from to reach target
    def getPushablePositions(self, piece_pos, target_pos):
        x1, y1, z1 = piece_pos
        x2, y2, z2 = target_pos
        positions = []
        max_c = self.max_coord

        # Check if pieces are in same row/column/diagonal and find pushable positions
        if x1 == x2:
            if y1 == y2:  # Same vertical line
                if z1 < z2:
                    positions.append((x1, y1, max(0, z1-1)))
                else:
                    positions.append((x1, y1, min(max_c, z1+1)))
            elif z1 == z2:  # Same horizontal line in x-plane
                if y1 < y2:
                    positions.append((x1, max(0, y1-1), z1))
                else:
                    positions.append((x1, min(max_c, y1+1), z1))

        elif y1 == y2:
            if z1 == z2:  # Same horizontal line in y-plane
                if x1 < x2:
                    positions.append((max(0, x1-1), y1, z1))
                else:
                    positions.append((min(max_c, x1+1), y1, z1))

        # For diagonal lines, add positions on both sides
        if abs(x2-x1) == abs(y2-y1) == 1:
            positions.extend([
                (2*x1-x2, 2*y1-y2, z1),
                (2*x2-x1, 2*y2-y1, z1)
            ])
        if abs(x2-x1) == abs(z2-z1) == 1:
            positions.extend([
                (2*x1-x2, y1, 2*z1-z2),
                (2*x2-x1, y1, 2*z2-z1)
            ])
        if abs(y2-y1) == abs(z2-z1) == 1:
            positions.extend([
                (x1, 2*y1-y2, 2*z1-z2),
                (x1, 2*y2-y1, 2*z2-z1)
            ])

        # Filter out invalid positions
        return [(x,y,z) for (x,y,z) in positions
                if 0 <= x <= max_c and 0 <= y <= max_c and 0 <= z <= max_c
                and not self.isCenter(x, y, z)]
    
    def _score_position_for_player(self, x, y, z, player: Piece):
        """Score how valuable a position is for the player's own piece (not blocker).
        Higher score = better position for player's piece = should NOT put blocker here."""
        score = 0
        pieces = self.pieces

        # Count how many of player's runs this position contributes to
        for run in self._runsByPosition.get((x, y, z), []):
            player_count = 0
            blocked = False
            for pos in run:
                piece = pieces[pos[0]][pos[1]][pos[2]]
                if piece == player:
                    player_count += 1
                elif piece != Piece.EMPTY and piece != Piece.BLACK:
                    blocked = True
                    break
            if not blocked:
                # More valuable if player already has pieces in this run
                score += (player_count + 1) * 10

        # Bonus for strategic positions
        corners = self.getCorners()
        if (x, y, z) in corners:
            # Corners are the most valuable positions
            score += 20

        if self.size == 3:
            # Face centers get a slight bonus (positions in the middle of each face)
            face_centers = [(1, 0, 1), (1, 2, 1), (0, 1, 1), (2, 1, 1), (1, 1, 0), (1, 1, 2)]
            if (x, y, z) in face_centers:
                score += 8
        else:  # 4x4x4
            # Middle 2x2 on each face gets a slight bonus
            face_middles = set()
            m = self.max_coord
            for i in [1, 2]:
                for j in [1, 2]:
                    face_middles.add((0, i, j))   # left face
                    face_middles.add((m, i, j))   # right face
                    face_middles.add((i, 0, j))   # front face
                    face_middles.add((i, m, j))   # back face
                    face_middles.add((i, j, 0))   # bottom face
                    face_middles.add((i, j, m))   # top face
            if (x, y, z) in face_middles:
                score += 8

        return score

    def getGoodBlockerMove(self, player: Piece, power_dict):
      defending_move = self.getDefendingMove(player, power_dict)
      winning_move = self.getWinInOne(player, power_dict)
      if defending_move or winning_move:
          return None

      # Find all blocker positions that would create a defending opportunity
      effective_blockers = []
      for blocker_move in self.getPossibleBlockerMoves():
          (x,y,z,dir) = blocker_move
          self.moveAI(x, y, z, dir, Piece.BLUE_BLOCKER)

          defending_move = self.getDefendingMove(player, power_dict)
          winning_move = self.getWinInOne(player, power_dict)

          if defending_move or winning_move:
              # Score this blocker position - LOWER score means better for blocker
              # (we want to save high-value positions for our actual pieces)
              pos_score = self._score_position_for_player(x, y, z, player)
              effective_blockers.append((blocker_move, pos_score, defending_move))
          self.undo()

      if effective_blockers:
          # Sort by position score (ascending) - put blocker in LEAST valuable position
          effective_blockers.sort(key=lambda item: item[1])
          best_blocker, _, _ = effective_blockers[0]
          return (best_blocker, False)

      if random.random() < 0.5:
        return (self.getRandomBlockerMove(), True)
      else:
        return (self.getGoodIntermediateBlockerMove(player), True)
    
    def getBetterBlockerMove(self, player: Piece, power_dict):
      opponent = self.otherPlayer(player)
      initial_defending_move = self.getDefendingMove(player, power_dict)
      initial_winning_move = self.getWinInOne(player, power_dict) or self.getWinInTwo(player, power_dict)
      if initial_winning_move:
          return None

      potential_blocks = []

      for run in self.winningRuns:
        # Check if opponent has pieces in this run
        opponent_pieces = [(x,y,z) for (x,y,z) in run if self.pieces[x][y][z] == opponent]
        if len(opponent_pieces) >= 1:
            # Get the empty positions in the run
            empty_positions = [(x,y,z) for (x,y,z) in run if self.pieces[x][y][z] == Piece.EMPTY]
            for pos in empty_positions:
                if not self.isCenter(pos[0], pos[1], pos[2]):
                    potential_blocks.append(pos)

            # Also consider positions that could block pushes
            for piece_pos in opponent_pieces:
                for empty_pos in empty_positions:
                    push_positions = self.getPushablePositions(piece_pos, empty_pos)
                    for pos in push_positions:
                        if self.pieces[pos[0]][pos[1]][pos[2]] == Piece.EMPTY:
                            potential_blocks.append(pos)

      # Remove duplicates and get valid moves
      potential_blocks = list(set(potential_blocks))
      valid_blocker_moves = [self.spotToValidDir(x,y,z) for (x,y,z) in potential_blocks if self.spotToValidDir(x,y,z)]

      # Find all effective blocker positions and score them
      effective_blockers = []
      for blocker_move in valid_blocker_moves:
          (x,y,z,dir) = blocker_move
          self.moveAI(x, y, z, dir, Piece.BLUE_BLOCKER)

          defending_move = self.getDefendingMove(player, power_dict)
          winning_move = self.getWinInOne(player, power_dict) or self.getWinInTwo(player, power_dict)

          if (defending_move and not initial_defending_move) or winning_move:
              # Score this position - LOWER is better for placing a blocker
              # (we want to save high-value positions for our actual pieces)
              pos_score = self._score_position_for_player(x, y, z, player)
              effective_blockers.append((blocker_move, pos_score))
          self.undo()

      if effective_blockers:
          # Sort by position score (ascending) - put blocker in LEAST valuable position
          effective_blockers.sort(key=lambda item: item[1])
          best_blocker, _ = effective_blockers[0]
          return (best_blocker, True)

      if initial_defending_move:
          return None
      return (self.getGoodIntermediateBlockerMove(player), True)
       
# Returns a winning move if one exists, otherwise picks a random move
class EasyAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num, power_dict):
        # Easy agent: basic threat detection and simple defense
        threat = board.getWinInOne(board.otherPlayer(self.player), power_dict)
        if threat:
            x,y,z,_ = threat
            if board.pieces[x][y][z] == Piece.EMPTY:
                return threat
        if move_num > 3:
           winningMove = board.getWinInOne(self.player, power_dict)
           if winningMove:
              return winningMove
        simpleDefendingMove = board.getSimpleDefendingMove(self.player, power_dict)
        if simpleDefendingMove:
            return simpleDefendingMove
        return board.getRandomMove(self.player, power_dict)

    def getBlockerMove(self, board: Board, power_dict):
       return None

# Returns a winning move if one exists, otherwise a move preventing the opponent from
# winning if one exists, otherwise a random move
class MediumAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num, power_dict):
        # Medium agent: win detection + good defending moves
        if move_num == 0:
           return board.getGoodStartMove(self.player, power_dict)
        winningMove = board.getWinInOne(self.player, power_dict)
        if move_num <= 2 or move_num > 3:
            if winningMove:
                return winningMove
            else:
                defendingMove = board.getGoodDefendingMove(self.player, power_dict)
                if defendingMove:
                    return defendingMove
                else:
                    return board.getRandomMove(self.player, power_dict)
        else:
            return board.getRandomMove(self.player, power_dict)

    def getBlockerMove(self, board: Board, power_dict):
       return (board.getRandomBlockerMove(), False)
          
class HardAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num, power_dict):
        # Hard agent: full win-in-two lookahead + best defending moves
        if move_num == 0:
           return board.getBestDefendingMove(self.player, power_dict)
        elif move_num == 1:
          winInTwo = board.getWinInTwo(self.player, power_dict)
          if winInTwo:
            return winInTwo
          else:
            defendingMove = board.getGoodDefendingMove(self.player, power_dict)
            if defendingMove:
              return defendingMove
            else:
              return board.getRandomMove(self.player, power_dict)
        else:
          winningMove = board.getWinInOne(self.player, power_dict)
          if winningMove:
            return winningMove
          else:
            winInTwo = board.getWinInTwo(self.player, power_dict)
            if winInTwo:
              return winInTwo
            else:
              defendingMove = board.getBestDefendingMove(self.player, power_dict)
              if defendingMove:
                return defendingMove
              else:
                return board.getRandomMove(self.player, power_dict)

    def getBlockerMove(self, board: Board, power_dict):
       return board.getGoodBlockerMove(self.player, power_dict)

class ExpertAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num, power_dict):
        # Expert agent: full win-in-two lookahead + best defending moves everywhere
        if move_num == 0:
           return board.getBestDefendingMove(self.player, power_dict)
        elif move_num == 1:
          winInTwo = board.getWinInTwo(self.player, power_dict)
          if winInTwo:
            return winInTwo
          else:
            defendingMove = board.getBestDefendingMove(self.player, power_dict)
            if defendingMove:
              return defendingMove
            else:
              return board.getRandomMove(self.player, power_dict)
        else:
          winningMove = board.getWinInOne(self.player, power_dict)
          if winningMove:
            return winningMove
          else:
            winInTwo = board.getWinInTwo(self.player, power_dict)
            if winInTwo:
              return winInTwo
            else:
              defendingMove = board.getBestDefendingMove(self.player, power_dict)
              if defendingMove:
                return defendingMove
              else:
                return board.getRandomMove(self.player, power_dict)

    def getBlockerMove(self, board: Board, power_dict):
       return board.getBetterBlockerMove(self.player, power_dict)
    
class GamePlayer:
    def __init__(self, difficulty, computerColor, board_size=DEFAULT_BOARD_SIZE):
        self.board_size = board_size
        self.board = Board(board_size)
        self.computer_color = Piece.RED if computerColor == 'RED' else Piece.BLUE
        self.red_power = 0
        self.blue_power = 1
        self.red_blocker_count = 0
        self.blue_blocker_count = 0
        self.moves_made = 0
        self.difficulty = difficulty
        # Set blocker limits (same for all board sizes and colors)
        self.max_red_blockers = 3
        self.max_blue_blockers = 3
        match(difficulty):
            case 'easy':
                self.computer = EasyAgent(self.computer_color)
            case 'medium':
                self.computer = MediumAgent(self.computer_color)
            case 'hard':
                self.computer = HardAgent(self.computer_color)
            case 'expert':
                self.computer = ExpertAgent(self.computer_color)

    @staticmethod
    def get_power_gain(moves_made):
        turn = (moves_made + 1) // 2
        return 1 if turn % 2 == 0 else 0

    def serialize(self):
        return json.dumps({
            'board_state': self.board.getState(),
            'board_size': self.board_size,
            'computer_color': self.computer_color.value,
            'red_blocker_count': self.red_blocker_count,
            'blue_blocker_count': self.blue_blocker_count,
            'red_power': self.red_power,
            'blue_power': self.blue_power,
            'difficulty': self.difficulty,
            'moves_made': self.moves_made
        })

    @classmethod
    def deserialize(cls, serialized_data):
        data = json.loads(serialized_data)
        board_size = data.get('board_size', DEFAULT_BOARD_SIZE)
        game_player = cls(data['difficulty'], data['computer_color'], board_size)
        game_player.board.setState(data['board_state'])
        game_player.red_blocker_count = data['red_blocker_count']
        game_player.blue_blocker_count = data['blue_blocker_count']
        game_player.red_power = data['red_power']
        game_player.blue_power = data['blue_power']
        game_player.moves_made = data['moves_made']
        return game_player

    def isOver(self):
        return self.board.hasWon(Piece.RED) or self.board.hasWon(Piece.BLUE)

    def makeComputerMove(self,isBlockerMove):
        power_dict = {
            'RED': self.red_power,
            'BLUE': self.blue_power
           }
        if isBlockerMove:
           move = self.computer.getBlockerMove(self.board, power_dict)
           if move:
            ((x,y,z,dir), block_again) = move
            if self.computer_color == Piece.RED:
               self.red_blocker_count += 1
               self.board.move(x,y,z,dir,Piece.RED,True)
            else:
               self.blue_blocker_count += 1
               self.board.move(x,y,z,dir,Piece.BLUE,True)
            return (move, block_again)
           else:
              return None
        else:
           (x,y,z,dir) = self.computer.getMove(self.board, self.board.numPieces(self.computer_color), power_dict)
           self.moves_made += 1
           pieces_pushed = self.board.count_pieces_pushed(x, y, z, dir)
           if self.computer_color == Piece.RED:
              self.red_power = min(5, self.red_power - pieces_pushed + self.get_power_gain(self.moves_made))
           else:
              self.blue_power = min(5, self.blue_power - pieces_pushed + self.get_power_gain(self.moves_made))
           self.board.moveAI(x,y,z,dir,self.computer_color)
           return (x,y,z,dir)

    def move(self,x,y,z,dir,player,isBlockerMove):
        if not self.board.validMove(x,y,z,dir,isBlockerMove):
              raise Exception("invalid_move")
        if isBlockerMove:
           if player == Piece.RED:
              if self.red_blocker_count >= self.max_red_blockers:
                 raise Exception("max_blocker_moves")
              self.red_blocker_count += 1
           else:
              if self.blue_blocker_count >= self.max_blue_blockers:
                 raise Exception("max_blocker_moves")
              self.blue_blocker_count += 1
        else:
           self.moves_made += 1
           available_power = self.red_power if player == Piece.RED else self.blue_power
           pieces_pushed = self.board.count_pieces_pushed(x, y, z, dir)
           if pieces_pushed > available_power:
                raise Exception("insufficient_power")
           if player == Piece.RED:
              self.red_power = min(5, self.red_power - pieces_pushed + self.get_power_gain(self.moves_made))
           else:
              self.blue_power = min(5, self.blue_power - pieces_pushed + self.get_power_gain(self.moves_made))
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

BOARD_SIZE_CHOICES = [
    (3, '3x3x3'),
    (4, '4x4x4'),
]

class Game(models.Model):
    # Player fields
    player_one = models.ForeignKey(User, related_name='games_as_player_one', on_delete=models.CASCADE)
    player_two = models.ForeignKey(User, related_name='games_as_player_two', on_delete=models.CASCADE)

    game_type = models.CharField(max_length=20, choices=GAME_TYPES)
    game_code = models.CharField(max_length=6, unique=True)
    board_size = models.IntegerField(choices=BOARD_SIZE_CHOICES, default=3)

    # Game state and status
    game_state = models.JSONField(default=list)
    turn = models.ForeignKey(User, on_delete=models.CASCADE)
    moves_made = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    winner = models.ForeignKey(User, related_name='winner', on_delete=models.SET_NULL, null=True, blank=True)
    elo_change = models.IntegerField(default=None, null=True)

    player_one_time_left = models.DurationField(default=timedelta(seconds=180))
    player_two_time_left = models.DurationField(default=timedelta(seconds=180))
    last_move_time = models.DateTimeField(auto_now_add=True)

    red_power = models.IntegerField(default=0)
    blue_power = models.IntegerField(default=1)
    red_blocker_count = models.IntegerField(default=0)
    blue_blocker_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now=True)

    def get_max_blockers(self, color):
        """Get max blocker count (same for all board sizes and colors)."""
        return 3

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
    def start_new_game(cls, player_one, player_two, game_type, board_size=DEFAULT_BOARD_SIZE):
        board = Board(board_size)
        game = cls.create(
            player_one=player_one,
            player_two=player_two,
            game_type=game_type,
            board_size=board_size,
            game_state=json.dumps(board.getState()),
            turn=player_one,
            completed=False
        )
        game.save()
        return game

    @staticmethod
    def get_power_gain(moves_made):
        turn = (moves_made + 1) // 2
        return 1 if turn % 2 == 0 else 0

    def move(self, x, y, z, dir, player, isBlockerMove):
        board = Board(self.board_size)
        board.setState(json.loads(self.game_state))
        if not board.validMove(x,y,z,dir,isBlockerMove):
           raise Exception("invalid_move")
        if isBlockerMove:
           if player == Piece.RED:
                if self.moves_made < 1:
                    raise Exception("red_first_move")
                if self.red_blocker_count >= self.get_max_blockers('RED'):
                    raise Exception("max_blocker_moves")
                self.red_blocker_count += 1
           else:
                if self.blue_blocker_count >= self.get_max_blockers('BLUE'):
                    raise Exception("max_blocker_moves")
                self.blue_blocker_count += 1
        else:
           self.moves_made += 1
           available_power = self.red_power if player == Piece.RED else self.blue_power
           pieces_pushed = board.count_pieces_pushed(x, y, z, dir)
           if pieces_pushed > available_power:
                raise Exception("insufficient_power")
           if player == Piece.RED:
              self.red_power = min(5, self.red_power - pieces_pushed + self.get_power_gain(self.moves_made))
           else:
              self.blue_power = min(5, self.blue_power - pieces_pushed + self.get_power_gain(self.moves_made))
        board.move(x,y,z,dir,player,isBlockerMove)
        self.game_state = json.dumps(board.getState())

    def __str__(self):
        return f"{self.player_one.username} vs {self.player_two.username} on {self.created_at.strftime('%Y-%m-%d')}"
