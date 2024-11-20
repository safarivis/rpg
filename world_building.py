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
    Generate a detailed world-building prompt based on the player's attributes.
    Parameters:
        - player (dict): The player's data.
    Returns:
        - str: A descriptive world-building prompt.
    """
    role_details = player.get("role_details", "a mysterious figure")
    motivation = player.get("role_motivation", "unknown reasons")
    factions = generate_factions(player)

    # Generate the prompt
    prompt = f"""
    Create a detailed world for a character named {player['name']}, a {player['race'].lower()} {player['gender'].lower()}.
    They are living in the {player['time_period']} in a {player['setting'].lower()} setting.
    They play the role of a {player['role']}.

    Here are additional details:
    - Strengths: {', '.join(player['strengths'])}
    - Weaknesses: {', '.join(player['weaknesses'])}
    {format_attributes(player['physical_attributes'], "Physical Attributes")}
    - Favorite Music: {player['favorites']['music']}
    - Favorite Movies: {player['favorites']['movies']}
    - Favorite Books: {player['favorites']['books']}
    - Favorite Graphics Style: {player['favorites']['graphics_style']}
    - Role Details: {role_details}
    - Motivation: {motivation}

    Factions shaping the world:
    {factions}

    Present a major conflict or challenge tied to their role and setting.
    """
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
