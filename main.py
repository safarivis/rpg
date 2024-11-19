from player import (
    load_player_data,
    default_player,
    save_player_data,
    update_personality,
)
from world_building import generate_world_prompt
from npc_generation import generate_npc
from events import generate_starting_conflict, generate_random_event
from character_creation import character_creation
from utilities import get_valid_input


def display_player_summary(player):
    """Display a summary of the player's current state."""
    print("\nCharacter Summary:")
    print(f"Name: {player['name']}")
    print(f"Gender: {player['gender']}")
    print(f"Race: {player['race']}")
    print(f"Time Period: {player['time_period']}")
    print(f"Setting: {player['setting']}")
    print(f"Role: {player['role']}")
    print(f"Strengths: {', '.join(player['strengths'])}")
    print(f"Weaknesses: {', '.join(player['weaknesses'])}")
    print(f"Skills: {', '.join(player['skills'])}")
    print(f"Inventory: {', '.join(player['inventory'])}")
    print("\nRelationships:")
    for npc, details in player["relationships"].items():
        print(f"- {npc}: Loyalty {details['loyalty']}, Status: {details['status']}")
    print("\nPersonality:")
    print(f"- Alignment: {player['personality']['alignment']}")
    print(f"- Traits: {', '.join(player['personality']['traits'])}")


def make_decision(player, npc):
    """Allow the player to make a decision, influenced by skills, traits, and relationships."""
    print("\nA distress signal has been detected. What will you do?")
    print("1. Respond to the distress signal and risk a trap.")
    print("2. Ignore the signal and continue your journey.")
    print("3. Investigate from a distance before making a decision.")
    
    choice = get_valid_input("Enter your choice (1, 2, or 3): ", ["1", "2", "3"])

    if choice == "1":
        if "Charisma" in player["strengths"]:
            result = f"You inspire your crew to prepare for danger. The situation resolves favorably, and {npc['name']} retreats."
            update_personality(player, "brave")
        else:
            result = f"Your crew hesitates under poor leadership. {npc['name']} launches an attack, and you suffer losses."
            update_personality(player, "reckless")
    elif choice == "2":
        if "Wisdom" in player["strengths"]:
            result = f"You wisely avoid the trap. {npc['name']} is left empty-handed."
            update_personality(player, "cautious")
        else:
            result = f"Your crew questions your decision to avoid the distress signal. Morale drops."
            update_personality(player, "selfish")
    elif choice == "3":
        if "Perception" in player["strengths"]:
            result = f"Your investigation reveals an ambush. You outmaneuver {npc['name']} and gain valuable intel."
            update_personality(player, "strategic")
        else:
            result = f"Your investigation is inconclusive. Time is wasted, and {npc['name']} gains the upper hand."
            update_personality(player, "hesitant")

    print("\nOutcome:")
    print(result)


if __name__ == "__main__":
    print("Welcome to Character Creation!")
    
    # Initialize the player dictionary
    player = default_player.copy()

    # Load or create a character
    character_name = input("Enter your character's name to load or create a new one: ").strip()
    player = load_player_data(character_name)

    if player["gender"]:  # If a character is already created, display details
        print(f"\nLoaded Character: {player['name']}")
        display_player_summary(player)
        choice = get_valid_input("\nDo you want to (1) Continue with this character or (2) Replace and create a new profile? Enter 1 or 2: ", ["1", "2"])
        if choice == "2":  # Replace the character
            player = default_player.copy()  # Reset player data
            player["name"] = character_name
            character_creation(player)
            save_player_data(player)
    else:
        # If no character exists, start a new one
        character_creation(player)
        save_player_data(player)

    # Generate World Description
    prompt = generate_world_prompt(player)
    print("\nGenerated World-Building Prompt:")
    print(prompt)

    # Generate NPC and starting conflict
    npc = generate_npc()
    conflict = generate_starting_conflict(npc, player)
    print("\nStarting Scenario:")
    print(conflict)

    # Decision-making scenario based on skills and relationships
    make_decision(player, npc)

    # Introduce a random event for variety
    random_event_outcome = generate_random_event(player)
    print(f"\nRandom Event Outcome: {random_event_outcome}")

    # Save updated player state after decision
    save_player_data(player)

    # Display updated player summary
    display_player_summary(player)
