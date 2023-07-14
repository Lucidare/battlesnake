import random
from typing import List, Dict
from scipy import spatial
import pprint

"""
This file can be a nice home for your move logic, and to write helper functions.

We have started this for you, with a function to help remove the 'neck' direction
from the list of possible moves!
"""
pp = pprint.PrettyPrinter(indent=2)

def avoid_my_body(my_body, possible_moves):
    """
    my_body: List of dictionaries of x/y coordinates for every segment of a Battlesnake.
            e.g. [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]
    possible_moves: List of strings. Moves to pick from.
            e.g. {"up": {0,1}, "down":{0,1}, "left":{0,1}, "right":{0,1}}

    return: The list of remaining possible_moves
    """

    remove = []
    for direction, location in possible_moves.items():
        if location in my_body:
            remove.append(direction)

    for direction in remove:
        del possible_moves[direction]

    return possible_moves

def avoid_snakes(snakes, possible_moves):
    """
    snakes: List of dictionaries of Snakes
    possible_moves: List of strings. Moves to pick from.
            e.g. {"up": {0,1}, "down":{0,1}, "left":{0,1}, "right":{0,1}}

    return: The list of remaining possible_moves
    """
    remove = []
    for snake in snakes:
        for direction, location in possible_moves.items():
            if location in snake["body"]:
                remove.append(direction)
    
    for direction in remove:
        del possible_moves[direction]
    
    return possible_moves

def avoid_walls(board_width: Dict[str, int], board_height: List[dict], possible_moves: List[str]) -> List[str]:
    remove = []

    for direction, location in possible_moves.items():
        x_out_range = (location["x"] < 0 or location["x"] == board_width)
        y_out_range = (location["y"] < 0 or location["y"] == board_height)
        if x_out_range or y_out_range:
            remove.append(direction)

    for direction in remove:
        del possible_moves[direction]

    return possible_moves

def get_target_close(foods, my_head):
    coordinates = []
    if len(foods) == 0:
        return None
    for food in foods:
        coordinates.append( (food["x"], food["y"]) )

    tree = spatial.KDTree(coordinates)
    results = tree.query([(my_head["x"], my_head["y"])])[1]
    return foods[results[0]]

def move_target(possible_moves, my_head, target):
    distance_x = abs(my_head["x"] - target["x"])
    distance_y = abs(my_head["y"] - target["y"])

    for direction, location in possible_moves.items():
        new_distance_x = abs(location["x"] - target["x"])
        new_distance_y = abs(location["y"] - target["y"])
        if new_distance_x < distance_x or new_distance_y < distance_y:
            return direction
    
    return list(possible_moves.keys())[0]

def choose_move(data: dict) -> str:
    """
    Random move but doesn't hit walls.

    """
    my_head = data["you"]["head"]  # A dictionary of x/y coordinates like {"x": 0, "y": 0}
    my_body = data["you"]["body"]  # A list of x/y coordinate dictionaries like [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]

    # pp.pprint(data)
    game = data.get("game")
    ruleset = game.get("ruleset", {})
    settings = ruleset.get("settings", {})
    foodSpawnChance = settings.get("foodSpawnChance")
    timeout = game["timeout"]

    # print(foodSpawnChance, timeout)
    
    
    # TODO: uncomment the lines below so you can see what this data looks like in your output!
    # print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    # print(f"All board data this turn: {data}")
    # print(f"My Battlesnakes head this turn is: {my_head}")
    # print(f"My Battlesnakes body this turn is: {my_body}")

    possible_moves = {
        "up": {
            "x": my_head["x"], 
            "y": my_head["y"] + 1
        }, 
        "down": {
            "x": my_head["x"], 
            "y":my_head["y"] - 1
        }, 
        "left": {
            "x": my_head["x"] - 1, 
            "y":my_head["y"]
        }, 
        "right": {
            "x": my_head["x"] + 1, 
            "y":my_head["y"]
        }, 
    }

    # Don't allow your Battlesnake to move back in on it's own neck
    possible_moves = avoid_my_body(my_body, possible_moves)

    # TODO: Using information from 'data', find the edges of the board and don't let your Battlesnake move beyond them
    board_height = data["board"]["height"]
    board_width = data["board"]["width"]
    foods = data["board"]["food"]
    snakes = data["board"]["snakes"]

    possible_moves = avoid_walls(board_width, board_height, possible_moves)


    possible_moves = avoid_snakes(snakes, possible_moves)

    target = get_target_close(foods, my_head)

    if len(possible_moves) > 0:
        if target is not None:
            move = move_target(possible_moves, my_head, target)
        else:
            possible_moves = list(possible_moves.keys())
            move = random.choice(possible_moves)
    else:
        print("We F'ed up")
        move = "down"

    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")

    return move