from flask import Flask, render_template, request, jsonify
from llm_service import LLMService
import json
import re

app = Flask(__name__)
llm_service = None

def init_llm_service():
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
        # Try to load the character, if it fails, create a new one
        if not llm_service.load_character("player"):
            llm_service.current_character = {
                "name": "Strijder",
                "resources": {
                    "health": 100,
                    "credits": 500
                },
                "location": "Neon District",
                "inventory": [
                    "Black Decoder Gadget",
                    "Data Chip from Eva",
                    "Standard Issue Pistol",
                    "Light Combat Armor"
                ],
                "relationships": {
                    "Eva": "Friendly - Helped with data retrieval",
                    "Mysterious Contact": "Unknown - Awaiting meeting"
                }
            }
            llm_service.current_character_name = "player"

def strip_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def get_character_state():
    global llm_service
    if llm_service is None or llm_service.current_character is None:
        init_llm_service()
    
    char = llm_service.current_character
    return {
        'name': char.get('name', 'Unknown'),
        'health': char.get('resources', {}).get('health', 100),
        'credits': char.get('resources', {}).get('credits', 0),
        'location': char.get('location', 'Unknown'),
        'inventory': char.get('inventory', []),
        'relationships': char.get('relationships', {})
    }

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
