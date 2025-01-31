from player import save_player_data

def format_attributes(attributes, title="Attributes"):
    """
    Format a dictionary of attributes for display or world-building.
    Parameters:
        - attributes (dict): The player's attributes or related data.
        - title (str): Title for the section (default is 'Attributes').
    Returns:
        - str: Formatted string for display.
    """
    formatted = [f"{title}:"]
    formatted += [f"- {key.replace('_', ' ').capitalize()}: {value}" for key, value in attributes.items()]
    return "\n".join(formatted)

def generate_world_prompt(player):
    """
    Generate a basic world-building prompt based on the player's attributes.
    Parameters:
        - player (dict): The player's data.
    Returns:
        - str: A descriptive world-building prompt.
    """
    # Get basic player info with defaults
    name = player.get('name', 'Unknown')
    race = player.get('race', 'being')
    gender = player.get('gender', 'unknown')
    role = player.get('role', 'adventurer')
    time_period = player.get('time_period', 'present')

    # Generate the prompt
    prompt = f"""You find yourself in a world where {race}s like yourself have carved out their own destiny. 
As a {role} from the {time_period}, you have unique perspectives and abilities that set you apart. 
What challenges await you in this vast realm? Only time will tell..."""

    return prompt

def generate_factions(player):
    """
    Dynamically create factions based on the player's setting and time period.
    Parameters:
        - player (dict): The player's data.
    Returns:
        - str: A list of factions as a formatted string.
    """
    if player["setting"].lower() == "fantasy":
        factions = [
            "The Order of the White Flame: A knightly order sworn to protect the realm.",
            "The Shadow Cabal: A secretive guild manipulating events from the shadows."
        ]
    elif player["setting"].lower() == "realism":
        factions = [
            "The Global Consortium: A powerful multinational corporation controlling resources.",
            "The Resistance: A group of rebels fighting against oppressive regimes."
        ]
    else:
        factions = [
            "The Unknown Collective: An enigmatic force shaping the world's destiny.",
            "The Wanderers: Nomadic groups struggling to survive in harsh conditions."
        ]
    
    return "\n".join([f"- {faction}" for faction in factions])
