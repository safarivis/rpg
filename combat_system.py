from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random
import json
import requests

@dataclass
class Ability:
    name: str
    damage_range: tuple[int, int]
    cooldown: int = 0
    current_cooldown: int = 0
    special_effects: Dict[str, any] = field(default_factory=dict)
    description: str = ""

@dataclass
class CombatEntity:
    name: str
    max_health: int
    current_health: int
    abilities: Dict[str, Ability]
    status_effects: Dict[str, int] = field(default_factory=dict)
    buffs: Dict[str, Dict[str, any]] = field(default_factory=dict)
    
    def is_alive(self) -> bool:
        return self.current_health > 0
    
    def apply_damage(self, damage: int):
        self.current_health = max(0, self.current_health - damage)
    
    def heal(self, amount: int):
        self.current_health = min(self.max_health, self.current_health + amount)
    
    def apply_status_effect(self, effect: str, duration: int):
        self.status_effects[effect] = duration
    
    def apply_buff(self, buff_name: str, effect: Dict[str, any], duration: int):
        self.buffs[buff_name] = {"effect": effect, "duration": duration}
    
    def update_cooldowns(self):
        for ability in self.abilities.values():
            if ability.current_cooldown > 0:
                ability.current_cooldown -= 1
    
    def update_status_effects(self):
        # Update duration of status effects and remove expired ones
        expired = []
        for effect, duration in self.status_effects.items():
            if duration <= 1:
                expired.append(effect)
            else:
                self.status_effects[effect] = duration - 1
        
        for effect in expired:
            del self.status_effects[effect]
        
        # Update buffs
        expired_buffs = []
        for buff_name, buff_data in self.buffs.items():
            if buff_data["duration"] <= 1:
                expired_buffs.append(buff_name)
            else:
                buff_data["duration"] -= 1
        
        for buff in expired_buffs:
            del self.buffs[buff]

class CombatSystem:
    def __init__(self, player: Dict[str, any], opponent: Dict[str, any]):
        """Initialize combat system with player and opponent."""
        # Convert player and opponent to combat entities
        self.player = CombatEntity(
            name=player["name"],
            max_health=300,  # Default player health
            current_health=300,
            abilities={
                "Sword Strike": Ability("Sword Strike", (20, 40), description="A powerful sword attack"),
                "Shield Bash": Ability("Shield Bash", (10, 20), description="A stunning shield attack"),
                "War Cry": Ability("War Cry", (0, 0), description="Boost damage for 2 turns")
            }
        )
        
        self.opponent = CombatEntity(
            name=opponent["name"],
            max_health=opponent.get("hp", 100),
            current_health=opponent.get("hp", 100),
            abilities={name: Ability(name, (15, 25), description=desc) 
                      for name, desc in opponent.get("abilities", {}).items()}
        )
        
        self.turn_number = 1
        self.combat_log = []
        self.dialogue_history = []
        
    def handle_dialogue(self, message: str) -> str:
        """Handle player dialogue with the opponent."""
        # Store the dialogue
        self.dialogue_history.append({"speaker": "player", "message": message})
        
        # Generate opponent response based on personality
        response = f"*{self.opponent.name} responds:*\n\n"
        response += f"I am {self.opponent.name}, and I shall be your doom!"
        
        # Store the response
        self.dialogue_history.append({"speaker": "opponent", "message": response})
        return response
        
    def handle_combat_action(self, action: str) -> str:
        """Handle a combat action."""
        if action == "status":
            return self.get_status_string()
            
        # Handle ability usage
        if action in self.player.abilities:
            ability = self.player.abilities[action]
            if ability.current_cooldown > 0:
                return f"{action} is on cooldown for {ability.current_cooldown} more turns!"
                
            # Calculate and apply damage
            damage = random.randint(*ability.damage_range)
            self.opponent.apply_damage(damage)
            
            # Apply cooldown
            ability.current_cooldown = ability.cooldown
            
            # Generate result message
            result = f"You use {action} and deal {damage} damage to {self.opponent.name}!"
            
            # Handle opponent turn
            if self.opponent.is_alive():
                # Choose random opponent ability
                opp_ability = random.choice(list(self.opponent.abilities.values()))
                opp_damage = random.randint(*opp_ability.damage_range)
                self.player.apply_damage(opp_damage)
                result += f"\n\n{self.opponent.name} uses {opp_ability.name} and deals {opp_damage} damage to you!"
            
            # Update turn counter
            self.turn_number += 1
            return result
            
        return "Invalid action!"
        
    def is_combat_finished(self) -> bool:
        """Check if the combat is finished."""
        return not self.player.is_alive() or not self.opponent.is_alive()
        
    def get_combat_state(self) -> Dict[str, any]:
        """Get the current state of combat."""
        return {
            "turn_number": self.turn_number,
            "player_hp": self.player.current_health,
            "player_max_hp": self.player.max_health,
            "opponent_hp": self.opponent.current_health,
            "opponent_max_hp": self.opponent.max_health,
            "available_actions": ["talk", "status"] + [
                ability for ability, data in self.player.abilities.items()
                if data.current_cooldown == 0
            ],
            "ability_descriptions": {
                name: ability.description
                for name, ability in self.player.abilities.items()
            }
        }
        
    def get_status_string(self) -> str:
        """Get a detailed status string."""
        status = f"\nCombat Status - Turn {self.turn_number}\n"
        status += "-" * 40 + "\n"
        status += f"{self.player.name}: {self.player.current_health}/{self.player.max_health} HP\n"
        status += f"{self.opponent.name}: {self.opponent.current_health}/{self.opponent.max_health} HP\n\n"
        
        status += "Your abilities:\n"
        for name, ability in self.player.abilities.items():
            cooldown = f"(Cooldown: {ability.current_cooldown})" if ability.current_cooldown > 0 else "(Ready)"
            status += f"{name}: {ability.description} {cooldown}\n"
            
        if self.player.status_effects:
            status += "\nStatus Effects:\n"
            for effect, duration in self.player.status_effects.items():
                status += f"{effect}: {duration} turns remaining\n"
                
        return status
