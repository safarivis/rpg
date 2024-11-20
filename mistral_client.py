"""Mistral AI API client."""
import os
import requests
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class ChatMessage:
    role: str
    content: str

@dataclass
class ChatChoice:
    index: int
    message: ChatMessage
    finish_reason: str

@dataclass
class ChatCompletion:
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Dict[str, int]

class MistralClient:
    """Simple client for the Mistral AI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the client with API key."""
        if not api_key:
            api_key = os.getenv("LLM_API_KEY")
        
        if not api_key:
            raise ValueError("Mistral API key not found")
            
        self.api_key = api_key
        self.api_base = "https://api.mistral.ai/v1"
        self.chat = self.Chat(self)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    class Chat:
        """Chat completion methods."""
        
        def __init__(self, client):
            self.client = client
            
        def completions(self):
            """Chat completion methods."""
            return self
            
        def create(self, model: str, messages: List[Dict[str, str]], 
                  temperature: float = 0.7, max_tokens: int = 500) -> ChatCompletion:
            """Create a chat completion."""
            url = f"{self.client.api_base}/chat/completions"
            
            data = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(url, headers=self.client._get_headers(), json=data)
            response.raise_for_status()
            
            result = response.json()
            
            # Convert the response to our dataclass format
            choices = [
                ChatChoice(
                    index=choice["index"],
                    message=ChatMessage(
                        role=choice["message"]["role"],
                        content=choice["message"]["content"]
                    ),
                    finish_reason=choice["finish_reason"]
                )
                for choice in result["choices"]
            ]
            
            return ChatCompletion(
                id=result["id"],
                object=result["object"],
                created=result["created"],
                model=result["model"],
                choices=choices,
                usage=result["usage"]
            )
