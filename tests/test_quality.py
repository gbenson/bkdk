import pytest
import random
from bkdk.board import Board
from bkdk.shapes import ALL_SHAPES


@pytest.fixture
def very_full_board():
    random.seed(23)
    board = Board(value=(
        (1, 1, 0,  1, 1, 1,  1, 1, 1),
        (1, 1, 1,  0, 1, 1,  1, 1, 1),
        (1, 1, 1,  1, 1, 1,  1, 1, 0),

        (1, 0, 1,  1, 1, 1,  1, 1, 1),
        (1, 1, 1,  1, 0, 1,  1, 0, 1),
        (1, 1, 1,  1, 1, 1,  1, 0, 1),

        (0, 1, 1,  1, 1, 1,  1, 1, 0),
        (1, 1, 1,  1, 1, 1,  0, 1, 1),
        (1, 1, 1,  1, 1, 0,  1, 1, 1),
    ))
    board.choices = [shape
                     for shape in ALL_SHAPES
                     if shape.code == "x-_-x"]
    return board


def test_vfb_is_stable(very_full_board):
    """Very full test board is stable."""
    board = very_full_board
    assert board.resolve() == 0


VFB_GOOD_MOVE = (0, (0, 2))
VFB_POOR_MOVE = (0, (5, 7))


def test_vfb_has_expected_valid_moves(very_full_board):
    """Very full test board has two valid moves."""
    board = very_full_board
    assert tuple(board.valid_moves) == (VFB_GOOD_MOVE, VFB_POOR_MOVE)


@pytest.mark.parametrize(
    "move, expect_score",
    ((VFB_GOOD_MOVE, 108),
     (VFB_POOR_MOVE, 19),
     ))
def test_vfb_move_scores(very_full_board, move, expect_score):
    """Very full test board moves score as expected."""
    board = very_full_board
    board.one_move(*move)
    assert board.score == expect_score


@pytest.mark.skip
def test_pre_move_quality(very_full_board):
    """Quality before any moves is XXX"""
    board = very_full_board
    print(board)
    assert board.rate_potential() == 0


@pytest.mark.skip
def test_post_good_move_quality(very_full_board):
    """Quality after good move is XXX"""
    board = very_full_board
    print(board.choices)
    board.one_move(*VFB_GOOD_MOVE)
    print(board)
    print(board.choices)
    board.choices = []
    assert board.rate_potential() == 0


def test_post_poor_move_quality(very_full_board):
    """Quality after poor move is XXX"""
    board = very_full_board
    board.one_move(*VFB_POOR_MOVE)
    print(board)
    board.choices = []
    assert board.rate_potential() == 0
