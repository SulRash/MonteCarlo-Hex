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

import math
import numpy as np

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
    def get_children(self, board: List[List[str]], board_size: int) -> List[Node]:
        children = []
        for i in range(board_size):
            for j in range(board_size):
                if board[i][j] == '0':
                    child = Node(parent = self, x = i, y = j)
                    children.append(child)
        return children

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
                
        return valid_moves    

class Tree:
    def __init__(self, boardsize: int = 11, root: Node, c: Colour = Colour.BLUE):
        self.boardsize = boardsize
        self.TIME = 0
        self.c = 0
        self.current_node = root


    def search(self, state: List[List["0" | str]] = [[]]) -> bytes:
        v0 = self.current_node
        while self.TIME > 0:
            v1 = self.tree_policy(v0)
            reward = self.default_policy(v1)
            self.backup(v1, reward)
        best_child = self.best_child(v0, self.c)
        # derive action from best child
        # convert to string
        # set current_node to best_child
        self.current_node = best_child
        action = bytes(f"{best_child.x},{best_child.y}\n", "utf-8")
        return action

    def default_policy(self, v: Node) -> int:
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

    def best_child(self, node: Node, c: int) -> Node:
        children = node.get_children()
        ucb_arr = []

        for child in children:
            exploit = child.Q / child.N
            explore = math.sqrt((2 * math.log(node.N)) / child.N)
            ucb = exploit + (c * explore)
            ucb_arr.append(ucb)

        argmax = int(np.argmax(ucb_arr))
        best_child = children[argmax]
        return best_child

    # If parent is the same node, we are at root.
    def backup(self, node: Node, reward: int):
        v = node
        while v:
            v.N += 1
            v.Q = v.Q + reward
            v = v.parent


