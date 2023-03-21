import copy
from .bitmap import Bitmap
from .shapes import ALL_SHAPES, random_shape


class Board(Bitmap):
    def __init__(self, random_number_generator=None, value=None):
        super().__init__(size=(9, 9), value=value)
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

    @property
    def valid_moves(self):
        for choice, shape in enumerate(self.choices):
            if shape is None:
                continue
            for row in range(self.num_rows):
                for column in range(self.num_columns):
                    rowcol = row, column
                    if self._can_place_at(rowcol, shape):
                        yield choice, rowcol

    def can_place_any_shape(self):
        """Return True if any shape may be placed on this board."""
        # XXX could test a reduced set of shapes (e.g if we can place
        # a horizontal line of 5 squares, we can place lines of 1-4
        # squares also)
        for shape in ALL_SHAPES:
            if not self.can_place(shape):
                return False
        return True

    def rate_potential(self, max_depth=5, offset_result=True):
        """If :param offset_result: is False, return the number of steps
        into the future it is guaranteed to be possible to take, up to a
        maximum of :param max_depth: plys, such that a result of 0 means
        the board has no valid moves, and a result of :param max_depth:
        means we stopped before being blocked.  If :param offset_result:
        is True, subtract :param max_depth: from the result, such that a
        value of 0 means we stopped before being blocked, and negative
        values indicate we were blocked before reaching :param max_depth:.
        """
        board = copy.copy(self)
        board._new_choices = lambda: None
        board._remaining_plys = max_depth
        try:
            return board._rate_potential_stage1()
        except StopIteration:
            return 0

    def _begin_ply(self):
        self._remaining_plys -= 1
        if self._remaining_plys < 1:
            raise StopIteration

    def _rate_potential_stage1(self):
        """Walk through choices visible to the user."""
        if not any(self.choices):
            return self._rate_potential_stage2()
        self._begin_ply()
        for move in self.valid_moves:
            print(self._remaining_plys, move)
            board = copy.deepcopy(self)
            board.one_move(*move)
            result = board._rate_potential_stage1()
            raise NotImplementedError(f"result = {result}")
        raise NotImplementedError

    def _rate_potential_stage2(self):
        """Walk through all future choices."""
        self._begin_ply()
        self.choices = list(ALL_SHAPES)
        valid_moves = list(self.valid_moves)
        print(f"{len(valid_moves)}/2656 valid moves")
        # The maximum, on blank board, is
        # 47 choices => 2,656 valid moves
        placable_choices = {choice for choice, rowcol in valid_moves}
        num_unplacables = len(self.choices) - len(placable_choices)
        if num_unplacables > 0:
            print(f"{num_unplacables} unplacable shapes found")
            return num_unplacables

        # for move in valid_moves:
        #    print(self._remaining_plys, move)
        #    board = copy.deepcopy(self)
        #    board.one_move(*move)
        #    board._choices = []  # XX unnecessary?
        #    result = board._rate_potential_stage2()
        #    raise NotImplementedError(f"result = {result}")

        # Every shape can be placed
        raise StopIteration  # XXX??
