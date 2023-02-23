import numpy as np
import pytest
import random
from bkdk.shapes import Shape, ALL_SHAPES, random_shape


@pytest.mark.parametrize(
    "input_code, expected_code",
    (("x", "x"),
     ("xx", "x_x"),
     ("xx_xx", "xx_xx"),
     ("x-_-x", "-x_x-"),
     ("x-_xx", "xx_x-"),
     ("x-x_xxx", "xx_x-_xx"),
     ))
def test_rotation(input_code, expected_code):
    assert Shape(code=input_code).rot90cw().code == expected_code


def test_all_shapes():
    """There are 47 shapes in total"""
    assert len(ALL_SHAPES) == 47


def test_random_shape():
    """random_shape produces random shapes"""
    random.seed(23)
    assert random_shape().code == "xx_x-_x-"
    assert random_shape().code == "xxxx"
    assert random_shape().code == "xx"
    assert random_shape().code == "--x_-x-_x--"


def test_finalized_size():
    """Shapes finalize to 5*5 = 25 cells."""
    assert ALL_SHAPES[0]._np_padded.shape == (5, 5)


@pytest.mark.parametrize(
    "input_code, padded_code",
    (("x",
      "".join(("-----",
               "-----",
               "--x--",
               "-----",
               "-----"))),
     ("xx",
      "".join(("-----",
               "-----",
               "-xx--",
               "-----",
               "-----"))),
     ("xxx",
      "".join(("-----",
               "-----",
               "-xxx-",
               "-----",
               "-----"))),
     ("x_x",
      "".join(("-----",
               "--x--",
               "--x--",
               "-----",
               "-----"))),
     ("x_x_x",
      "".join(("-----",
               "--x--",
               "--x--",
               "--x--",
               "-----"))),
     ("xx_xx",
      "".join(("-----",
               "-xx--",
               "-xx--",
               "-----",
               "-----"))),
     ))
def test_finalized_padding(input_code, padded_code):
    """Shapes are centred or left/up of centre"""
    shape = Shape(code=input_code)
    shape._finalize((5, 5))
    padded_cells = np.concatenate(shape._np_padded)
    assert "".join(("-x")[v] for v in padded_cells) == padded_code


@pytest.mark.parametrize(
    "input_code, expected_set_cells",
    (("x",
      ((0, 0),)),
     ("xx",
      ((0, 0), (0, 1))),
     ("x_x",
      ((0, 0), (1, 0))),
     ("x-_-x",
      ((0, 0), (1, 1))),
     ("-x_x-",
      ((0, 1), (1, 0))),
     ("x-_xx",
      ((0, 0), (1, 0), (1, 1))),
     ("--x_--x_xxx",
      ((0, 2), (1, 2), (2, 0), (2, 1), (2, 2))),
     ))
def test_set_cells(input_code, expected_set_cells):
    """Shape.set_cells is an sorted tuple of the shape's set cells."""
    assert Shape(code=input_code).set_cells == expected_set_cells


@pytest.mark.parametrize(
    "input_code, expected_size",
    (("x", (1, 1)),
     ("xx", (1, 2)),
     ("x_x", (2, 1)),
     ("x-_-x", (2, 2)),
     ("-x_x-", (2, 2)),
     ("x-_xx", (2, 2)),
     ("-x-_xxx", (2, 3)),
     ("--x_--x_xxx", (3, 3)),
     ))
def test_size(input_code, expected_size):
    """Shape.size is the rows, columns of the shape."""
    assert Shape(code=input_code).size == expected_size
