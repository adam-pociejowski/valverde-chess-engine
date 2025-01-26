import pygame as p
import ChessEngine
import RandomMoveFinder

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
p.init()
whiteColor = p.Color("white")
blackColor = p.Color("gray")
highlightSelectedSquareColor = p.Color("blue")
highlightPossibleMovesColor = p.Color("yellow")


def loadImages():
    pieces = [ 'wP', 'wR', 'wN', 'wB', 'wQ', 'wK',
               'bP', 'bR', 'bN', 'bB', 'bQ', 'bK' ]
    for piece in pieces:
        IMAGES[piece] = p.image.load('images/'+piece+'.png')


def main():
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    loadImages()
    running = True
    sqSelected = () # last click tuple (x,y)
    playerClicks = [] # keeps track of layer clicks to move piece
    playerWhite = False # player is white
    playerBlack = False # computer is black
    isGameOver = False


    while running:
        isHumanTurn = (gs.whiteToMove and playerWhite) or (not gs.whiteToMove and playerBlack)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN: # human moving
                if not isGameOver and isHumanTurn:
                    location = p.mouse.get_pos() # (x, y)
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col): # clicked the same square twice
                        sqSelected = () # unselect
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                print(move.getChessNotation())
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
                            print('Cannot move ', move.getChessNotation())

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True

        # AI move logic
        if not isGameOver and not isHumanTurn:
            aiMove = RandomMoveFinder.findMove(validMoves)
            gs.makeMove(aiMove)
            moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
            if len(validMoves) == 0:
                isGameOver = True

        drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()


def highlightMoveSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(90)
            s.fill(highlightSelectedSquareColor)
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))

            # highlight possible moves squares
            s.fill(highlightPossibleMovesColor)
            s.set_alpha(60)
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightMoveSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    colors = [whiteColor, blackColor]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()