from elevenlabs import voices, generate, play, set_api_key
import os

class TTSService:
    def __init__(self, api_key=None):
        """Initialize the TTS service."""
        if not api_key:
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                raise ValueError("ElevenLabs API key not found in environment variables")
        
        set_api_key(api_key)
        self.api_key = api_key
        
        # Voice mappings for different NPCs
        self.voice_mappings = {
            "Master Eldred": "Antoni",  # Wise, elderly voice
            "Captain Marcus": "Arnold",  # Strong, commanding voice
            "Grace": "Bella",  # Gentle, nurturing voice
            "default": "Josh"  # Default voice for other characters
        }
    
    def speak(self, text, character=None):
        """Generate and play speech for the given text."""
        try:
            # Select voice based on character
            voice_name = self.voice_mappings.get(character, self.voice_mappings["default"])
            
            # Generate audio
            audio = generate(
                text=text,
                voice=voice_name,
                model="eleven_multilingual_v2"
            )
            
            # Play the audio
            play(audio)
            
            return True
        except Exception as e:
            print(f"TTS Error: {str(e)}")
            return False
    
    def speak_as_character(self, text, character):
        """Speak text as a specific character."""
        return self.speak(text, character)
    
    def narrate(self, text):
        """Narrate text using the default voice."""
        return self.speak(text, "default")
