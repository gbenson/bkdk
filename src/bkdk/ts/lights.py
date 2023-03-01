import importlib
import numpy as np


pygame = None


class Blinkenlights:
    """Blinkenlights renderer for TinyScreen."""

    def __init__(self, render_mode, options={}):
        self.render_mode = render_mode
        self.render_fps = options.get("render_fps", 60)
        self._surface = None

    def _init_pygame(self, cellsize=40):
        global pygame
        pygame = importlib.import_module("pygame")
        pygame.init()

        dsize = [d * cellsize
                 for d in reversed(self._buf.shape)]

        if self.render_mode == "human":
            pygame.display.set_caption("BKDK")
            self._clock = pygame.time.Clock()
            self._surface = pygame.display.set_mode(dsize)

        elif self.render_mode == "rgb_array":
            self._surface = pygame.Surface(dsize)

    def close(self):
        if pygame is None:
            return
        if self._surface is None:
            return
        pygame.quit()

    def __call__(self):
        if self._surface is None:
            self._init_surface()

        self._render(self._buf, self._surface)

        if self.render_mode == "human":
            pygame.display.update()
            self._clock.tick(self.render_fps)
        elif mode == "rgb_array":
            pixels = np.array(pygame.surfarray.pixels3d(self._surface))
            return np.transpose(pixels, axes=(1, 0, 2))

    def _render(self, buf, window):
        num_rows, num_cols = buf.shape
        rowheight = window.height // rows
    
        for row in range(shape[0]):
            y = row * self.CELLSIZE
            for col in range(shape[1]):
                x = col * self.CELLSIZE
                is_set = self._screen[row][col]
                color = (0, is_set * 255, 0)
                rect = pygame.Rect((x, y,
                                    self.CELLSIZE,
                                    self.CELLSIZE))

                pygame.draw.rect(self._surface,
                                 color,
                                 rect,
                                 border_radius=self.CELLSIZE//5)
                pygame.draw.rect(self._surface,
                                 (0, 0, 112),
                                 rect,
                                 width=self.CELLSIZE//20,
                                 border_radius=self.CELLSIZE//5)


