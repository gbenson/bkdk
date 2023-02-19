import gymnasium as gym
import numpy as np

from gymnasium import spaces


class BkdkEnv(gym.Env):
    def __init__(self, render_mode=None):
        self.observation_space = spaces.Dict({
            "board": spaces.Box(low=0, high=1, dtype=np.uint8, shape=(9, 9)),
            })

        self.action_space = gym.spaces.Discrete(2)
