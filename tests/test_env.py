"""Tests for the Gymnasium environment."""

import pytest
import gymnasium as gym
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


@pytest.fixture
def observation(env):
    return env.observation_space.sample()


@pytest.mark.filterwarnings(f"ignore:{_GYMNASIUM_269}")
def test_observed_board(observation):
    """Observations include a 9x9 board."""
    assert "board" in observation
    assert observation["board"].shape == (9, 9)


@pytest.mark.filterwarnings(f"ignore:{_GYMNASIUM_269}")
def test_observed_choices(observation):
    """Observations include three 5x5 choices."""
    assert "choices" in observation
    assert observation["choices"].shape == (3, 5, 5)
