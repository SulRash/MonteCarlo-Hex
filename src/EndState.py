from enum import Enum


class EndState(Enum):
    """This enum describes the possible end conditions of a match."""

    WIN = (1, 0, 0)
    TIMEOUT = (0, 1, 0)
    BAD_MOVE = (0, 0, 1)

    def get_text(state):
        """Returns the name of the state as a string."""

        if (state == EndState.WIN):
            return "Win"
        elif (state == EndState.TIMEOUT):
            return "Timeout"
        elif (state == EndState.BAD_MOVE):
            return "Illegal move"
        else:
            return "None"
