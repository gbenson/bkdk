import gymnasium as gym
import numpy as np

from gymnasium import spaces

from ..board import Board


class BkdkEnv(gym.Env):
    def __init__(self, render_mode=None):
        # XXX fetch these from somewhere... bkdk.Board?
        board_size = 9
        shape_size = 5
        num_choices = 3

        self.observation_space = spaces.Dict({
            "board": spaces.Box(
                low=0, high=1, dtype=np.uint8,
                shape=(board_size, board_size)),
            "choices": spaces.Box(
                low=0, high=1, dtype=np.uint8,
                shape=(num_choices, shape_size, shape_size)),
            })

        """The action is encoded as an integer,
        `column + row*BOARD_SIZE + choice_index*BOARD_SIZE**2`.
        """
        self.action_space = spaces.Discrete(board_size**2 * num_choices)

    @property
    def _observation(self):
        return {
            "board": np.asarray([[int(cell.is_set) for cell in row]
                                 for row in self._board.rows],
                                dtype=np.uint8),
            "choices": np.asarray([shape._rows
                                   for shape in self._board.choices],
                                  dtype=np.uint8),
        }

    @property
    def _info(self):
        # XXX put valid moves in here? current score?? choice scores???
        return {}

    def reset(self, seed=None, options={}):
        """Start a new game. Returns the first observation and its
        associated auxilliary information."""
        super().reset(seed=seed)
        self._board = Board(random_number_generator=self.np_random)
        return self._observation, self._info
