# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import typing
import server_logic
import argparse

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Lucid Snake",
        "color": "#888888",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
async def move(game_state: typing.Dict) -> typing.Dict:
    next_move = await server_logic.choose_move(game_state)
    return {"move": next_move}


# Start server when `python main.py` is run
# python your_battlesnake_server.py --port 8001
# If you don't specify the --port argument, the server will default to port 8000.
if __name__ == "__main__":
    from server import run_server
    import os

    # Get the value of the 'APP_BRANCH' environment variable
    branch_name = os.environ.get('APP_BRANCH')

    # Check if the variable exists and use its value
    if branch_name is not None:
        print(f"APP_BRANCH environment variable is set to: {branch_name}")
    else:
        print("APP_BRANCH environment variable is not set.")
        exit(1)

    import subprocess
    from git import git_stash, switch_git_branch
    
    # if using main branch, keep local changes
    if branch_name != "lucid-snake":
        git_stash()
    else:
        print("Skipping stash, using local")
    switch_git_branch(branch_name)
    
    parser = argparse.ArgumentParser(description="Battlesnake server")
    parser.add_argument("--port", type=int, default=8000, help="Port number for the Battlesnake server")
    args = parser.parse_args()

    handlers = {
        "info": info,
        "start": start,
        "move": move,
        "end": end,
    }
    run_server(handlers, args.port)
