import random

def findMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]