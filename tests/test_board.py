import copy
import pytest
import random
from bkdk.board import Board
from bkdk.shapes import Shape, ALL_SHAPES


def test_boards_start_blank():
    """Boards are created blank."""
    assert Board().tolist() == [[0] * 9] * 9


@pytest.fixture
def shape_sequence():
    return (
        ((5, 4), Shape(code="xx_x-_xx"), """\
Board[.........
      .........
      .........
      .........
      .........
      ....##...
      ....#....
      ....##...
      .........]""",
         ),
        ((4, 0), Shape(code="xx_xx"), """\
Board[.........
      .........
      .........
      .........
      ##.......
      ##..##...
      ....#....
      ....##...
      .........]""",
         ),
        ((4, 2), Shape(code="-xx_xx-"), """\
Board[.........
      .........
      .........
      .........
      ##.##....
      ######...
      ....#....
      ....##...
      .........]""",
         ),
        ((3, 6), Shape(code="-x-_-x-_xxx"), """\
Board[.........
      .........
      .........
      .......#.
      ##.##..#.
      #########
      ....#....
      ....##...
      .........]""",
         ),
        )


# Match what Board.__str__ did when the above fixture was written.
def _old_str_board(board, prefix="Board["):
    sep = f"\n{' ' * len(prefix)}"
    cells = sep.join(
        "".join(".#"[cell] for cell in row)
        for row in board.tolist())
    return f"{prefix}{cells}]"


@pytest.mark.parametrize("sequence_length", (1, 2, 3, 4))
def test_shape_placement(shape_sequence, sequence_length):
    """Shapes can be placed onto the board."""
    board = Board()
    for rowcol, shape, expect_board in shape_sequence[:sequence_length]:
        board.place_at(rowcol, shape)
        assert _old_str_board(board) == expect_board


def test_allowed_shape_placement():
    """Shapes that don't intersect may be placed on the board."""
    board = Board()
    shape1 = Shape(code="x-x_-x-_x-x")
    shape2 = Shape(code="-x-_x-x_-x-")
    rowcol = (5, 5)
    assert board.can_place_at(rowcol, shape1)
    board.place_at(rowcol, shape1)
    assert board.can_place_at(rowcol, shape2)


def test_rejected_shape_placement():
    """Shapes that intersect may not be placed on the board."""
    board = Board()
    shape1 = Shape(code="x-x_-x-_x-x")
    shape2 = Shape(code="-x-_x-x_-x-")
    rowcol = (5, 5)
    assert board.can_place_at(rowcol, shape1)
    board.place_at(rowcol, shape1)
    rowcol2 = tuple(a-b for b, a in enumerate(rowcol))
    assert not board.can_place_at(rowcol2, shape2)


@pytest.mark.parametrize(
    "rowcol, shape, is_allowed",
    (((0, 0), "x", True),
     ((0, 8), "x", True),
     ((0, 8), "x_x", True),
     ((0, 8), "xx", False),
     ((0, 9), "x", False),
     ((0, 3), "x", True),
     ((8, 3), "x", True),
     ((8, 3), "xx", True),
     ((8, 3), "x_x", False),
     ((9, 3), "x", False),
     ))
def test_shape_placement_clamping(rowcol, shape, is_allowed):
    """Check shapes may not be placed outside the board."""
    assert Board().can_place_at(rowcol, Shape(code=shape)) == is_allowed


def test_any_placement_allowed():
    """Check a shape may be placed somewhere."""
    assert Board().can_place(Shape(code="x_x_x_x_x"))


def test_all_placement_denied():
    """Check shape that may not be placed somewhere."""
    board = Board()
    board.place_at((4, 0), Shape(code="xxxx"))
    board.place_at((4, 4), Shape(code="xxxxx"))
    assert not board.can_place(Shape(code="x_x_x_x_x"))


def test_initial_choices():
    """Boards start with three initial choices of shape."""
    random.seed(23)
    board = Board()
    assert len(board.choices) == 3
    assert board.choices[0].code == "xx_x-_x-"
    assert board.choices[1].code == "xxxx"
    assert board.choices[2].code == "xx"


def test_one_move_placement_allowed():
    """one_move allows valid placements."""
    random.seed(23)
    board = Board()
    assert board.score == 0
    assert board.one_move(1, (2, 2)) == 4
    assert board.score == 4
    assert board.tolist() == [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]]


def test_one_move_choice_used_up():
    """one_move checks for used-up choices."""
    random.seed(23)
    board = Board()
    assert board.choices[1] is not None
    board.one_move(1, (3, 2))
    assert board.choices[1] is None
    assert board.score == 4
    assert board.one_move(1, (2, 2)) == 0
    assert board.score == 4
    assert board.tolist() == [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]]


def test_one_move_placement_denied():
    """one_move disallows illegal placements."""
    random.seed(23)
    board = Board()
    board.place_at((1, 4), Shape(code="x_x_x_x"))
    assert board.score == 0
    assert board.one_move(1, (2, 2)) == 0
    assert board.score == 0
    assert board.tolist() == [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]]


@pytest.mark.parametrize(
    "rowcol, shape",
    (((3, 0), "x" * 9),
     ((0, 5), "_".join("x" * 9)),
     ((6, 3), "_".join(["xxx"] * 3)),
     ))
def test_single_resolution(rowcol, shape):
    """Completed rows, columns and boxes resolve as expected."""
    board = Board()
    board.place_at(rowcol, Shape(code=shape))
    assert board.resolve() == 1
    assert board.tolist() == [[0] * 9] * 9


@pytest.mark.parametrize(
    "rowcol, shape",
    (((3, 0), f"-{'x' * 8}_x{'-' * 8}"),
     ((3, 0), f"{'-' * 8}x_{'x' * 8}-"),

     ((0, 5), "_".join(["-x"] + ["x-"] * 7 + ["x-"])),
     ((0, 5), "_".join(["-x"] + ["-x"] * 7 + ["x-"])),

     ((2, 3), "_".join(["xxx"] * 3)),
     ((4, 3), "_".join(["xxx"] * 3)),
     ((3, 2), "_".join(["xxx"] * 3)),
     ((3, 4), "_".join(["xxx"] * 3)),
     ))
def test_offset_nonresolution(rowcol, shape):
    """Offset/shifted rows, columns and boxes do not resolve."""
    board = Board()
    board.place_at(rowcol, Shape(code=shape))
    print(board)
    saved_rows = copy.copy(board.rows)
    assert board.resolve() == 0
    assert board.rows == saved_rows


@pytest.fixture
def real_game_1():
    board = Board()
    board.choices = [shape
                     for shape in ALL_SHAPES
                     if shape.code in ("x--_x--_xxx",
                                       "xxx",
                                       "-x_-x_xx")]
    return board


def test_score_no_completion_1(real_game_1):
    """A placed shape that doesn't complete groups scores the number
    of cells it covers (test 1 of 2)."""
    board = real_game_1
    assert board.score == 0
    assert board.one_move(2, (6, 0)) == 5
    assert board.score == 5
    assert board.tolist() == [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0, 0, 0]]


def test_score_no_completion_2(real_game_1):
    """A placed shape that doesn't complete groups scores the number
    of cells it covers (test 2 of 2)."""
    board = real_game_1
    board.one_move(2, (6, 0))
    assert board.score == 5
    assert board.one_move(0, (7, 1)) == 3
    assert board.score == 8
    assert board.tolist() == [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0, 0, 0]]


def test_score_with_completion(real_game_1):
    """A placed shape that completes a group scores the completion
    score and cells that don't get cleared only."""
    board = real_game_1
    board.one_move(2, (6, 0))
    board.one_move(0, (7, 1))
    assert board.score == 8
    assert board.one_move(1, (4, 1)) == 20
    assert board.score == 28
    assert board.tolist() == [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]]


def test_initial_valid_moves():
    """Most moves are valid on a blank board."""
    random.seed(23)
    valid_moves = list(Board().valid_moves)
    assert len(valid_moves) == 182
    assert (0, (5, 4)) in valid_moves
    assert (1, (5, 4)) in valid_moves
    assert (2, (5, 4)) in valid_moves


def test_valid_moves_one_shape_down():
    """Removing a choice removes its valid moves."""
    random.seed(23)
    board = Board()
    board.choices[1] = None
    valid_moves = list(board.valid_moves)
    assert len(valid_moves) == 128
    assert (0, (5, 4)) in valid_moves
    assert (1, (5, 4)) not in valid_moves
    assert (2, (5, 4)) in valid_moves


def test_valid_moves_one_shape_placecd():
    """Placing a shape reduces other shapes' valid moves."""
    random.seed(23)
    board = Board()
    board.one_move(1, (6, 4))
    valid_moves = list(board.valid_moves)
    assert len(valid_moves) == 110
    assert (0, (5, 4)) not in valid_moves
    assert (1, (5, 4)) not in valid_moves
    assert (2, (5, 4)) in valid_moves
