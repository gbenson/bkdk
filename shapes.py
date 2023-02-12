class Shape:
    def __init__(self, code=None):
        if code is not None:
            self._init_from_code(code)
            assert self.code == code

    def _init_from_code(self, code):
        self.rows = tuple(tuple(int(c == "x")
                                for c in row)
                          for row in code.split("_"))

    @property
    def code(self):
        return "_".join("".join("-x"[c]
                                for c in row)
                        for row in self.rows)

    def __str__(self):
        return (f'<{__name__}.{self.__class__.__name__}'
                f' code="{self.code}">')

    def as_asciiart(self):
        return "\n".join("".join((" #")[c]
                                 for c in row)
                         for row in self.rows)

    def mirror(self):
        return Shape("_".join("".join(reversed(col))
                              for col in self.code.split("_")))

    def rot90cw(self):
        return Shape("_".join("".join(reversed(x))
                              for x in zip(*self.code.split("_"))))

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

        # 3x3 shapes
        self._add(code="x--_-x-_--x")  # 3x3 diagonals
        self._add(code="x--_x--_xxx")  # 3x3 Ls
        self._add(code="xxx_-x-_-x-")  # 3x3 Ts

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

shapes = tuple(ShapeSetBuilder()._shapes.values())

if __name__ == "__main__":
    for shape in shapes:
        print(f"{shape}:")
        print(shape.as_asciiart())
        print()
    print(f"{len(shapes)} shapes total")
