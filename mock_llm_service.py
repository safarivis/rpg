class MockLLMService:
    def __init__(self):
        self.current_character = None
        self.current_character_name = None

    def generate_response(self, input_text, context=None):
        """Mock response generation for development"""
        character = context.get('character', {})
        action = context.get('action', '')
        
        # Simulate different responses based on context
        if 'battle' in input_text.lower():
            return f"You prepare for battle! Your health is at {character.get('resources', {}).get('health', 100)}."
        elif 'explore' in input_text.lower():
            return f"You carefully explore the area. The {character.get('role', 'adventurer')} in you senses something interesting nearby."
        elif 'talk' in input_text.lower() or 'speak' in input_text.lower():
            return "The person listens intently to what you have to say."
        else:
            return f"As a {character.get('race', 'being')} {character.get('role', 'adventurer')}, you consider your next move carefully."

    def load_character(self, name):
        """Mock character loading"""
        self.current_character_name = name
        return True

    def save_character(self):
        """Mock character saving"""
        return True
