import os
from pathlib import Path

class Config:
    def __init__(self):
        self.api_key = None
        self.load_config()
        
    def load_config(self):
        """Load configuration from .env file."""
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if key.strip() == 'LLM_API_KEY':
                            self.api_key = value.strip()
                            break
        
    @property
    def has_valid_api_key(self) -> bool:
        """Check if a valid API key is available."""
        return bool(self.api_key and len(self.api_key) > 0)

# Create a global config instance
config = Config()
