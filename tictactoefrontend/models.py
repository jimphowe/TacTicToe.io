import random
from enum import Enum

class Piece(Enum):
    EMPTY = 'EMPTY'
    BLACK = 'BLACK'
    WHITE = 'WHITE'
    RED = 'RED'

class Board:
    def __init__(self):
        # A 3x3x3 grid of pieces (empty, red, black, white)
        self.setupBoard(11)
        #self.winningRuns = self.getWinningRuns()
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

    # Return true if the specified location is empty, or is pieces can be pushed without pushing a piece out of the board"
    def validMove(self,x,y,z,dir):
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
                if self.validMove(x,y,z,dir):
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
    def move(self,x,y,z,dir,player):
        if player == "RED":
            player = Piece.RED
        elif player == "WHITE":
            player = Piece.WHITE
        if not self.validMove(x,y,z,dir):
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
        displayStr = { Piece.RED : ' RED ', Piece.BLACK : 'BLACK', Piece.WHITE : 'WHITE', Piece.EMPTY : 'EMPTY'}
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
        while not self.validMove(x,y,z,dir):
            x = random.randint(0,2)
            y = random.randint(0,2)
            z = random.randint(0,2)
            dir = random.choice(directions)
        return (x,y,z,dir)
    
    # Returns the other player color. Red -> White. White -> Red
    def otherPlayer(self,player: Piece):
        return Piece.RED if player == Piece.WHITE else Piece.WHITE

    # Loops through possible moves and returns if a move wins the game, else returns None
    def getWinInOne(self,player: Piece):
        for (x,y,z,dir) in self.getPossibleMoves():
          self.move(x,y,z,dir,player)
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
    
    # Loops through possible moves and for each one examines all possible opponent moves.
    # If there are any moves which allow the given player to win after any opponent move, 
    # return one at random. Otherwise, return None
    def getWinInTwo(self,player: Piece):
        potential_moves = []
        for (x,y,z,dir) in self.getPossibleMoves():
          self.move(x,y,z,dir,player)
          if self.getWinInOne(self.otherPlayer(player)) == None:
            winner = True
            for (x2,y2,z2,dir2) in self.getPossibleMoves():
              self.move(x2,y2,z2,dir2,self.otherPlayer(player))
              if self.getWinInOne(player) == None:
                winner = False
              self.undo()
            if winner:
              potential_moves.append((x,y,z,dir))
          self.undo()
        if potential_moves:
          return random.choice(potential_moves)
        return None
    
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
        for run in self.getWinningRuns():
            if all(self.pieces[x][y][z] == player for (x,y,z) in run):
                return True
        return False
    
# Returns a winning move if one exists, otherwise picks a random move
class EasyAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num):
        winningMove = board.getWinInOne(self.player)
        if winningMove:
          return winningMove
        else:
          return board.getRandomMove(self.player)
        
# Returns a winning move if one exists, otherwise a move preventing the opponent from 
# winning if one exists, otherwise a random move
class MediumAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num):
        winningMove = board.getWinInOne(self.player)
        if winningMove:
          return winningMove
        else:
          defendingMove = board.getDefendingMove(self.player)
          if defendingMove:
            return defendingMove
          else:
            return board.getRandomMove(self.player)
          
# Returns a winning move if one exists, otherwise a move which wins in two turns if one exists, 
# otherwise a move preventing the opponent from winning, otherwise a random move
class HardAgent:
    def __init__(self,player):
        self.player = player

    def getMove(self, board: Board, move_num):
        if move_num < 2:
          defendingMove = board.getDefendingMove(self.player)
          if defendingMove:
            return defendingMove
          else:
            return board.getRandomMove(self.player)
        elif move_num < 3:
          winInTwo = board.getWinInTwo(self.player)
          if winInTwo:
            return winInTwo
          else:
            defendingMove = board.getDefendingMove(self.player)
            if defendingMove:
              return defendingMove
            else:
              return board.getRandomMove(self.player)
        else:
          winningMove = board.getWinInOne(self.player)
          if move_num > 2 and winningMove:
            return winningMove
          else:
            winInTwo = board.getWinInTwo(self.player)
            if winInTwo:
              return winInTwo
            else:
              defendingMove = board.getDefendingMove(self.player)
              if defendingMove:
                return defendingMove
              else:
                return board.getRandomMove(self.player)
    
class GamePlayer:
    def __init__(self, difficulty):
        self.board = Board()
        self.computerColor = Piece.WHITE
        match(difficulty):
            case 'easy':
                self.computer = EasyAgent(self.computerColor)
            case 'medium':
                self.computer = MediumAgent(self.computerColor)
            case 'hard':
                self.computer = HardAgent(self.computerColor)

    def isOver(self):
        return self.board.hasWon(Piece.RED) or self.board.hasWon(Piece.WHITE)

    def makeComputerMove(self):
        (x,y,z,dir) = self.computer.getMove(self.board, self.board.numPieces(self.computerColor))
        self.board.move(x,y,z,dir,self.computerColor)

    def move(self,x,y,z,dir,player):
        self.board.move(x,y,z,dir,player)
    

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    elo_rating = models.IntegerField(default=1000)
    is_paid_account = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()


class Game(models.Model):
    # Player fields
    player_one = models.ForeignKey(User, related_name='games_as_player_one', on_delete=models.CASCADE)
    player_two = models.ForeignKey(User, related_name='games_as_player_two', on_delete=models.CASCADE)
    
    # Game state and status
    game_state = models.JSONField(default=list)  # Storing the 3D grid as a list of lists of lists
    turn = models.ForeignKey(User, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    winner = models.ForeignKey(User, related_name='winner', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now=True)

    def start_new_game(player_one, player_two):
        board = Board()  # Initialize a new Board
        game = Game(
            player_one=player_one,
            player_two=player_two,
            game_state=board.getState(),  # Serialize the initial state of the board
            turn=random.choice([player_one, player_two]),
            completed=False
        )
        game.save()
        return game

    def __str__(self):
        return f"{self.player_one.username} vs {self.player_two.username} on {self.created_at.strftime('%Y-%m-%d')}"
