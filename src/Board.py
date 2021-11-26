from Tile import Tile
from Colour import Colour


class Board:
    """Class that describes the Hex board."""

    def __init__(self, board_size=11):
        super().__init__()

        self._board_size = board_size

        self._tiles = []
        for i in range(board_size):
            new_line = []
            for j in range(board_size):
                new_line.append(Tile(i, j))
            self._tiles.append(new_line)

        self._winner = None

    def from_string(string_input, board_size=11, bnf=True):
        """Loads a board from a string representation. If bnf=True, it will
        load a protocol-formatted string. Otherwise, it will load from a
        human-readable-formatted board.
        """

        b = Board(board_size=board_size)

        if (bnf):
            lines = string_input.split(",")
            for i, line in enumerate(lines):
                for j, char in enumerate(line):
                    b.set_tile_colour(i, j, Colour.from_char(char))
        else:
            lines = [line.strip() for line in string_input.split("\n")]
            for i, line in enumerate(lines):
                chars = line.split(" ")
                for j, char in enumerate(chars):
                    b.set_tile_colour(i, j, Colour.from_char(char))

        return b

    def has_ended(self):
        """Checks if the game has ended. It will attempt to find a red chain
        from top to bottom or a blue chain from left to right of the board.
        """

        # Red
        # for all top tiles, check if they connect to bottom
        for idx in range(self._board_size):
            tile = self._tiles[0][idx]
            if (not tile.is_visited() and
                tile.get_colour() == Colour.RED and
                    self._winner is None):
                self.DFS_colour(0, idx, Colour.RED)
        # Blue
        # for all left tiles, check if they connect to right
        for idx in range(self._board_size):
            tile = self._tiles[idx][0]
            if (not tile.is_visited() and
                tile.get_colour() == Colour.BLUE and
                    self._winner is None):
                self.DFS_colour(idx, 0, Colour.BLUE)

        # un-visit tiles
        self.clear_tiles()

        return self._winner is not None

    def clear_tiles(self):
        """Clears the visited status from all tiles."""

        for line in self._tiles:
            for tile in line:
                tile.clear_visit()

    def DFS_colour(self, x, y, colour):
        """A recursive DFS method that iterates through connected same-colour
        tiles until it finds a bottom tile (Red) or a right tile (Blue).
        """

        self._tiles[x][y].visit()

        # win conditions
        if (colour == Colour.RED):
            if (x == self._board_size-1):
                self._winner = colour
        elif (colour == Colour.BLUE):
            if (y == self._board_size-1):
                self._winner = colour
        else:
            return

        # end condition
        if (self._winner is not None):
            return

        # visit neighbours
        for idx in range(Tile.NEIGHBOUR_COUNT):
            x_n = x + Tile.I_DISPLACEMENTS[idx]
            y_n = y + Tile.J_DISPLACEMENTS[idx]
            if (x_n >= 0 and x_n < self._board_size and
                    y_n >= 0 and y_n < self._board_size):
                neighbour = self._tiles[x_n][y_n]
                if (not neighbour.is_visited() and
                        neighbour.get_colour() == colour):
                    self.DFS_colour(x_n, y_n, colour)

    def print_board(self, bnf=True):
        """Returns the string representation of a board. If bnf=True, the
        string will be formatted according to the communication protocol.
        """

        output = ""
        if (bnf):
            for line in self._tiles:
                for tile in line:
                    output += Colour.get_char(tile.get_colour())
                output += ","
            output = output[:-1]
        else:
            leading_spaces = ""
            for line in self._tiles:
                output += leading_spaces
                leading_spaces += " "
                for tile in line:
                    output += Colour.get_char(tile.get_colour()) + " "
                output += "\n"

        return output

    def get_winner(self):
        return self._winner

    def get_size(self):
        return self._board_size

    def get_tiles(self):
        return self._tiles

    def set_tile_colour(self, x, y, colour):
        self._tiles[x][y].set_colour(colour)


if (__name__ == "__main__"):
    b = Board.from_string(
        "0R000B00000,0R000000000,0RBB0000000,0R000000000,0R00B000000," +
        "0R000BB0000,0R0000B0000,0R00000B000,0R000000B00,0R0000000B0," +
        "0R00000000B", bnf=True
    )
    b.print_board(bnf=False)
    print(b.has_ended(), b.get_winner())
