"""
Character Manager Module
======================

This module handles all aspects of character data persistence and management in the RPG game.
It provides a robust system for saving, loading, and tracking character progression over time.

Key Features:
------------
1. Character Data Persistence:
   - Saves character state to JSON files
   - Maintains character history logs
   - Tracks significant changes and events

2. Character State Management:
   - Stats (health, credits, etc.)
   - Skills and attributes
   - Inventory and equipment
   - Relationships and reputation
   - Quest progress
   - Combat statistics

3. History Tracking:
   - Logs important character events
   - Records significant decisions
   - Tracks character progression
   - Maintains relationship changes

4. Conversation History and Context:
   - Saves conversation history
   - Saves current conversation context

Directory Structure:
------------------
characters/
├── [character_name]/
│   ├── character.json  # Current character state
│   └── history.json    # Character progression log

Usage:
-----
```python
# Initialize the manager
manager = CharacterManager()

# Load a character
character_data = manager.load_character("player_name")

# Update and save character data
manager.save_character(character_data, conversation_history, current_context)
```

Integration:
-----------
This module is primarily used by the LLMService to maintain character
persistence and provide character context for the AI's responses.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class CharacterManager:
    def __init__(self, save_directory: str = "characters"):
        """Initialize the character manager with a save directory."""
        self.save_directory = save_directory
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

    def save_character(self, character_data: Dict[str, Any], conversation_history: Optional[list] = None, current_context: Optional[Dict[str, Any]] = None) -> None:
        """Save character data along with conversation history and context."""
        if not character_data.get('name'):
            raise ValueError("Character must have a name")

        # Add conversation history and context to the save data
        save_data = {
            'character': character_data,
            'conversation_history': conversation_history or [],
            'current_context': current_context or {},
            'last_saved': datetime.now().isoformat()
        }

        filename = f"{character_data['name'].lower()}.json"
        filepath = os.path.join(self.save_directory, filename)
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=4)
        print(f"Character saved as '{filename}'!")

    def load_character(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Load character data including conversation history and context."""
        filename = f"{character_name.lower()}.json"
        filepath = os.path.join(self.save_directory, filename)
        
        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r') as f:
            save_data = json.load(f)

        return {
            'character': save_data.get('character', {}),
            'conversation_history': save_data.get('conversation_history', []),
            'current_context': save_data.get('current_context', {})
        }

    def delete_character(self, character_name: str) -> bool:
        """Delete a character's save file."""
        filename = f"{character_name.lower()}.json"
        filepath = os.path.join(self.save_directory, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def list_characters(self) -> list:
        """List all saved characters."""
        characters = []
        for filename in os.listdir(self.save_directory):
            if filename.endswith('.json'):
                characters.append(filename[:-5])  # Remove .json extension
        return characters

    def get_character_template(self) -> Dict[str, Any]:
        """Get a template for creating a new character."""
        return {
            'name': '',
            'created_at': datetime.now().isoformat(),
            'health': 100,
            'max_health': 100,
            'credits': 1000,
            'inventory': [],
            'equipped_items': {},
            'skills': {
                'hacking': 0,
                'combat': 0,
                'stealth': 0,
                'negotiation': 0,
                'tech': 0
            },
            'attributes': {
                'strength': 10,
                'agility': 10,
                'intelligence': 10,
                'charisma': 10,
                'endurance': 10
            },
            'experience': 0,
            'level': 1,
            'background': '',
            'reputation': {},
            'relationships': {},
            'quests': {
                'active': [],
                'completed': []
            },
            'current_location': 'starting_area',
            'visited_locations': ['starting_area'],
            'story_flags': {},  # Track story decisions and progress
            'combat_stats': {
                'kills': 0,
                'deaths': 0,
                'damage_dealt': 0,
                'damage_taken': 0
            },
            'playtime': 0,
            'achievements': []
        }

    def _update_character_log(self, character_name: str, new_data: Dict[str, Any]) -> None:
        """Update character history log with significant changes."""
        log_file = os.path.join(self.save_directory, character_name, "history.json")
        
        # Load existing history
        try:
            with open(log_file, 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []

        # Create new log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'changes': self._detect_significant_changes(new_data),
            'stats': {
                'health': new_data.get('health'),
                'credits': new_data.get('credits'),
                'location': new_data.get('current_location'),
                'reputation': new_data.get('reputation', {})
            }
        }
        
        history.append(log_entry)
        
        # Save updated history
        with open(log_file, 'w') as f:
            json.dump(history, f, indent=4)

    def _detect_significant_changes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect significant changes in character data."""
        significant_changes = {}
        
        # Track important changes
        tracked_fields = [
            'health', 'credits', 'inventory', 'quests',
            'relationships', 'skills', 'reputation'
        ]
        
        for field in tracked_fields:
            if field in data:
                significant_changes[field] = data[field]
        
        return significant_changes
