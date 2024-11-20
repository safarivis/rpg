# RPG: Role-Playing Game Project

## **Project Overview**
This project is a modular, text-based role-playing game (RPG) designed for flexibility, reusability, and ease of expansion. It combines elements of procedural storytelling, dynamic relationships, and skill-based gameplay to create an engaging experience for players.

---

## **Plan and Goals**
### **Key Objectives**
1. **Player-Centric Design**: Focus on player-driven decisions, dynamically influenced by skills, weaknesses, and relationships.
2. **Dynamic World Building**: Create a customizable world based on player inputs like role, personality, and strengths.
3. **Replayability**: Include randomized events and NPC interactions to ensure no two playthroughs are the same.
4. **Storytelling**: Build a dynamic story engine that responds to player choices and evolves with their actions.

### **Key Features**
- **Character Creation**: Allows players to define physical attributes, strengths, skills, and relationships.
- **Skill-Based Gameplay**: Player choices and success are influenced by selected skills and dynamic skill checks.
- **NPC Relationships**: Interactions with NPCs affect loyalty, trust, and outcomes.
- **Dynamic Events**: Random events and challenges adapt to the player's strengths and weaknesses.
- **Story Engine**: A modular system to progress the narrative, balancing predefined and random elements.

---

## **Completed Tasks**
1. **Modular Code Structure**: Split the game into modules (`character_creation.py`, `events.py`, `npc_generation.py`, etc.) for better organization and scalability.
2. **Git Repository Setup**: Created a version-controlled repository on [GitHub](https://github.com/safarivis/rpg).
3. **Player Creation System**:
   - Players can define their name, gender, race, time period, setting, and role.
   - Players select strengths, skills, and relationships, with random weaknesses added for balance.
4. **Dynamic World-Building**: The game generates a custom world prompt based on player inputs.
5. **Event-Based Decision Making**:
   - Integrated skill checks for choices in events.
   - Player choices dynamically influence the narrative, personality traits, and NPC relationships.
6. **NPC System**:
   - Generated NPCs with motivations and relationships with the player.
   - Added dynamic loyalty tracking.

---

## **Recent Updates**
### **Major Improvements (Latest Version)**
1. **LLM Integration**:
   - Integrated Mistral AI for dynamic storytelling and NPC interactions
   - Added conversation history and context management
   - Improved response generation with proper formatting

2. **UI/UX Improvements**:
   - Added ANSI color formatting for better readability
   - Cyan for headers and section titles
   - Green for labels
   - Yellow for narrative text
   - White for regular text

3. **Character Management**:
   - Implemented save/load functionality for character data
   - Added conversation history persistence
   - Enhanced context handling for more coherent storytelling

4. **Bug Fixes**:
   - Fixed Mistral API response handling
   - Improved error handling and user feedback
   - Enhanced stability in WSL environment

### **Current Features**
1. **Dynamic Storytelling**:
   - AI-powered narrative generation
   - Context-aware responses
   - Persistent conversation history

2. **Character System**:
   - Detailed character creation
   - Persistent character state
   - Dynamic attribute tracking

3. **World Interaction**:
   - Rich environmental descriptions
   - NPC interactions
   - Quest system
   - Economic system with credits

4. **Technical Improvements**:
   - Modular code structure
   - Proper API integration
   - Enhanced error handling
   - Color-coded interface

---

## **Next Steps**
1. **Random Events Expansion**:
   - Broaden the pool of random events and ensure they adapt to world state and player attributes.
2. **Story Engine Development**:
   - Expand the `StoryEngine` class to fully integrate story progression, branching narratives, and consequences.
   - Add location-based storytelling and deeper plot generation.
3. **Combat and Diplomacy Systems**:
   - Introduce a turn-based combat system influenced by player skills and inventory.
   - Expand negotiation and diplomacy options to include NPC-specific behaviors.
4. **Dynamic Inventory Management**:
   - Allow players to acquire, use, and lose items during events.
   - Introduce trade mechanics with NPCs.
5. **AI Integration**:
   - Explore integrating LLMs for dynamically generated text and event descriptions.
   - Consider AI-driven NPC responses for richer interactions.
6. **User Interface**:
   - Develop a CLI-based or simple graphical interface for improved usability.

---

## **System Documentation**

### **System Architecture**

#### **Core Components**

1. **LLM Service (`llm_service.py`)**
   - Acts as an AI Dungeon Master
   - Generates narrative responses
   - Processes player actions
   - Maintains game balance
   - Tracks story progression

2. **Character Manager (`character_manager.py`)**
   - Handles character persistence
   - Tracks character progression
   - Manages character stats and inventory
   - Records character history
   - Maintains relationships and reputation

#### **Data Flow**

```
Player Input → LLM Service → Character Manager
     ↑                            ↓
     └────── Game Response ───────┘
```

1. Player provides input (action, dialogue, etc.)
2. LLM Service:
   - Processes the input
   - Considers character context
   - Generates appropriate response
   - Updates character state
3. Character Manager:
   - Saves character updates
   - Maintains history
   - Tracks progression

#### **File Structure**

```
RPG/
├── llm_service.py      # AI Dungeon Master
├── character_manager.py # Character data management
├── config.py           # Configuration settings
├── characters/         # Character save files
│   └── [character_name]/
│       ├── character.json  # Current state
│       └── history.json    # Progression log
└── .env                # Environment variables
```

### **Features**

#### **Dynamic Storytelling**
- Free-form player input
- Contextual responses
- Persistent world state
- Character-driven narrative

#### **Character Management**
- Detailed character stats
- Skill progression
- Inventory system
- Relationship tracking
- Quest management

#### **Game Balance**
- Dynamic difficulty scaling
- Context-aware challenges
- Balanced rewards
- Economic consistency

### **Setup**

1. Create a `.env` file with your Mistral AI API key:
   ```
   LLM_API_KEY=your_api_key_here
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the game:
   ```bash
   python main.py
   ```

### **Usage**

1. Start a new game or load a character
2. Type any action you want to take
3. The AI will:
   - Process your action
   - Consider your character's abilities
   - Generate appropriate responses
   - Update your character's state
   - Save your progress

### **Examples**

```python
# Initialize the game
llm = LLMService()
llm.load_character("your_character")

# Take any action
response = llm.generate_response("I want to hack into the corporate database")
# The AI considers your hacking skill, security level, equipment, etc.

response = llm.generate_response("I try to negotiate with the street gang")
# The AI considers your charisma, reputation, relationships, etc.
```

---

## **Why We Made These Choices**
### **Modular Structure**
- **Reason**: A modular design makes it easier to expand individual components without breaking the entire system. It also allows future developers to replace or improve specific modules independently.

### **Dynamic Systems**
- **Reason**: Systems like skill checks, NPC relationships, and event randomness ensure high replayability and player agency, enhancing engagement.

### **Python as the Language**
- **Reason**: Python is ideal for prototyping and developing text-based games due to its simplicity, large library ecosystem, and active community.

### **GitHub for Version Control**
- **Reason**: GitHub provides a central repository to collaborate, track changes, and maintain code integrity.

---

## **Future Goals**
1. **AI-Driven Narratives**: Implement GPT-based storytelling for richer, more dynamic plotlines and dialogue.
2. **Multiplayer Support**: Enable cooperative or competitive gameplay between multiple players.
3. **Enhanced Graphics**: Move towards a graphical interface for better user interaction while keeping the text-based charm.
4. **Cross-Platform Support**: Package the game as an executable for easy distribution across different operating systems.

---

## **How to Contribute**
1. Clone the repository:
   ```bash
   git clone https://github.com/safarivis/rpg.git
   ```

2. Open issues for bugs or suggestions
3. Submit pull requests
4. Improve documentation
5. Add new features

## License

This project is licensed under the MIT License - see the LICENSE file for details.
