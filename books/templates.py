# I did letter first followed by number, based on this website http://www.lutanho.net/play/hex.html

templates = {
    
    "Bottleneck": {
        
        """
            When checking for bottleneck, we check for the following tuple:
                ( (x, y), (x2, y2), (x3, y3), (x4, y4), (x5, y5) )
            Where:
                ( (Relative to player on edge position empty tile), (Relative to player on edge position empty tile), (Players own other tile relative to the first),
                    (Player's own other tile relative to the first), (Enemy's tile relative to the first) )
            We return tiles to mark as owned intrusion tiles.
        """
        
            # Blue defending
            ( (0, -1), (1, -1), (0, -2), (2, -2), (1, -2) ): {
                
                "Intrusions": ( (0, -1), (1, -1), (-1, 0), (1, 0), (2, -1), (-1, -1) ),
                "Responses": {
                    # Intrusion Tile    # Response
                    (0, -1):            (-1, 0),
                    (1, -1):            (1, 0),
                    (-1, 0):            (0, -1),
                    (1, 0):             (1, -1),
                    (-1, -1):           (0, -1)
                }
            },
            
            ( (0, 1), (-1, 1), (-2, 2), (0, 2), (-1, 2) ): {
            
                "Intrusions": ( (0, 1), (-1, 1), (1, 0), (-1, 0), (1, 1), (-2, 1) ),
                "Responses": {
                    # Intrusion Tile    # Response
                    (0, 1):             (1, 0),
                    (-1, 1):            (-1, 0),
                    (1, 0):             (0, 1),
                    (-1, 0):            (-1, 1),
                    (1, 1):             (0, 1),
                    (-2, 1):            (-1, 1)
                }
            },
        
            # Red defending
            ( (-1, 1), (-1, 0), (-2, 0), (-2, 2), (-1, 1) ):{
                
                "Intrusions": ( (-1, 1), (-1, 0), (0, 1), (0, -1), (-1, -1), (-1, 2) ),
                "Responses": {
                    # Intrusion Tile    # Response
                    (-1, 1):            (0, 1),
                    (-1, 0):            (0, -1),
                    (0, 1):             (-1, 1),
                    (0, -1):            (0, 1),
                    (-1, -1):           (-1, 0),
                    (-1, 2):            (-1, 1)
                }
            },
            
            ( (1, 0), (1, -1), (2, 0), (2, -2), (2, -1) ): {
                "Intrusions": ( (0, 1), (1, 1), (1, 0), (1, -1), (1, -2), (0, -1) ),
                "Responses": {
                        # Intrusion Tile    # Response
                        (0, 1):             (1, 0),
                        (1, 1):             (1, 0),
                        (1, 0):             (0, 1),
                        (1, -1):            (0, -1),
                        (1, -2):            (1, -1), 
                        (0, -1):            (1, -1)
                }
            }
        },
    
    # Remember to check that edge templates are only checked if tile is on edge.
    # Remember to check that player only plays his own counters. I should only add the player's counters to the counter list.
    "Edge Template 31b": {
        ( (0, -1), (0, 1), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-2, -1), (-2, 0), (-2, 2), (-2, 3) ): {
            "Intrusions": ( (0, -1), (0, 1), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-2, -1), (-2, 0), (-2, 2), (-2, 3) ),
            "Responses": {
                # Intrusion Tile    # Response
                (0, -1):            (-1, 2),
                (0, 1):             (-1, -1),
                (-1, -1):           (-1, 2),
                (-1, 0):            (-1, 2),
                (-1, 1):            (-1, -1),
                (-1, 2):            (-1, -1),
                (-2, -1):           (-1, 2),
                (-2, 0):            (-1, 2),
                (-2, 2):            (-1, -1),
                (-2, 3):            (-1, -1)
            }
        },
        
        ( (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1), (2, -1), (-1, -2), (0, -2), (2, -2), (3, -2) ): {
            "Intrusions": ( (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1), (2, -1), (-1, -2), (0, -2), (2, -2), (3, -2) ),
            "Responses": {
                # Intrusion Tile    # Response
                (-1, 0):            (2, -1),
                (1, 0):             (-1, -1),
                (-1, -1):           (2, -1),
                (0, -1):            (2, -1), 
                (1, -1):            (-1, -1),
                (2, -1):            (-1, -1),
                (-1, -2):           (2, -1),
                (0, -2):            (2, -1),
                (2, -2):            (-1, -1),
                (3, -2):            (-1, -1)
            }
        },
        
        ( (-1, 0), (1, 0), (-2, 1), (-1, 1), (0, 1), (1, 1), (-3, 2), (-2, 2), (0, 2), (1, 2) ): {
            "Intrusions": ( (-1, 0), (1, 0), (-2, 1), (-1, 1), (0, 1), (1, 1), (-3, 2), (-2, 2), (0, 2), (1, 2) ),
            "Responses": {
                # Intrusion Tile    # Response
                (-1, 0):            (1, 1),
                (1, 0):             (-2, 1), 
                (-2, 1):            (1, 1),
                (-1, 1):            (1, 1),
                (0, 1):             (-2, 1),
                (1, 1):             (-2, 1),
                (-3, 2):            (1, 1),
                (-2, 2):            (1, 1),
                (0, 2):             (-2, 1),
                (1, 2):             (-2, 1)
            }
        },
        
        ( (0, -1), (0, 1), (1, -2), (1, -1), (1, 0), (1, 1), (2, -3), (2, -2), (2, 0), (2, 1) ): {
            "Intrusions": ( (0, -1), (0, 1), (1, -2), (1, -1), (1, 0), (1, 1), (2, -3), (2, -2), (2, 0), (2, 1) ),
            "Responses": {
                # Intrusion Tile    # Response
                (0, -1):            (1, 1),
                (0, 1):             (1, -2),
                (1, -2):            (1, 1), 
                (1, -1):            (1, 1),
                (1, 0):             (1, -2),
                (1, 1):             (1, -2),
                (2, -3):            (1, 1),
                (2, -2):            (1, 1),
                (2, 0):             (1, -2),
                (2, 1):             (1, -2)
            }
        },
        
    },
    
    "Edge Template 2": {
        ( (-1, 0), (-1, 1) ): {
            "Intrusions": ( (-1, 0), (-1, 1) ),
            "Responses": {
                # Intrusion Tile    # Response
                (-1, 0):            (-1, 1),
                (-1, 1):            (-1, 0)
            }
        },
        
        ( (0, -1), (1, -1) ): {
            "Intrusions": ( (0, -1), (1, -1) ),
            "Responses": {
                # Intrusion Tile    # Response
                (0, 1):             (1, -1),
                (1, -1):            (0, 1),
            }
        }, 
        
        ( (-1, 1), (0, 1) ): {
            "Intrusions": ( (-1, 1), (0, 1) ),
            "Responses": {
                # Intrusion Tile    # Response
                (-1, 1):            (0, 1),
                (0, 1):             (-1, 1)
            }
        },
        
        ( (1, -1), (1, 0) ): {
            "Intrusions": ( (1, -1), (1, 0) ),
            "Responses": {
                # Intrusion Tile    # Response
                (1, -1):            (1, 0),
                (1, 0):             (1, -1)
            }
        }
    },
    # Update like the rest in terms of formatting.
    "Connections": {
        
        """
            When checking for connections, we check for the following tuple:
                ( (x, y), (x2, y2), (x3, y3) )
            Where:
                ( (Relative to player position's empty tile), (Relative to player position's empty tile), (Players own other tiles) )
        """
        
        ( (-1, 0), (0, -1), (-1, -1) ): {
            "Intrusions": ( (-1, 0), (0, -1) ),
            "Responses": {
                # Intrusion Tile     # Response
                (-1, 0):             (0, -1),
                (0, -1):             (-1, 0)
            }
        },
        
        ( (1, -1), (0, -1), (1, -2) ): {
            "Intrusions": ( (1, -1), (0, -1) ),
            "Responses": {
                # Intrusion Tile     # Response
                (1, -1):             (0, -1),
                (0, -1):             (1, -1)
            }
        },
        
        ( (1, -1), (1, 0), (2, -1) ): {
            "Intrusions": ( (1, -1), (1, 0) ),
            "Responses": {
                # Intrusion Tile     # Response
                (1, -1):             (1, 0),
                (1, 0):              (1, -1)
            }
        },
        
        ( (1, 0), (0, 1), (1, 1) ): {
            "Intrusions": ( (1, 0), (0, 1) ),
            "Responses": {
                # Intrusion Tile     # Response
                (1, 0):             (0, 1),
                (0, 1):             (1, 0)
            }
        },
        
        ( (-1, 1), (0, 1), (-1, 2) ): {
            "Intrusions": ( (-1, 1), (0, 1) ),
            "Responses": {
                # Intrusion Tile     # Response
                (-1, 1):             (0, 1),
                (0, 1):              (-1, 1)
            }
        },
        
        ( (-1, 1), (-1, 0), (-2, 1) ): {
            "Intrusions": ( (-1, 1), (-1, 0) ),
            "Responses": {
                # Intrusion Tile     # Response
                (-1, 1):             (-1, 0),
                (-1, 0):             (-1, 1)
            }
        }   
    }  
}   