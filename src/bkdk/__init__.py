from gymnasium.envs.registration import register as _gym_env_register

from .board import Board

__version__ = "0.0.2.dev"

_gym_env_register(
    id="bkdk/BKDK-v0",
    entry_point="bkdk.envs:BkdkEnv",
)
