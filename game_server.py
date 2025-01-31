from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from character_creation import character_creation
from player import load_player_data, save_player_data, default_player
from llm_service import LLMService
from world_building import generate_world_prompt
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

app = FastAPI()

# Initialize services
llm_service = LLMService()

# Configure CORS - allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins during development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# API Models
class CharacterCreationRequest(BaseModel):
    name: str
    step: str
    input_value: Optional[str] = None

class GameActionRequest(BaseModel):
    action: str
    character_name: str
    input_text: str
    context: Optional[Dict[str, Any]] = None

# Character Creation Endpoint
@app.post("/api/character/create")
async def create_character(request: CharacterCreationRequest):
    try:
        player = load_player_data(request.name)
        if not player:
            player = default_player.copy()
            player["name"] = request.name

        if request.step == "initial":
            return {
                "step": "gender",
                "prompt": "The voice asks: 'What is your gender?'",
                "options": ["Male", "Female", "Other"],
                "character_data": player
            }
        elif request.step == "gender":
            player["gender"] = request.input_value
            save_player_data(player)
            return {
                "step": "race",
                "prompt": "The voice continues: 'What race are you?'",
                "options": ["Human", "Elf", "Dwarf", "Other"],
                "character_data": player
            }
        elif request.step == "race":
            player["race"] = request.input_value
            save_player_data(player)
            return {
                "step": "time_period",
                "prompt": "When are you from?",
                "options": ["Past", "Present", "Future"],
                "character_data": player
            }
        elif request.step == "time_period":
            player["time_period"] = request.input_value
            save_player_data(player)
            return {
                "step": "genre",
                "prompt": "Is your world Fantasy or Realism?",
                "options": ["Fantasy", "Realism"],
                "character_data": player
            }
        elif request.step == "genre":
            player["setting"] = request.input_value
            save_player_data(player)
            return {
                "step": "role",
                "prompt": "What is your role in this world?",
                "options": ["Warrior", "Mage", "Rogue", "Healer"],
                "character_data": player
            }
        elif request.step == "role":
            player["role"] = request.input_value
            save_player_data(player)
            # Generate initial world context based on character choices
            world_context = generate_world_prompt(player)
            return {
                "step": "complete",
                "prompt": f"Welcome, {player['name']} the {player['race']} {player['role']}. {world_context}",
                "character_data": player
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Game Action Endpoint
@app.post("/api/game/action")
async def game_action(request: GameActionRequest):
    try:
        player = load_player_data(request.character_name)
        if not player:
            raise HTTPException(status_code=404, detail="Character not found")

        # Process the game action using LLM service
        response = llm_service.generate_response(
            request.input_text,
            {
                "character": player,
                "action": request.action,
                "context": request.context or {}
            }
        )

        # Update and save character state if needed
        save_player_data(player)

        return {
            "message": response,
            "character_data": player
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Character Data Endpoint
@app.get("/api/character/{name}")
async def get_character(name: str):
    player = load_player_data(name)
    if not player:
        raise HTTPException(status_code=404, detail="Character not found")
    return player

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
