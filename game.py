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

    def _init_choices(self):
        xcen = int(self.surfsize[0] // 2)
        xcen_pm = int(self.surfsize[0] * 5 // 16)
        ycen = (self.board.rect.bottom
                + int(self.surfsize[0] * 5 // 19))
        cellsize = int(self.surfsize[0] // 18)

        print("3 choices, x-centred at:")
        print(f" x = {(xcen - xcen_pm, xcen, xcen + xcen_pm)}")
        print(f" y = {ycen}")
        print(f"with cellsize = {cellsize}")

        raise SystemExit

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

    @property
    def cells(self):
        for row in self.grid:
            for subrow in range(3):
                for sbr in row:
                    for cell in sbr.grid[subrow]:
                        yield cell

    def render(self, surf):
        pygame.draw.rect(surf, self.dark_color, self.rect, 2)
        for row in self.grid:
            for sbr in row:
                sbr.render(surf)
        for index, cell in enumerate(self.cells):
            if index & 1:
                cell.render(surf, True)

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
    border_color = pygame.Color("#01152e")
    lo_fill_color = pygame.Color("#3164d1")
    hi_fill_color = pygame.Color("#5391de")

    def __init__(self, cellsize, topleft, unfilled_color):
        rect = pygame.Rect(topleft, (cellsize, cellsize))
        self.unfilled_rect = rect.inflate(-2, -2)
        self.unfilled_color = unfilled_color
        self.border_rect = rect.inflate(2, 2)
        self.hi_fill_rect = self.border_rect.inflate(-4, -4)
        self.lo_fill_rect = self.hi_fill_rect.inflate(-4, -4)

    @property
    def rect(self):
        return self.unfilled_rect

    def render(self, surf, filled=False):
        if filled:
            pygame.draw.rect(surf, self.border_color, self.border_rect)
            pygame.draw.rect(surf, self.hi_fill_color, self.hi_fill_rect)
            pygame.draw.rect(surf, self.lo_fill_color, self.lo_fill_rect)
        else:
            pygame.draw.rect(surf, self.unfilled_color, self.unfilled_rect)

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
