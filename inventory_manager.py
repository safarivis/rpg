"""
Inventory Management System for RPG Game
"""
from typing import Dict, List, Optional, Union
import json
import os

def load_player_data(name: str) -> Optional[Dict]:
    """Load player data from JSON file."""
    try:
        file_path = f"{name}.json"
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading player data: {e}")
    return None

def save_player_data(player_data: Dict) -> bool:
    """Save player data to JSON file."""
    try:
        file_path = f"{player_data['name']}.json"
        with open(file_path, 'w') as f:
            json.dump(player_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving player data: {e}")
        return False

def add_item_to_inventory(player_name: str, item: str, quantity: int = 1) -> bool:
    """Add an item to player's inventory."""
    player_data = load_player_data(player_name)
    if not player_data:
        return False
    
    if 'inventory' not in player_data:
        player_data['inventory'] = []
    
    for _ in range(quantity):
        player_data['inventory'].append(item)
    
    return save_player_data(player_data)

def remove_item_from_inventory(player_name: str, item: str, quantity: int = 1) -> bool:
    """Remove an item from player's inventory."""
    player_data = load_player_data(player_name)
    if not player_data or 'inventory' not in player_data:
        return False
    
    removed = 0
    for _ in range(quantity):
        if item in player_data['inventory']:
            player_data['inventory'].remove(item)
            removed += 1
    
    if removed > 0:
        return save_player_data(player_data)
    return False

def get_inventory(player_name: str) -> List[str]:
    """Get the player's current inventory."""
    player_data = load_player_data(player_name)
    if player_data and 'inventory' in player_data:
        return player_data['inventory']
    return []

def has_item(player_name: str, item: str) -> bool:
    """Check if player has a specific item."""
    inventory = get_inventory(player_name)
    return item in inventory

def get_item_count(player_name: str, item: str) -> int:
    """Get the count of a specific item in inventory."""
    inventory = get_inventory(player_name)
    return inventory.count(item)

def modify_credits(player_name: str, amount: int) -> bool:
    """Modify player's credits (positive for adding, negative for subtracting)."""
    player_data = load_player_data(player_name)
    if not player_data:
        return False
    
    if 'resources' not in player_data:
        player_data['resources'] = {'credits': 0}
    elif 'credits' not in player_data['resources']:
        player_data['resources']['credits'] = 0
    
    # Check if player has enough credits for deduction
    if amount < 0 and abs(amount) > player_data['resources']['credits']:
        return False
    
    player_data['resources']['credits'] += amount
    return save_player_data(player_data)

def can_afford(player_name: str, cost: int) -> bool:
    """Check if player can afford a purchase."""
    player_data = load_player_data(player_name)
    if not player_data or 'resources' not in player_data:
        return False
    return player_data['resources'].get('credits', 0) >= cost

def purchase_item(player_name: str, item: str, cost: int) -> bool:
    """Handle a complete purchase transaction."""
    if not can_afford(player_name, cost):
        return False
    
    # First deduct credits
    if not modify_credits(player_name, -cost):
        return False
    
    # Then add item to inventory
    if not add_item_to_inventory(player_name, item):
        # Rollback credits if adding item fails
        modify_credits(player_name, cost)
        return False
    
    return True
