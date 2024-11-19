import json
import random

# Default Player Template
default_player = {
    "name": "",
    "gender": "",
    "race": "",
    "time_period": "",
    "setting": "",
    "role": "",
    "favorites": {
        "music": "",
        "movies": "",
        "books": "",
        "graphics_style": ""
    },
    "physical_attributes": {
        "weight": "",
        "height": "",
        "looks": "",
        "hair_color": "",
        "hair_length": "",
        "tattoos": ""
    },
    "strengths": [],
    "weaknesses": [],
    "skills": [],
    "inventory": [],
    "relationships": {},
    "personality": {
        "alignment": "Neutral",
        "traits": []
    },
    "role_details": "",
    "role_motivation": "",
    "role_field": "",
    "role_goal": "",
    "role_ship": "",
    "role_fleet": ""
}

# Predefined Skills and Weaknesses
available_skills = ["Lockpicking", "Strategy", "Weapons Mastery", "Stealth", "Negotiation"]
random_weaknesses = ["Fear of Heights", "Weakness for Beautiful Women", "Allergy to Dust", "Claustrophobia", "Recklessness"]

# --- Utility Functions ---
def load_player_data(name):
    """Load player data from a JSON file."""
    filename = f"{name.lower()}.json"
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"No saved character found with the name '{name}'. Starting fresh.")
        return default_player.copy()

def save_player_data(player):
    """Save player data to a JSON file."""
    if player["name"]:
        filename = f"{player['name'].lower()}.json"
        with open(filename, "w") as file:
            json.dump(player, file, indent=4)
        print(f"Character saved as '{filename}'!")
    else:
        print("Character name is missing. Cannot save data.")

# --- Character Feature Initializations ---
def choose_skills(player):
    """Allow the player to select three skills."""
    print("\nChoose 3 skills for your character:")
    for idx, skill in enumerate(available_skills, 1):
        print(f"{idx}. {skill}")

    selected_skills = []
    while len(selected_skills) < 3:
        try:
            choice = int(input("Enter your choice: ")) - 1
            if 0 <= choice < len(available_skills) and available_skills[choice] not in selected_skills:
                selected_skills.append(available_skills[choice])
            else:
                print("Invalid choice or skill already selected.")
        except ValueError:
            print("Please enter a valid number.")
    player["skills"] = selected_skills
    print(f"Selected Skills: {', '.join(selected_skills)}")

def assign_weaknesses(player):
    """Assign three random weaknesses to the player."""
    player["weaknesses"] += random.sample(random_weaknesses, 3)
    print(f"\nAssigned Weaknesses: {', '.join(player['weaknesses'])}")

def initialize_inventory(player):
    """Set initial inventory based on the player's role."""
    role_based_inventory = {
        "warrior": ["Sword", "Shield", "Health Potion"],
        "scientist": ["Lab Kit", "Energy Scanner", "Tablet"],
        "pilot": ["Blaster", "Toolkit", "Space Map"]
    }
    player["inventory"] = role_based_inventory.get(player["role"].lower(), ["Basic Supplies"])
    print(f"\nStarting Inventory: {', '.join(player['inventory'])}")

def initialize_relationships(player):
    """Set up initial NPC relationships for the player."""
    player["relationships"] = {
        "Varok": {"loyalty": -10, "status": "Rival"},
        "Lira": {"loyalty": 20, "status": "Ally"}
    }
    print("\nInitialized Relationships:")
    for name, details in player["relationships"].items():
        print(f"{name}: {details}")

# --- Dynamic Updates ---
def update_loyalty(player, npc_name, change):
    """Update NPC loyalty based on player actions."""
    if npc_name in player["relationships"]:
        player["relationships"][npc_name]["loyalty"] += change
        print(f"\n{npc_name}'s loyalty has {'increased' if change > 0 else 'decreased'} to {player['relationships'][npc_name]['loyalty']}.")

def update_personality(player, trait):
    """Update personality traits and alignment dynamically."""
    if trait not in player["personality"]["traits"]:
        player["personality"]["traits"].append(trait)

    alignments = {
        "Altruistic": "Lawful Good",
        "Selfish": "Chaotic Evil",
        "Neutral": "True Neutral"
    }
    player["personality"]["alignment"] = alignments.get(trait, player["personality"]["alignment"])
    print(f"\nPersonality updated: Alignment - {player['personality']['alignment']}, Traits - {', '.join(player['personality']['traits'])}")
