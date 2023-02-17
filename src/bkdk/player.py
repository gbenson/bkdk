class Player:
    def __init__(self, activate, verbose=False):
        self._activate = activate
        self.verbose = verbose

    _EMPTY_CHOICE = tuple(0 for _ in range(25))

    def _choice_states_for(self, board):
        for shape in board.choices:
            if shape is None:
                yield None
            else:
                yield board.can_place(shape)

    def _collect_state_from(self, board):
        choice_states = tuple(self._choice_states_for(board))
        if not any(cs is True for cs in choice_states):
            return

        # XXX might this method be faster with s/int/float/ ?
        state = [int(cell.is_set) for cell in board.cells]
        for shape, can_place in zip(board.choices, choice_states):
            if shape is None:
                state.extend(self._EMPTY_CHOICE)
                continue
            values = [0, int(can_place) * 2 - 1]
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

    def next_move(self, board):
        inputs = self._collect_state_from(board)
        if inputs is None:
            return  # No moves!
        # print(self._state_to_str(inputs))
        outputs = self._activate(inputs)
        ranked_outputs = list(sorted(
            ((activation, output)
             for output, activation in enumerate(outputs)),
            reverse=True))
        penalty = 0
        for activation, output in ranked_outputs:
            cell, choice = divmod(output, 3)
            rowcol = divmod(cell, 9)
            shape = board.choices[choice]
            is_legal = (shape is not None
                        and board.can_place_at(rowcol, shape))
            if self.verbose:
                print(f"output {output} => shape {choice} at {rowcol}?"
                      f" {is_legal and 'YES!' or 'no'}")
            if not is_legal:
                penalty += 1
                continue
            return choice, rowcol, penalty

    def run_game(self, board):
        score = penalties = 0
        while (move := self.next_move(board)) is not None:
            choice, rowcol, penalty = move
            penalties += penalty
            shape = board.choices[choice]
            board.place_at(rowcol, shape)
            board.choices[choice] = None
            if all(c is None for c in board.choices):
                board._new_choices()
            last_score = score
            score += shape.score
            score += len(board.resolve()) * 9
            if self.verbose:
                print(board)
                print(f"score {last_score} => {score}")
        return score, penalties
