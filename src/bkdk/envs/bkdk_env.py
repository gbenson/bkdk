import gymnasium as gym
import numpy as np

from gymnasium import spaces


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
