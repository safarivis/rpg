import json
import os
from typing import Dict, List, Optional

# Story scenarios define the main plot points and their requirements
STORY_SCENARIOS = [
    {
        "id": "intro",
        "title": "Welcome to Neo-Tokyo",
        "description": "Your first day in the sprawling cyberpunk metropolis.",
        "requirements": [],
        "next_scenarios": ["mysterious_signal", "local_trouble"]
    },
    {
        "id": "mysterious_signal",
        "title": "The Mysterious Signal",
        "description": "A strange signal leads you to an abandoned research facility.",
        "requirements": ["intro"],
        "next_scenarios": ["ai_awakening", "corporate_intrigue"]
    },
    {
        "id": "local_trouble",
        "title": "Local Trouble",
        "description": "The local neighborhood is being harassed by a gang of rogue combat droids.",
        "requirements": ["intro"],
        "next_scenarios": ["gang_war", "corporate_intrigue"]
    },
    {
        "id": "ai_awakening",
        "title": "AI Awakening",
        "description": "You discover a dormant artificial intelligence in the facility.",
        "requirements": ["mysterious_signal"],
        "next_scenarios": ["final_confrontation"]
    },
    {
        "id": "corporate_intrigue",
        "title": "Corporate Intrigue",
        "description": "A megacorporation seems to be behind recent events.",
        "requirements": ["mysterious_signal", "local_trouble"],
        "next_scenarios": ["final_confrontation"]
    },
    {
        "id": "gang_war",
        "title": "Gang War",
        "description": "The situation escalates as multiple factions vie for control.",
        "requirements": ["local_trouble"],
        "next_scenarios": ["final_confrontation"]
    },
    {
        "id": "final_confrontation",
        "title": "Final Confrontation",
        "description": "All paths lead to a climactic showdown.",
        "requirements": ["ai_awakening", "corporate_intrigue", "gang_war"],
        "next_scenarios": []
    }
]

def load_game_state() -> Optional[Dict]:
    """Load the game state from file."""
    try:
        with open("game_state.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_game_state(game_state: Dict) -> None:
    """Save the game state to file."""
    with open("game_state.json", "w") as f:
        json.dump(game_state, f)

def get_next_available_scenario() -> Optional[Dict]:
    """Get the next available scenario based on completed scenarios."""
    game_state = load_game_state()
    if not game_state:
        # Start with intro if no game state
        return next(s for s in STORY_SCENARIOS if s["id"] == "intro")
    
    completed = set(game_state["completed_scenarios"])
    
    # Find scenarios where all requirements are met
    available_scenarios = [
        s for s in STORY_SCENARIOS
        if s["id"] not in completed and
        all(req in completed for req in s["requirements"])
    ]
    
    return available_scenarios[0] if available_scenarios else None

def generate_story_event(scenario: Dict, player: Dict) -> Dict:
    """Generate an event based on the current scenario."""
    if "signal" in scenario["id"]:
        return {
            "type": "investigation",
            "description": scenario["description"],
            "choices": [
                "Investigate carefully",
                "Rush in",
                "Look for alternative entrance"
            ],
            "scenario_id": scenario["id"]
        }
    elif "trouble" in scenario["id"] or "war" in scenario["id"]:
        return {
            "type": "combat",
            "description": scenario["description"],
            "opponent": {
                "name": "Rogue Combat Droid",
                "level": player["level"],
                "abilities": ["Laser Strike", "Shield Generator", "Missile Barrage"]
            },
            "scenario_id": scenario["id"]
        }
    else:
        return {
            "type": "dialogue",
            "description": scenario["description"],
            "choices": [
                "Gather information",
                "Take action",
                "Call for backup"
            ],
            "scenario_id": scenario["id"]
        }

def mark_scenario_complete(scenario_id: str) -> None:
    """Mark a scenario as complete in the game state."""
    game_state = load_game_state()
    if not game_state:
        game_state = {"completed_scenarios": [], "current_scenario": None}
    
    if scenario_id not in game_state["completed_scenarios"]:
        game_state["completed_scenarios"].append(scenario_id)
    
    game_state["current_scenario"] = None
    save_game_state(game_state)
