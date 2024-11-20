import random

def get_valid_input(prompt, options=None):
    """
    Get valid input from the player.
    Parameters:
        - prompt (str): The message to display to the user.
        - options (list): A list of valid options (optional).
    Returns:
        - str: The validated input.
    """
    while True:
        response = input(prompt).strip().lower()
        if not options:
            return response
        options_lower = [opt.lower() for opt in options]
        if response in options_lower:
            return response
        print(f"Invalid choice. Valid options are: {', '.join(options)}")

def perform_skill_check(player, skill, difficulty=0.6):
    """
    Perform a skill check and return success or failure.
    Parameters:
        - player (dict): The player's data.
        - skill (str): The skill to check.
        - difficulty (float): The success threshold (default 0.6).
    Returns:
        - bool: True if the skill check succeeds, False otherwise.
    """
    if skill not in player["skills"]:
        print(f"Warning: {skill} is not one of the player's known skills.")
        success_chance = 0.4  # Lower base chance for unknown skills
    else:
        success_chance = 0.8  # Higher success chance for known skills

    roll = random.random()  # Generate a random number between 0 and 1
    print(f"Skill check roll: {roll:.2f} (Difficulty: {difficulty:.2f})")
    return roll < success_chance

def calculate_probability(player, base_chance, modifiers=None):
    """
    Calculate probability for a game event based on player attributes and modifiers.
    Parameters:
        - player (dict): The player's data.
        - base_chance (float): The base probability of success.
        - modifiers (dict): A dictionary of factors that modify success (optional).
    Returns:
        - float: The adjusted probability.
    """
    probability = base_chance
    if modifiers:
        for factor, impact in modifiers.items():
            if factor in player["strengths"]:
                probability += impact  # Positive impact for strengths
            elif factor in player["weaknesses"]:
                probability -= impact  # Negative impact for weaknesses

    return max(0, min(probability, 1))  # Ensure probability stays between 0 and 1
