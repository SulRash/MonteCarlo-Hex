from __future__ import annotations

import socket
from random import choice
from time import sleep

from typing import List

import math
import numpy as np

class Node:

    # Look into type of state.
    def __init__(self, parent: Node = None, x: int, y: int):
        self.parent = parent
        # self.state = state
        self.x = x
        self.y = y

        # How many times node has been passed through.
        self.N = 0
        # Reward function, accumulated reward.
        self.Q = 0

    # All valid moves in current state.
    def get_children(self, board: List[List[str]], board_size: int) -> List[Node]:
        children = []
        for i in range(board_size):
            for j in range(board_size):
                if board[i][j] == '0':
                    child = Node(parent = self, x = i, y = j)
                    children.append(child)
        return children

class Tree:
    def __init__(self, boardsize: int = 11, root: Node):
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

    def default_policy(self, node: Node) -> int:
        pass

    def tree_policy(self) -> Node:
        pass

    def expand(self, node: Node) -> Node:
        pass

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


