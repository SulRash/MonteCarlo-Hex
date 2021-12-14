class Move():
    """Represents a player move in a turn of Hex."""

    def __init__(self, colour, x=-1, y=-1):
        super().__init__()

        self.colour = colour
        self.x = x  # -1 if swap
        self.y = y  # -1 if swap

    def is_valid_move(self, game):
        """Checks if the move can be made by the given player at the given
        position.
        """

        b = game.get_board()
        colour = game.get_player()
        turn = game.get_turn()

        # out of bounds
        if (self.x < 0 or self.x >= b.get_size() or
                self.y < 0 or self.y >= b.get_size()):
            # allowed if it is a swap move
            if (self.x == -1 and self.y == -1 and turn == 2):
                return True

            return False

        # tile is empty and colour corresponds to current player
        tile = b.get_tiles()[self.x][self.y]
        return tile.get_colour() is None and colour == self.colour

    def is_swap(self):
        # a swap move is defined as -1,-1
        return self.x == -1 and self.y == -1

    def move(self, b):
        # fill the tile
        tile = b.get_tiles()[self.x][self.y]
        tile.set_colour(self.colour)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y
