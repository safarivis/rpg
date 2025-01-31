from flask import Flask, render_template, request, jsonify
from llm_service import LLMService
from character_creation import character_creation
from player import load_player_data, save_player_data, default_player
import json
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
llm_service = None

def init_llm_service():
    global llm_service
    if llm_service is None:
        llm_service = LLMService()

def strip_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def get_character_state():
    global llm_service
    if llm_service is None:
        init_llm_service()
    
    char = load_player_data("player")
    if not char:
        return None
        
    return {
        'name': char.get('name', 'Unknown'),
        'health': char.get('resources', {}).get('health', 100),
        'credits': char.get('resources', {}).get('credits', 0),
        'location': char.get('location', 'Unknown'),
        'inventory': char.get('inventory', []),
        'relationships': char.get('relationships', {})
    }

@app.route('/api/character/create', methods=['POST'])
def create_character():
    try:
        data = request.json
        name = data.get('name')
        step = data.get('step')
        input_value = data.get('input_value')

        player = load_player_data(name)
        if not player:
            player = default_player.copy()
            player["name"] = name

        if step == "initial":
            return jsonify({
                "step": "gender",
                "prompt": "The voice asks: 'What is your gender?'",
                "options": ["Male", "Female", "Other"],
                "character_data": player
            })
        elif step == "gender":
            player["gender"] = input_value
            save_player_data(player)
            return jsonify({
                "step": "race",
                "prompt": "The voice continues: 'What race are you?'",
                "options": ["Human", "Elf", "Dwarf", "Other"],
                "character_data": player
            })
        elif step == "race":
            player["race"] = input_value
            save_player_data(player)
            return jsonify({
                "step": "time_period",
                "prompt": "When are you from?",
                "options": ["Past", "Present", "Future"],
                "character_data": player
            })
        elif step == "time_period":
            player["time_period"] = input_value
            save_player_data(player)
            return jsonify({
                "step": "role",
                "prompt": "What is your role in this world?",
                "options": ["Warrior", "Mage", "Rogue", "Healer"],
                "character_data": player
            })
        elif step == "role":
            player["role"] = input_value
            save_player_data(player)
            return jsonify({
                "step": "complete",
                "prompt": f"Welcome, {player['name']} the {player['race']} {player['role']}. Your journey begins...",
                "character_data": player
            })
        else:
            return jsonify({"error": "Invalid step"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/character/<name>', methods=['GET'])
def get_character(name):
    player = load_player_data(name)
    if not player:
        return jsonify({"error": "Character not found"}), 404
    return jsonify(player)

@app.route('/')
def index():
    init_llm_service()  # Initialize on first page load
    return render_template('index.html')

@app.route('/send_command', methods=['POST'])
def send_command():
    global llm_service
    if llm_service is None:
        init_llm_service()
    
    try:
        data = request.get_json()
        command = data.get('command', '').lower()
        
        # Check if this is a command to view NPC info
        if command.startswith('info ') or command.startswith('check '):
            npc_name = command.split(' ', 1)[1].strip()
            npc_data = llm_service.npc_manager.get_npc(npc_name)
            if npc_data:
                # Format NPC information for display
                appearance = npc_data['data']['appearance']
                npc_info = f"""=== {npc_data['data']['name']} ===
{npc_data['data']['description']}

Location: {npc_data['data']['location']}
Occupation: {npc_data['data']['occupation']}

Appearance:
{appearance['overview']}

Face & Features:
{appearance.get('face', '')}

Hair:
{appearance.get('hair', '')}

Armor & Attire:
{appearance.get('armor', '')}
{appearance.get('clothing', '')}

Equipment:
{appearance.get('equipment', '')}

Presence:
{appearance.get('presence', '')}

Recent Events:
{chr(10).join(f"• {event['description']}" for event in npc_data['story_progression'][-3:])}

Your Relationship: {npc_data['relationships'].get('player', {}).get('status', 'neutral')}
Trust Level: {npc_data['relationships'].get('player', {}).get('trust_level', 0)}/10
"""
                return jsonify({
                    'response': npc_info,
                    'character_state': get_character_state()
                })
            else:
                return jsonify({
                    'response': f"No information found about {npc_name}.",
                    'character_state': get_character_state()
                })
        
        # Generate response using LLM service
        response = llm_service.generate_response(command)
        response = strip_ansi_codes(response)  # Strip ANSI codes
        
        # If the response mentions an NPC, update their data
        if 'eva' in command.lower() or 'eva' in response.lower():
            llm_service.update_npc_after_interaction('eva', {
                'conversation': command,
                'context': {
                    'location': llm_service.current_character.get('location', 'unknown'),
                    'player_command': command
                },
                'important_points': []
            })
        
        return jsonify({
            'response': response,
            'character_state': get_character_state()
        })
    except Exception as e:
        print(f"Error in send_command: {str(e)}")
        return jsonify({
            'response': 'An error occurred while processing your command.',
            'character_state': get_character_state()
        }), 500

@app.route('/get_status')
def get_status():
    global llm_service
    if llm_service is None:
        init_llm_service()
    
    try:
        return jsonify(get_character_state())
    except Exception as e:
        print(f"Error in get_status: {str(e)}")
        return jsonify(get_character_state()), 500

if __name__ == '__main__':
    app.run(debug=True)
