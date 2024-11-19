import random

class StoryEngine:
    def __init__(self, player):
        self.player = player
        self.story_state = {
            "current_chapter": 0,
            "world_state": "peace",
            "consequences": [],
            "past_events": []
        }

    def generate_chapter(self):
        """Generate the next chapter with dynamic elements."""
        self.story_state["current_chapter"] += 1
        chapter = {
            "title": f"Chapter {self.story_state['current_chapter']}",
            "description": f"The world is in a state of {self.story_state['world_state']}.",
            "choices": self._generate_choices(),
            "relevant_npcs": self._get_relevant_npcs(),
            "random_events": self._generate_random_events()
        }
        return chapter

    def _generate_choices(self):
        """Create skill-based choices for the current chapter."""
        choices = []
        if "Charisma" in self.player["skills"]:
            choices.append({"id": "negotiate", "text": "Attempt to negotiate", "skill_check": "Charisma"})
        if "Perception" in self.player["skills"]:
            choices.append({"id": "investigate", "text": "Investigate a suspicious situation", "skill_check": "Perception"})
        if "Weapons Mastery" in self.player["skills"]:
            choices.append({"id": "fight", "text": "Engage in combat", "skill_check": "Weapons Mastery"})
        return choices

    def _get_relevant_npcs(self):
        """Find NPCs relevant to the chapter based on loyalty."""
        relevant_npcs = []
        for npc, details in self.player["relationships"].items():
            if details["loyalty"] > 0:
                relevant_npcs.append({"name": npc, "attitude": "friendly", "can_help": True})
            else:
                relevant_npcs.append({"name": npc, "attitude": "hostile", "can_help": False})
        return relevant_npcs

    def _generate_random_events(self):
        """Generate events influenced by player state."""
        events = [
            {"description": "An ambush occurs!", "type": "combat", "requires": "Weapons Mastery"},
            {"description": "A mysterious traveler offers a riddle.", "type": "social", "requires": "Wisdom"},
            {"description": "A hidden trap is detected!", "type": "exploration", "requires": "Perception"}
        ]
        return random.sample(events, 2)

    def resolve_choice(self, choice_id):
        """Resolve a player choice and update story state."""
        success = False
        if choice_id == "negotiate" and self._perform_skill_check("Charisma"):
            success = True
        elif choice_id == "investigate" and self._perform_skill_check("Perception"):
            success = True
        elif choice_id == "fight" and self._perform_skill_check("Weapons Mastery"):
            success = True

        outcome = self._calculate_outcome(success)
        self._update_world_state(outcome)
        self.story_state["past_events"].append(outcome)
        return outcome

    def _perform_skill_check(self, required_skill):
        """Check if the player has the required skill."""
        return required_skill in self.player["skills"]

    def _calculate_outcome(self, success):
        """Determine the outcome of a choice."""
        if success:
            return {"success": True, "effect": "The situation resolves in your favor.", "world_impact": "positive"}
        else:
            return {"success": False, "effect": "The situation becomes more complicated.", "world_impact": "negative"}

    def _update_world_state(self, outcome):
        """Update the world state based on the choice outcome."""
        if outcome["world_impact"] == "positive":
            self.story_state["world_state"] = "stability"
        elif outcome["world_impact"] == "negative":
            self.story_state["world_state"] = "chaos"

    def get_story_summary(self):
        """Provide a summary of the story so far."""
        summary = f"World State: {self.story_state['world_state']}\n"
        summary += "Past Events:\n"
        for i, event in enumerate(self.story_state["past_events"], 1):
            summary += f"{i}. {event['effect']} (Success: {event['success']})\n"
        return summary
