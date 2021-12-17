from __future__ import annotations

import multiprocessing
from random import choice
from copy import deepcopy
import random
import time
from typing import List
import math
import numpy as np
from mcts.node import Node
from mcts.Board import Board
from mcts.Move import Move
from mcts.Colour import Colour

class UCT:
    def __init__(self, board_size: int = 11, colour: Colour = Colour.BLUE, c: int = 1/math.sqrt(2)):
        self.board_size = board_size
        self.TIME = 8 
        self.colour = colour
        self.c = c

    def search2(self, state: str, t: int) -> bytes:
        self.TIME = min(12-0.3*(t-1), 1)
        t0 = time.time()

        board = Board.from_string(state, self.board_size)
        v0 = Node(None, None, board, self.colour)
        
        while self.TIME > (time.time() - t0):
            v1 = self.tree_policy(v0)
            reward = self.default_policy(v1)
            self.backup(v1, reward)

        # derive action from best child
        best_child = self.best_child(v0)
        
        print(len(v0.children))
        
        # convert to string
        move_string = bytes(f"{best_child.a.x},{best_child.a.y}\n", "utf-8")
        # for c in v0.children:
        #     print(c.N)
        return move_string

    def multiprocess_loop(self, v0: Node, t0):
        while self.TIME > (time.time() - t0):
            v1 = self.tree_policy(v0)
            reward = self.default_policy(v1)
            self.backup(v1, reward)
        return v0.children, v0.N

    def search(self, state: str, t: int) -> bytes:
        self.TIME = max(12-0.3*(t-1), 1)
        board = Board.from_string(state, self.board_size)
        v0 = Node(None, None, board, self.colour)
        
        subprocs = multiprocessing.Pool(int(multiprocessing.cpu_count()/2))
        t0 = time.time()
        children = subprocs.starmap(self.multiprocess_loop, [(v0,t0)]*int(multiprocessing.cpu_count()/2))
        acum_rew = []
        for child in children:
            acum_rew.append(child[1])
            v0.children += child[0]
        v0.N = sum(acum_rew)/len(acum_rew)
        print(len(v0.children))
        
        # derive action from best child
        best_child = self.best_child(v0)
        
        # convert to string
        move_string = bytes(f"{best_child.a.x},{best_child.a.y}\n", "utf-8")
        # for c in v0.children:
        #     print(c.N)
        return move_string

    def default_policy(self, v: Node) -> int:
        # loop until a terminal node is reached.
        while not v.s.has_ended():
            action = choice(v.get_valid_actions(self.board_size, v.colour))
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
            valid_actions = v.get_valid_actions(
                board_size = self.board_size,
                colour = v.colour.opposite()
            )
            if len(valid_actions) != len(v.children):
                # print(len(valid_actions))
                # print('Expand')
                return self.expand(v)
            
            # Choose next node with best_child function
            else:
                # print('Choose')
                v = self.best_child(v)
                # print(v.a.x)
                # print(v.a.y)
        
        # Returns v when it is a terminal node
        return v
    
    def get_untried_actions(self, v: Node) -> List[Move]:
        '''
        Returns all untried actions of a node v.
        '''

        all_valid_actions = v.get_valid_actions(self.board_size, self.colour) # Get all valid actions from v
        
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

    def best_child(self, node: Node) -> Node:
        children = node.get_children()
        ucb_arr = []

        for child in children:
            exploit = child.Q / child.N
            explore = math.sqrt((2 * math.log(node.N)) / child.N)
            ucb = exploit + 2 * self.c * explore
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