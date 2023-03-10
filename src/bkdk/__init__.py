import warnings

from gymnasium.envs.registration import register as _gym_env_register

from .ts.core import TinyScreen

__version__ = "0.0.5.dev"

_gym_env_register(
    id="bkdk/BKDK-v0",
    entry_point="bkdk.env:Env",
)

# Gymnasium's passive environment checker issues warnings about our
# observation spaces having unconventional shapes and bounds, twice
# for every genome we evaluate.  There's a Gymnasium issue, #269:
# https://github.com/Farama-Foundation/Gymnasium/issues/269
warnings.filterwarnings("ignore", message=r".*Box observation space.*")
