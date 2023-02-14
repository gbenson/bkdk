import pytest
from bkdk.board import Board

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
        assert len(group) is 9

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
