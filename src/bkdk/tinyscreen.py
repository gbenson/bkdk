import gymnasium as gym
import numpy as np
import time

from gymnasium import spaces


class TinyScreen(gym.ObservationWrapper):
    """Replace the board and choices observation space with a
    representation of a tiny 1-bit screen.
    """

    @classmethod
    def _initialize(cls):
        A = (0, 1, 1, 0, 0)
        B = (0, 1, 0, 1, 0)

        rows = [A] + [B]*7 + [A]
        cls._big_D = np.array(rows, dtype=np.uint8)

        rows[4] = A
        cls._big_B = np.array(rows, dtype=np.uint8)

        cls._inter_shape_pad = np.zeros((5, 1), dtype=np.uint8)
        cls._inter_area_pad = np.zeros((1, 19), dtype=np.uint8)

        scorebits = np.arange(20, dtype=np.uint8)
        evens, odds = scorebits.reshape((10, 2)).T.tolist()
        odds.reverse()
        cls._scorebits = tuple(odds[1:] + evens)

    _initialized = False

    def __init__(self, env):
        if not self._initialized:
            self._initialize()
            self._initialized = True

        super().__init__(env)

        self.observation_space = spaces.Box(
            low=0, high=1, dtype=np.uint8, shape=(19, 19))

        # Rendering
        if self.render_mode in ("human", "rgb_array"):
            self._window = None
            self._clock = None

    def observation(self, obs):
        # Score area (19x1)
        score_area = np.array(
            [[(self.unwrapped._board.score & (1 << bit)) >> bit
              for bit in self._scorebits]],
            dtype=np.uint8)

        # Board area (19x9; shape=(19, 9))
        board_area = (self._big_B, obs["board"], self._big_D)
        board_area = np.concatenate(board_area, axis=1)

        # Choice area (19x5; shape = (5,19))
        choices_area = sum(((choice, self._inter_shape_pad)
                            for choice in obs["choices"]),
                           start=(self._inter_shape_pad,))
        choices_area = np.concatenate(choices_area, axis=1)

        # Everything
        screen = sum(((area, self._inter_area_pad)
                      for area in (score_area,
                                   board_area,
                                   choices_area)),
                     start=(self._inter_area_pad,))
        self._screen = np.concatenate(screen, axis=0)

        if self.render_mode == "human":
            self.render()

        return self._screen

    def render(self):
        if self.render_mode is None:
            return
        return self._render_pygame(self.render_mode)

    CELLSIZE = 40

    def _render_pygame(self, mode):
        import pygame

        shape = self._screen.shape
        if self._window is None:
            pygame.init()
            window_size = [d * self.CELLSIZE for d in reversed(shape)]
            if mode == "human":
                pygame.display.set_caption("BKDK")
                self._window = pygame.display.set_mode(window_size)
            elif mode == "rgb_array":
                self._window = pygame.Surface(window_size)

        if self._clock is None:
            self._clock = pygame.time.Clock()

        for row in range(shape[0]):
            y = row * self.CELLSIZE
            for col in range(shape[1]):
                x = col * self.CELLSIZE
                is_set = self._screen[row][col]
                color = (0, is_set * 255, 0)
                rect = pygame.Rect((x, y,
                                    self.CELLSIZE,
                                    self.CELLSIZE))

                pygame.draw.rect(self._window,
                                 color,
                                 rect,
                                 border_radius=self.CELLSIZE//5)
                pygame.draw.rect(self._window,
                                 (0, 0, 112),
                                 rect,
                                 width=self.CELLSIZE//20,
                                 border_radius=self.CELLSIZE//5)

        if mode == "human":
            pygame.display.update()
            self._clock.tick(self.metadata["render_fps"])
        elif mode == "rgb_array":
            pixels = np.array(pygame.surfarray.pixels3d(self._window))
            return np.transpose(pixels, axes=(1, 0, 2))

    def close(self):
        if getattr(self, "_window", None) is not None:
            import pygame
            pygame.quit()


def profile(run_length_seconds=5, render_mode=None):
    """Profile everything so far: Board, Shape, Env and TinyScreen."""
    env = gym.make("bkdk/BKDK-v0", render_mode=render_mode)
    env = TinyScreen(env)

    # Limit how often we read the clock
    frames_per_chunk = env.metadata["render_fps"] // 5
    if env.render_mode != "human":
        frames_per_chunk *= 10
    if env.render_mode is None:
        frames_per_chunk *= 10

    env.reset(seed=186283)
    needs_reset = False
    total_frames = 0
    start_time = time.perf_counter()
    limit_time = start_time + run_length_seconds

    while (end_time := time.perf_counter()) < limit_time:
        for _ in range(frames_per_chunk):
            if needs_reset:
                env.reset()
                needs_reset = False
            else:
                needs_reset = _profile_oneframe(env)
            total_frames += 1

    total_time = end_time - start_time
    framerate = total_frames / total_time
    print(f"{framerate:.0f} fps (render_mode = {env.render_mode})")

    env.close()


def _profile_oneframe(env):
    board = env.unwrapped._board
    for choice, shape in enumerate(board.choices):
        if shape is None:
            continue
        for row in range(9):
            for column in range(9):
                if not board._can_place_at((row, column), shape):
                    continue
                action = choice, row, column
                terminated, truncated = env.step(action)[2:4]
                return terminated or truncated


def main():
    env = gym.make("bkdk/BKDK-v0", render_mode="human")
    env = TinyScreen(env)

    observation, info = env.reset()
    import time
    while True:
        time.sleep(1)
