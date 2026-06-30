import json

def read_game_state():
    """Opens the notebook (world_state.json) and reads the player's info."""
    with open("world_state.json", "r") as file:
        return json.load(file)

def update_game_state(new_state):
    """Opens the notebook (world_state.json) and saves new changes into it."""
    with open("world_state.json", "r+") as file: # "r+" lets us read and write safely
        file.seek(0)                             # Move to the very beginning of the file
        json.dump(new_state, file, indent=2)
        file.truncate()                          # Erase any leftover text from before!