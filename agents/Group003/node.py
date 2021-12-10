from __future__ import annotations
from copy import deepcopy
from typing import List
from src.Board import Board
from src.Move import Move
from src.Colour import Colour

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
    
    def get_children(self, board_size: int) -> List[Node]:
        '''
        Returns all children nodes.
        '''
        children = []
        actions = self.get_valid_actions(board_size, self.colour)
        for action in actions:
            new_state = deepcopy(self.s)
            action.move(new_state)
            child = Node(self, action, new_state, self.colour.opposite())
            children.append(child)
        return children

    def get_valid_actions(self, board_size: int, colour: Colour) -> List[Move]:
        '''
        Returns the list of all possible moves.
        '''

        all_moves: List[Move] = [] # Stores all moves
        valid_moves: List[Move] = [] # Stores valid moves

        # Append all moves
        for y in range(board_size):
            for x in range(board_size):
                all_moves.append(Move(colour=colour, x=x, y=y))
        
        for m in all_moves:
            # Get the corresponding tile
            tile = self.s.get_tiles()[m.x][m.y]
            # Check if tile is not occupied
            if tile.get_colour() is None:
                valid_moves.append(m)
                
        return valid_moves