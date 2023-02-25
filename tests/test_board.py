import copy
import pytest
import random
from bkdk.board import Board
from bkdk.shapes import Shape


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
