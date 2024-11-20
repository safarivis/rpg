from utilities import get_valid_input
import random
import json
import os
from items import generate_random_item, generate_quest_reward, add_item_to_inventory, add_credits, generate_treasure
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Dictionary to store all possible scenarios
STORY_SCENARIOS = {
    "starting_conflict": {
        "id": "starting_conflict",
        "title": "Distress Signal from Nebula Dawn",
        "completed": False,
        "required_previous": None,  # No prerequisites for starting scenario
        "description": "A distress signal from a rival ship tests your judgment and crew leadership."
    },
    "consortium_contract": {
        "id": "consortium_contract",
        "title": "The Global Consortium's Offer",
        "completed": False,
        "required_previous": ["starting_conflict"],
        "description": "The Global Consortium approaches with a lucrative but morally ambiguous contract."
    },
    "resistance_contact": {
        "id": "resistance_contact",
        "title": "Message from the Resistance",
        "completed": False,
        "required_previous": ["starting_conflict"],
        "description": "A covert message from the Resistance seeks your aid against the Consortium."
    },
    "spiritual_awakening": {
        "id": "spiritual_awakening",
        "title": "The Ancient Temple Discovery",
        "completed": False,
        "required_previous": ["starting_conflict"],
        "description": "Your crew discovers an ancient temple floating in deep space."
    }
}

@dataclass
class EventChoice:
    description: str
    costs: Dict[str, int] = None
    rewards: Dict[str, Any] = None
    message: Optional[str] = None
    morale_change: Optional[int] = None

    def __post_init__(self):
        if self.costs is None:
            self.costs = {}
        if self.rewards is None:
            self.rewards = {}

class GameEvent:
    """Class representing a game event."""
    def __init__(self, type: str, description: str, choices=None, context=None):
        self.type = type
        self.description = description
        self.choices = choices if choices is not None else []
        self.context = context if context is not None else {}
        self.last_interaction = None
        self.last_scene = None

    def generate_narrative(self, player, llm_service):
        """Generate narrative for this event using LLM."""
        if llm_service:
            context = {
                "player": player,
                "event_type": self.type,
                "description": self.description,
                "last_interaction": self.last_interaction,
                "context": self.context
            }
            return llm_service.generate_response(self.description, context)
        return self.description

    def to_dict(self):
        """Convert event to dictionary for serialization."""
        return {
            "type": self.type,
            "description": self.description,
            "choices": self.choices,
            "context": self.context,
            "last_interaction": self.last_interaction,
            "last_scene": self.last_scene
        }

    @classmethod
    def from_dict(cls, data):
        """Create event from dictionary after deserialization."""
        if isinstance(data, dict):
            event = cls(
                type=data.get("type", "exploration"),
                description=data.get("description", ""),
                choices=data.get("choices", []),
                context=data.get("context", {})
            )
            event.last_interaction = data.get("last_interaction")
            event.last_scene = data.get("last_scene")
            return event
        return data  # Return as is if not a dict

class EventSystem:
    def __init__(self):
        self.events = {
            "normal": self._create_normal_events(),
            "morale": self._create_morale_events()
        }

    def _create_normal_events(self) -> List[GameEvent]:
        return [
            GameEvent(
                type="normal",
                description="Your ship encounters a powerful solar storm.",
                choices=[
                    EventChoice(
                        description="Try to navigate through it",
                        message="You bravely navigate through the storm, testing your ship's capabilities.",
                        costs={'fuel': -20},
                        rewards={'credits': 200, 'items': ['Shield Upgrade']},
                    ),
                    EventChoice(
                        description="Find shelter in a nearby asteroid field",
                        message="You find refuge in the asteroid field, waiting for the storm to pass.",
                        costs={'fuel': -10},
                        rewards={'credits': 100, 'items': ['Asteroid Sample']},
                    ),
                    EventChoice(
                        description="Return to the nearest space station",
                        message="You return to the station, prioritizing safety over time.",
                        costs={'fuel': -30},
                        rewards={'credits': 50, 'items': []},
                    )
                ]
            )
        ]

    def _create_morale_events(self) -> List[GameEvent]:
        return [
            GameEvent(
                type="morale",
                description="Your crew's morale is low after weeks in deep space.",
                choices=[
                    EventChoice(
                        description="Lead a group meditation session",
                        message="The meditation session helps calm the crew's nerves.",
                        costs={'fuel': 0},
                        rewards={'credits': 0, 'items': []},
                        morale_change=15
                    ),
                    EventChoice(
                        description="Make an emergency stop at a trading post",
                        message="The brief respite at the trading post lifts everyone's spirits.",
                        costs={'fuel': -20, 'credits': -100},
                        rewards={'credits': 0, 'items': ['Crew Supplies']},
                        morale_change=25
                    ),
                    EventChoice(
                        description="Push forward to the next mission",
                        message="The crew's determination is tested as you continue the mission.",
                        costs={'fuel': -5},
                        rewards={'credits': 50, 'items': []},
                        morale_change=-10
                    )
                ]
            )
        ]

    def generate_event(self, player: Dict) -> GameEvent:
        """Generate a random event based on player's state."""
        if 'crew' in player and player.get('crew', {}).get('morale', 75) < 50:
            return random.choice(self.events['morale'])
        return random.choice(self.events['normal'])

    def handle_choice(self, player: Dict, event: GameEvent, choice_num: int) -> Dict[str, Any]:
        """Handle a player's choice for an event."""
        try:
            # Convert choice to 0-based index and validate
            idx = int(choice_num) - 1
            if idx < 0 or idx >= len(event.choices):
                raise ValueError(f"Invalid choice number: {choice_num}")

            choice = event.choices[idx]

            # Initialize player resources if needed
            if 'resources' not in player:
                player['resources'] = {'fuel': 100}
            if 'credits' not in player:
                player['credits'] = 1000
            if 'inventory' not in player:
                player['inventory'] = []

            # Apply costs
            player['resources']['fuel'] = max(0, player['resources']['fuel'] + choice.costs.get('fuel', 0))
            if 'credits' in choice.costs:
                player['credits'] = max(0, player['credits'] + choice.costs['credits'])

            # Apply rewards
            player['credits'] += choice.rewards.get('credits', 0)
            player['inventory'].extend(choice.rewards.get('items', []))

            # Handle morale changes
            if choice.morale_change is not None:
                if 'crew' not in player:
                    player['crew'] = {'morale': 75}
                player['crew']['morale'] = max(0, min(100, player['crew']['morale'] + choice.morale_change))

            return {
                'message': choice.message,
                'costs': choice.costs,
                'rewards': choice.rewards,
                'morale_change': choice.morale_change,
                'success': True
            }

        except ValueError as e:
            raise ValueError(f"Invalid choice: {str(e)}")
        except Exception as e:
            raise Exception(f"Error handling event outcome: {str(e)}")

# Create a global instance of the event system
event_system = EventSystem()

@dataclass
class TimeManager:
    current_date: int = 0
    crew_birthdays: Dict[str, int] = field(default_factory=dict)
    events_calendar: Dict[str, List[str]] = field(default_factory=dict)
    
    def initialize_crew_birthdays(self, crew):
        """Assign random but fixed birthday dates to crew members."""
        for member in crew:
            if member['id'] not in self.crew_birthdays:
                self.crew_birthdays[member['id']] = random.randint(1, 365)
    
    def check_birthdays(self, current_date):
        """Return list of crew members whose birthdays are today."""
        return [crew_id for crew_id, bday in self.crew_birthdays.items() 
                if (current_date % 365) == bday]
    
    def advance_time(self, days=1):
        """Advance time by specified number of days."""
        self.current_date += days
        return self.check_events()
    
    def check_events(self):
        """Check for any scheduled events on the current date."""
        return self.events_calendar.get(str(self.current_date), [])

@dataclass
class Relationship:
    character_id: str
    affinity: int = 0  # -100 to 100
    relationship_type: str = "neutral"  # friend, rival, romantic, etc.
    shared_experiences: List[str] = field(default_factory=list)
    development_opportunities: List[str] = field(default_factory=list)
    
    def update_affinity(self, amount):
        """Update relationship affinity within bounds."""
        self.affinity = max(-100, min(100, self.affinity + amount))
    
    def add_experience(self, experience):
        """Add a shared experience to the relationship."""
        self.shared_experiences.append(experience)

@dataclass
class RelationshipManager:
    relationships: Dict[str, Relationship] = field(default_factory=dict)
    
    def get_or_create_relationship(self, character_id):
        """Get existing relationship or create new one."""
        if character_id not in self.relationships:
            self.relationships[character_id] = Relationship(character_id)
        return self.relationships[character_id]
    
    def update_relationship(self, character_id, affinity_change, experience=None):
        """Update relationship with a character."""
        relationship = self.get_or_create_relationship(character_id)
        relationship.update_affinity(affinity_change)
        if experience:
            relationship.add_experience(experience)

@dataclass
class StoryEvent:
    description: str
    choices: List[EventChoice]
    context: Dict[str, Any] = field(default_factory=dict)
    type: str = "story"
    llm_generated: bool = False
    last_interaction: Optional[str] = None
    
    def generate_narrative(self, player, llm_service):
        """Generate dynamic narrative based on context using LLM."""
        prompt = f"""
        Player {player['name']} is a {player['role']} with {player['personality']['alignment']} alignment.
        Previous interaction: {self.last_interaction}
        Current relationships: {self.context.get('relationships', {})}
        Current situation: {self.description}
        
        Generate a detailed narrative interaction with choices that consider:
        1. Player's personality and past choices
        2. Current relationships with crew and NPCs
        3. Potential for character development
        4. Impact on existing relationships
        """
        # Here we would call the LLM service with the prompt
        # For now, return a placeholder
        return self.description

@dataclass
class CombatEvent(StoryEvent):
    opponent: Dict[str, Any] = field(default_factory=dict)
    combat_system: Any = None
    
    def initialize_combat(self, player, opponent):
        """Initialize the combat system with player and opponent."""
        from combat_system import CombatSystem
        self.opponent = opponent
        self.combat_system = CombatSystem(player, opponent)
        
    def handle_combat_turn(self, player_action, player_input=None):
        """Handle a single turn of combat."""
        if not self.combat_system:
            raise ValueError("Combat system not initialized")
            
        if player_action == "talk":
            return self.combat_system.handle_dialogue(player_input)
        else:
            return self.combat_system.handle_combat_action(player_action)
            
    def is_combat_finished(self):
        """Check if the combat is finished."""
        return self.combat_system.is_combat_finished() if self.combat_system else False
        
    def get_combat_state(self):
        """Get the current state of combat."""
        return self.combat_system.get_combat_state() if self.combat_system else None

    def generate_combat_narrative(self, player, llm_service):
        """Generate dynamic combat narrative using LLM."""
        if not self.combat_system:
            return self.description
            
        state = self.get_combat_state()
        prompt = f"""
        Player {player['name']} with combat style {player.get('combat_style', 'unknown')}
        is facing {self.opponent['name']}.
        
        Current tactical situation:
        - Player HP: {state['player_hp']}/{state['player_max_hp']}
        - Opponent HP: {state['opponent_hp']}/{state['opponent_max_hp']}
        - Environment: {self.context.get('environment', 'battlefield')}
        - Available actions: {', '.join(state['available_actions'])}
        
        Generate a detailed combat interaction with:
        1. Vivid description of the current situation
        2. Tactical choices based on player's skills
        3. Potential consequences of each choice
        4. Dramatic tension and character development opportunities
        """
        return llm_service.generate_text(prompt)

def load_game_state():
    """Load the game state from a JSON file."""
    save_file = "game_state.json"
    if os.path.exists(save_file):
        with open(save_file, 'r') as f:
            return json.load(f)
    return {"completed_scenarios": [], "current_scenario": None}

def save_game_state(state):
    """Save the game state to a JSON file."""
    with open("game_state.json", 'w') as f:
        json.dump(state, f)

def mark_scenario_complete(scenario_id):
    """Mark a scenario as completed and save the state."""
    game_state = load_game_state()
    if scenario_id not in game_state["completed_scenarios"]:
        game_state["completed_scenarios"].append(scenario_id)
    save_game_state(game_state)

def get_next_available_scenario():
    """Get the next available scenario based on completion status and prerequisites."""
    game_state = load_game_state()
    completed = set(game_state["completed_scenarios"])
    
    available_scenarios = []
    for scenario in STORY_SCENARIOS.values():
        if scenario["id"] not in completed:  # Not completed yet
            if scenario["required_previous"] is None:  # No prerequisites
                available_scenarios.append(scenario)
            else:  # Check if prerequisites are met
                if all(req in completed for req in scenario["required_previous"]):
                    available_scenarios.append(scenario)
    
    return random.choice(available_scenarios) if available_scenarios else None

def generate_starting_conflict():
    """Generate a starting conflict scenario with skill integration."""
    game_state = load_game_state()
    
    # If starting conflict is already completed, move to random events
    if "starting_conflict" in game_state.get("completed_scenarios", []):
        return generate_random_event()
    
    # Create the starting conflict event
    return GameEvent(
        type="story",
        description="""
        As your ship, the *Ecliptica*, drifts through the cold void of space, a distress signal breaks the silence.
        The message crackles through your comms: "This is the merchant vessel 'Star Wanderer'. We're experiencing critical system failures.
        Any ships in range, please respond. We have valuable cargo and can offer compensation for assistance."
        """,
        choices=[
            EventChoice(
                description="Respond to the distress call and offer assistance",
                rewards={'credits': 200, 'items': ['Rare Components']},
                costs={'fuel': -20},
                morale_change=1,
                message="You successfully assist the merchant vessel and are rewarded for your help."
            ),
            EventChoice(
                description="Investigate from a distance first",
                costs={'time': 1},
                message="You cautiously observe the situation from a safe distance."
            ),
            EventChoice(
                description="Ignore the distress call and continue your journey",
                morale_change=-2,
                message="Your crew is disappointed by your decision to ignore those in need."
            )
        ]
    )

def generate_random_event() -> GameEvent:
    """Generate a random event with proper initialization."""
    event_types = ["exploration", "combat", "social", "trade", "quest"]
    event_type = random.choice(event_types)
    
    # Create base event context
    context = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "location": "current_area",  # This would be updated with actual location
        "event_type": event_type
    }
    
    events = {
        "exploration": GameEvent(
            type="exploration",
            description="You discover an intriguing area in the cyberpunk cityscape.",
            context=context
        ),
        "combat": GameEvent(
            type="combat",
            description="You encounter potential hostiles in the neon-lit streets.",
            context=context
        ),
        "social": GameEvent(
            type="social",
            description="You come across an interesting character in a local establishment.",
            context=context
        ),
        "trade": GameEvent(
            type="trade",
            description="You find a unique opportunity for business or trade.",
            context=context
        ),
        "quest": GameEvent(
            type="quest",
            description="A potential job opportunity presents itself.",
            context=context
        )
    }
    
    return events[event_type]

def calculate_event_costs(choice, player):
    """Calculate the resource costs for a given choice."""
    costs = {
        'time': {'hours': 0},
        'fuel': 0,
        'supplies': 0,
        'health': 0,
        'credits': 0,
        'reputation': 0
    }
    
    if choice == "1":  # Respond to signal
        costs['fuel'] = -20
        costs['time']['hours'] = 2
        if "Endurance" not in player['strengths']:
            costs['health'] = -10
    elif choice == "2":  # Find shelter
        costs['fuel'] = -10
        costs['time']['hours'] = 4
        costs['supplies'] = -5
    elif choice == "3":  # Return to station
        costs['fuel'] = -30
        costs['time']['hours'] = 6
        costs['credits'] = -100
        costs['reputation'] = -5
    
    return costs

def calculate_event_rewards(choice, player, success=True):
    """Calculate rewards for event choices."""
    rewards = {
        'items': [],
        'credits': 0,
        'special_rewards': None
    }
    
    # Base difficulty based on choice
    difficulty = {
        "1": "Hard",    # Responding to signal (risky but potentially more rewarding)
        "2": "Normal",  # Finding shelter (moderate risk and reward)
        "3": "Easy"     # Returning to station (safe but less rewarding)
    }[choice]
    
    # Generate rewards based on difficulty and success
    if success:
        quest_reward = generate_quest_reward(difficulty)
        rewards['credits'] = quest_reward['credits']
        rewards['items'].extend(quest_reward['items'])
        if 'special_reward' in quest_reward:
            rewards['special_rewards'] = quest_reward['special_reward']
            
        # Bonus reward for brave choices
        if choice == "1" and "Bravery" in player.get('personality', {}).get('traits', []):
            bonus_item = generate_random_item(min_rarity="Rare")
            rewards['items'].append(bonus_item)
    else:
        # Even on failure, give some compensation
        rewards['credits'] = 50  # Base compensation
        if random.random() < 0.3:  # 30% chance for consolation item
            rewards['items'].append(generate_random_item("Common"))
    
    return rewards

def handle_special_reward(player, special_reward):
    """Handle special rewards like maps, blueprints, etc."""
    if special_reward == "map_fragment":
        if "discovered_locations" not in player:
            player["discovered_locations"] = []
        # Generate a new treasure and add its location
        treasure = generate_treasure("Normal")
        player["discovered_locations"].append(treasure.to_dict())
        print(f"\nSpecial Reward: Found a map fragment revealing {treasure.name}!")
        print(f"Description: {treasure.description}")
        print(f"Location: X:{treasure.location['x']:.1f}, Y:{treasure.location['y']:.1f}, Z:{treasure.location['z']:.1f}")
    
    elif special_reward == "rare_blueprint":
        if "blueprints" not in player:
            player["blueprints"] = []
        blueprint = generate_random_item("Epic")
        player["blueprints"].append(blueprint.to_dict())
        print(f"\nSpecial Reward: Acquired blueprint for {blueprint.name}!")
    
    elif special_reward == "faction_reputation":
        reputation_gain = random.randint(5, 15)
        player["resources"]["reputation"] += reputation_gain
        print(f"\nSpecial Reward: Gained {reputation_gain} reputation with the local faction!")
    
    elif special_reward == "special_weapon":
        weapon = generate_random_item("Legendary")
        add_item_to_inventory(player, weapon)
        print("\nSpecial Reward: Found a legendary weapon!")
    
    elif special_reward == "unique_ability":
        if "abilities" not in player:
            player["abilities"] = []
        new_ability = random.choice([
            "Time Manipulation",
            "Energy Absorption",
            "Matter Conversion",
            "Quantum Tunneling",
            "Neural Override"
        ])
        player["abilities"].append(new_ability)
        print(f"\nSpecial Reward: Learned the {new_ability} ability!")