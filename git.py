

import subprocess

def switch_git_branch(branch_name):
    try:
        # Check if the branch exists
        subprocess.run(['git', 'rev-parse', '--verify', branch_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print(f"Error: Branch '{branch_name}' does not exist.")
        return False

    # Checkout the specified branch
    subprocess.run(['git', 'checkout', branch_name], check=True)

    print(f"Switched to branch '{branch_name}'.")
    return True

def git_stash():
    try:
        # Stash changes using the 'git stash' command
        subprocess.run(['git', 'stash'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        # Handle any errors during the stash operation
        print(f"Error: {e.stderr.decode().strip()}")
        return False

    print("Changes successfully stashed.")
    return True
