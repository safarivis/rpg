"""
Status Management System for RPG Game
Handles displaying changes to player stats, inventory, and relationships
"""
from typing import Dict, Any, Union, List
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

class StatusManager:
    def __init__(self):
        self.previous_state = {}
        
    def update_state(self, player_data: Dict[str, Any]) -> None:
        """Update the previous state with new player data."""
        if not self.previous_state:
            # First time initialization
            self.previous_state = self._get_comparable_state(player_data)
            return
            
        new_state = self._get_comparable_state(player_data)
        self._show_changes(new_state)
        self.previous_state = new_state
        
    def _get_comparable_state(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant stats for comparison."""
        return {
            'health': player_data.get('health', 100),
            'credits': player_data.get('resources', {}).get('credits', 0),
            'inventory': set(player_data.get('inventory', [])),
            'relationships': player_data.get('relationships', {}),
            'skills': player_data.get('skills', []),
            'knowledge': player_data.get('knowledge', []),
            'location': player_data.get('location', 'Unknown'),
            'reputation': player_data.get('resources', {}).get('reputation', 0)
        }
        
    def _show_changes(self, new_state: Dict[str, Any]) -> None:
        """Display any changes in player state."""
        changes = []
        
        # Check numeric stats
        for stat in ['health', 'credits', 'reputation']:
            old_val = self.previous_state.get(stat, 0)
            new_val = new_state.get(stat, 0)
            if old_val != new_val:
                diff = new_val - old_val
                color = Fore.GREEN if diff > 0 else Fore.RED
                changes.append(f"{stat.title()}: {color}{diff:+d}{Style.RESET_ALL}")
        
        # Check inventory changes
        old_inv = self.previous_state.get('inventory', set())
        new_inv = new_state.get('inventory', set())
        added_items = new_inv - old_inv
        removed_items = old_inv - new_inv
        
        for item in added_items:
            changes.append(f"Added to inventory: {Fore.GREEN}{item}{Style.RESET_ALL}")
        for item in removed_items:
            changes.append(f"Removed from inventory: {Fore.RED}{item}{Style.RESET_ALL}")
            
        # Check relationship changes
        old_rel = self.previous_state.get('relationships', {})
        new_rel = new_state.get('relationships', {})
        for npc, status in new_rel.items():
            if npc not in old_rel:
                changes.append(f"New relationship: {Fore.CYAN}{npc}{Style.RESET_ALL} ({status})")
            elif old_rel[npc] != status:
                changes.append(f"Relationship changed - {npc}: {old_rel[npc]} → {status}")
                
        # Check skill changes
        old_skills = set(self.previous_state.get('skills', []))
        new_skills = set(new_state.get('skills', []))
        new_learned = new_skills - old_skills
        for skill in new_learned:
            changes.append(f"Learned new skill: {Fore.YELLOW}{skill}{Style.RESET_ALL}")
            
        # Check knowledge changes
        old_knowledge = set(self.previous_state.get('knowledge', []))
        new_knowledge = set(new_state.get('knowledge', []))
        new_info = new_knowledge - old_knowledge
        for info in new_info:
            changes.append(f"Gained knowledge: {Fore.BLUE}{info}{Style.RESET_ALL}")
            
        # Check location changes
        if new_state.get('location') != self.previous_state.get('location'):
            changes.append(f"Location: {self.previous_state.get('location', 'Unknown')} → {new_state.get('location', 'Unknown')}")
            
        # Display all changes
        if changes:
            print("\n=== STATUS UPDATE ===")
            for change in changes:
                print(change)
            print("====================")
