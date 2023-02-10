import pygame

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
        unfilled_colors = (
            pygame.Color("white"),
            pygame.Color("#e4e9ef"),
        )
        count = 0
        self.grid = [
            [SubBoardRenderer(cellsize,
                              (x0 + j * cellsize * 3,
                               y0 + i * cellsize * 3),
                              unfilled_colors[(count := count + 1)
                                              % len(unfilled_colors)])
             for j in range(3)]
            for i in range(3)]
        self.rect = self.grid[0][0].rect.union(
            self.grid[2][2].rect)
        self.rect.inflate_ip(4, 4)

    @property
    def dark_color(self):
        return self.grid[0][0].dark_color

    def render(self, surf):
        pygame.draw.rect(surf, self.dark_color, self.rect, 2)
        for row in self.grid:
            for sbr in row:
                sbr.render(surf)

class SubBoardRenderer:
    dark_color = pygame.Color("#585f72")
    light_color = pygame.Color("#cdd6e5")

    def __init__(self, cellsize, topleft, unfilled_color):
        x0, y0 = topleft
        self.grid = [
            [CellRenderer(cellsize,
                          (x0 + j * cellsize,
                           y0 + i * cellsize),
                          unfilled_color)
             for j in range(3)]
            for i in range(3)]
        self.inner_rect = self.grid[0][0].rect.union(
            self.grid[2][2].rect)
        self.outer_rect = self.inner_rect.inflate(2, 2)

    @property
    def rect(self):
        return self.outer_rect

    def render(self, surf):
        pygame.draw.rect(surf, self.light_color, self.inner_rect)
        for row in self.grid:
            for cell in row:
                cell.render(surf)
        pygame.draw.rect(surf, self.dark_color, self.outer_rect, 2)

class CellRenderer:
    def __init__(self, cellsize, topleft, unfilled_color):
        self.rect = pygame.Rect(topleft, (cellsize, cellsize))
        self.rect.inflate_ip(-2, -2)
        self.unfilled_color = unfilled_color

    def render(self, surf):
        pygame.draw.rect(surf, self.unfilled_color, self.rect)

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
