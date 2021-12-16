openings = {
    # We are player one.
    1: {
        # Opening move is B2 if we start.
        "Move": (1,1),
        "Responses": {
            # Enemy Move        # Response
            (5,5):              (8,7),
            (6,4):              (8,7),
            (4,6):              (8,7),
            (5,4):              (8,7),
            (4,5):              (8,7),
            (5,6):              (8,7),
            (6,5):              (8,7)
        }
    },
    
    # We are player two.
    2: {
        "Move": (5,5)
    }    
    
}