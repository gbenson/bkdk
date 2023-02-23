"""Tests for the Gymnasium environment."""

import numpy as np
import pytest
import gymnasium as gym
from gymnasium.spaces.utils import flatten_space
import bkdk  # noqa: F401

# Gymnasium's passive environment checker issues warnings about our
# observation spaces having unconventional shapes, which clutters
# pytest's output unnecessarily.  There's a Gymnasium issue, #269:
# https://github.com/Farama-Foundation/Gymnasium/issues/269
_GYMNASIUM_269 = r".*Box observation space.*"


@pytest.fixture
def env():
    env = gym.make("bkdk/BKDK-v0")
    yield env
    env.close()


@pytest.mark.filterwarnings(f"ignore:{_GYMNASIUM_269}")
class TestSpaces:
    """Testcases for the action and observation spaces."""

    @pytest.fixture(params=(
        ("observation", 9*9 + 3*5*5),
        ("action", 3*9*9),
    ))
    def spacename_expectsize(self, request):
        spacename_base, expect_size = request.param
        return spacename_base + "_space", expect_size

    @pytest.fixture
    def testspace(self, env, spacename_expectsize):
        spacename, _ = spacename_expectsize
        return getattr(env, spacename)

    @pytest.fixture
    def expect_size(self, env, spacename_expectsize):
        _, expect_size = spacename_expectsize
        return expect_size

    @pytest.fixture
    def flatspace(self, testspace):
        return flatten_space(testspace)

    def test_is_flattenable(self, testspace):
        """The space is flattenable."""
        assert testspace.is_np_flattenable

    def test_flattened_dtype(self, flatspace):
        """The flattened space has an integer dtype."""
        assert np.issubdtype(flatspace.dtype, np.integer)

    def test_flattened_lower_bound(self, flatspace, expect_size):
        """The flattened space has the correct lower bound."""
        assert np.array_equal(flatspace.low,
                              np.zeros(expect_size, dtype=np.uint8))

    def test_flattened_upper_bound(self, flatspace, expect_size):
        """The flattened space has the correct upper bound."""
        assert np.array_equal(flatspace.high,
                              np.ones(expect_size, dtype=np.uint8))

    def test_flattened_shape(self, flatspace, expect_size):
        """The flattened space has the correct shape."""
        assert flatspace.shape == (expect_size,)


@pytest.fixture
def initial_observation(env):
    return env.reset(seed=23)[0]


@pytest.fixture
def initial_board(initial_observation):
    return initial_observation["board"]


@pytest.fixture
def initial_choices(initial_observation):
    return initial_observation["choices"]


@pytest.mark.filterwarnings(f"ignore:{_GYMNASIUM_269}")
def test_observed_board(initial_board):
    """Observations include a 9x9 board."""
    assert isinstance(initial_board, np.ndarray)
    assert initial_board.shape == (9, 9)
    assert initial_board.dtype == np.uint8


@pytest.mark.filterwarnings(f"ignore:{_GYMNASIUM_269}")
def test_observed_choices(initial_choices):
    """Observations include three 5x5 choices."""
    assert isinstance(initial_choices, np.ndarray)
    assert initial_choices.shape == (3, 5, 5)
    assert initial_choices.dtype == np.uint8


@pytest.mark.filterwarnings(f"ignore:{_GYMNASIUM_269}")
def test_initial_board(initial_board):
    """env.reset() creates a new, empty board."""
    assert np.array_equal(initial_board,
                          np.zeros((9, 9), dtype=np.uint8))


@pytest.mark.filterwarnings(f"ignore:{_GYMNASIUM_269}")
def test_initial_choices(initial_choices):
    """env.reset(seed=23) creates the three choices we expect."""
    ZEROS = tuple(0 for _ in range(5))
    assert np.array_equal(
        initial_choices,
        np.array(
            (
                # shape 0: code="xx"
                (ZEROS, ZEROS,
                 (0, 1, 1, 0, 0),
                 ZEROS, ZEROS),

                # shape 1: code="-xx_xx-"
                (ZEROS,
                 (0, 0, 1, 1, 0),
                 (0, 1, 1, 0, 0),
                 ZEROS, ZEROS),

                # shape 2: code="xx_-x_-x"
                (ZEROS,
                 (0, 1, 1, 0, 0),
                 (0, 0, 1, 0, 0),
                 (0, 0, 1, 0, 0),
                 ZEROS),
            ),
            dtype=np.uint8))


@pytest.mark.parametrize(
    "action",
    ((2, 3, 4),  # shape 2, row 3, column 4
     193,        # ditto, but flattened into an int
     ))
@pytest.mark.filterwarnings(f"ignore:{_GYMNASIUM_269}")
def test_step(env, action):
    """env.step() does what it should."""
    observation, info = env.reset(seed=23)
    observation, reward, terminated, truncated, info = env.step(action)

    ZEROS = tuple(0 for _ in range(9))
    assert np.array_equal(
        observation["board"],
        np.array((ZEROS, ZEROS, ZEROS,
                  (0, 0, 0,  0, 1, 1,  0, 0, 0),
                  (0, 0, 0,  0, 0, 1,  0, 0, 0),
                  (0, 0, 0,  0, 0, 1,  0, 0, 0),
                  ZEROS, ZEROS, ZEROS), dtype=np.uint8))

    ZEROS = tuple(0 for _ in range(5))
    assert np.array_equal(
        observation["choices"],
        np.array(
            (
                # shape 0: code="xx"
                (ZEROS, ZEROS,
                 (0, 1, 1, 0, 0),
                 ZEROS, ZEROS),

                # shape 1: code="-xx_xx-"
                (ZEROS,
                 (0, 0, 1, 1, 0),
                 (0, 1, 1, 0, 0),
                 ZEROS, ZEROS),

                # shape 2: used up
                tuple(ZEROS for _ in range(5)),
            ),
            dtype=np.uint8))
