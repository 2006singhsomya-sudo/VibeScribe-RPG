import streamlit as str  # Standard alias for Streamlit
import os
import sys

# Ensure Python looks directly in this folder for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools import read_game_state
import agent  # Import the agent module directly!

# 1. Page Configuration
str.set_page_config(page_title="VibeScribe RPG", page_icon="⚔️", layout="wide")

# 2. Inject Custom RPG Styling (Dark Theme & Text Styling)
str.markdown(
    """
    <style>
    /* Main Background and text adjustments */
    .stApp {
        background-color: #0f1115;
        color: #e0e6ed;
    }
    
    /* Style the main title */
    h1 {
        color: #ffb300 !important;
        font-family: 'Georgia', serif;
        text-shadow: 2px 2px 4px #000000;
    }
    
    /* Make the story history container look premium */
    .stAlert {
        background-color: #1a1d24 !important;
        border: 1px solid #3b4252 !important;
        border-radius: 10px;
    }
    
    /* Style the custom story blocks */
    .story-card {
        background-color: #161920;
        padding: 20px;
        border-left: 4px solid #ffb300;
        border-radius: 5px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .action-text {
        color: #00ffd5;
        font-weight: bold;
        font-family: 'Courier New', monospace;
    }
    .narrative-text {
        font-family: 'Georgia', serif;
        font-size: 1.15rem;
        line-height: 1.6;
        color: #d8dee9;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Initialize Visual Session Memory
if "story_history" not in str.session_state:
    str.session_state.story_history = [
        {"action": "Game Started", "narrative": "The heavy oak door thuds softly shut behind you, leaving the tempest outside. You stand inside the tavern..."}
    ]

# Read fresh world data
current_state = read_game_state()
player = current_state["player"]
world = current_state["world"]

# 4. SIDEBAR: The Character Dashboard
with str.sidebar:
    str.markdown("<h2 style='color: #ffb300; font-family: Georgia;'>👤 Character</h2>", unsafe_allow_html=True)
    str.markdown(f"### **{player['name']}**")
    str.markdown(f"🧭 **Location:** `{player['location'].replace('_', ' ').title()}`")
    
    str.markdown("---")
    
    # Custom Styled Health Metrics
    health_pct = max(0.0, min(1.0, player["health"] / player["max_health"]))
    str.markdown(f"❤️ **Health:** `{player['health']} / {player['max_health']}`")
    str.progress(health_pct)
    
    str.markdown("---")
    str.markdown("<h3 style='color: #ffb300;'>🎒 Inventory</h3>", unsafe_allow_html=True)
    if player["inventory"]:
        for item in player["inventory"]:
            str.markdown(f"✨ `{item.title()}`")
    else:
        str.write("*Your pockets are empty.*")

# 5. MAIN INTERFACE: The Chronicles
str.markdown("<h1>🔮 VibeScribe Chronicles</h1>", unsafe_allow_html=True)
str.caption("Multi-Agent AI Engine • Powered by Gemini 2.5 Flash")

str.markdown("### 📜 The Story So Far")

# Display stories in custom HTML cards inside the container
story_container = str.container(height=450, border=True)
with story_container:
    for block in str.session_state.story_history:
        str.markdown(
            f"""
            <div class="story-card">
                <div class="action-text">> {block['action']}</div>
                <div class="narrative-text">{block['narrative']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

# 6. INPUT: The Action Bar
player_input = str.chat_input("What do you want to do next, Somya?")

if player_input:
    with str.spinner("The Loom of Fate spins..."):
        # Run action through engine (using the direct agent module reference)
        new_narrative = agent.engine.play_turn(player_input)
        
        # Save structured layout
        str.session_state.story_history.append({
            "action": player_input,
            "narrative": new_narrative
        })
        
        str.rerun()