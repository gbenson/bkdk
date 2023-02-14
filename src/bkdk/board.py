from dataclasses import dataclass

@dataclass
class Cell:
    rowcol: tuple[int, int]
    is_set: bool = False

    def set(self):
        self.is_set = True

    def __str__(self):
        return f"Cell({self.rowcol}, is_set={self.is_set})"

class Board:
    def __init__(self):
        self.rows = tuple(tuple(Cell((row_index, column_index))
                                for column_index in range(9))
                          for row_index in range(9))
        self.columns = tuple(zip(*self.rows))
        self.cells = sum(self.rows, start=())
        self.boxes = self._init_boxes()

    def _init_boxes(self):
        boxes = [[] for _ in range(9)]
        for cell in self.cells:
            row_index, column_index = cell.rowcol
            box_index = (row_index // 3) * 3 + column_index // 3
            boxes[box_index].append(cell)
        return tuple(tuple(box) for box in boxes)
