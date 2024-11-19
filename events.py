from utilities import get_valid_input

def generate_starting_conflict(npc, player):
    """Generate a starting conflict scenario with skill integration."""
    # Introduce the scenario
    conflict = f"""
    As your ship, the *Ecliptica*, drifts through the cold void of space, a distress signal breaks the silence.
    The message crackles through your comms: 
    "This is Captain Lira of the *Nebula Dawn*. We're under attack and require immediate assistance. Coordinates attached."
    
    You recognize the name—it’s a rival ship with a checkered past. {npc['name']}, your rival {npc['role'].lower()}, might be behind this.
    The signal could be genuine, or it might be an elaborate trap set by {npc['name']} to lure you into danger.
    
    Ignoring the signal could mean turning your back on potential allies—or valuable resources. But answering it might lead your crew into an ambush.
    
    Your crew waits for your decision, tension thick in the air.
    
    What will you do?

    Options:
    1. Respond to the distress signal and risk a trap.
    2. Ignore the signal and continue your journey.
    3. Investigate from a distance using your ship's sensors before making a decision.
    """
    print(conflict)

    # Get player's choice and handle it
    choice = get_valid_input("Enter your choice (1, 2, or 3): ", ["1", "2", "3"])
    if choice == "1":
        return handle_respond(player, npc)
    elif choice == "2":
        return handle_ignore(player, npc)
    elif choice == "3":
        return handle_investigate(player, npc)


def handle_respond(player, npc):
    """Handle the decision to respond to the distress signal."""
    if "Charisma" in player["strengths"]:
        return f"""
        You decide to respond to the distress signal, rallying your crew with a charismatic speech.
        Your crew feels inspired, and they prepare for potential danger with renewed vigor.
        Upon arrival, the *Nebula Dawn* seems genuinely under attack, but {npc['name']} is not far behind.
        """
    else:
        return f"""
        You respond to the distress signal. Tension is high as your crew prepares for a possible ambush.
        When you arrive, it’s an ambush! {npc['name']} attacks with a full force, and your crew scrambles to defend themselves.
        """


def handle_ignore(player, npc):
    """Handle the decision to ignore the distress signal."""
    if "Wisdom" in player["strengths"]:
        return f"""
        You wisely decide to ignore the distress signal, suspecting it to be a trap. 
        Later, your sensors pick up faint traces of {npc['name']}’s fleet lurking near the signal's coordinates. You avoided disaster.
        """
    else:
        return f"""
        You decide to ignore the signal, choosing caution over risk. 
        However, your crew is divided about your decision, and morale takes a hit. {npc['name']} might still be tracking you.
        """


def handle_investigate(player, npc):
    """Handle the decision to investigate the signal."""
    if "Perception" in player["strengths"]:
        return f"""
        You decide to investigate the signal from a safe distance. Using your perception skills, you detect a faint secondary signal—a hidden fleet near the coordinates.
        It’s a trap! You alert your crew and evade the ambush set by {npc['name']}.
        """
    else:
        return f"""
        You investigate from a distance, but your ship’s sensors fail to detect anything unusual. 
        Unsure of the situation, you hesitate, losing precious time. {npc['name']} might have gained an advantage over you.
        """


# Utility Function to Add Random Events
def generate_random_event(player):
    """Generate a random event based on the player's attributes and current state."""
    random_events = [
        {
            "description": "You find an abandoned cargo ship with unknown contents.",
            "required_skill": "Perception",
            "outcome": {
                "success": "You uncover valuable supplies!",
                "failure": "The ship's contents were a trap, and you lose resources."
            }
        },
        {
            "description": "Your ship’s engine malfunctions in deep space.",
            "required_skill": "Engineering",
            "outcome": {
                "success": "You quickly repair the engine and continue your journey.",
                "failure": "Your delay causes you to lose time and miss an opportunity."
            }
        },
        {
            "description": "A rogue asteroid field blocks your path.",
            "required_skill": "Strategy",
            "outcome": {
                "success": "You navigate safely, avoiding the dangers.",
                "failure": "Your ship sustains damage, requiring resources to repair."
            }
        }
    ]

    # Select a random event
    import random
    event = random.choice(random_events)
    print(f"\nRandom Event: {event['description']}")

    # Check for the required skill
    if event["required_skill"] in player["skills"]:
        print(f"Outcome: {event['outcome']['success']}")
        return event["outcome"]["success"]
    else:
        print(f"Outcome: {event['outcome']['failure']}")
        return event["outcome"]["failure"]
