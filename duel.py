import subprocess
import matplotlib.pyplot as plt

def run_duel(name1="snake1", url1="http://localhost:8000", name2="snake2", url2="http://localhost:8001", games=100):
    num_games = games  # Number of games to play

    snake1_wins = 0
    snake2_wins = 0
    draws = 0

    for _ in range(num_games):
        result = subprocess.run(
            [
                "battlesnake",
                "play",
                "-W",
                "11",
                "-H",
                "11",
                "--name",
                name1,
                "--url",
                url1,
                "--name",
                name2,
                "--url",
                url2,
                "-g",
                "duel",
            ],
            capture_output=True,
            text=True,
        )

        output = result.stderr.splitlines()
        last_line = output[-1]

        # Check the output to determine the winner
        if name1 in last_line:
            snake1_wins += 1
        elif name2 in last_line:
            snake2_wins += 1
        else:
            draws += 1

    print(f"{name1} wins: {snake1_wins}")
    print(f"{name2} wins: {snake2_wins}")
    print(f"draws: {draws}")


    # Visualize the results as a single stacked bar
    snakes = [name1, name2, "Draws"]
    wins = [snake1_wins, snake2_wins, draws]

    plt.barh(name1 + " vs " +  name2, snake1_wins, color="g")
    plt.barh(name1 + " vs " +  name2, draws, left=snake1_wins, color="gray")
    plt.barh(name1 + " vs " +  name2, snake2_wins, left=snake1_wins+draws, color="r")
    plt.title("Battlesnake Duel Results")
    plt.show()

if __name__ == "__main__":
    run_duel(name1="Lucidare1", url1="http://localhost:8000", name2="Lucidare2", url2="http://localhost:8001", games=100)

