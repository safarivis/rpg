from player import save_player_data, default_player
from utilities import get_valid_input

# Dark Room Introduction
def dark_room_intro(player):
    """Guide the player through initial character setup."""
    print("You awaken in a pitch-black room. A voice echoes in the void...\n")
    player["name"] = input("What is your name? ").strip()
    print(f"\n'{player['name']}, it is time to shape your destiny.'\n")

    # Gender Selection
    player["gender"] = get_valid_input(
        "The voice asks: 'Were you made to bear children?' (yes/no): ", 
        ["Yes", "No"]
    ).lower()
    player["gender"] = "Female" if player["gender"] == "yes" else "Male"

    # Race Selection
    print("\nThe voice continues: 'What race are you?'")
    player["race"] = get_valid_input(
        "Enter your race (e.g., Human, Elf, Dwarf): ", 
        None
    )

    # Time Period
    player["time_period"] = get_valid_input(
        "When are you from? (Past, Present, Future): ", 
        ["Past", "Present", "Future"]
    )

    # Setting
    player["setting"] = get_valid_input(
        "Is your world Fantasy or Realism? (Fantasy/Realism): ", 
        ["Fantasy", "Realism"]
    )

    # Role Description
    player["role"] = input(
        "What do you do in this world (e.g., Warrior, Scientist, Pilot)? "
    ).capitalize()


# Role Clarification
def clarify_role(player):
    """Gather detailed information about the player's role."""
    print(f"\nTell me more about your role as a {player['role']}:")
    if "warrior" in player["role"].lower():
        player["role_details"] = input("What type of warrior are you? (e.g., Knight, Mercenary, Gladiator): ").strip().capitalize()
        player["role_motivation"] = input("What drives you? (e.g., Honor, Revenge, Survival): ").strip().capitalize()
    elif "scientist" in player["role"].lower():
        player["role_field"] = input("What is your field of expertise? (e.g., Genetics, AI, Physics): ").strip().capitalize()
        player["role_goal"] = input("What is your primary goal? (e.g., Save humanity, Discover immortality): ").strip().capitalize()
    elif "pilot" in player["role"].lower():
        player["role_ship"] = input("What is your ship's name? ").strip().capitalize()
        player["role_fleet"] = input("Are you part of a fleet or independent? ").strip().capitalize()
    else:
        player["role_details"] = input(f"Describe your role as a {player['role']} in more detail: ").strip()
    print("\nRole details updated successfully.")


# Physical Attributes Input
def customize_physical_attributes(player):
    """Ask the player to define their physical attributes."""
    print("\nThe voice asks about your physical form...")
    attributes = {
        "weight": "What is your weight (e.g., 70kg, 150lbs)? ",
        "height": "What is your height (e.g., 5'10\", 180cm)? ",
        "looks": "How would you describe your looks (e.g., handsome, plain)? ",
        "hair_color": "What is your hair color? ",
        "hair_length": "What is your hair length (e.g., short, long)? ",
        "tattoos": "Do you have tattoos (yes/no)? "
    }
    for attr, question in attributes.items():
        player["physical_attributes"][attr] = input(question).strip().capitalize()


# Collect Favorites
def customize_favorites(player):
    """Collect the player's personal preferences."""
    print("\nTo better understand you, the voice asks about your tastes...")
    player["favorites"]["music"] = input("What is your favorite music genre (e.g., Rock, Classical)? ").strip().capitalize()
    player["favorites"]["movies"] = input("What are your favorite movies (e.g., Blade Runner, Interstellar)? ").strip().capitalize()
    player["favorites"]["books"] = input("What are your favorite books (e.g., Dune, Lord of the Rings, Bible)? ").strip().capitalize()
    player["favorites"]["graphics_style"] = input("What is your favorite graphics style (e.g., Realistic, Fantasy)? ").strip().capitalize()


# Strength Selection
def choose_strengths(player):
    """Allow the player to select their strengths."""
    questions = {
        "Combat": ["Physical Strength", "Agility", "Endurance"],
        "Social": ["Charisma", "Leadership", "Perception"],
        "Psychological": ["Wisdom", "Mental Resilience", "Spiritual Guidance"]
    }
    print("\nChoose your strengths:")
    for category, options in questions.items():
        print(f"\n{category} Strengths:")
        for idx, strength in enumerate(options, 1):
            print(f"{idx}. {strength}")
        while True:
            try:
                choice = int(input("Enter your choice: ")) - 1
                if 0 <= choice < len(options):
                    selected_strength = options[choice]
                    if selected_strength not in player["strengths"]:
                        player["strengths"].append(selected_strength)
                        break
                    else:
                        print("You already selected this strength. Choose another.")
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a valid number.")


# Character Creation Orchestrator
def character_creation(player):
    """Orchestrates the full character creation process."""
    dark_room_intro(player)
    clarify_role(player)
    customize_physical_attributes(player)
    customize_favorites(player)
    choose_strengths(player)
    save_player_data(player)
