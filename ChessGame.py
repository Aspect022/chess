import pygame as p
import ChessEngine
import ChessAI

WIDTH = HEIGHT = 512
DIMENSIONS = 8
SQ_SIZE = HEIGHT// DIMENSIONS
MAX_FPS = 15
IMAGES = {}


icon = p.image.load("chess/images/icon.ico")

p.display.set_icon(icon)
p.display.set_caption("Chess Game")

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK' ]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("D:/Coding/games/chess/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main(playerTwo):
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    playerOne = True # if a human is playing white, then this will be true

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 1 and (gs.board[row][col] == "--"):
                        sqSelected = ()
                        playerClicks = []
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(move)
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
        if not gameOver and not humanTurn:
            AIMove = ChessAI.findBestMove(gs, validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animatedMoves(gs.moveLog[-1], screen, gs.board,clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
        drawGameState(screen, gs, validMoves, sqSelected)
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver =True
            drawText(screen, 'Stalemate');
        clock.tick(MAX_FPS)
        p.display.flip()

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color("yellow"))
            for moves in validMoves:
                if moves.startRow == r and moves.startCol == c:
                    screen.blit(s, (SQ_SIZE*moves.endCol, SQ_SIZE*moves.endRow))

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animatedMoves(move, screen,board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r,c =((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, True, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, True, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2,2))

def drawHomeScreen(screen):
    font = p.font.SysFont("Helvitca", 50, True, False)
    textObject = font.render("Chess", True, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/4 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

    button_width = 200
    button_height = 50
    button_y = HEIGHT/2 - button_height/2

    # Play with Human button
    human_button = p.Rect(WIDTH/4 - button_width/2, button_y, button_width, button_height)
    p.draw.rect(screen, p.Color('light gray'), human_button)
    font = p.font.SysFont("Helvitca", 30, True, False)
    textObject = font.render("Play with Human", True, p.Color('black'))
    textLocation = human_button.move(button_width/2 - textObject.get_width()/2, button_height/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

    # Play with AI button
    ai_button = p.Rect(3*WIDTH/4 - button_width/2, button_y, button_width, button_height)
    p.draw.rect(screen, p.Color('light gray'), ai_button)
    textObject = font.render("Play with AI", True, p.Color('black'))
    textLocation = ai_button.move(button_width/2 - textObject.get_width()/2, button_height/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

    return human_button, ai_button


if __name__ == "__main__":
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()

    playerOne = True # if a human is playing white, then this will be true
    playerTwo = False # if a human is playing black, then this will be true

    homeScreen = True
    while homeScreen:
        human_button, ai_button = drawHomeScreen(screen)
        p.display.flip()
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                quit()
            if e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                if human_button.collidepoint(location):
                    playerTwo = True
                    homeScreen = False
                elif ai_button.collidepoint(location):
                    playerTwo = False
                    homeScreen = False

    main(playerTwo)