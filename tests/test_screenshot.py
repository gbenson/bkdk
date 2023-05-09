import os
import pytest
from PIL import Image
from bkdk.screenshot import Screenshot


def load_test_screenshot(basename):
    testdir = os.path.dirname(__file__)
    resourcedir = os.path.join(testdir, "resources")
    ssdir = os.path.join(resourcedir, "screenshots")
    return Screenshot(os.path.join(ssdir, basename))


@pytest.fixture
def test_screenshot():
    return load_test_screenshot("20230430-103701.jpg")


def test_screenshots_subclass_PIL_Image(test_screenshot):
    """Screenshots subclass PIL.Image."""
    assert isinstance(test_screenshot, Image.Image)
    assert test_screenshot.size == (720, 1520)


def test_screenshot_board_cells(test_screenshot):
    """Screenshots have 81 board cells"""
    cells = list(test_screenshot.board.cells)
    assert len(cells) == 81


@pytest.mark.parametrize(
    "index,expect_set",
    ((0, False),
     (1, True),
     ))
def test_screenshot_board_cell_setness(test_screenshot, index, expect_set):
    """Board cells can be set or not"""
    cells = list(test_screenshot.board.cells)
    assert cells[index].is_set == expect_set
