"""
NPC Manager Module
================

Handles the management of Non-Player Characters (NPCs) in the game world.
Stores and manages NPC data, relationships, and story progression.
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

class NPCManager:
    def __init__(self, npcs_directory: str = "npcs"):
        """Initialize the NPC manager."""
        self.npcs_directory = npcs_directory
        if not os.path.exists(npcs_directory):
            os.makedirs(npcs_directory)

    def create_npc(self, npc_id: str, data: Dict[str, Any]) -> bool:
        """Create a new NPC with initial data."""
        npc_path = os.path.join(self.npcs_directory, f"{npc_id}.json")
        if os.path.exists(npc_path):
            return False

        npc_data = {
            "id": npc_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "data": data,
            "story_progression": [],
            "relationships": {},
            "conversation_history": []
        }

        with open(npc_path, 'w', encoding='utf-8') as f:
            json.dump(npc_data, f, indent=4)
        return True

    def get_npc(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """Get NPC data by ID."""
        npc_path = os.path.join(self.npcs_directory, f"{npc_id}.json")
        if not os.path.exists(npc_path):
            return None

        with open(npc_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def update_npc(self, npc_id: str, data: Dict[str, Any]) -> bool:
        """Update NPC data."""
        npc_data = self.get_npc(npc_id)
        if not npc_data:
            return False

        npc_data["data"].update(data)
        npc_data["last_updated"] = datetime.now().isoformat()

        npc_path = os.path.join(self.npcs_directory, f"{npc_id}.json")
        with open(npc_path, 'w', encoding='utf-8') as f:
            json.dump(npc_data, f, indent=4)
        return True

    def add_story_event(self, npc_id: str, event: Dict[str, Any]) -> bool:
        """Add a story progression event for the NPC."""
        npc_data = self.get_npc(npc_id)
        if not npc_data:
            return False

        event["timestamp"] = datetime.now().isoformat()
        npc_data["story_progression"].append(event)
        npc_data["last_updated"] = datetime.now().isoformat()

        npc_path = os.path.join(self.npcs_directory, f"{npc_id}.json")
        with open(npc_path, 'w', encoding='utf-8') as f:
            json.dump(npc_data, f, indent=4)
        return True

    def update_relationship(self, npc_id: str, other_id: str, relationship_data: Dict[str, Any]) -> bool:
        """Update relationship between NPCs or with the player."""
        npc_data = self.get_npc(npc_id)
        if not npc_data:
            return False

        npc_data["relationships"][other_id] = {
            "status": relationship_data.get("status", "neutral"),
            "trust_level": relationship_data.get("trust_level", 0),
            "last_interaction": datetime.now().isoformat(),
            "notes": relationship_data.get("notes", ""),
            "history": npc_data["relationships"].get(other_id, {}).get("history", []) + [
                {
                    "timestamp": datetime.now().isoformat(),
                    "change": relationship_data.get("change_description", "Relationship updated")
                }
            ]
        }

        npc_path = os.path.join(self.npcs_directory, f"{npc_id}.json")
        with open(npc_path, 'w', encoding='utf-8') as f:
            json.dump(npc_data, f, indent=4)
        return True

    def add_conversation(self, npc_id: str, conversation_data: Dict[str, Any]) -> bool:
        """Add a conversation entry to NPC's history."""
        npc_data = self.get_npc(npc_id)
        if not npc_data:
            return False

        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "content": conversation_data.get("content", ""),
            "location": conversation_data.get("location", "unknown"),
            "context": conversation_data.get("context", {}),
            "important_points": conversation_data.get("important_points", [])
        }

        npc_data["conversation_history"].append(conversation_entry)
        npc_data["last_updated"] = datetime.now().isoformat()

        npc_path = os.path.join(self.npcs_directory, f"{npc_id}.json")
        with open(npc_path, 'w', encoding='utf-8') as f:
            json.dump(npc_data, f, indent=4)
        return True

    def list_npcs(self) -> List[str]:
        """List all available NPCs."""
        return [f.split('.')[0] for f in os.listdir(self.npcs_directory) 
                if f.endswith('.json')]
