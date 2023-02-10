import pygame
import random

class Renderer:
    def __init__(self, surfsize):
        self.surfsize = surfsize
        self._init_board()

    def _init_board(self):
        cellsize = int(min(self.surfsize) * 2 // 19)
        boardsize = cellsize * 9
        self.board = MainBoardRenderer(
            cellsize=cellsize,
            topleft=(int((self.surfsize[0] - boardsize) // 2) + 1,
                     int((self.surfsize[1] - boardsize) // 2) - 53))

    def render(self, surf):
        assert surf.get_size() == self.surfsize
        self.board.render(surf)

class MainBoardRenderer:
    def __init__(self, cellsize, topleft):
        x0, y0 = topleft
        self.grid = [
            [SubBoardRenderer(cellsize,
                              (x0 + j * cellsize * 3,
                               y0 + i * cellsize * 3))
             for j in range(3)]
            for i in range(3)]

    def render(self, surf):
        for row in self.grid:
            for sbr in row:
                sbr.render(surf)

class SubBoardRenderer:
    def __init__(self, cellsize, topleft):
        x0, y0 = topleft
        self.grid = [
            [CellRenderer(cellsize,
                          (x0 + j * cellsize,
                           y0 + i * cellsize))
             for j in range(3)]
            for i in range(3)]

    def render(self, surf):
        for row in self.grid:
            for cell in row:
                cell.render(surf)

class CellRenderer:
    def __init__(self, cellsize, topleft):
        self.rect = pygame.Rect(topleft, (cellsize, cellsize))
        self.rect.inflate_ip(-2, -2)
        self.color = pygame.Color(
            random.randrange(256),
            random.randrange(256),
            random.randrange(256),
        )

    def render(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)

pygame.init()

reference = pygame.image.load("reference.png")

screen = pygame.display.set_mode(reference.get_size())
renderer = Renderer(screen.get_size())

reference.convert()  # Speed up Surface.blit
reference.set_alpha(64)  # 25% opaque

clock = pygame.time.Clock()

while True:
    # Process player inputs.
    for event in pygame.event.get():
        if (event.type == pygame.KEYUP
            and event.key in (pygame.K_ESCAPE,
                              pygame.K_q)):
            event = pygame.event.Event(pygame.QUIT)
        if event.type == pygame.QUIT:
            pygame.image.save(screen, "screenshot.png")
            pygame.quit()
            raise SystemExit

    # Do logical updates here.
    # ...

    # Render the graphics.
    screen.fill("purple")  # Fill the display with a solid color
    pygame.Surface.blit(screen, reference, (0, 0))
    renderer.render(screen)

    pygame.display.flip()  # Refresh on-screen display
    clock.tick(60)         # wait until next frame (at 60 FPS)
