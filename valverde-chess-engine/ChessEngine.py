
class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = { "P": self.addPawnMoves, "R": self.addRockMoves, "B": self.addBishopMoves,
                               "N": self.addKnightMoves, "Q": self.addQueenMoves, "K": self.addKingMoves }
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [self.copyOfCastleRights(self.currentCastlingRights)]


    def makeMove(self, move, simulate = False):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        # Update king position
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0]+'Q'

        # enpassant move
        if move.isEnpassant:
            self.board[move.startRow][move.endCol] = '--' # capture pawn

        # update enpassant possible
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2: # only 2 square pawn advance
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.endCol)

        # castle move
        if move.isCastle:
            if move.endCol - move.startCol == 2: # king side castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] # move rook
                self.board[move.endRow][move.endCol+1] = '--'
            else: # queen side castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # move rook
                self.board[move.endRow][move.endCol - 2] = '--'

        # update castling rights, when rook or king moves
        self.updateCastleRights(move)
        self.castleRightsLog.append(self.copyOfCastleRights(self.currentCastlingRights))


    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR': # white rook
            if move.startRow == 7:
                if move.startCol == 0: # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR': # black rook
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.bks = False


    def undoMove(self):
        if len(self.moveLog) > 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isEnpassant:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)

            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:  # only 2 square pawn advance
                self.enpassantPossible = ()

            # undo castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRights = self.copyOfCastleRights(self.castleRightsLog[-1])

            # undo castle move
            if move.isCastle:
                if move.endCol - move.startCol == 2:  # king side castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]  # move rook
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # queen side castle
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]  # move rook
                    self.board[move.endRow][move.endCol + 1] = '--'

            self.checkMate = False
            self.staleMate = False

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        tmpEnpassantPossible = self.enpassantPossible
        tmpCastlingRights = self.copyOfCastleRights(self.currentCastlingRights)
        moves = self.getPossibleMoves()
        if self.whiteToMove:
            self.addCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.addCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i], simulate=True)
            self.whiteToMove = not self.whiteToMove
            if self.isInCheck():
                moves.remove(moves[i])

            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0: # check mate or stale mate
            if self.isInCheck(): # check mate
                self.checkMate = True
            else:
                self.staleMate = True

        self.enpassantPossible = tmpEnpassantPossible
        self.currentCastlingRights = tmpCastlingRights
        return moves


    def isInCheck(self):
        if self.whiteToMove:
            return self.isSquareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.isSquareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])


    def isSquareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True

        return False

    '''
    All moves without considering checks
    '''
    def getPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)

        return moves


    def addPawnMoves(self, r, c, moves):
        if self.whiteToMove: # moving white pawns
            if self.board[r-1][c] == '--': # 1 square pawn advance
                moves.append(Move((r, c),(r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == '--': # 2 square pawn advance
                    moves.append(Move((r, c),(r-2, c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b': # black piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible and self.board[r][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))

            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':  # black piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible and self.board[r][c+1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        else: # moving black pawns
            if self.board[r + 1][c] == '--':  # 1 square pawn advance
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == '--':  # 2 square pawn advance
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':  # white piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible and self.board[r][c-1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':  # white piece to capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible and self.board[r][c+1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))


    def addRockMoves(self, r, c, moves):
        self.addMovesVertical(r, c, moves, r-1, -1)  # move up
        self.addMovesVertical(r, c, moves, r+1, 1)  # move down
        self.addMovesHorizontal(r, c, moves, c-1, -1)  # move left
        self.addMovesHorizontal(r, c, moves, c+1, 1)  # move right


    def addMovesVertical(self, r, c, moves, startIndex, direction):
        if direction == 1:
            endIndex = 8
        else:
            endIndex = -1

        for ri in range(startIndex, endIndex, direction):
            doContinue = self.addMove(r, c, moves, ri, c)
            if not doContinue:
                break


    def addMovesHorizontal(self, r, c, moves, startIndex, direction):
        if direction == 1:
            endIndex = 8
        else:
            endIndex = -1

        for ci in range(startIndex, endIndex, direction):
            doContinue = self.addMove(r, c, moves, r, ci)
            if not doContinue:
                break


    def addBishopMoves(self, r, c, moves):
        self.addDiagonalMoves(r, c, moves, 1, 1)
        self.addDiagonalMoves(r, c, moves, 1, -1)
        self.addDiagonalMoves(r, c, moves, -1, -1)
        self.addDiagonalMoves(r, c, moves, -1, 1)


    def addDiagonalMoves(self, r, c, moves, vDir, hDir):
        if hDir == 1:
            hEndIndex = 8
        else:
            hEndIndex = -1

        if vDir == 1:
            vEndIndex = 8
        else:
            vEndIndex = -1

        ri = r + vDir
        ci = c + hDir

        while ri != vEndIndex and ci != hEndIndex:
            doContinue = self.addMove(r, c, moves, ri, ci)
            if not doContinue:
                break

            ri += vDir
            ci += hDir


    def addKnightMoves(self, r, c, moves):
        knightMoves = [(1, -2), (2, -1), (2, 1), (1, 2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
        for knightMove in knightMoves:
            self.addMove(r, c, moves, r + knightMove[0], c + knightMove[1])


    def addQueenMoves(self, r, c, moves):
        self.addBishopMoves(r, c, moves)
        self.addRockMoves(r, c, moves)


    def addKingMoves(self, r, c, moves):
        kingMoves = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        for kingMove in kingMoves:
            self.addMove(r, c, moves, r + kingMove[0], c + kingMove[1])


    def addCastleMoves(self, r, c, moves):
        if self.isSquareUnderAttack(r, c): # cannot castle in check
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.addKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.addQueenSideCastleMoves(r, c, moves)


    def addKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.isSquareUnderAttack(r, c+1) and not self.isSquareUnderAttack(r, c+2):
                moves.append(Move((r,c), (r, c+2), self.board, isCastle=True))


    def addQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.isSquareUnderAttack(r, c-1) and not self.isSquareUnderAttack(r, c-2):
                moves.append(Move((r,c), (r, c-2), self.board, isCastle=True))


    def addMove(self, r, c, moves, ri, ci):
        if ri < 0 or ri > 7 or ci < 0 or ci > 7: # move out of the board
            return True

        squareToMove = self.board[ri][ci]
        if squareToMove == '--':
            moves.append(Move((r, c), (ri, ci), self.board))
        elif self.whiteToMove:
            if squareToMove[0] == 'b':
                moves.append(Move((r, c), (ri, ci), self.board))
            return False
        elif not self.whiteToMove:
            if squareToMove[0] == 'w':
                moves.append(Move((r, c), (ri, ci), self.board))
            return False
        return True


    def copyOfCastleRights(self, castleRights):
        return CastleRights(castleRights.wks,castleRights.bks,castleRights.wqs,castleRights.bqs)


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

    def __str__(self):
        return f"wks: {self.wks}, wqs: {self.wqs}, bks: {self.bks}, bqs: {self.bqs}"


    def __repr__(self):
        return self.__str__()



class Move():
    ranksToRows = {
        "1": 7, "2": 6, "3": 5, "4": 4,
        "5": 3, "6": 2, "7": 1, "8": 0
    }
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {
        "a": 0, "b": 1, "c": 2, "d": 3,
        "e": 4, "f": 5, "g": 6, "h": 7
    }
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastle = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveHashcode = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)
        self.isEnpassant = isEnpassantMove

        if self.isEnpassant:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

        self.isCastle = isCastle


    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveHashcode == other.moveHashcode
        return False


    def __str__(self):
        return f"({self.startRow}, {self.startCol}) -> ({self.endRow}, {self.endCol})"


    def __repr__(self):
        return self.__str__()


    def getChessNotation(self):
        return self.pieceMoved + self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
