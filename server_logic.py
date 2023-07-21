from typing import List, Dict
from scipy import spatial
import numpy as np
import time
import json
import asyncio
import pprint

"""
This file can be a nice home for your move logic, and to write helper functions.

We have started this for you, with a function to help remove the 'neck' direction
from the list of possible moves!
"""
pp = pprint.PrettyPrinter(indent=2)

def evaluate_board(board, my_snake_id):
    return 0
    # Evaluate the current board and return a score
    # based on the position of the snake and its health.
    my_snake = board["snakes"][my_snake_id]
    my_health = my_snake["health"]
    my_length = my_snake["length"]
    other_snakes = [snake for snake in board["snakes"] if snake["id"] != my_snake_id]

    # Reward for staying alive and having high health
    score = my_health + my_length

    # Penalize for colliding with walls or other snakes
    if my_snake["is_collided_wall"] or my_snake["is_collided_snake"]:
        score -= 1000

    # Penalize for being close to other snakes' heads to avoid collisions
    for snake in other_snakes:
        dist = abs(snake["head"]["x"] - my_snake["head"]["x"]) + abs(snake["head"]["y"] - my_snake["head"]["y"])
        if dist < 2:
            score -= 500

    return score

def current_milliseconds():
    return int(round(time.time() * 1000))
import asyncio

async def minimax(board, depth, my_snake_id, player_ids, maximizing_player, start_time, max_time_in_milliseconds):
    if await is_time_limit_exceeded(start_time, max_time_in_milliseconds):
        return 0  # Return a default value if the time limit is exceeded.

    if game_over(board, my_snake_id):
        return float("-inf")

    if depth == 0:
        return evaluate_board(board, my_snake_id)

    possible_moves = get_possible_moves(board, my_snake_id)

    if maximizing_player:
        max_eval = float("-inf")
        for my_move in possible_moves:
            new_board = get_next_board_state(board, my_snake_id, my_move)
            eval = await minimax(new_board, depth - 1, my_snake_id, player_ids, False, start_time, max_time_in_milliseconds)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float("inf")
        next_snake = player_ids[0]
        for opp_move in get_possible_moves(board, next_snake):
            new_board = get_next_board_state(board, next_snake, opp_move)
            for i in range(1, len(player_ids)):
                next_snake = player_ids[i]
                opp_move = get_possible_moves(new_board, next_snake)
                new_board = get_next_board_state(new_board, next_snake, opp_move)
            eval = await minimax(new_board, depth - 1, my_snake_id, player_ids, True, start_time, max_time_in_milliseconds)
            min_eval = min(min_eval, eval)
        return min_eval

async def is_time_limit_exceeded(start_time, max_time_in_milliseconds):
    current_time = current_milliseconds()
    return current_time - start_time >= max_time_in_milliseconds


# Function to get the next board state after making a move
def get_next_board_state(board_state, my_snake_id, move):
    # Create a deep copy of the board state to avoid modifying the original state
    next_board_state = json.loads(json.dumps(board_state))

    # Extract necessary information from the board_state
    snakes = board_state["snakes"]
    my_snake = get_snake(my_snake_id, snakes)
    # print(board_state)
    # print(my_snake)
    my_head_x, my_head_y = my_snake["head"]["x"], my_snake["head"]["y"]
    my_body = my_snake["body"]
    width, height = next_board_state["width"], next_board_state["height"]
    food = next_board_state["food"]

    # Move the snake based on the chosen direction
    if move == "left":
        my_head_x -= 1
    elif move == "right":
        my_head_x += 1
    elif move == "up":
        my_head_y -= 1
    elif move == "down":
        my_head_y += 1

    # Update the snake's body with the new head position
    my_body.insert(0, {"x": my_head_x, "y": my_head_y})

    # If the new head position coincides with food, keep the tail and don't pop it
    if {"x": my_head_x, "y": my_head_y} in food:
        # Remove the eaten food from the board
        next_board_state["food"] = [f for f in food if f != {"x": my_head_x, "y": my_head_y}]
    else:
        # If no food was eaten, remove the tail to simulate movement
        my_body.pop()

    # Update the head position for the snake
    # my_snake["x"] = my_head_x
    # my_snake["y"] = my_head_y
    
    for snake in next_board_state["snakes"]:
        if snake["id"] == my_snake_id:
            snake = my_snake

    return next_board_state

def game_over(board, snake_id):
    # Check if the game is over based on some specific conditions.
    # For example, you can check if there's only one snake remaining.

    # Get the number of alive snakes on the board
    other_snakes = [snake for snake in board["snakes"] if snake["id"] != snake_id]

    # If there's only one snake left, the game is over.
    if len(other_snakes) == 0:
        return True

    # Additional conditions can be added here based on your game's rules.
    # For example, you can check if a specific snake has reached a certain length,
    # or if the number of alive snakes falls below a certain threshold, etc.

    # If none of the specific conditions are met, the game is not over yet.
    return False

async def get_best_move(board, my_snake_id, depth, max_time_in_milliseconds):
    best_move = None
    best_eval = float("-inf")
    start_time = current_milliseconds()
    other_snakes_ids = [snake["id"] for snake in board["snakes"] if snake["id"] != my_snake_id]


    for move in get_possible_moves(board, my_snake_id):
        new_board = get_next_board_state(board, my_snake_id, move)
        eval = await minimax(new_board, depth - 1, my_snake_id, other_snakes_ids, False, start_time, max_time_in_milliseconds)
        if eval > best_eval:
            best_eval = eval
            best_move = move

    return best_move

def avoid_my_body(my_head, my_body, possible_moves):
    """
    my_body: List of dictionaries of x/y coordinates for every segment of a Battlesnake.
            e.g. [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]
    possible_moves: List of strings. Moves to pick from.
            e.g. {"up": {0,1}, "down":{0,1}, "left":{0,1}, "right":{0,1}}

    return: The list of remaining possible_moves
    """

    remove = []
    for direction in possible_moves:
        location = get_location(direction, my_head)
        if location in my_body:
            remove.append(direction)

    for direction in remove:
        possible_moves.remove(direction)

    return possible_moves

def avoid_snakes(my_head, snakes, possible_moves):
    """
    snakes: List of dictionaries of Snakes
    possible_moves: List of strings. Moves to pick from.
            e.g. {"up": {0,1}, "down":{0,1}, "left":{0,1}, "right":{0,1}}

    return: The list of remaining possible_moves
    """
    remove = []
    for snake in snakes:
        for direction in possible_moves:
            location = get_location(direction, my_head)
            if location in snake["body"]:
                remove.append(direction)
    
    for direction in remove:
        possible_moves.remove(direction)
    
    return possible_moves

def avoid_walls(my_head, board_width: Dict[str, int], board_height: List[dict], possible_moves: List[str]) -> List[str]:
    remove = []

    for direction in possible_moves:
        location = get_location(direction, my_head)
        x_out_range = (location["x"] < 0 or location["x"] == board_width)
        y_out_range = (location["y"] < 0 or location["y"] == board_height)
        if x_out_range or y_out_range:
            remove.append(direction)

    for direction in remove:
        possible_moves.remove(direction)

    return possible_moves

def get_snake(snake_id, snakes):
    for snake in snakes:
        if snake["id"] == snake_id:
            return snake

def get_possible_moves(board, my_snake_id):
    board_height = board["height"]
    board_width = board["width"]
    snakes = board["snakes"]
    
    my_snake = get_snake(my_snake_id, snakes)
    my_head = my_snake["head"]
    my_body = my_snake["body"]  # A list of x/y coordinate dictionaries like [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]

    possible_moves = ["up", "down", "left", "right"]
    possible_moves = avoid_my_body(my_head, my_body, possible_moves)
    possible_moves = avoid_walls(my_head, board_width, board_height, possible_moves)
    possible_moves = avoid_snakes(my_head, snakes, possible_moves)
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

    for direction in possible_moves:
        location = get_location(direction, my_head)
        new_distance_x = abs(location["x"] - target["x"])
        new_distance_y = abs(location["y"] - target["y"])
        if new_distance_x < distance_x or new_distance_y < distance_y:
            return direction
    
    return list(possible_moves.keys())[0]

def get_location(move, my_head):
    location = {}
    location["x"] = my_head["x"]
    location["y"] = my_head["y"]
    if move == "up":
        location["y"] += 1
    elif move == "down":
        location["y"] -= 1
    elif move == "left":
        location["x"] -= 1
    elif move == "right":
        location["x"] += 1
    return location

async def choose_move(data: dict) -> str:
    """
    Random move but doesn't hit walls.

    """
    my_snake_id = data["you"]["id"]
    my_head = data["you"]["head"]  # A dictionary of x/y coordinates like {"x": 0, "y": 0}
    my_body = data["you"]["body"]  # A list of x/y coordinate dictionaries like [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]

    # pp.pprint(data)
    game = data.get("game")
    ruleset = game.get("ruleset", {})
    settings = ruleset.get("settings", {})
    foodSpawnChance = settings.get("foodSpawnChance")
    timeout = game["timeout"]

    # print(foodSpawnChance, timeout)
    possible_moves = get_possible_moves(data["board"], my_snake_id)
    
    # TODO: uncomment the lines below so you can see what this data looks like in your output!
    # print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    # print(f"All board data this turn: {data}")
    # print(f"My Battlesnakes head this turn is: {my_head}")
    # print(f"My Battlesnakes body this turn is: {my_body}")

    foods = data["board"]["food"]
    target = get_target_close(foods, my_head)

    # # Example usage:
    # # board = YourGameBoard()  # Initialize your game board
    # # my_snake_id = "your_snake_id"  # Your snake's ID
    # # depth = 4  # Set the depth of the search (higher depth for deeper search, but more computation time)
    # # best_move = get_best_move(board, my_snake_id, depth)
    # # Make the best move on the actual board: board.make_move(my_snake_id, best_move)

    move = await get_best_move(data["board"], my_snake_id, 3, 450)
    # if len(possible_moves) > 0:
    #     if target is not None:
    #         move = move_target(possible_moves, my_head, target)
    #     else:
    #         possible_moves = list(possible_moves.keys())
    #         move = random.choice(possible_moves)
    # else:
    #     print("We F'ed up")
    #     move = "down"
    pp.pprint(data["board"]["snakes"])
    pp.pprint(data["you"])
    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")

    return move