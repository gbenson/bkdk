import numpy as np
import pytest
import gymnasium as gym
from gymnasium.envs.registration import register as _gym_env_register
from bkdk.tinyscreen import TinyScreen


# Gymnasium's passive environment checker issues warnings about our
# observation spaces having unconventional shapes, which clutters
# pytest's output unnecessarily.  There's a Gymnasium issue, #269:
# https://github.com/Farama-Foundation/Gymnasium/issues/269
_GYMNASIUM_269 = r".*Box observation space.*"


# We create test environments via gym.make("bkdk/test_tinyscreen")
# so we're testing it wrapped in Gymnasium's checking wrappers
# (which spit out all kinds of warnings and errors if you don't
# do things right!)
_gym_env_register(
    id="bkdk/tinyscreen_test",
    entry_point=lambda: TinyScreen(gym.make("bkdk/BKDK-v0")),
)


@pytest.fixture
def env():
    env = gym.make("bkdk/tinyscreen_test")
    yield env
    env.close()


@pytest.fixture
def initial_observation(env):
    return env.reset(seed=23)[0]


@pytest.mark.filterwarnings(f"ignore:{_GYMNASIUM_269}")
def test_screen_parameters(initial_observation):
    """The initial screen is a 19x19 array of unsigned bytes."""
    screen = initial_observation
    assert isinstance(screen, np.ndarray)
    assert screen.shape == (19, 19)
    assert screen.dtype == np.uint8


def _transform(obs):
    """Return an ASCII art representation of our tiny screen."""
    return "|{}|".format(
        "|\n|".join("".join(" #"[pix] for pix in row)
                    for row in obs))


@pytest.mark.filterwarnings(f"ignore:{_GYMNASIUM_269}")
def test_initial_image(initial_observation):
    """The initial image is as expected."""
    assert _transform(initial_observation) == """\
|                   |
|                   |
|                   |
| ##            ##  |
| # #           # # |
| # #           # # |
| # #           # # |
| ##            # # |
| # #           # # |
| # #           # # |
| # #           # # |
| ##            ##  |
|                   |
|                   |
|         ##   ##   |
|  ##    ##     #   |
|               #   |
|                   |
|                   |"""


@pytest.mark.parametrize(
    "actions, expect_observation",
    (((0,), """\
|                   |
|        #          |
|                   |
| ##  ##        ##  |
| # #           # # |
| # #           # # |
| # #           # # |
| ##            # # |
| # #           # # |
| # #           # # |
| # #           # # |
| ##            ##  |
|                   |
|                   |
|         ##   ##   |
|        ##     #   |
|               #   |
|                   |
|                   |""",
      ),
     ((0, (1, 0, 1)), """\
|                   |
|        # #        |
|                   |
| ##  ####      ##  |
| # #  ##       # # |
| # #           # # |
| # #           # # |
| ##            # # |
| # #           # # |
| # #           # # |
| # #           # # |
| ##            ##  |
|                   |
|                   |
|              ##   |
|               #   |
|               #   |
|                   |
|                   |""",
      ),
     ((0, (1, 0, 1), (2, 0, 7)), """\
|                   |
|       ##          |
|                   |
| ##  ####   ## ##  |
| # #  ##     # # # |
| # #         # # # |
| # #           # # |
| ##            # # |
| # #           # # |
| # #           # # |
| # #           # # |
| ##            ##  |
|                   |
|               #   |
|  ##     #     #   |
|   #    ##     #   |
|  ##           #   |
|                   |
|                   |""",
      ),
     ((0, (1, 0, 1), (2, 0, 7), (1, 0, 3)), """\
|                   |
|       # ##        |
|                   |
| ##  #####  ## ##  |
| # #  ####   # # # |
| # #         # # # |
| # #           # # |
| ##            # # |
| # #           # # |
| # #           # # |
| # #           # # |
| ##            ##  |
|                   |
|               #   |
|  ##           #   |
|   #           #   |
|  ##           #   |
|                   |
|                   |""",
      ),
     ((0, (1, 0, 1), (2, 0, 7), (1, 0, 3), (0, 0, 5)), """\
|                   |
|      # #          |
|                   |
| ##            ##  |
| # #  #### # # # # |
| # #      ## # # # |
| # #           # # |
| ##            # # |
| # #           # # |
| # #           # # |
| # #           # # |
| ##            ##  |
|                   |
|               #   |
|               #   |
|               #   |
|               #   |
|                   |
|                   |""",
      )
     ))
@pytest.mark.filterwarnings(f"ignore:{_GYMNASIUM_269}")
def test_step(env, actions, expect_observation):
    """env.step() does what it should."""
    observation, info = env.reset(seed=23)
    for action in actions:
        observation = env.step(action)[0]
    actual_observation = _transform(observation)
    print(actual_observation)
    assert actual_observation == expect_observation
