class Bitmap:
    def __init__(self, size=None, value=None):
        if size is None:
            size = None, len(value[0])
        num_rows, self.num_columns = size
        if value is None:
            self.rows = [0 for _ in range(num_rows)]
        else:
            self.rows = list(map(self._init_row, value))
            if num_rows is not None and size != self.size:
                raise ValueError

    def _init_row(self, row):
        if len(row) != self.num_columns:
            raise ValueError
        result = 0
        for col in reversed(row):
            if col:
                result |= 1
            result <<= 1
        return result >> 1

    @property
    def num_rows(self):
        return len(self.rows)

    @property
    def size(self):
        return self.num_rows, self.num_columns

    def tolist(self):
        return [[(row & (1 << i)) >> i
                 for i in range(self.num_columns)]
                for row in self.rows]

    def __str__(self):
        return str(self.tolist()).replace("], ", "],\n ")

    def can_place_at(self, rowcol, other):
        """Return True if other may be placed on self with its
        top-left corner at rowcol, False otherwise."""
        if any(d < 0 for d in rowcol):
            return False
        return self._can_place_at(rowcol, other)

    def _can_place_at(self, rowcol, other):
        row, col = rowcol
        if other.num_columns > self.num_columns - col:
            return False
        s_rows = self.rows[row:]
        o_rows = other.rows
        if len(o_rows) > len(s_rows):
            return False
        for s_row, o_row in zip(s_rows, o_rows):
            s_row >>= col
            mask = (1 << other.num_columns) - 1
            if s_row & o_row & mask:
                return False
        return True

    def can_place(self, other):
        """Return True if other may be placed somewhere on self,
        False otherwise."""
        for row in range(self.num_rows - other.num_rows + 1):
            for col in range(self.num_columns - other.num_columns + 1):
                if self._can_place_at((row, col), other):
                    return True
        return False

    def place_at(self, rowcol, other):
        """Place other on self, such that the top left corner of
        other is located at rowcol on self.
        """
        if not self.can_place_at(rowcol, other):
            raise ValueError
        row, col = rowcol
        for i, o_row in enumerate(other.rows):
            self.rows[i + row] |= (o_row << col)

    def _num_set_bits_under(self, rowcol, other):
        """Count the number of set bits in self under set bits
        in other, when other is located over rowcol on self.
        Prefixed with underscore because it doesn't check for
        the placed shape extending outside of self's borders.
        """
        row, col = rowcol
        total = 0
        for i, o_row in enumerate(other.rows):
            masked = self.rows[i + row] & (o_row << col)
            total += self._num_set_bits_in(masked)
        return total

    @classmethod
    def _num_set_bits_in(cls, x):
        """Return the number of set bits in x."""
        return bin(x).count("1")
