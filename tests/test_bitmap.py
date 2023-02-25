import copy
import pytest
from bkdk.bitmap import Bitmap


def test_bitmaps_start_empty():
    """Bitmaps start empty."""
    assert str(Bitmap((3, 4))) == """\
[[0, 0, 0, 0],
 [0, 0, 0, 0],
 [0, 0, 0, 0]]"""


def test_can_initialize_nonempty():
    """Bitmaps can be initialized with a value"""
    assert str(Bitmap((6, 4), [[0, 1, 1, 0],
                               [1, 0, 0, 1],
                               [1, 0, 0, 0],
                               [1, 0, 1, 1],
                               [1, 0, 0, 1],
                               [0, 1, 1, 0]])) == """\
[[0, 1, 1, 0],
 [1, 0, 0, 1],
 [1, 0, 0, 0],
 [1, 0, 1, 1],
 [1, 0, 0, 1],
 [0, 1, 1, 0]]"""


def test_can_initialize_unsized():
    """Bitmaps can be initialized unsized with a value."""
    b = Bitmap(value=[[0, 1, 1], [1, 1, 0]])
    assert b.num_rows == 2
    assert b.num_columns == 3
    assert b.size == (2, 3)
    assert str(b) == """\
[[0, 1, 1],
 [1, 1, 0]]"""


@pytest.mark.parametrize(
    "size",
    ([2, 3],
     [3, 2]))
def test_cant_initialize_inconsistent(size):
    """Bitmaps can't be initialized with inconsistent size+value."""
    with pytest.raises(ValueError):
        Bitmap(size=size, value=[[1, 2], [3, 4]])


@pytest.mark.parametrize(
    "value",
    ([[1, 2],
      [1, 2, 3],
      [1, 2, 3]],
     [[1, 2, 3],
      [1, 2],
      [1, 2, 3]],
     [[1, 2, 3],
      [1, 2, 3],
      [1, 2]]))
def test_cant_initialize_ragged(value):
    """Bitmaps can't be initialized with ragged values."""
    with pytest.raises(ValueError):
        Bitmap(value=value)


@pytest.mark.parametrize(
    "rowcol",
    sum([[(row, col)
          for col in range(-1, 2)]
         for row in range(-1, 2)],
        start=[]))
def test_can_place_on_blank_works(rowcol):
    """can_place rejects out-of-shape placement."""
    b = Bitmap((4, 4))
    should_allow = (rowcol == (0, 0))
    print(f"rowcol = {rowcol}, should_allow = {should_allow}")
    assert b.can_place_at(rowcol, b) == should_allow


def test_can_place_nonblank():
    """You can_place nonblank onto blank."""
    a = Bitmap((3, 3))
    b = Bitmap((3, 3))
    b.rows[1] = 2
    assert a.can_place_at((0, 0), a)
    assert a.can_place_at((0, 0), b)
    assert b.can_place_at((0, 0), a)
    assert not b.can_place_at((0, 0), b)


def test_can_interlace():
    """Placements can interlace."""
    x, y = (1, 0, 1), (0, 1, 0)
    a = Bitmap((3, 3), (x, y, x))
    b = Bitmap((3, 3), (y, x, y))
    print(f"A =\n{a},\nB =\n{b}")
    assert not a.can_place_at((0, 0), a)
    assert a.can_place_at((0, 0), b)
    assert b.can_place_at((0, 0), a)
    assert not b.can_place_at((0, 0), b)


@pytest.mark.parametrize(
    "rowcol",
    sum([[(row, col)
          for col in range(-1, 2)
          if row != 0 or col != 0]
         for row in range(-1, 2)],
        start=[]))
def test_place_at_checks_borders(rowcol):
    """place_at rejects out-of-border placement."""
    b = Bitmap((3, 3))
    print(f"rowcol = {rowcol!r}")
    with pytest.raises(ValueError):
        b.place_at(rowcol, b)


def test_can_place_succeeding():
    """Check can_place on a shape than can be placed."""
    a = Bitmap(value=[[1, 1, 1], [1, 0, 1], [0, 0, 1], [0, 1, 1]])
    b = Bitmap(value=[[1, 1], [1, 0]])
    print(f"A:\n{a}\nB:\n{b}")
    assert a.can_place(b)
    assert not b.can_place(a)


def test_can_place_failing():
    """Check can_place on a shape than can't be placed."""
    a = Bitmap(value=[[1, 1, 1], [1, 0, 1], [0, 0, 1], [0, 1, 1]])
    b = Bitmap(value=[[1, 1], [1, 1]])
    print(f"A:\n{a}\nB:\n{b}")
    assert not a.can_place(b)
    assert not b.can_place(a)


def test_place_at_nonblank_onto_blank():
    """place_at (nonblank onto blank) within borders"""
    a = Bitmap((3, 3), value=((1, 1, 1),
                              (0, 0, 1),
                              (0, 1, 1)))
    b = Bitmap((3, 3))

    assert b.rows != a.rows

    saved_a_rows_list = a.rows
    saved_a_rows_data = copy.copy(a.rows)
    saved_b_rows_list = b.rows
    saved_b_rows_data = copy.copy(b.rows)

    b.place_at((0, 0), a)

    assert a.rows is saved_a_rows_list
    assert a.rows == saved_a_rows_data
    assert b.rows is saved_b_rows_list
    assert b.rows != saved_b_rows_data
    assert b.rows == a.rows
    assert b.rows is not a.rows


def test_place_at_blank_onto_nonblank():
    """place_at (blank onto nonblank) within borders"""
    a = Bitmap((3, 3), value=((1, 1, 1),
                              (0, 0, 1),
                              (0, 1, 1)))
    b = Bitmap((3, 3))

    assert b.rows != a.rows

    saved_a_rows_list = a.rows
    saved_a_rows_data = copy.copy(a.rows)
    saved_b_rows_list = b.rows
    saved_b_rows_data = copy.copy(b.rows)

    a.place_at((0, 0), b)

    assert a.rows is saved_a_rows_list
    assert a.rows == saved_a_rows_data
    assert b.rows is saved_b_rows_list
    assert b.rows == saved_b_rows_data
