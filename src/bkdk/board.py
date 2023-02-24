from dataclasses import dataclass
from .shapes import random_shape


@dataclass
class Cell:
    rowcol: tuple[int, int]
    is_set: bool = False

    def set(self):
        self.is_set = True

    def clear(self):
        self.is_set = False

    def __str__(self):
        return f"Cell({self.rowcol}, is_set={self.is_set})"


class Grouping(tuple):
    """One row, column, or box."""
    @property
    def is_complete(self):
        return all(cell.is_set for cell in self)

    def clear(self):
        for cell in self:
            cell.clear()

    def __str__(self):
        return "".join(".#"[cell.is_set] for cell in self)


class Board:
    def __init__(self, random_number_generator=None):
        self._rng = random_number_generator
        self.rows = tuple(Grouping(Cell((row_index, column_index))
                                   for column_index in range(9))
                          for row_index in range(9))
        self.columns = tuple(map(Grouping, zip(*self.rows)))
        self.cells = sum(self.rows, start=())
        self.boxes = self._init_boxes()
        self._new_choices()

    def _init_boxes(self):
        boxes = [[] for _ in range(9)]
        for cell in self.cells:
            row_index, column_index = cell.rowcol
            box_index = (row_index // 3) * 3 + column_index // 3
            boxes[box_index].append(cell)
        return tuple(Grouping(box) for box in boxes)

    def _new_choices(self):
        self.choices = [random_shape(self._rng) for _ in range(3)]

    def __str__(self):
        prefix = f"{self.__class__.__name__}["
        sep = f"\n{' ' * len(prefix)}"
        return f"{prefix}{sep.join(str(row) for row in self.rows)}]"

    def _cells_beneath(self, rowcol, shape):
        """Return a generator that yields the board cells that would
        become set were shape to be placed at rowcol."""
        place_row, place_col = rowcol
        for row, col in shape.set_cells:
            yield self.rows[place_row + row][place_col + col]

    def can_place_at(self, rowcol, shape):
        """Return True if shape may be placed on the board with its
        top-left corner at rowcol, False otherwise."""
        if any(d < 0 for d in rowcol):
            return False
        return self._can_place_at(rowcol, shape)

    def _can_place_at(self, rowcol, shape):
        # Board.can_place_at is second only to net.activate in the
        # profile, in terms of where the processor is spending its
        # time, and the negative coordinate check in can_place_at
        # comprises approximately 1/3 of its time taken.  Calling
        # this method over can_place_at means can_place can avoid
        # the expensive check.
        try:
            return not any(cell.is_set
                           for cell in self._cells_beneath(rowcol,
                                                           shape))
        except IndexError:
            return False

    def can_place(self, shape):
        """Return True if shape may be placed somewhere on the board,
        False otherwise."""
        if any(self._can_place_at(cell.rowcol, shape)
               for cell in self.cells):
            return True
        return False

    def place_at(self, rowcol, shape):
        """Place shape on the board, such that the top left corner of
        the shape is located at rowcol."""
        for cell in self._cells_beneath(rowcol, shape):
            cell.set()

    def resolve(self):
        """Resolve any solved sections, returning the number of
        sections cleared."""
        completed = sum(
            ([grouping
              for grouping in groupings
              if grouping.is_complete]
             for groupings in (self.rows, self.columns, self.boxes)),
            start=[])
        for grouping in completed:
            grouping.clear()
        return len(completed)

    def one_move(self, choice, rowcol):
        """Perform one move of the game.  Returns the points resulting
        from the move.  Returns 0 if the move is invalid."""
        shape = self.choices[choice]
        if shape is None:
            return 0
        if not self.can_place_at(rowcol, shape):
            return 0
        self.place_at(rowcol, shape)
        self.choices[choice] = None
        if all(c is None for c in self.choices):
            self._new_choices()
        return shape.score + self.resolve() * 9
