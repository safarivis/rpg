"""
Module for handling items, equipment, and rewards in the RPG game.
"""
import random
import json
from typing import Dict, List, Optional

# Item rarity levels and their probabilities
RARITY_LEVELS = {
    "Common": 0.5,
    "Uncommon": 0.25,
    "Rare": 0.15,
    "Epic": 0.08,
    "Legendary": 0.02
}

# Base item types and their properties
ITEM_TYPES = {
    "weapon": {
        "attributes": ["damage", "range", "speed"],
        "slots": ["primary", "secondary"],
        "examples": {
            "Common": ["Rusty Blaster", "Basic Sword", "Standard Rifle"],
            "Uncommon": ["Plasma Pistol", "Energy Blade", "Precision Rifle"],
            "Rare": ["Quantum Disruptor", "Phase Blade", "Particle Cannon"],
            "Epic": ["Void Reaper", "Star Slicer", "Galaxy Driver"],
            "Legendary": ["The Annihilator", "Cosmic Cleaver", "Nova Nemesis"]
        }
    },
    "armor": {
        "attributes": ["defense", "mobility", "shield"],
        "slots": ["head", "chest", "legs", "arms"],
        "examples": {
            "Common": ["Basic Shield", "Light Armor", "Standard Helmet"],
            "Uncommon": ["Energy Shield", "Reinforced Suit", "Combat Helmet"],
            "Rare": ["Quantum Barrier", "Nano-weave Armor", "Neural Helm"],
            "Epic": ["Void Shield", "Stellar Plate", "Cosmic Crown"],
            "Legendary": ["The Impenetrable", "Celestial Shell", "Crown of Eternity"]
        }
    },
    "consumable": {
        "attributes": ["healing", "buff_duration", "effect_power"],
        "examples": {
            "Common": ["Health Pack", "Energy Cell", "Repair Kit"],
            "Uncommon": ["Advanced Medkit", "Shield Booster", "Quantum Cell"],
            "Rare": ["Regeneration Matrix", "Time Dilation Device", "Neural Enhancer"],
            "Epic": ["Phoenix Protocol", "Reality Anchor", "Mind Matrix"],
            "Legendary": ["Lazarus Protocol", "Time Loop Generator", "God Mode Matrix"]
        }
    },
    "quest_item": {
        "attributes": ["quest_id", "value"],
        "examples": {
            "Common": ["Data Pad", "Access Card", "Star Map Fragment"],
            "Uncommon": ["Encrypted Drive", "Security Clearance", "Ancient Tablet"],
            "Rare": ["AI Core", "Void Crystal", "Prophet's Scroll"],
            "Epic": ["Reality Shard", "Dragon Heart", "Elder Scroll"],
            "Legendary": ["Universal Core", "Creation Seed", "Infinity Matrix"]
        }
    }
}

class Item:
    def __init__(self, name: str, item_type: str, rarity: str, attributes: Dict = None):
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.attributes = attributes or {}
        self.value = self._calculate_value()
        
    def _calculate_value(self) -> int:
        """Calculate item value based on rarity and attributes."""
        rarity_multiplier = {
            "Common": 1,
            "Uncommon": 2,
            "Rare": 5,
            "Epic": 10,
            "Legendary": 25
        }
        base_value = rarity_multiplier[self.rarity] * 100
        attr_value = sum(self.attributes.values()) if self.attributes else 0
        return base_value + attr_value

    def to_dict(self) -> Dict:
        """Convert item to dictionary for storage."""
        return {
            "name": self.name,
            "type": self.item_type,
            "rarity": self.rarity,
            "attributes": self.attributes,
            "value": self.value
        }

def generate_random_item(min_rarity: str = "Common") -> Item:
    """Generate a random item with specified minimum rarity."""
    # Filter rarities based on minimum
    rarities = list(RARITY_LEVELS.keys())
    min_idx = rarities.index(min_rarity)
    possible_rarities = rarities[min_idx:]
    
    # Select rarity based on weighted probabilities
    rarity = random.choices(
        possible_rarities,
        [RARITY_LEVELS[r] for r in possible_rarities]
    )[0]
    
    # Select item type and generate attributes
    item_type = random.choice(list(ITEM_TYPES.keys()))
    item_data = ITEM_TYPES[item_type]
    
    # Generate name from examples or create a new one
    name = random.choice(item_data["examples"][rarity])
    
    # Generate random attributes
    attributes = {}
    if "attributes" in item_data:
        for attr in item_data["attributes"]:
            base_value = random.randint(1, 10)
            rarity_multiplier = rarities.index(rarity) + 1
            attributes[attr] = base_value * rarity_multiplier
    
    return Item(name, item_type, rarity, attributes)

class Treasure:
    def __init__(self, name: str, description: str, contents: List[Item], location: Dict[str, float]):
        self.name = name
        self.description = description
        self.contents = contents
        self.location = location  # {"x": float, "y": float, "z": float}
        self.discovered = False
        self.claimed = False

    def to_dict(self) -> Dict:
        """Convert treasure to dictionary for storage."""
        return {
            "name": self.name,
            "description": self.description,
            "contents": [item.to_dict() for item in self.contents],
            "location": self.location,
            "discovered": self.discovered,
            "claimed": self.claimed
        }

def generate_treasure(difficulty: str = "Normal") -> Treasure:
    """Generate a treasure with appropriate rewards based on difficulty."""
    difficulty_settings = {
        "Easy": {"items": (1, 3), "min_rarity": "Common"},
        "Normal": {"items": (2, 4), "min_rarity": "Uncommon"},
        "Hard": {"items": (3, 5), "min_rarity": "Rare"},
        "Epic": {"items": (4, 6), "min_rarity": "Epic"}
    }
    
    settings = difficulty_settings[difficulty]
    num_items = random.randint(*settings["items"])
    
    # Generate items
    items = [generate_random_item(settings["min_rarity"]) for _ in range(num_items)]
    
    # Generate treasure name and description
    treasure_types = ["Cache", "Vault", "Stash", "Trove", "Hoard"]
    treasure_name = f"{random.choice(['Ancient', 'Hidden', 'Secret', 'Lost', 'Forgotten'])} {random.choice(treasure_types)}"
    description = f"A {difficulty.lower()} difficulty treasure containing {num_items} items."
    
    # Random location in 3D space
    location = {
        "x": random.uniform(-1000, 1000),
        "y": random.uniform(-1000, 1000),
        "z": random.uniform(-1000, 1000)
    }
    
    return Treasure(treasure_name, description, items, location)

def add_item_to_inventory(player: Dict, item: Item) -> None:
    """Add an item to the player's inventory."""
    if "inventory" not in player:
        player["inventory"] = []
    
    player["inventory"].append(item.to_dict())
    print(f"\nAcquired: {item.name} ({item.rarity})")
    if item.attributes:
        print("Attributes:")
        for attr, value in item.attributes.items():
            print(f"- {attr}: {value}")

def add_credits(player: Dict, amount: int) -> None:
    """Add credits to the player's account."""
    if "resources" not in player:
        player["resources"] = {"credits": 0}
    elif "credits" not in player["resources"]:
        player["resources"]["credits"] = 0
    
    player["resources"]["credits"] += amount
    print(f"\nCredits {'gained' if amount > 0 else 'lost'}: {abs(amount)}")
    print(f"Current balance: {player['resources']['credits']}")

def generate_quest_reward(difficulty: str = "Normal") -> Dict:
    """Generate a quest reward including items, credits, and possibly special rewards."""
    difficulty_multiplier = {
        "Easy": 1,
        "Normal": 2,
        "Hard": 3,
        "Epic": 5
    }
    
    multiplier = difficulty_multiplier[difficulty]
    
    reward = {
        "credits": random.randint(100, 500) * multiplier,
        "items": [generate_random_item(difficulty_settings[difficulty]["min_rarity"])
                 for difficulty_settings in [{"Easy": {"min_rarity": "Common"},
                                           "Normal": {"min_rarity": "Uncommon"},
                                           "Hard": {"min_rarity": "Rare"},
                                           "Epic": {"min_rarity": "Epic"}}]],
        "experience": random.randint(50, 200) * multiplier
    }
    
    # Chance for special reward
    if random.random() < 0.2:  # 20% chance
        special_rewards = [
            "map_fragment",
            "rare_blueprint",
            "faction_reputation",
            "special_weapon",
            "unique_ability"
        ]
        reward["special_reward"] = random.choice(special_rewards)
    
    return reward
