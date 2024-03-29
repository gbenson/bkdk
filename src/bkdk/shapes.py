import random
import numpy as np
from .bitmap import Bitmap


class Shape(Bitmap):
    def __init__(self, code=None):
        super().__init__(value=[[cell == "x"
                                 for cell in row]
                                for row in code.split("_")])
        assert self.code == code

    @property
    def code(self):
        return "_".join("".join("-x"[cell]
                                for cell in row)
                        for row in self.tolist())

    def mirror(self):
        return Shape("_".join("".join(reversed(col))
                              for col in self.code.split("_")))

    def rot90cw(self):
        return Shape("_".join("".join(reversed(x))
                              for x in zip(*self.code.split("_"))))

    def _finalize(self, max_size):
        max_rows, max_columns = max_size
        self._np_padded = np.asarray(
            (self._pad_rows(
                (self._pad_row(row, max_columns)
                 for row in self.tolist()),
                max_rows)),
            dtype=np.uint8)
        self.uid = self._bits_to_int(self._np_padded.flatten())

    def _pad_rows(self, rows, max_rows):
        rows = list(rows)
        return self._pad_seq(rows, max_rows, tuple(0 for _ in rows[0]))

    def _pad_row(self, cells, max_cells):
        return self._pad_seq(cells, max_cells, 0)

    def _pad_seq(self, items, to_length, pad_with):
        items = list(items)
        items[:0] = [pad_with] * ((to_length - len(items)) // 2)
        items.extend([pad_with] * (to_length - len(items)))
        return tuple(items)


class ShapeSetBuilder:
    def __init__(self):
        self._shapes = {}

        # 1xN and Nx1 lines
        for i in range(1, 6):
            self._add(code="x" * i)

        # 2x2 shapes
        self._add(code="x-_-x")  # 2x2 diagonals
        self._add(code="x-_xx")  # 2x2 Ls
        self._add(code="xx_xx")  # 2x2 square

        # 2x3 shapes
        self._add(code="x--_xxx")  # 2x3 Ls
        self._add(code="-x-_xxx")  # 2x3 Ts
        self._add(code="x-x_xxx")  # 2x3 Us
        self._add(code="-xx_xx-")  # 2x3 the offset ones

        # 3x3 shapes
        self._add(code="x--_-x-_--x")  # 3x3 diagonals
        self._add(code="x--_x--_xxx")  # 3x3 Ls
        self._add(code="xxx_-x-_-x-")  # 3x3 Ts
        self._add(code="-x-_xxx_-x-")  # 3x3 plus

    def _add(self, code=None):
        """Add a shape, and all rotated and mirrored equivalents."""
        shape = Shape(code)
        for _ in range(4):
            self._add_1(shape)
            shape = shape.rot90cw()

    def _add_1(self, shape):
        """Add a shape and its mirrored equivalent."""
        self._add_2(shape)
        self._add_2(shape.mirror())

    def _add_2(self, shape):
        """Add the shape, if it doesn't already exist."""
        code = shape.code
        if code not in self._shapes:
            self._shapes[code] = shape

    @property
    def shapes(self):
        return self._shapes.values()

    @property
    def max_rows(self):
        return max(shape.num_rows for shape in self.shapes)

    @property
    def max_columns(self):
        return max(shape.num_columns for shape in self.shapes)

    @property
    def max_size(self):
        return self.max_rows, self.max_columns

    def finalize(self):
        shapes = self.shapes
        max_size = self.max_size
        self._shapes = None
        for shape in shapes:
            shape._finalize(max_size)
        return shapes


ALL_SHAPES = tuple(ShapeSetBuilder().finalize())


def random_shape(_random=None):
    if _random is None:
        _random = random
    return _random.choice(ALL_SHAPES)


if __name__ == "__main__":  # pragma: no cover
    for i, shape in enumerate(ALL_SHAPES):
        if i != 0:
            print()
        for line in ("".join((" #")[c]
                             for c in row).rstrip()
                     for row in shape.rows):
            print(f"{i+1:02}: {line}")
