"""Tests for the Gymnasium environment."""

import pytest
import gymnasium as gym
import bkdk  # noqa: F401

# Gymnasium's passive environment checker issues warnings about our
# observation spaces having unconventional shapes, which clutters
# pytest's output unnecessarily.  There's a Gymnasium issue, #269:
# https://github.com/Farama-Foundation/Gymnasium/issues/269
_GYMNASIUM_269 = r".*Box observation space has an unconventional shape"


@pytest.fixture
def env():
    env = gym.make("bkdk/BKDK-v0")
    yield env
    env.close()


@pytest.mark.filterwarnings(f"ignore:{_GYMNASIUM_269}")
def test_observed_board_is_9x9(env):
    """Environments have a 9x9 board in their observation space."""
    observation = env.observation_space.sample()
    assert "board" in observation
    assert observation["board"].shape == (9, 9)
