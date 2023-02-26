from .bitmap import Bitmap
from .shapes import random_shape


class Board(Bitmap):
    def __init__(self, random_number_generator=None):
        super().__init__(size=(9, 9))
        self._rng = random_number_generator
        self.score = 0
        self._new_choices()

    def _new_choices(self):
        self.choices = [random_shape(self._rng) for _ in range(3)]

    def resolve(self):
        """Resolve any solved sections, returning the number of
        sections cleared."""
        full_rows = set()
        full_cols = rowmask = 0x1FF
        full_boxes = [0x1FF] * 3
        for row_index, row in enumerate(self.rows):
            if row == rowmask:
                full_rows.add(row_index)
            full_cols &= row
            full_boxes[row_index // 3] &= row

        # Count and clear completed lines
        num_full_rows = len(full_rows)
        num_full_cols = self._num_set_bits_in(full_cols)

        nonfull_mask = ~full_cols
        for row_index in range(len(self.rows)):
            if row_index in full_rows:
                self.rows[row_index] = 0
                continue
            self.rows[row_index] &= nonfull_mask

        # Count and clear completed boxes
        num_full_boxes = 0
        for box_row_index, box_row in enumerate(full_boxes):
            full_boxes_mask = 0
            for box_mask in (0x1C0, 0x38, 0x7):
                if (box_row & box_mask) == box_mask:
                    num_full_boxes += 1
                    full_boxes_mask |= box_mask
            if full_boxes_mask:
                nonfull_mask = ~full_boxes_mask
                box_row_index *= 3
                for i in range(3):
                    self.rows[box_row_index + i] &= nonfull_mask

        return num_full_rows + num_full_cols + num_full_boxes

    def one_move(self, choice, rowcol):
        """Perform one move of the game.  Returns the points resulting
        from the move.  Returns 0 if the move is invalid."""
        shape = self.choices[choice]
        if shape is None:
            return 0

        # Place the shape on the board
        try:
            self.place_at(rowcol, shape)
        except ValueError:
            return 0

        # Resolve completed groupings and update score
        saved_score = self.score
        self.score += self.resolve() * 18
        self.score += self._num_set_bits_under(rowcol, shape)

        # Update the choices for the next round
        self.choices[choice] = None
        if all(c is None for c in self.choices):
            self._new_choices()

        return self.score - saved_score
