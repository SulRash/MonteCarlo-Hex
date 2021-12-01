from __future__ import annotations

import socket
from random import choice
from time import sleep
from copy import deepcopy
import random
from src.Board import Board
from src.Move import Move
from src.Colour import Colour

from typing import List, Tuple

class Node:
    
    # Look into type of state.
    def __init__(
        self,
        parent: Node,
        action: Move,
        state: Board,
        colour: Colour,
    ) -> None:
        self.parent = parent

        # Associated node
        self.s = state
        # Incoming action
        self.a = action
        # How many times node has been passed through.
        self.N = 0
        # Reward function, accumulated reward.
        self.Q = 0
        # Player who made the incoming action leading to these node
        self.colour = colour

        # List of all children
        self.children: List[Node] = []
    
    # All valid moves in current state.
    def get_children(self) -> List[Node]:
        children = []
        for x in self.state:
            for y in self.state:
                # Loop over all tiles in state and add all valid moves as children.
                pass

    def get_valid_actions(self, baord_size: int, c: Colour) -> List[Move]:
        '''
        Returns the list of all possible moves.
        '''

        all_moves: List[Move] = [] # Stores all moves
        valid_moves: List[Move] = [] # Stores valid moves

        # Append all moves
        for y in range(baord_size):
            for x in range(baord_size):
                all_moves.append(Move(colour=c, x=x, y=y))
        
        for m in all_moves:
            # Get the corresponding tile
            tile = self.s.get_tiles()[m.x][m.y]
            # Check if tile is not occupied
            if tile.get_colour() is None:
                valid_moves.append(m)
            
class Tree:
    def __init__(self, boardsize: int = 11, c: Colour = Colour.BLUE):
        self.boardsize = boardsize
        self.colour = c
    
    def search(state: List[List["0" | str]]  = [[]]) -> str:
        pass
    
    def default_policy(self, v: Node) -> Node:
        # loop until a terminal node is reached.
        while v.s.has_ended():
            action = choice(v.get_valid_actions(self.boardsize, v.colour))
            new_state = deepcopy(v.s)
            action.move(new_state)
        
            v = Node(v, action, new_state, v.colour.opposite())
        
        if v.s.get_winner() == self.colour:
            return 1
        else:
            return -1

    
    def tree_policy(self, v: Node) -> Node:
        '''
        Chooses a node for game simulation.
        '''
        
        # Check if v is terminal
        while not v.s.has_ended():
            
            # Checks if v is not fully expanded
            if v.get_valid_actions(
                board_size = self.boardsize,
                colour = v.colour.opposite()
            ) != len(v.children): 
                return self.expand(v)
            
            # Choose next node with best_child function
            else:
                v = self.best_child(v)
        
        # Returns v when it is a terminal node
        return v
    
    def get_untried_actions(self, v: Node) -> List[Move]:
        '''
        Returns all untried actions of a node v.
        '''

        all_valid_actions = v.get_valid_actions() # Get all valid actions from v
        
        # Check if v has children
        if len(v.children) != 0:
            untried_actions: List[Move] = [] # Contains all untried actions

            for action in all_valid_actions:
                is_tried = False # Label action asuntried
                
                for child in v.children:
                    if action.x == child.a.x and action.y == child.a.y:
                        is_tried = True # Action was already applied
                        break
                
                if not is_tried: # Add action to untried list
                    untried_actions.append(action)
            
            return untried_actions

        return all_valid_actions

    def expand(self, v: Node) -> Node:
        # Find untried actions
        next_player = v.colour.opposite()
        untried_actions = self.get_untried_actions(v)
        
        if len(untried_actions) == 1:
            a = untried_actions[0]
        else: # Pick a random action
            a = untried_actions[random.randint(0, len(untried_actions)-1)]
        
        # Create a copy of state s
        s_prime = deepcopy(v.s)
        # Apply the move
        a.move(s_prime)

        # Add a new child
        v_prime = Node(
            parent=v,
            action=a,
            state=s_prime,
            colour=next_player
        )
        v.children.append(v_prime)

        # Return the new child
        return v_prime
    
    def best_child(node: Node) -> Node:
        pass
    
    # If parent is the same node, we are at root.
    def backup(node: Node):
        pass
    
   

class NaiveAgent():
    """This class describes the default Hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
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
                self.colour = s[2]
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
                    if s[3] == self.colour:
                        self.make_move()

                elif s[3] == self.colour:
                    action = [int(x) for x in s[1].split(",")]
                    self.board[action[0]][action[1]] = self.opp_colour()

                    self.make_move()

        return False

    def make_move(self):
        """Makes a random move from the available pool of choices. If it can
        swap, chooses to do so 50% of the time.
        """

        # print(f"{self.colour} making move")
        if self.colour == "B" and self.turn_count == 0:
            if choice([0, 1]) == 1:
                self.s.sendall(bytes("SWAP\n", "utf-8"))
            else:
                # same as below
                choices = []
                for i in range(self.board_size):
                    for j in range(self.board_size):
                        if self.board[i][j] == 0:
                            choices.append((i, j))
                pos = choice(choices)
                self.s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))
                self.board[pos[0]][pos[1]] = self.colour
        else:
            choices = []
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.board[i][j] == 0:
                        choices.append((i, j))
            pos = choice(choices)

            self.s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))
            self.board[pos[0]][pos[1]] = self.colour
        self.turn_count += 1

    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """
        if self.colour == "R":
            return "B"
        elif self.colour == "B":
            return "R"
        else:
            return "None"


if (__name__ == "__main__"):
    agent = NaiveAgent()
    agent.run()