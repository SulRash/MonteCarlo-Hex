import socket
import math
from mcts.uct_algorithm import UCT
from mcts.Colour import Colour

class Agent003():
    """
    This class describes Group 3 agent based on UCT.
    """

    HOST = "127.0.0.1"
    PORT = 1234

    def __init__(self, board_size=11):
        self.s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )

        self.s.connect((self.HOST, self.PORT))

        self.board_size = board_size
        self.board = []
        self.colour = ""
        self.turn_count = 0
        self.n_openings = 0
        self.board_string = ""
        self.uct = UCT(
            board_size = self.board_size,
            colour= Colour.from_char(self.colour), 
            c = 1/math.sqrt(2)
        )

    def run(self):
        """Reads data until it receives an END message or the socket closes."""

        while True:
            data = self.s.recv(1024)
            if not data:
                break
            # print(f"{self.colour} {data.decode('utf-8')}", end="")
            if (self.interpret_data(data)):
                break

        # print(f"Naive agent {self.colour} terminated")

    def interpret_data(self, data):
        """Checks the type of message and responds accordingly. Returns True
        if the game ended, False otherwise.
        """

        messages = data.decode("utf-8").strip().split("\n")
        messages = [x.split(";") for x in messages]
        # print(messages)
        for s in messages:
            if s[0] == "START":
                self.board_size = int(s[1])
                self.uct.board_size = self.board_size
                self.colour = s[2]
                self.uct.colour = Colour.from_char(s[2])
                self.board = [
                    [0]*self.board_size for i in range(self.board_size)]

                if self.colour == "R":
                    self.make_move()

            elif s[0] == "END":
                return True

            elif s[0] == "CHANGE":
                if s[3] == "END":
                    return True

                elif s[1] == "SWAP":
                    self.colour = self.opp_colour()
                    self.uct.colour = self.uct.colour.opposite()
                    self.board_string = s[2]
                    if s[3] == self.colour:
                        self.make_move()

                elif s[3] == self.colour:
                    self.board_string = s[2]
                    action = [int(x) for x in s[1].split(",")]
                    self.board[action[0]][action[1]] = self.opp_colour()

                    self.make_move()

        return False

    def make_move(self):
        """
        (-1,-1) for swap, else play the move on the tile.
        """
        print(self.colour)
        print(self.uct.board_size)

        if self.turn_count < self.n_openings and self.board_size == 11:
            # Opening book moves are handled here
            # Including SWAP
            pass
        else:
            action = self.uct.search(self.board_string)
            self.s.sendall(action)

        self.turn_count += 1

    def opp_colour(self):
        """
        Returns the char representation of the colour opposite to the
        current one.
        """
        if self.colour == "R":
            return "B"
        elif self.colour == "B":
            return "R"
        else:
            return "None"

if (__name__ == "__main__"):
    agent = Agent003()
    agent.run()