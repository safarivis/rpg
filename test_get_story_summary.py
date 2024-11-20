from story_engine import StoryEngine

# Create a player object
player = {
    "skills": ["Charisma", "Perception", "Weapons Mastery"],
    "relationships": {
        "Alice": {"loyalty": 5},
        "Bob": {"loyalty": 0},
        "Charlie": {"loyalty": 3}
    }
}

# Create an instance of the StoryEngine class
story_engine = StoryEngine(player)

# Generate the first chapter
chapter = story_engine.generate_chapter()

# Resolve a choice
choice_id = "negotiate"
outcome = story_engine.resolve_choice(choice_id)

# Get a summary of the story
summary = story_engine.get_story_summary()
print(summary)
