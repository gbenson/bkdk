class Player:
    def __init__(self, activate):
        self._activate = activate

    def _collect_state_from(self, board):
        # XXX might this method be faster with s/int/float/ ?
        state = [int(cell.is_set) for cell in board.cells]
        for shape in board.choices:
            values = [0, int(board.can_place(shape)) * 2 - 1]
            state.extend(values[i] for i in shape.cells)
        return state

    def _state_to_str(self, state):
        # XXX make state a class extending tuple, with a __str__?
        start = 0
        lines = []
        for size in (9, 5, 5, 5):
            if lines:
                lines.append("")
            for row in range(size):
                limit = start + size
                lines.append(f"[{start}..{limit}): " + str(state[start:limit]))
                start = limit
        return "\n".join(lines)

    def one_move(self, board):
        inputs = self._collect_state_from(board)
        # print(self._state_to_str(inputs))
        outputs = self._activate(inputs)
        ranked_outputs = list(sorted(
            ((activation, output)
             for output, activation in enumerate(outputs)),
            reverse=True))
        for activation, output in ranked_outputs:
            cell, choice = divmod(output, 3)
            rowcol = divmod(cell, 9)
            shape = board.choices[choice]
            is_legal = board.can_place_at(rowcol, shape)
            print(f"output {output} => shape {choice} at {rowcol}?"
                  f" {is_legal and 'YES!' or 'no'}")
            if not is_legal:
                continue
            board.place_at(rowcol, shape)
            board.choices[choice] = None
            break
        print(board)
