from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
from character_creation import character_creation
from player import load_player_data, save_player_data, default_player

app = FastAPI()

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CharacterRequest(BaseModel):
    name: str
    step: str
    input_value: Optional[str] = None

class CharacterResponse(BaseModel):
    step: str
    prompt: str
    options: Optional[List[str]] = None
    character_data: Optional[Dict] = None

@app.post("/api/character/create")
async def create_character(request: CharacterRequest):
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
                "step": "role",
                "prompt": "What is your role in this world?",
                "options": ["Warrior", "Mage", "Rogue", "Healer"],
                "character_data": player
            }
        elif request.step == "role":
            player["role"] = request.input_value
            save_player_data(player)
            return {
                "step": "complete",
                "prompt": f"Welcome, {player['name']} the {player['race']} {player['role']}. Your journey begins...",
                "character_data": player
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid step")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/character/{name}")
async def get_character(name: str):
    player = load_player_data(name)
    if not player:
        raise HTTPException(status_code=404, detail="Character not found")
    return player

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
