import socket
import math
from mcts.uct_algorithm import UCT
from mcts.Colour import Colour
from books.book import TemplateBook, OpeningBook

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
        self.global_turn = 0
        self.board_string = ""
        self.uct = UCT(
            board_size = self.board_size,
            colour= Colour.from_char(self.colour), 
            c = 1/math.sqrt(2)
        )
        
        self.init_template = 1

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
                    self.opening_book = OpeningBook(self.board, True)
                    self.make_move()
                else:
                    self.opening_book = OpeningBook(self.board, False)

            elif s[0] == "END":
                return True

            elif s[0] == "CHANGE":
                
                self.opening_book.current_move += 1
                
                if s[3] == "END":
                    return True

                elif s[1] == "SWAP":
                    self.opening_book.first, self.opening_book.flag = False, False
                    self.colour = self.opp_colour()
                    self.uct.colour = self.uct.colour.opposite()
                    self.board_string = s[2]
                    if s[3] == self.colour:
                        self.make_move()

                elif s[3] == self.colour:
                    self.board_string = s[2]
                    action = [int(x) for x in s[1].split(",")]
                    self.opponent_move = action
                    self.board[action[0]][action[1]] = self.opp_colour()

                    self.make_move()

        return False

    def make_move(self):
        """
        (-1,-1) for swap, else play the move on the tile.
        """
        if self.turn_count < 2 and self.board_size == 11:
            action = self.opening_book.get_opening()
            if action == True:
                print(action)
                self.s.sendall(bytes(f"-1,-1\n", "utf-8"))
            elif action == False:
                action = self.uct.search(self.board_string, self.turn_count)
                print(action)
                self.s.sendall(action)
            else:
                print(action)    
                self.s.sendall(bytes(f"{action[0]},{action[1]}\n", "utf-8"))
        else:
            
            if self.init_template:
                self.template_book = TemplateBook(self.board, self.colour)
                self.init_template = 0
            move = self.template_book.update_board(self.opponent_move)
            if move == None:
                action = self.uct.search(self.board_string, self.turn_count)
                self.s.sendall(action)
                action = action.decode("utf-8").strip().split("\n")
                action = action[0].split(",")
                self.previous_move = (int(action[0]), int(action[1]))
                self.template_book.check_for_all((self.previous_move[0], self.previous_move[1]))
            elif self.board[move[0]][move[1]] == "0":
                self.template_book.check_for_all((move[0], move[1]))
                self.s.sendall(bytes(f"{move[0]},{move[1]}\n", "utf-8"))
            else:
                action = self.uct.search(self.board_string, self.turn_count)
                self.s.sendall(action)
                action = action.decode("utf-8").strip().split("\n")
                action = action[0].split(",")
                self.previous_move = (int(action[0]), int(action[1]))
                self.template_book.check_for_all((self.previous_move[0], self.previous_move[1]))
                
            print(self.template_book.responses)
                

        self.turn_count += 1
        self.global_turn += 2

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