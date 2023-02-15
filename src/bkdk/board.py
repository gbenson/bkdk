from dataclasses import dataclass

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
    def __init__(self):
        self.rows = tuple(Grouping(Cell((row_index, column_index))
                                for column_index in range(9))
                          for row_index in range(9))
        self.columns = tuple(map(Grouping, zip(*self.rows)))
        self.cells = sum(self.rows, start=())
        self.boxes = self._init_boxes()

    def _init_boxes(self):
        boxes = [[] for _ in range(9)]
        for cell in self.cells:
            row_index, column_index = cell.rowcol
            box_index = (row_index // 3) * 3 + column_index // 3
            boxes[box_index].append(cell)
        return tuple(Grouping(box) for box in boxes)

    def __str__(self):
        prefix = f"{self.__class__.__name__}["
        sep = f"\n{' ' * len(prefix)}"
        return f"{prefix}{sep.join(str(row) for row in self.rows)}]"

    def _cells_beneath(self, rowcol, shape):
        """Return a generator that yields the board cells that would
        become set were shape to be placed at rowcol."""
        row_index, column_index = rowcol
        for srcrow, dstrow in zip(shape.rows, self.rows[row_index:]):
            for srccell, dstcell in zip(srcrow, dstrow[column_index:]):
                if srccell:
                    yield dstcell

    def can_place_at(self, rowcol, shape):
        """Return True if shape may be placed on the board with its
        top-left corner at rowcol, False otherwise."""
        if any(d < 0 for d in rowcol):
            return False
        print(f"{shape.code} at {rowcol}: "
              f"shape.size = {shape.size}: ",
              tuple(d + s
                    for d, s in zip(rowcol, shape.size)))
        if any(d + s > 9 for d, s in zip(rowcol, shape.size)):
            return False
        return not any(cell.is_set
                       for cell in self._cells_beneath(rowcol, shape))

    def place_at(self, rowcol, shape):
        """Place shape on the board, such that the top left corner of
        the shape is located at rowcol."""
        for cell in self._cells_beneath(rowcol, shape):
            cell.set()
