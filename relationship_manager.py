from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Relationship:
    """Represents a relationship with a character."""
    character_id: str
    affinity: int = 0  # -100 to 100
    relationship_type: str = "neutral"  # friendly, neutral, hostile
    shared_experiences: List[str] = field(default_factory=list)
    development_opportunities: List[str] = field(default_factory=list)

    def update_affinity(self, amount):
        """Update relationship affinity within bounds."""
        self.affinity = max(-100, min(100, self.affinity + amount))
        
        # Update relationship type based on affinity
        if self.affinity >= 30:
            self.relationship_type = "friendly"
        elif self.affinity <= -30:
            self.relationship_type = "hostile"
        else:
            self.relationship_type = "neutral"

    def add_experience(self, experience):
        """Add a shared experience to the relationship."""
        self.shared_experiences.append(experience)

    def get_status(self) -> Dict:
        """Get the current status of the relationship."""
        return {
            "affinity": self.affinity,
            "type": self.relationship_type,
            "experiences": len(self.shared_experiences),
            "opportunities": len(self.development_opportunities)
        }

@dataclass
class RelationshipManager:
    """Manages relationships with NPCs and crew members."""
    relationships: Dict[str, Relationship] = field(default_factory=dict)

    def get_or_create_relationship(self, character_id: str) -> Relationship:
        """Get existing relationship or create new one."""
        if character_id not in self.relationships:
            self.relationships[character_id] = Relationship(character_id)
        return self.relationships[character_id]

    def update_relationship(self, character_id: str, affinity_change: int, experience: Optional[str] = None):
        """Update relationship with a character."""
        relationship = self.get_or_create_relationship(character_id)
        relationship.update_affinity(affinity_change)
        if experience:
            relationship.add_experience(experience)

    def get_relationship_status(self, character_id: str) -> Dict:
        """Get the status of a relationship."""
        if character_id in self.relationships:
            return self.relationships[character_id].get_status()
        return None

    def get_all_relationships(self) -> Dict[str, Dict]:
        """Get status of all relationships."""
        return {char_id: rel.get_status() for char_id, rel in self.relationships.items()}
