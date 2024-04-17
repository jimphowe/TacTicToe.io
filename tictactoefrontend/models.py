import random
from django.db import models
from enum import Enum

class Piece(Enum):
    EMPTY = 'EMPTY'
    BLACK = 'BLACK'
    WHITE = 'WHITE'
    RED = ' RED '

class Board:
    def __init__(self):
        # A 3x3x3 grid of pieces (empty, red, black, white)
        self.setupBoard(11)
        #self.winningRuns = self.getWinningRuns()
        self.moveHistory = []

    def setupBoard(self,pieces):
      self.pieces = [[[Piece.EMPTY for k in range(3)] for j in range(3)] for i in range(3)]
      for i in range(pieces):
        x = random.randrange(3)
        y = random.randrange(3)
        z = random.randrange(3)
        while (self.pieces[x][y][z] == Piece.BLACK):
          x = random.randrange(3)
          y = random.randrange(3)
          z = random.randrange(3)
        self.pieces[x][y][z] = Piece.BLACK

class Game(models.Model):
    def __init__(self):
        self.board = Board()

    def getState(self):
        return [[[piece for piece in row] for row in layer] for layer in self.board.pieces]
