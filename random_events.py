import random

def generate_random_event(player):
    """Create random events based on the player's strengths and setting."""
    events = [
        {"description": "Your ship's engine malfunctions in deep space.", "strength": "Perception", "outcome": "You quickly identify and fix the issue."},
        {"description": "A rival mercenary challenges your authority.", "strength": "Charisma", "outcome": "You defuse the situation diplomatically."},
        {"description": "A long journey tests your limits.", "strength": "Endurance", "outcome": "Your stamina sees you through."},
        {"description": "A mysterious artifact appears.", "strength": "Wisdom", "outcome": "You wisely determine its purpose."},
        {"description": "A spiritual crisis emerges.", "strength": "Spiritual Guidance", "outcome": "Your faith guides you through."}
    ]

    # Select a random event
    event = random.choice(events)
    
    # Check if player has the relevant strength
    if event["strength"] in player["strengths"]:
        return f"Random Event: {event['description']}\nOutcome: {event['outcome']}"
    else:
        return f"Random Event: {event['description']}\nOutcome: You struggle to handle the situation."