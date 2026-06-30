import sys
import os
import json
from google import genai
from dotenv import load_dotenv

# 1. Fix paths and import our data tools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.tools import read_game_state, update_game_state

# 2. Load API Key configuration
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

class VibeScribeEngine:
    def __init__(self):
        self.client = genai.Client(api_key=api_key)
        self.rules_model = "gemini-2.5-flash"
        self.story_model = "gemini-2.5-flash"

    def play_turn(self, player_action):
        # Read current state from world_state.json
        current_state = read_game_state()

        # STEP A: Ask the Rules Lawyer to calculate changes and return them as JSON instructions
        # STEP A: Create a strict prompt for the Rules Lawyer
        rules_prompt = f"""
        You are a rigid RPG mechanics engine. Look at the current world state and the player's action.
        Calculate what changes. If they use an item, verify it's in their inventory and remove it.
        
        CURRENT STATE: {json.dumps(current_state)}
        PLAYER ACTION: "{player_action}"
        
        You must respond ONLY with a valid JSON object containing these keys:
        1. "player_changes": A dictionary of fields to update inside the player state (e.g., {{"health": 18}}).
        2. "world_changes": A dictionary of fields to update inside the world state if they move or change the room (e.g., {{"current_room_description": "A cozy tavern room."}}).
        3. "summary": A brief text summary of what mechanically happened.
        
        Rules for world_changes:
        - Only include "world_changes" if the action successfully moves them to a new area or alters the room.
        - If they change locations, update "current_room_description" with a vivid description of the new setting.
        """
        
        
        print("\n[Rules Lawyer is calculating mechanics...]")
        rules_response = self.client.models.generate_content(
            model=self.rules_model,
            contents=rules_prompt,
            # We enforce that the AI must reply in clean JSON format
            config={"response_mime_type": "application/json"}
        )
        
        # Parse the AI's response into a Python dictionary
        mechanics = json.loads(rules_response.text)
        print(f"-> Mechanics Determined: {mechanics['summary']}")

        # 🔍 Add this line right here:
        print(f"\n[DEBUG] Raw data from Gemini: {mechanics}\n")

        # STEP B: Apply the AI's requested changes directly to our notebook!
        if "player_changes" in mechanics:
            for key, value in mechanics["player_changes"].items():
                current_state["player"][key] = value

        # 🔍 ADD THESE 3 LINES RIGHT HERE:
        if "world_changes" in mechanics:
            for key, value in mechanics["world_changes"].items():
                current_state["world"][key] = value
            
        # Save the updated notebook back to disk
        update_game_state(current_state)
        print("-> world_state.json successfully updated live!")

        # STEP C: Hand everything over to the Narrative Weaver to write the story
        story_prompt = f"""
        You are an immersive fantasy Dungeon Master. Take the raw mechanical outcomes from the rules engine
        and translate them into a vibrant, atmosphere-heavy story block for the player.
        
        MECHANICAL OUTCOME: {mechanics['summary']}
        NEW STATE: {current_state}
        """
        
        print("[Narrative Weaver is crafting your story...]")
        story_response = self.client.models.generate_content(
            model=self.story_model,
            contents=story_prompt,
        )
        
        return story_response.text

# Initialize our engine instance
engine = VibeScribeEngine()

if __name__ == "__main__":
    print("====================================================")
    print("--- VibeScribe Multi-Agent RPG Engine Live ---")
    print("       (Type 'quit' or 'exit' to end the game)      ")
    print("====================================================")
    
    # Read the initial state to welcome the player
    initial_state = read_game_state()
    print(f"\nWelcome back, {initial_state['player']['name']}!")
    print(f"Current Location: {initial_state['world']['current_room_description']}")
    print(f"Health: {initial_state['player']['health']}/{initial_state['player']['max_health']}")
    print(f"Inventory: {initial_state['player']['inventory']}")
    print("-" * 50)

    # The Continuous Loop
    while True:
        # Get live text input from you in the terminal
        player_action = input("\nWhat do you want to do? > ")
        
        # Check if the player wants to stop playing
        if player_action.lower() in ["quit", "exit"]:
            print("\nSaving world state... Thanks for playing!")
            break
            
        # Skip empty inputs
        if not player_action.strip():
            continue

        try:
            # Run the multi-agent turn processing
            story_output = engine.play_turn(player_action)
            
            # Print the beautiful story block from the Narrative Weaver
            print("\n=== STORY ===")
            print(story_output)
            print("=============")
            
        except Exception as e:
            print(f"\n[Engine Error]: {e}. Let's try another action.")