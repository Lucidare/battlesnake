import argparse
import os
import signal
import subprocess
import time

def cleanup_containers(signum, frame, branch_list):
    print("\nCleaning up and stopping containers...")
    for container in branch_list:
        stop_and_remove_container(container)
    exit(0)

def build_docker_image(branch):
    subprocess.run(["docker", "build", "-t", f"myapp:{branch}", "."], check=True)

def run_docker_container(branch, container_name, host_port, container_port=8000):
    # Pass the environment variable APP_BRANCH with the desired branch value
    subprocess.Popen(
        ["docker", "run", "-d", "--name", container_name, "-e", f"APP_BRANCH={branch}", "-p", f"{host_port}:{container_port}", f"myapp:{branch}"],
        stdout=subprocess.DEVNULL
    )

def stop_and_remove_container(container_name):
    try:
        # Check if the container exists
        subprocess.run(["docker", "inspect", container_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        # Container does not exist, no need to stop and remove
        return

    # Stop the container
    subprocess.run(["docker", "stop", container_name], stdout=subprocess.DEVNULL)

    # Remove the container
    subprocess.run(["docker", "rm", container_name], stdout=subprocess.DEVNULL)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('branches', nargs='+', help='Names of the branches')
    args = parser.parse_args()

    # Convert the 'branches' attribute from the Namespace object to a list
    branch_list = args.branches

    print(f"Setting up branches {branch_list}")

    # Now you have the list of branches
    # Host ports starting at 8000
    host_port = 8000
    for branch in branch_list:
        # Check and remove containers if they already exist
        stop_and_remove_container(branch)

        # Build the Docker images
        build_docker_image(branch)

        # Run the containers
        run_docker_container(branch, branch, host_port)
        host_port += 1

    # Wait indefinitely, handling Ctrl+C
    signal.signal(signal.SIGINT, lambda signum, frame: cleanup_containers(signum, frame, branch_list))
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
