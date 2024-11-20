from typing import Dict, Any, Optional, List
from colorama import init, Fore, Style
import os
import json
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from config import config
from character_manager import CharacterManager
from npc_manager import NPCManager
from datetime import datetime

# Initialize colorama for Windows compatibility
init(convert=True, strip=False)

class LLMService:
    def __init__(self, api_key=None):
        """Initialize the LLM service."""
        if not api_key:
            api_key = os.getenv("LLM_API_KEY")
            if not api_key:
                raise ValueError("LLM API key not found in environment variables")
        
        self.api_key = api_key
        self.client = MistralClient(api_key=self.api_key)
        self.story_context = {
            "quests": [],
            "major_events": [],
            "relationships": {},
            "locations": {},
            "current_plot": None,
            "story_progress": []
        }
        self.conversation_history = []
        self.character_manager = CharacterManager()
        self.npc_manager = NPCManager()
        self.current_character = None
        self.current_character_name = None
        
        if not config.has_valid_api_key:
            raise ValueError("No valid API key found. Please check your .env file.")

    def load_character(self, character_name: str) -> bool:
        """Load a character's data and context."""
        save_data = self.character_manager.load_character(character_name)
        if save_data:
            self.current_character = save_data['character']
            self.current_character_name = character_name
            self.conversation_history = save_data['conversation_history']
            self.story_context = save_data['current_context']
            return True
        return False

    def save_current_character(self) -> bool:
        """Save the current character's state."""
        if self.current_character and self.current_character_name:
            self.character_manager.save_character(
                self.current_character,
                self.conversation_history,
                self.story_context
            )
            return True
        return False

    def update_character_state(self, updates: Dict[str, Any]) -> None:
        """
        Update character state with new information.

        Args:
        updates (Dict[str, Any]): A dictionary of updates to apply to the character state.
        """
        if not self.current_character:
            return
            
        # Update character data
        for key, value in updates.items():
            if key in self.current_character:
                if isinstance(self.current_character[key], dict):
                    self.current_character[key].update(value)
                else:
                    self.current_character[key] = value
        
        # Save after significant updates
        self.save_current_character()

    def _format_character_state(self, player=None):
        """Format character state for LLM context."""
        if not player:
            return "No character data available."
            
        state = [
            f"Name: {player.get('name', 'Unknown')}",
            f"Role: {player.get('role', 'Unknown')}",
            f"Health: {player.get('health', 100)}/100",
            f"Credits: {player.get('credits', 0)}",
            f"Location: {player.get('current_location', 'Unknown')}"
        ]
        
        if player.get('inventory'):
            state.append(f"Inventory: {', '.join(player['inventory'])}")
            
        if player.get('relationships'):
            rels = [f"{name} ({data.get('status', 'Neutral')})" 
                   for name, data in player['relationships'].items()]
            state.append(f"Relationships: {', '.join(rels)}")
            
        return "\n".join(state)

    def _format_quests(self):
        """Format active quests for LLM context."""
        if not self.story_context['quests']:
            return "No active quests"
        return "\n".join([f"- {quest}" for quest in self.story_context['quests']])

    def update_story_context(self, context_update):
        """Update the story context with new information."""
        if isinstance(context_update, dict):
            for key, value in context_update.items():
                if key in self.story_context:
                    if isinstance(value, list):
                        self.story_context[key].extend(value)
                    elif isinstance(value, dict):
                        self.story_context[key].update(value)
                    else:
                        self.story_context[key] = value

    def generate_response(self, prompt, context=None):
        """Generate a response from the LLM."""
        try:
            # Format the context for the prompt
            char_state = self._format_character_state(context.get('player') if context else None)
            conversation_history = self._format_conversation_history()
            story_context = self._format_story_context()
            
            # Build a narrative of recent events
            recent_narrative = self._build_recent_narrative()
            
            # Track major story events and quest progress
            if 'story_progress' not in self.story_context:
                self.story_context['story_progress'] = []
            
            # Track important story beats
            story_beats = {
                'black decoder': 'Acquired the black decoder device',
                'data chip': 'Received encrypted data chip from Eva',
                'cargo': 'Assigned to protect valuable cargo',
                'safe house': 'Moved to safe house location',
                'compromised': 'Cargo and device were compromised'
            }
            
            for beat_key, beat_desc in story_beats.items():
                if beat_key in prompt.lower() or beat_key in recent_narrative.lower():
                    if beat_desc not in self.story_context['story_progress']:
                        self.story_context['story_progress'].append(beat_desc)

            system_prompt = f"""You are the AI Dungeon Master for a cyberpunk RPG game. Your role is to create an immersive, atmospheric experience.

Current Character State:
{char_state}

Story Progress:
{chr(10).join(f"- {event}" for event in self.story_context['story_progress'])}

Recent Events:
{recent_narrative}

Story Context:
{story_context}

Conversation History:
{conversation_history}

Setting: A gritty cyberpunk future where high technology meets low life. Neon lights pierce the perpetual smog, megacorporations rule from gleaming towers, while life on the streets is a daily struggle for survival.

Guidelines:
1. Describe what the player sees, hears, and experiences in vivid detail
2. Include sensory details: smells, sounds, sights, atmosphere
3. Maintain consistency with previous events and character relationships
4. React to player actions with realistic consequences
5. NEVER repeat exact dialogue or scenes
6. Keep track of items, relationships, and story progress
7. NEVER include system messages or DM notes in your responses
8. Continue the scene from where we left off, maintaining consistency with recent events

Remember: You are actively narrating a scene. Never break character or include meta-commentary about being a DM."""

            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                messages=messages,
                model="mistral-tiny",
                temperature=0.7,
                max_tokens=500
            )
            
            # Update conversation history and analyze response
            result = response.choices[0].message.content
            self._update_conversation_history(prompt, result)
            self._analyze_and_update_character(prompt, result)
            
            # Save character state after each interaction
            self.save_current_character()
            
            # Add yellow color to the narrative text
            return f"\033[33m{result}\033[0m"
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "I encountered an error processing your action. Please try again."

    def _format_story_context(self):
        """Format story context for the LLM."""
        context = []
        
        if self.story_context.get('quests'):
            context.append("Active Quests:")
            for quest in self.story_context['quests']:
                context.append(f"- {quest}")
        
        if self.story_context.get('major_events'):
            context.append("\nMajor Events:")
            for event in self.story_context['major_events']:
                context.append(f"- {event}")
        
        if self.story_context.get('relationships'):
            context.append("\nKey Relationships:")
            for name, details in self.story_context['relationships'].items():
                context.append(f"- {name}: {details}")
        
        return "\n".join(context)

    def _format_conversation_history(self):
        """Format recent conversation history for context."""
        if not self.conversation_history:
            return ""
            
        # Get last 3 interactions for context
        recent_history = self.conversation_history[-3:]
        formatted = []
        
        for interaction in recent_history:
            formatted.append(f"Player: {interaction['prompt']}")
            formatted.append(f"Response: {interaction['response']}\n")
            
        return "\n".join(formatted)

    def _update_conversation_history(self, prompt: str, response: str) -> None:
        """Update conversation history with new interaction."""
        self.conversation_history.append({
            'prompt': prompt,
            'response': response
        })
        # Keep only last 5 interactions
        if len(self.conversation_history) > 5:
            self.conversation_history = self.conversation_history[-5:]

    def _analyze_and_update_character(self, prompt: str, response: str) -> None:
        """Analyze interaction and update character state."""
        if not self.current_character:
            return

        # Initialize required dictionaries
        if 'inventory' not in self.current_character:
            self.current_character['inventory'] = []
        if 'relationships' not in self.current_character:
            self.current_character['relationships'] = {}
        if 'npcs' not in self.current_character:
            self.current_character['npcs'] = {}

        # NPC descriptions
        npc_descriptions = {
            'eva': {
                'name': 'Eva',
                'appearance': 'A young woman with a stylish, edgy appearance. She has short, slightly messy, platinum-blonde hair with hints of pastel or cool tones, giving her a modern and bold look. Her makeup is subtle but accentuates her sharp features, particularly her eyes and lips.',
                'style': 'She wears layered necklaces, including chains and chokers, along with earrings that add to her contemporary and slightly alternative vibe. Her outfit includes a leather jacket, contributing to her urban and confident style.',
                'personality': 'Confident, mysterious, and tech-savvy',
                'role': 'Tech specialist and information broker'
            },
            'fixer jack': {
                'name': 'Fixer Jack',
                'appearance': 'A tall, lean man with a scar running down the left side of his face. His eyes are cold and calculating.',
                'style': 'Professional but intimidating demeanor',
                'personality': 'Direct, business-oriented, and commanding respect',
                'role': 'Underground job broker and fixer'
            }
        }

        # Check for item acquisitions
        items_to_check = {
            'black decoder': 'Black Decoder Device',
            'energy sword': 'Energy Sword',
            'body armor': 'Reinforced Body Armor',
            'stims': 'Stim Packs',
            'healing packs': 'Healing Packs',
            'data chip': 'Encrypted Data Chip'
        }
        
        for item_text, item_name in items_to_check.items():
            if item_text in response.lower() and item_name not in self.current_character['inventory']:
                self.current_character['inventory'].append(item_name)

        # Update relationships and NPC descriptions
        for npc_key, npc_data in npc_descriptions.items():
            if npc_key in response.lower():
                # Add or update NPC description
                self.current_character['npcs'][npc_data['name']] = npc_data
                
                # Update relationship if not exists
                if npc_data['name'] not in self.current_character['relationships']:
                    self.current_character['relationships'][npc_data['name']] = 'Neutral'
                    
                # Update relationship based on interaction
                if any(pos in response.lower() for pos in ['smile', 'help', 'thank', 'impressed']):
                    self.current_character['relationships'][npc_data['name']] = 'Friendly'
                elif any(neg in response.lower() for neg in ['threat', 'warning', 'danger']):
                    self.current_character['relationships'][npc_data['name']] = 'Cautious'

        # Update location if it changed
        if 'you arrive at' in response.lower() or 'you reach' in response.lower():
            for line in response.split('.'):
                if 'you arrive at' in line.lower() or 'you reach' in response.lower():
                    self.current_character['current_location'] = line.strip()
                    break

        # Save any updates
        self.save_current_character()

    def _build_recent_narrative(self):
        """Build a narrative of recent events from conversation history."""
        if not self.conversation_history:
            return "You have just started your adventure."
            
        # Get the last 3 interactions
        recent_history = self.conversation_history[-3:]
        narrative = []
        
        for interaction in recent_history:
            narrative.append(f"You {interaction['prompt']}")
            narrative.append(interaction['response'])
            
        return "\n\n".join(narrative)

    def generate_event_narrative(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a narrative and choices for an event based on context.

        Args:
        context (Dict[str, Any]): A dictionary of context information.

        Returns:
        Dict[str, Any]: A dictionary containing the narrative and choices.
        """
        try:
            # Create a prompt that includes all relevant context
            prompt = f"""
            You are the game master for a cyberpunk RPG. The player is in the following situation:
            
            Player Info:
            - Name: {context.get('player', {}).get('name', 'Unknown')}
            - Role: {context.get('player', {}).get('role', 'Mercenary')}
            - Setting: Cyberpunk Future
            - Current Location: {context.get('location', 'Neo-Tokyo')}
            
            Current Situation:
            {context.get('description', '')}
            
            Last Interaction: {context.get('last_interaction', 'None')}
            
            Generate:
            1. A rich, atmospheric description of the current scene (2-3 sentences)
            2. A list of 6-8 meaningful choices the player can make, considering:
               - Exploring the city
               - Making money
               - Finding work/contracts
               - Meeting people/building relationships
               - Buying equipment/ships
               - Combat opportunities
               - Character development
            
            Format the response as a JSON object with two fields:
            {
                "narrative": "your atmospheric description here",
                "choices": ["choice 1", "choice 2", etc.]
            }
            """

            response = self.generate_response(prompt, context)
            try:
                # Try to parse as JSON
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                # Fallback to basic format if JSON parsing fails
                return {
                    "narrative": context.get('description', ''),
                    "choices": [
                        "Explore the area",
                        "Look for work",
                        "Visit the marketplace",
                        "Head to the bar",
                        "Check the shipyard",
                        "Visit the info broker"
                    ]
                }
            
        except Exception as e:
            print(f"Error generating event narrative: {str(e)}")
            return {
                "narrative": context.get('description', ''),
                "choices": [
                    "Explore the area",
                    "Look for work",
                    "Visit the marketplace",
                    "Head to the bar",
                    "Check the shipyard",
                    "Visit the info broker"
                ]
            }

    def generate_combat_narrative(self, combat_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate dynamic combat narrative and choices.

        Args:
        combat_context (Dict[str, Any]): A dictionary of combat context information.

        Returns:
        Dict[str, Any]: A dictionary containing the combat description and actions.
        """
        prompt = self._create_combat_prompt(combat_context)
        response = self.generate_response(prompt)
        return self._parse_combat_response(response)
    
    def generate_dialogue(self, dialogue_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate NPC dialogue and responses based on context.

        Args:
        dialogue_context (Dict[str, Any]): A dictionary of dialogue context information.

        Returns:
        Dict[str, Any]: A dictionary containing the dialogue and responses.
        """
        prompt = self._create_dialogue_prompt(dialogue_context)
        response = self.generate_response(prompt)
        return self._parse_dialogue_response(response)
    
    def get_npc_context(self, npc_id: str) -> Dict[str, Any]:
        """Get NPC context for the story."""
        npc_data = self.npc_manager.get_npc(npc_id)
        if not npc_data:
            return {}
        
        # Get relevant NPC information for the current context
        return {
            "name": npc_data["data"]["name"],
            "description": npc_data["data"]["description"],
            "current_relationship": npc_data["relationships"].get("player", {}).get("status", "neutral"),
            "last_interaction": npc_data["relationships"].get("player", {}).get("last_interaction", None),
            "recent_events": [event for event in npc_data["story_progression"][-3:]]  # Get last 3 events
        }

    def update_npc_after_interaction(self, npc_id: str, interaction_data: Dict[str, Any]):
        """Update NPC state after an interaction."""
        # Add the conversation
        self.npc_manager.add_conversation(npc_id, {
            "content": interaction_data.get("conversation", ""),
            "location": self.current_character.get("location", "unknown"),
            "context": interaction_data.get("context", {}),
            "important_points": interaction_data.get("important_points", [])
        })

        # Update relationship if needed
        if "relationship_change" in interaction_data:
            self.npc_manager.update_relationship(npc_id, "player", {
                "status": interaction_data["relationship_change"].get("new_status"),
                "trust_level": interaction_data["relationship_change"].get("trust_level"),
                "change_description": interaction_data["relationship_change"].get("description")
            })

        # Add story event if significant
        if "story_event" in interaction_data:
            self.npc_manager.add_story_event(npc_id, interaction_data["story_event"])

    def _create_story_prompt(self, player_context: Dict[str, Any], event_type: str) -> str:
        """
        Create a detailed prompt for story generation.

        Args:
        player_context (Dict[str, Any]): A dictionary of player context information.
        event_type (str): The type of event to generate.

        Returns:
        str: The prompt for story generation.
        """
        return f"""
        Generate a detailed story event for:
        Player: {player_context.get('name')}
        Role: {player_context.get('role')}
        Alignment: {player_context.get('alignment')}
        Current Location: {player_context.get('location')}
        Event Type: {event_type}
        
        Consider:
        - Player's personality and past choices
        - Current relationships and crew dynamics
        - Potential consequences and character development
        - Environmental and situational factors
        
        Format the response as a JSON object with:
        - description: Event description
        - choices: List of possible actions
        - consequences: Potential outcomes for each choice
        """
    
    def _create_combat_prompt(self, combat_context: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for combat narrative.

        Args:
        combat_context (Dict[str, Any]): A dictionary of combat context information.

        Returns:
        str: The prompt for combat narrative.
        """
        return f"""
        Generate a dynamic combat scene for:
        Player: {combat_context.get('player_name')}
        Opponent: {combat_context.get('opponent_name')}
        Environment: {combat_context.get('environment')}
        
        Consider:
        - Combat styles and abilities
        - Environmental factors
        - Tactical options
        - Dramatic tension
        
        Format the response as a JSON object with:
        - description: Combat situation
        - actions: Available combat moves
        - consequences: Potential outcomes
        """
    
    def _create_dialogue_prompt(self, dialogue_context: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for NPC dialogue.

        Args:
        dialogue_context (Dict[str, Any]): A dictionary of dialogue context information.

        Returns:
        str: The prompt for NPC dialogue.
        """
        return f"""
        Generate dialogue for interaction between:
        Player: {dialogue_context.get('player_name')}
        NPC: {dialogue_context.get('npc_name')}
        Relationship: {dialogue_context.get('relationship')}
        
        Consider:
        - Previous interactions
        - Current relationship status
        - Character personalities
        - Situation context
        
        Format the response as a JSON object with:
        - dialogue: NPC's speech
        - responses: Player response options
        - implications: How each response affects the relationship
        """
    
    def generate_story_event(self, player_context: Dict[str, Any], event_type: str) -> Dict[str, Any]:
        """
        Generate a new story event based on player context and event type.

        Args:
        player_context (Dict[str, Any]): A dictionary of player context information.
        event_type (str): The type of event to generate.

        Returns:
        Dict[str, Any]: A dictionary containing the event description and choices.
        """
        prompt = self._create_story_prompt(player_context, event_type)
        response = self.generate_response(prompt)
        return self._parse_story_response(response)
    
    def _parse_story_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response into a structured story event.

        Args:
        response (str): The response from the LLM.

        Returns:
        Dict[str, Any]: A dictionary containing the story event description and choices.
        """
        # Here you would parse the LLM response into a proper format
        # For now, return a simple structure
        return {
            "description": "A story event occurs...",
            "choices": ["Option 1", "Option 2", "Option 3"],
            "consequences": ["Outcome 1", "Outcome 2", "Outcome 3"]
        }
    
    def _parse_combat_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response into a structured combat event.

        Args:
        response (str): The response from the LLM.

        Returns:
        Dict[str, Any]: A dictionary containing the combat description and actions.
        """
        return {
            "description": "A combat situation unfolds...",
            "actions": ["Attack", "Defend", "Retreat"],
            "consequences": ["Hit", "Block", "Escape"]
        }
    
    def _parse_dialogue_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response into a structured dialogue event.

        Args:
        response (str): The response from the LLM.

        Returns:
        Dict[str, Any]: A dictionary containing the dialogue and responses.
        """
        return {
            "dialogue": "NPC speaks...",
            "responses": ["Response 1", "Response 2", "Response 3"],
            "implications": ["Effect 1", "Effect 2", "Effect 3"]
        }
