import pytest
import random
from bkdk import Shape, ALL_SHAPES, random_shape


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
    """There are 42 shapes in total"""
    assert len(ALL_SHAPES) == 42


def test_random_shape():
    """random_shape produces random shapes"""
    random.seed(23)
    assert random_shape().code == "xx_x-_x-"
    assert random_shape().code == "xxxx"
    assert random_shape().code == "xx"
    assert random_shape().code == "xxx_--x_--x"
