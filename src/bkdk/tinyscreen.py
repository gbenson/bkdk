import gymnasium as gym
import numpy as np

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
        screen = np.concatenate(screen, axis=0)

        return screen
