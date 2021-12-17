from typing import List, Tuple

from books.templates import templates
from books.openings import openings

import numpy as np
import random

# x is up and down and y is left and right.
class OpeningBook():
    
    def __init__(self, board, first: bool) -> None:
        self.board = board
        self.first = first
        self.current_move = 0
        self.flag = True
        
    def get_opening(self, opponent_move: Tuple[int, int] = None) -> Tuple[int, int] or bool:
        """
        Gets opening moves to play for the first three moves in the game.

        Args:
            opponent_move (Tuple[int, int], optional): Opponent's previous move, used to determine first player's second move. Defaults to None.

        Returns:
            Tuple[int, int] or bool: Returns x,y coordinates of opening moves or False if you should play a random move, True if player two should swap.
        """
        if self.first:
            if not self.current_move:
                return openings[1]["Move"]
            else:
                if opponent_move in list(openings[1]["Responses"].keys()):
                    return openings[1]["Responses"][opponent_move]
                else:
                    return False
                
        else:
            if self.flag and self.swap(opponent_move):
                return True
            else:
                return openings[2]["Move"]
        
    def swap(self, opponent_move: Tuple[int, int]) -> bool:
        for i in range(0,10):
            if opponent_move == (0, i):
                return bool(random.randint(0,1))
            elif opponent_move == (10, i):
                return bool(random.randint(0,1))
            elif opponent_move == (i, 0):
                return bool(random.randint(0,1))
            elif opponent_move == (i, 10):
                return bool(random.randint(0,1))
        return True 

class TemplateBook():
    
    # Experimenting about whether I should use a detailed dict like this or just saving responses.
    found_ingame = {
        "Bottleneck": {"Intrusions": (), "Responses": {}},
        "Edge Template 31b": {"Intrusions": (), "Responses": {}},
        "Edge Template 2": {"Intrusions": (), "Responses": {}},
        "Connections": {"Intrusions": (), "Responses": {}}  
    }
    
    responses = {}
    
    def __init__(self, board: List[List[str]], colour: str) -> None:
        self.board = np.array(board)
        self.filled_board = np.array(board)
        self.checked_tiles = set()
        self.checked_tiles_conns = set()
        self.templates = templates
        
        #Can be either "R" or "B"
        self.colour = colour
    
    def update_board(self, tile_coords: Tuple[int, int]) -> None or Tuple[int, int]:
        """
        Updates board by checking which tiles are new and finding out if any patterns are found.

        Args:
            board (List[List[str]]): Game board.
            
        Returns:
            (Tuple[int, int] Optional): Can return move for player if immediate counter found.
        
        To-Do:
        Idea for optimization: When our agent plays a move we should calculate more templates since our timer is not being used.
        """
        x, y = tile_coords
        if self.board[x,y] != self.colour and (x,y) in self.responses:
            move = self.responses[(x,y)]
            del self.responses[(x,y)]
            return move
        self.board[x,y] = self.colour
        self.filled_board[x,y] = self.colour
        
    def check_for_all(self, coords: Tuple[int, int]) -> List[List[int or str]]:
        self.board[coords[0], coords[1]] = self.colour
        self.check_for_connection(coords)
        self.check_for_bottleneck(coords)
        self.check_for_edge_31b(coords)
        self.check_for_edge_2(coords)
    
    def check_for_connection(self, tile_coords: Tuple[int, int]) -> None:
        """
        An example of a connection:
            0 1 2 3 4
             1    R
              2  R* R*
               3  R
                4
        Where R is the red player's tiles and R* is an empty tile that connects the red player's tiles together.
        If the opponent attempts to block this move (called an intrustion), the red player should respond with an immediate response by taking
        the other free tile.
        
        Coords is the most recently played move.
        """
        #print("Checking for connection...")
        x, y = tile_coords
        # Loop over all keys to check all possible bottlenecks.
        for key in self.templates["Connections"]:
            #print("Checking", tile_coords[0] + key[0][0], tile_coords[1] + key[0][1], "is 0", tile_coords[0] + key[1][0], tile_coords[1] + key[1][1], "is 0", tile_coords[0] + key[2][0], tile_coords[1] + key[2][1], "is R")
            # If index out of range, continue since the pattern doesn't fit.
            # Runs conditional to check for validity of pattern. (Runs according to how bottlenecks are defined in dictionary above)
            if self.check_validity(tile_coords, key, ["0", "0", self.colour]):
                for x2, y2 in self.templates["Connections"][key]["Responses"]:
                    if x+x2 < 0 or y+y2 < 0:
                        #print("Connection continued... (not found)")
                        continue
                    else:
                        #print("Connection found!")
                        self.update_ingame_info("Connections", tile_coords, (x2, y2), key)
                break        
    
    def check_for_bottleneck(self, tile_coords: Tuple[int, int]) -> None:
        """
        Checks for the following pattern:
            0 1 2 3 4 5
             1    0 B 0 
              2  0 0 0 0 
               3  B R B
                4
                
        Where R is red, B is blue, and 0 is an empty tile. Bottlenecks are vital in dictating the flow of the game defense wise.

        Args:
            tile_coords (Tuple[int, int]): Coordinates of tile checking.
        """
        x, y = tile_coords
        
        # Check colour of placed piece to find out opposite colour.
        if self.board[x, y] == "R":
            opposite = "B"
        else:
            opposite = "R"
            
        # Loop over all keys to check all possible bottlenecks.
        for key in self.templates["Bottleneck"]:
            
            # If index out of range, continue since the pattern doesn't fit.
            # Runs conditional to check for validity of pattern. (Runs according to how bottlenecks are defined in dictionary above)
            if self.check_validity(tile_coords, key, ["0", "0", self.colour, self.colour, opposite]):
                for x2, y2 in self.templates["Bottleneck"][key]["Responses"]:
                    if x+x2 < 0 or y+y2 < 0:
                        continue
                    else:
                        self.update_ingame_info("Bottleneck", tile_coords, (x2, y2), key)
                break        
        
    def check_for_edge_31b(self, tile_coords: Tuple[int, int]) -> None:
        """
        Checks for the following pattern:
            0 1 2 3 4 5 6
             1   0 0 0 0 0
              2   0 0 0 0 
               3   0 R 0
                4
                
        Where R is the red player and 0 are empty spaces. This pattern has huge attacking potential.
        
        Args:
            tile_coords (Tuple[int, int]): Coordinates of tile checking.
        """
        x,y = tile_coords
        if tile_coords[0] - 3 == 0 or tile_coords[1] - 3 == 0:
            for key in self.templates["Edge Template 31b"]:
                if self.check_validity(tile_coords, key, ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]):
                    for x2, y2 in self.templates["Edge Template 31b"][key]["Responses"]:
                        if x+x2 < 0 or y+y2 < 0:
                            continue
                        else:
                            self.update_ingame_info("Edge Template 31b", tile_coords, (x2, y2), key)
                    break
    
    def check_for_edge_2(self, tile_coords: Tuple[int, int]) -> None:
        """
        Checks for the following pattern:
            0 1 2 3  
             1  0 0  
              2  R  
                
        Args:
            tile_coords (Tuple[int, int]): Coordinates of tile checking.
        """
        x,y = tile_coords
        if tile_coords[0] - 2 == 0 or tile_coords[1] - 2 == 0:
            for key in self.templates["Edge Template 2"]:
                if self.check_validity(tile_coords, key, ["0", "0"]):
                    for x2, y2 in self.templates["Edge Template 2"][key]["Responses"]:
                        if x+x2 < 0 or y+y2 < 0:
                            continue
                        else:
                            self.update_ingame_info("Edge Template 2", tile_coords, (x2, y2), key)
                    break
                
    def check_validity(self, tile_coords: Tuple[int, int], to_check: Tuple[Tuple[int, int]], desired_result = List[str]) -> bool:
        """
        A helper function made for checking the validity of patterns by looping over the necessary requirements to be met for the
        pattern to exist.

        Args:
            tile_coords (Tuple[int, int]): Coordinates of tile checking.
            to_check (Tuple[Tuple[int, int]]): The tuple containing all the necessary coordinates for the pattern.
            desired_result (List[str]): A list containing all necessary results from coordinates in to_check for pattern to be met.

        Returns:
            bool: True if pattern is met, False otherwise.
        """
        x, y = tile_coords
        for i in range(len(to_check)):
            try:
                if self.board[x + to_check[i][0], y + to_check[i][1]] == desired_result[i]:
                    continue
                else:
                    return False
            except IndexError:
                return False
        return True
    
    def update_ingame_info(self, template_name: str, tile_coords: Tuple[int, int], intrusion_coords: Tuple[int, int], key: Tuple[Tuple[int, int]]) -> None:
        """
        A helper function dedicated to updating our filled in board (includes virtual tiles) and updates in_game dictionary with responses to certain moves,
        translated from relative positions to absolute positions on the board.

        Args:
            template_name (str): Name of template updating.
            tile_coords (Tuple[int, int]): Coordinates of tile checking.
            intrusion_coords (Tuple[int, int]): Coordinates where counters are required to play against.
            key (Tuple[Tuple[int, int]]): Key from template dictionary that includes all necessary positional coordinates for pattern. (Used here to access dictionary).
        """
        try:
            x, y = tile_coords
            x2, y2 = intrusion_coords
            if self.board[x,y] == self.colour:
                self.found_ingame[template_name]["Responses"][(x+x2, y+y2)] = ( self.templates[template_name][key]["Responses"][(x2, y2)][0] + x, self.templates[template_name][key]["Responses"][(x2, y2)][1] + y )
                self.responses[(x+x2, y+y2)] = self.found_ingame[template_name]["Responses"][(x+x2, y+y2)]
            self.filled_board[x + x2, y + y2] = self.board[x,y] + "*"
        except IndexError:
            return