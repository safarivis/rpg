from player import (
    load_player_data,
    default_player,
    save_player_data,
    update_personality,
)
from world_building import generate_world_prompt
from npc_generation import generate_npc
from events import (
    EventSystem,
    GameEvent,
    EventChoice,
    CombatEvent,
    generate_starting_conflict,
    generate_random_event
)
from character_creation import character_creation
from utilities import get_valid_input
from crew import (
    initialize_crew,
    update_crew_status,
    perform_crew_activity,
    display_crew_status,
    get_available_activities
)
from time_manager import TimeManager
from relationship_manager import RelationshipManager
from llm_service import LLMService
from story_manager import (
    load_game_state,
    save_game_state,
    get_next_available_scenario,
    generate_story_event,
    mark_scenario_complete
)
from inventory_manager import (
    purchase_item,
    can_afford,
    get_inventory,
    modify_credits
)
from status_manager import StatusManager
import os
import json
import random
from dotenv import load_dotenv

# ANSI color codes
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

# Get absolute path to .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

event_system = EventSystem()


def display_player_summary(player):
    """Display a summary of the player's current state."""
    print(f"\n{CYAN}Character Summary:{RESET}")
    print(f"{GREEN}Name: {RESET}{player['name']}")
    print(f"{GREEN}Gender: {RESET}{player['gender']}")
    print(f"{GREEN}Race: {RESET}{player['race']}")
    print(f"{GREEN}Time Period: {RESET}{player['time_period']}")
    print(f"{GREEN}Setting: {RESET}{player['setting']}")
    print(f"{GREEN}Role: {RESET}{player['role']}")
    print(f"{GREEN}Strengths: {RESET}{', '.join(player['strengths'])}")
    print(f"{GREEN}Weaknesses: {RESET}{', '.join(player['weaknesses'])}")

    # Optional fields
    if 'skills' in player:
        print(f"{GREEN}Skills: {RESET}{', '.join(player['skills'])}")
    if 'inventory' in player:
        print(f"{GREEN}Inventory: {RESET}{', '.join(player['inventory'])}")

    # Physical attributes
    if 'physical_attributes' in player:
        print(f"\n{CYAN}Physical Attributes:{RESET}")
        for attr, value in player['physical_attributes'].items():
            print(f"- {attr.replace('_', ' ').title()}: {value}")

    # Favorites
    if 'favorites' in player:
        print(f"\n{CYAN}Favorites:{RESET}")
        for pref, value in player['favorites'].items():
            print(f"- {pref.replace('_', ' ').title()}: {value}")

    # Role details
    if any(key.startswith('role_') for key in player.keys()):
        print(f"\n{CYAN}Role Information:{RESET}")
        for key in player:
            if key.startswith('role_') and key != 'role' and player[key]:
                print(f"- {key.replace('role_', '').replace('_', ' ').title()}: {player[key]}")

    # Relationships
    if 'relationships' in player:
        print(f"\n{CYAN}Relationships:{RESET}")
        for npc, details in player["relationships"].items():
            print(f"- {npc}: Loyalty {details['loyalty']}, Status: {details['status']}")

    # Personality
    if 'personality' in player:
        print(f"\n{CYAN}Personality:{RESET}")
        if 'alignment' in player['personality']:
            print(f"- Alignment: {player['personality']['alignment']}")
        if 'traits' in player['personality']:
            print(f"- Traits: {', '.join(player['personality']['traits'])}")


def make_decision(player, npc):
    """Allow the player to make a decision, influenced by skills, traits, and relationships."""
    # Check if we should skip the distress signal scenario
    game_state = load_game_state()
    if "starting_conflict" in game_state["completed_scenarios"]:
        return None

    # Initialize personality if it doesn't exist
    if 'personality' not in player:
        player['personality'] = {
            'alignment': 'Neutral',
            'traits': []
        }

    print("\nA distress signal has been detected. What will you do?")
    print("1. Respond to the distress signal and risk a trap.")
    print("2. Ignore the signal and continue your journey.")
    print("3. Investigate from a distance before making a decision.")

    choice = get_valid_input("Enter your choice (1, 2, or 3): ", ["1", "2", "3"])

    if choice == "1":
        if "Charisma" in player["strengths"]:
            result = f"You inspire your crew to prepare for danger. The situation resolves favorably, and {npc.get('name', 'the enemy')} retreats."
            update_personality(player, "brave")
        else:
            result = f"Your crew hesitates under poor leadership. {npc.get('name', 'the enemy')} launches an attack, and you suffer losses."
            update_personality(player, "reckless")
    elif choice == "2":
        if "Wisdom" in player["strengths"]:
            result = f"You wisely avoid the trap. {npc.get('name', 'the enemy')} is left empty-handed."
            update_personality(player, "cautious")
        else:
            result = f"Your crew questions your decision to avoid the distress signal. Morale drops."
            update_personality(player, "selfish")
    elif choice == "3":
        if "Perception" in player["strengths"]:
            result = f"Your investigation reveals an ambush. You outmaneuver {npc.get('name', 'the enemy')} and gain valuable intel."
            update_personality(player, "strategic")
        else:
            result = f"Your investigation is inconclusive. Time is wasted, and {npc.get('name', 'the enemy')} gains the upper hand."
            update_personality(player, "hesitant")

    print("\nOutcome:")
    print(result)
    return result


def display_choice_effects(player, outcome):
    """Display the effects of a player's choice."""
    print("\n=== Choice Outcome ===")
    print(outcome['message'])
    
    if outcome['costs']:
        print("\nResource Changes:")
        for resource, change in outcome['costs'].items():
            if resource == 'time':
                print(f"- Time passed: {change['hours']} hours")
            elif change != 0:
                print(f"- {resource.title()}: {change:+d}")
    
    if outcome['rewards']:
        if outcome['rewards']['credits']:
            print(f"\nCredits earned: {outcome['rewards']['credits']:+d}")
        if outcome['rewards']['items']:
            print("\nItems acquired:")
            for item in outcome['rewards']['items']:
                print(f"- {item.name} ({item.rarity})")
                if item.attributes:
                    for attr, value in item.attributes.items():
                        print(f"  * {attr}: {value}")
    
    print("\nCurrent Resources:")
    for resource, value in player['resources'].items():
        if resource == 'time':
            print(f"- Time elapsed: {value['hours']} hours ({value['cycles']} cycles)")
        else:
            print(f"- {resource.title()}: {value}")
    
    if outcome['relationship_changes']:
        print("\nRelationship Changes:")
        for npc, changes in outcome['relationship_changes'].items():
            if changes['loyalty_change'] != 0:
                print(f"- {npc}'s loyalty: {changes['loyalty_change']:+d}")
            if changes['new_status']:
                print(f"- {npc}'s status: {changes['new_status']}")


def handle_event_outcome(player, choice, event_type):
    """Handle the outcome of an event and provide choices."""
    display_choice_effects(player, choice)
    
    while True:
        print("\nWhat would you like to do next?")
        print("1. Continue exploring")
        print("2. Check character status")
        print("3. Check crew status")
        print("4. Perform crew activity")
        print("5. Return to base")
        print("6. Visit trading station")
        
        choice = get_valid_input("Enter your choice (1-6): ", ["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            return "continue"
        elif choice == "2":
            display_player_summary(player)
        elif choice == "3":
            display_crew_status(player)
        elif choice == "4":
            # Show available activities
            activities = get_available_activities(player)
            if not activities:
                print("\nNo activities available - insufficient credits!")
                continue
                
            print("\nAvailable Activities:")
            for i, activity in enumerate(activities, 1):
                print(f"{i}. {activity['name']} - {activity['description']}")
                print(f"   Cost: {activity['cost']} credits, Duration: {activity['duration']} hours")
            
            activity_choice = get_valid_input(
                f"Choose an activity (1-{len(activities)}) or 0 to cancel: ",
                [str(i) for i in range(len(activities) + 1)]
            )
            
            if activity_choice == "0":
                continue
                
            # Perform the chosen activity
            activity = activities[int(activity_choice) - 1]
            result = perform_crew_activity(player, activity['name'])
            print(f"\n{result['message']}")
            if result['success']:
                print("Effects:")
                print(f"- Rest: +{result['effects']['rest_gained']}")
                print(f"- Morale: +{result['effects']['morale_gained']}")
                print(f"- Credits spent: {result['effects']['credits_spent']}")
                print(f"- Time taken: {result['effects']['duration']} hours")
        elif choice == "5":
            print("Returning to base...")
            save_player_data(player)
            return "base"
        elif choice == "6":
            print("Visiting trading station...")
            return "trade"


def handle_event(player, event=None, time_manager=None, relationship_manager=None, llm_service=None):
    """Handle a game event with free-form interaction."""
    try:
        # Generate event if none provided
        if event is None:
            event = generate_random_event()
        elif isinstance(event, dict):
            # Convert dict to GameEvent if needed
            from events import GameEvent
            event = GameEvent.from_dict(event)
            
        # Store current event in player data
        player['current_event'] = event
        
        # Display status at start of event
        display_status(player, getattr(event, 'last_scene', None))
        
        print("\n=== Current Situation ===")
        
        # Generate narrative from event
        scene = event.generate_narrative(player, llm_service)
        print(f"\n{scene}\n")
        
        # Interactive loop
        while True:
            print("\nCommands:")
            print("- Type 'status' to view your status")
            print("- Type 'quit' to exit")
            print("- Or simply describe what you want to do")
            action = input("\nWhat would you like to do?: ").strip().lower()
            
            if action == 'quit':
                save_player_data(player)  # Save before quitting
                return True
            elif action == 'status':
                display_status(player, scene)
                continue
            elif action == 'nsfw':  # Keep the functionality but don't show it in commands
                toggle_nsfw(player)
                continue
            
            # Handle purchases
            if any(word in action.lower() for word in ['buy', 'purchase', "i'll take", 'get']):
                if 'ghost blade' in action.lower():
                    if can_afford(player['name'], 12000):
                        if purchase_item(player['name'], 'Ghost Blade Energy Sword', 12000):
                            print("Purchase successful! The Ghost Blade has been added to your inventory.")
                            player = load_player_data(player['name'])  # Reload player data
                    else:
                        print("You don't have enough credits for this purchase.")
                elif 'neon slasher' in action.lower():
                    if can_afford(player['name'], 15000):
                        if purchase_item(player['name'], 'Neon Slasher Energy Sword', 15000):
                            print("Purchase successful! The Neon Slasher has been added to your inventory.")
                            player = load_player_data(player['name'])  # Reload player data
                    else:
                        print("You don't have enough credits for this purchase.")
                
            # Generate response to player's action
            action_context = {
                "player": player,
                "current_scene": scene,
                "nsfw_enabled": player.get('nsfw_enabled', False)
            }
            
            # Get LLM response
            if llm_service:
                response = llm_service.generate_response(action, action_context)
                print(f"\n{response}\n")
                
                # Update event context and scene
                event.last_interaction = action
                event.last_scene = scene
                scene = response
                
                # Save after significant interaction
                save_player_data(player)
            else:
                print("\nNo LLM service available. Using basic response.")
                print("Your action was noted. What would you like to do next?")
            
        return True
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False


def handle_combat_event(player, event, llm_service):
    """Handle a combat event with dialogue options."""
    try:
        if isinstance(event, dict):
            # Handle dictionary-based combat event
            opponent = event["opponent"]
            print(f"\n=== Combat Event ===\n{event['description']}\n")
            print(f"Opponent: {opponent['name']}")
            print(f"Level: {opponent['level']}")
            print("Abilities:", ", ".join(opponent['abilities']))
            
            # Simple turn-based combat
            player_hp = 100  # Base player HP
            opponent_hp = 100  # Base opponent HP
            
            while player_hp > 0 and opponent_hp > 0:
                print(f"\n{player['name']} HP: {player_hp}")
                print(f"{opponent['name']} HP: {opponent_hp}")
                
                # Player turn
                print("\nYour turn! Choose your action:")
                print("1. Attack")
                print("2. Defend")
                print("3. Use Special Ability")
                
                action = get_valid_input("Choose your action (1-3): ", ["1", "2", "3"])
                
                damage = 0
                if action == "1":
                    damage = 20  # Base attack damage
                    print(f"\nYou attack {opponent['name']} for {damage} damage!")
                elif action == "2":
                    print("\nYou take a defensive stance, reducing incoming damage!")
                elif action == "3":
                    damage = 30  # Special ability damage
                    print(f"\nYou use a special ability, dealing {damage} damage!")
                
                opponent_hp -= damage
                
                if opponent_hp <= 0:
                    print(f"\nVictory! You have defeated {opponent['name']}!")
                    # Handle rewards if any
                    if "rewards" in event:
                        print("\nRewards:")
                        rewards = event["rewards"]
                        if "credits" in rewards:
                            add_credits(player, rewards["credits"])
                            print(f"Credits: +{rewards['credits']}")
                        if "items" in rewards:
                            for item in rewards["items"]:
                                add_item_to_inventory(player, item)
                                print(f"Item: {item}")
                    return True
                
                # Opponent turn
                print(f"\n{opponent['name']}'s turn!")
                ability = random.choice(opponent['abilities'])
                damage = 15  # Base opponent damage
                if action == "2":  # Player defended
                    damage = damage // 2
                player_hp -= damage
                print(f"{opponent['name']} uses {ability}, dealing {damage} damage!")
                
                if player_hp <= 0:
                    print(f"\nDefeat! {opponent['name']} has defeated you!")
                    return False
        else:
            # Handle Event object combat
            if not event.combat_system:
                event.initialize_combat(player, event.opponent)
            
            while not event.is_combat_finished():
                state = event.get_combat_state()
                print(f"\nTurn {state['turn_number']}")
                print("-" * 20)
                print(f"{player['name']} HP: {state['player_hp']}/{state['player_max_hp']}")
                print(f"{event.opponent['name']} HP: {state['opponent_hp']}/{state['opponent_max_hp']}")
                
                # Get available actions
                actions = event.get_available_actions()
                print("\nAvailable Actions:")
                for i, action in enumerate(actions, 1):
                    print(f"{i}. {action['name']} - {action['description']}")
                
                # Get player choice
                choice = get_valid_input(f"Choose your action (1-{len(actions)}): ", 
                                      [str(i) for i in range(1, len(actions) + 1)])
                choice_idx = int(choice) - 1
                
                # Execute action
                result = event.execute_action(actions[choice_idx]['id'])
                print(f"\n{result['message']}")
                
                # Check if combat is finished
                if event.is_combat_finished():
                    state = event.get_combat_state()
                    if state['player_hp'] <= 0:
                        print(f"\nYou have been defeated by {event.opponent['name']}!")
                        return False
                    else:
                        print(f"\nVictory! You have defeated {event.opponent['name']}!")
                        return True
        
        return True
        
    except Exception as e:
        print(f"An error occurred in combat: {str(e)}")
        return False


def initialize_game_systems():
    """Initialize all game systems."""
    time_manager = TimeManager()
    relationship_manager = RelationshipManager()
    llm_service = LLMService()
    return time_manager, relationship_manager, llm_service


def add_credits(player: dict, amount: int) -> None:
    """Add (or subtract) credits from player."""
    if 'credits' not in player:
        player['credits'] = 0
    player['credits'] += amount

def add_item_to_inventory(player: dict, item: str) -> None:
    """Add an item to player's inventory."""
    if 'inventory' not in player:
        player['inventory'] = []
    player['inventory'].append(item)


def display_status(player, last_scene=None):
    """Display comprehensive player status."""
    print(f"\n{CYAN}=== CHARACTER STATUS ==={RESET}")
    print(f"{GREEN}Name: {RESET}{player.get('name', 'Unknown')}")
    print(f"{GREEN}Role: {RESET}{player.get('role', 'Unknown')}")
    print(f"{GREEN}Health: {RESET}{player.get('health', 100)}/100")
    print(f"{GREEN}Credits: {RESET}{player.get('resources', {}).get('credits', 0)}")
    print(f"{GREEN}Location: {RESET}{player.get('location', 'Unknown')}")
    
    if player.get('inventory'):
        print(f"\n{CYAN}=== INVENTORY ==={RESET}")
        for item in player['inventory']:
            print(f"- {item}")
    
    if last_scene:
        print(f"\n{CYAN}=== LAST SCENE ==={RESET}")
        # Format the text to fit standard terminal width (80 characters)
        words = last_scene.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 <= 80:
                line += word + " "
            else:
                print(f"{YELLOW}{line}{RESET}")
                line = word + " "
        if line:
            print(f"{YELLOW}{line}{RESET}")

    print(f"\n{CYAN}Commands:{RESET}")
    print("- Type 'status' to view your status")
    print("- Type 'quit' to exit")
    print("- Or simply describe what you want to do")


def initialize_player(name, role):
    """Initialize a new player with default values."""
    return {
        'name': name,
        'role': role,
        'health': 100,
        'credits': 1000,
        'inventory': [],
        'relationships': {},
        'current_location': 'Night City - Downtown',
        'nsfw_enabled': False,  # Default to safe content
        'resources': {
            'fuel': 100
        }
    }


def toggle_nsfw(player):
    """Toggle NSFW content setting."""
    player['nsfw_enabled'] = not player.get('nsfw_enabled', False)
    status = "enabled" if player['nsfw_enabled'] else "disabled"
    print(f"\nNSFW content is now {status}")
    save_player_data(player)


def save_player_data(player):
    """Save player data to a JSON file."""
    try:
        # Convert current event to dict if it exists
        if 'current_event' in player and hasattr(player['current_event'], 'to_dict'):
            player['current_event'] = player['current_event'].to_dict()
            
        save_path = os.path.join(os.getcwd(), f"{player['name'].lower()}.json")
        with open(save_path, 'w') as f:
            json.dump(player, f, indent=4)
        print(f"Character saved as '{os.path.basename(save_path)}'!")
        return True
    except Exception as e:
        print(f"Error saving character: {str(e)}")
        return False

def load_player_data(name):
    """Load player data from a JSON file."""
    try:
        load_path = os.path.join(os.getcwd(), f"{name.lower()}.json")
        with open(load_path, 'r') as f:
            player = json.load(f)
            
        # Convert event dict back to GameEvent if it exists
        if 'current_event' in player:
            from events import GameEvent
            player['current_event'] = GameEvent.from_dict(player['current_event'])
            
        return player
    except FileNotFoundError:
        print(f"No saved character found with name '{name}'")
        return None
    except Exception as e:
        print(f"Error loading character: {str(e)}")
        return None


def main():
    """Main game loop."""
    print("Script is starting...")
    
    # Load environment variables
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        print("Error: LLM_API_KEY not found in environment variables")
        print("Please make sure you have a .env file with LLM_API_KEY=your_api_key")
        return
    
    # Initialize game systems
    time_manager = TimeManager()
    relationship_manager = RelationshipManager()
    status_manager = StatusManager()
    
    # Initialize LLM service
    try:
        llm_service = LLMService(api_key)
        print("LLM service initialized successfully")
    except Exception as e:
        print(f"Error initializing LLM service: {str(e)}")
        print("Please check your API key and try again")
        return
    
    # Load or create player
    player = load_player_data("strijder")  # Try to load existing player
    if not player:
        print("Creating new character...")
        player = default_player()  # Use default player if no save exists
        save_player_data(player)
    
    # Initialize status manager with current state
    status_manager.update_state(player)
    
    # Load game state
    game_state = load_game_state()
    if not game_state:
        game_state = {"completed_scenarios": [], "current_scenario": None}
    
    # Main game loop
    scene = None  # Initialize scene variable
    while True:
        print("\nCommands:")
        print("- Type 'status' to view your status")
        print("- Type 'quit' to exit")
        print("- Or simply describe what you want to do")
        action = input("\nWhat would you like to do?: ").strip().lower()
        
        if action == 'quit':
            save_player_data(player)  # Save before quitting
            return True
        elif action == 'status':
            display_status(player, scene)
            continue
        elif action == 'nsfw':  # Keep the functionality but don't show it in commands
            toggle_nsfw(player)
            continue
        
        # Handle purchases
        if any(word in action.lower() for word in ['buy', 'purchase', "i'll take", 'get']):
            if 'ghost blade' in action.lower():
                if can_afford(player['name'], 12000):
                    if purchase_item(player['name'], 'Ghost Blade Energy Sword', 12000):
                        print("Purchase successful! The Ghost Blade has been added to your inventory.")
                        player = load_player_data(player['name'])  # Reload player data
                        status_manager.update_state(player)  # Show status changes
                else:
                    print("You don't have enough credits for this purchase.")
            elif 'neon slasher' in action.lower():
                if can_afford(player['name'], 15000):
                    if purchase_item(player['name'], 'Neon Slasher Energy Sword', 15000):
                        print("Purchase successful! The Neon Slasher has been added to your inventory.")
                        player = load_player_data(player['name'])  # Reload player data
                        status_manager.update_state(player)  # Show status changes
                else:
                    print("You don't have enough credits for this purchase.")
            
        # Generate response to player's action
        action_context = {
            "player": player,
            "current_scene": scene,
            "nsfw_enabled": player.get('nsfw_enabled', False)
        }
        
        # Get LLM response
        if llm_service:
            scene = llm_service.generate_response(action, action_context)
            print("\n" + scene)
            
            # Check for any state changes after LLM response
            new_player = load_player_data(player['name'])
            if new_player != player:
                player = new_player
                status_manager.update_state(player)
        
        # Display player status
        display_player_summary(player)
        
        # Get next story event or random event
        if not game_state["current_scenario"]:
            # Get next story scenario if available
            next_scenario = get_next_available_scenario()
            if next_scenario:
                game_state["current_scenario"] = next_scenario
                event = generate_story_event(next_scenario, player)
            else:
                # Fall back to random events if no story scenarios available
                event = generate_random_event()
        else:
            # Continue current scenario
            event = generate_story_event(game_state["current_scenario"], player)
        
        # Handle event based on type
        if isinstance(event, CombatEvent):
            success = handle_combat_event(player, event, llm_service)
            if not success:
                print("\nGame Over!")
                break
            
            # Update scenario progress after combat
            if game_state["current_scenario"]:
                mark_scenario_complete(game_state["current_scenario"])
                game_state["current_scenario"] = None
        else:
            result = handle_event(player, event, time_manager, relationship_manager, llm_service)
            if result and game_state["current_scenario"]:
                # Story event completed successfully
                mark_scenario_complete(game_state["current_scenario"])
                game_state["current_scenario"] = None
        
        # Save game state
        save_player_data(player)
        save_game_state(game_state)
        
        # Ask to continue
        if get_valid_input("\nContinue playing? (yes/no): ", ["yes", "no"]) != "yes":
            break

if __name__ == "__main__":
    main()