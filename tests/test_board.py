import copy
import pytest
import random
from bkdk import Board
from bkdk.shapes import Shape


def test_boards_have_81_cells():
    """Boards have 81 cells."""
    assert len(Board().cells) == 81


# Three different ways cells are grouped together.
CELL_GROUPINGS = ("rows", "columns", "boxes")


@pytest.mark.parametrize("grouping", CELL_GROUPINGS)
def test_boards_have_9(grouping):
    """Boards have 9 rows, columns and boxes."""
    assert len(getattr(Board(), grouping)) == 9


@pytest.mark.parametrize("grouping", CELL_GROUPINGS)
def test_grouping_has_9_cells(grouping):
    """Rows, columns and boxes each have 9 cells."""
    for group in getattr(Board(), grouping):
        assert len(group) == 9


@pytest.mark.parametrize(
    "grouping, a, b",
    (("rows", 2, 5),
     ("columns", 5, 2),
     ("boxes", 1, 8)
     ))
def test_grouping_echoes_cells(grouping, a, b):
    """Cells in Board.<groupings> are the same as in Board.cells"""
    board = Board()
    cell = board.cells[23]
    cellgroup = getattr(board, grouping)
    assert cellgroup[a][b] is cell
    assert cellgroup[a - 1][b] is not cell
    assert cellgroup[a][b - 1] is not cell


def test_boards_start_blank():
    """Boards are created blank."""
    for cell in Board().cells:
        assert not cell.is_set


def test_grouping_starts_incomplete():
    """Groupings are initially incomplete."""
    assert not Board().rows[7].is_complete


def test_part_set_grouping_not_completes():
    """Partially set groupings are not complete."""
    group = Board().rows[7]
    group[4].set()
    assert not group.is_complete


def test_grouping_completes():
    """Groupings complete when all cells are set."""
    group = Board().rows[7]
    for cell in group:
        cell.set()
    assert group.is_complete


def test_grouping_clear_clears_all_cells():
    """Grouping.clear clears all the cells in a group."""
    group = Board().rows[7]
    for cell in group:
        cell.set()
    group.clear()
    for cell in group:
        assert not cell.is_set


def test_cleared_grouping_becomes_incomplete():
    """Groupings become incomplete when cleared."""
    group = Board().rows[7]
    for cell in group:
        cell.set()
    group.clear()
    assert not group.is_complete


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


@pytest.mark.parametrize("sequence_length", (1, 2, 3, 4))
def test_shape_placement(shape_sequence, sequence_length):
    """Shapes can be placed onto the board."""
    board = Board()
    for rowcol, shape, expect_board in shape_sequence[:sequence_length]:
        board.place_at(rowcol, shape)
        assert str(board) == expect_board


def test_shapes_complete_groups(shape_sequence):
    """Placing shapes causes groupings to complete."""
    board = Board()
    testrow = board.rows[5]
    for rowcol, shape, expect_board in shape_sequence:
        assert not testrow.is_complete
        board.place_at(rowcol, shape)
    assert testrow.is_complete


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
    """Check a shape may be placed somewhere."""
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
    assert not any(cell.is_set for cell in board.cells)


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
    saved_cells = copy.copy(board.cells)
    assert board.resolve() == 0
    assert board.cells == saved_cells
