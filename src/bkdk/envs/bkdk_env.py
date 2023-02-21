import gymnasium as gym
import numpy as np

from gymnasium import spaces

from ..board import Board


class BkdkEnv(gym.Env):
    def __init__(self, render_mode=None):
        # XXX fetch these from somewhere... bkdk.Board?
        self.board_size = 9
        self.shape_size = 5
        num_choices = 3

        self.observation_space = spaces.Dict({
            "board": spaces.Box(
                low=0, high=1, dtype=np.uint8,
                shape=(self.board_size, self.board_size)),
            "choices": spaces.Box(
                low=0, high=1, dtype=np.uint8,
                shape=(num_choices, self.shape_size, self.shape_size)),
            })

        # An integer, encoded as per self.step.__doc__
        self.action_space = spaces.Discrete(self.board_size**2 * num_choices)

    @property
    def _observation(self):
        return {
            "board": np.asarray([[int(cell.is_set) for cell in row]
                                 for row in self._board.rows],
                                dtype=np.uint8),
            "choices": np.asarray([
                shape is None
                and tuple(tuple(0 for _ in range(self.shape_size))
                          for _ in range(self.shape_size))
                or shape._rows
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

    def step(self, action):
        """Run one move of the game.

        :param action: may be a tuple of (choice, row, column),
        or the same encoded as as an integer via:
        `column + row*BOARD_SIZE + choice_index*BOARD_SIZE**2`.
        """
        if isinstance(action, type(0)):
            choice_row, column = divmod(action, self.board_size)
            choice, row = divmod(choice_row, self.board_size)
        else:
            choice, row, column = action

        reward = self._board.one_move(choice, (row, column))
        terminated = not any(self._board.can_place(shape)
                             for shape in self._board.choices
                             if shape is not None)

        return self._observation, reward, terminated, False, self._info
