import random

def generate_random_event(player):
    """Create random events considering player skills, weaknesses, and outcomes."""
    # Event pool
    events = [
        {"id": "trap", "description": "A hidden trap springs!", "requires": "Perception", "penalty": "Lose 10 health."},
        {"id": "diplomacy", "description": "An argument breaks out.", "requires": "Charisma", "reward": "Increase loyalty."},
        {"id": "ambush", "description": "You're ambushed by bandits!", "requires": "Weapons Mastery", "penalty": "Lose 20 resources."},
        {"id": "riddle", "description": "A mysterious figure challenges you with a riddle.", "requires": "Wisdom", "reward": "Gain rare item."}
    ]

    # Select a random event
    event = random.choice(events)
    print(f"\nEvent: {event['description']}")

    # Perform skill check
    success = perform_skill_check(player, event["requires"])
    
    if success:
        print("You successfully navigate the event!")
        if "reward" in event:
            print(f"Reward: {event['reward']}")
            apply_event_reward(player, event)
    else:
        print("You fail to address the event properly.")
        if "penalty" in event:
            print(f"Penalty: {event['penalty']}")
            apply_event_penalty(player, event)


def perform_skill_check(player, required_skill):
    """Check if the player has the required skill."""
    return required_skill in player["skills"]


def apply_event_reward(player, event):
    """Apply rewards for successful event resolution."""
    if event["id"] == "diplomacy":
        for npc in player["relationships"]:
            player["relationships"][npc]["loyalty"] += 5
    elif event["id"] == "riddle":
        player["inventory"].append("Rare Artifact")


def apply_event_penalty(player, event):
    """Apply penalties for failing an event."""
    if event["id"] == "trap":
        player["physical_attributes"]["weight"] = str(int(player["physical_attributes"]["weight"].rstrip("kg")) - 10) + "kg"
    elif event["id"] == "ambush":
        player["inventory"].remove("Health Potion") if "Health Potion" in player["inventory"] else None
