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


@pytest.fixture
def test_screenshot2():
    return load_test_screenshot("20230430-105149.jpg")


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


def test_screenshot_board_tolist(test_screenshot):
    """Board cells can be set or not"""
    assert test_screenshot.board.tolist() == [
        [0, 1, 0,  0, 0, 1,  1, 1, 0],
        [1, 1, 0,  1, 1, 1,  0, 0, 1],
        [0, 1, 0,  1, 1, 1,  1, 1, 1],

        [0, 0, 0,  0, 0, 0,  0, 0, 0],
        [0, 1, 0,  0, 0, 0,  1, 0, 0],
        [0, 1, 0,  1, 0, 0,  0, 1, 1],

        [0, 1, 0,  1, 1, 1,  0, 0, 0],
        [1, 0, 0,  1, 1, 1,  0, 0, 0],
        [1, 0, 0,  0, 0, 0,  0, 0, 0],
    ]


def test_screenshot_choices(test_screenshot):
    """Screenshots have 3 choices"""
    assert len(test_screenshot.choices) == 3


def test_screenshot_centred_choice_cells(test_screenshot):
    """Choices with centred cells may be decoded."""
    choice = test_screenshot.choices[0]
    assert choice._shape == (5, 5)
    assert choice.tolist() == [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0],
    ]


def test_screenshot_hoffset_choice_cells(test_screenshot):
    """Choices with horizontally offset cells may be decoded."""
    choice = test_screenshot.choices[2]
    assert choice._shape == (5, 4)
    assert choice.tolist() == [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]


def test_screenshot_voffset_choice_cells(test_screenshot2):
    """Choices with vertically offset cells may be decoded."""
    choice = test_screenshot2.choices[0]
    assert choice._shape == (4, 5)
    assert choice.tolist() == [
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]


def test_screenshot_fullskew_choice_cells(test_screenshot2):
    """Choices with fully offset cells may be decoded."""
    choice = test_screenshot2.choices[1]
    assert choice._shape == (4, 4)
    assert choice.tolist() == [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
