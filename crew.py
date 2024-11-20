"""
Module for handling crew management, morale, and rest mechanics.
"""
import random
from typing import Dict, List

# Crew status effects and their impacts
CREW_STATUS_EFFECTS = {
    "Well Rested": {"morale_mod": 10, "performance_mod": 1.2},
    "Rested": {"morale_mod": 5, "performance_mod": 1.1},
    "Tired": {"morale_mod": -5, "performance_mod": 0.9},
    "Exhausted": {"morale_mod": -10, "performance_mod": 0.7},
    "Inspired": {"morale_mod": 15, "performance_mod": 1.3},
    "Demoralized": {"morale_mod": -15, "performance_mod": 0.6}
}

# Activities and their effects
CREW_ACTIVITIES = {
    "Shore Leave": {
        "rest": 40,
        "morale": 30,
        "duration": 48,
        "cost": 500,
        "description": "Extended rest period at a space station or planet"
    },
    "Recreation Time": {
        "rest": 20,
        "morale": 15,
        "duration": 8,
        "cost": 100,
        "description": "Organized recreational activities on the ship"
    },
    "Training Exercise": {
        "rest": -10,
        "morale": 10,
        "duration": 4,
        "cost": 50,
        "description": "Group training to improve skills and teamwork"
    },
    "Meditation Session": {
        "rest": 15,
        "morale": 10,
        "duration": 2,
        "cost": 0,
        "description": "Group meditation for mental recovery"
    },
    "Movie Night": {
        "rest": 10,
        "morale": 20,
        "duration": 3,
        "cost": 20,
        "description": "Watch entertainment together as a crew"
    },
    "Feast": {
        "rest": 5,
        "morale": 25,
        "duration": 4,
        "cost": 200,
        "description": "Special meal with premium provisions"
    }
}

def initialize_crew(player: Dict) -> None:
    """Initialize or reset crew stats."""
    if 'crew' not in player:
        player['crew'] = {
            'morale': 100,
            'rest': 100,
            'status': "Well Rested",
            'hours_since_rest': 0,
            'activity_log': [],
            'current_activity': None
        }

def update_crew_status(player: Dict, hours_passed: int) -> None:
    """Update crew status based on time passed and conditions."""
    if 'crew' not in player:
        initialize_crew(player)
    
    crew = player['crew']
    crew['hours_since_rest'] += hours_passed
    
    # Natural decay of rest and morale over time
    rest_decay = hours_passed * 0.5  # Lose 0.5 rest points per hour
    morale_decay = hours_passed * 0.2  # Lose 0.2 morale points per hour
    
    crew['rest'] = max(0, min(100, crew['rest'] - rest_decay))
    crew['morale'] = max(0, min(100, crew['morale'] - morale_decay))
    
    # Update status based on rest and morale levels
    if crew['rest'] >= 80 and crew['morale'] >= 80:
        crew['status'] = "Well Rested"
    elif crew['rest'] >= 60 and crew['morale'] >= 60:
        crew['status'] = "Rested"
    elif crew['rest'] <= 30 or crew['morale'] <= 30:
        crew['status'] = "Exhausted"
    elif crew['rest'] <= 50 or crew['morale'] <= 50:
        crew['status'] = "Tired"

def perform_crew_activity(player: Dict, activity_name: str) -> Dict:
    """Perform a crew activity and return the results."""
    if activity_name not in CREW_ACTIVITIES:
        return {"success": False, "message": "Invalid activity"}
    
    if 'crew' not in player:
        initialize_crew(player)
    
    activity = CREW_ACTIVITIES[activity_name]
    crew = player['crew']
    
    # Check if player has enough credits
    if player['resources']['credits'] < activity['cost']:
        return {
            "success": False,
            "message": f"Not enough credits. Need {activity['cost']} credits."
        }
    
    # Apply activity effects
    crew['rest'] = max(0, min(100, crew['rest'] + activity['rest']))
    crew['morale'] = max(0, min(100, crew['morale'] + activity['morale']))
    crew['hours_since_rest'] = 0
    player['resources']['credits'] -= activity['cost']
    
    # Log the activity
    crew['activity_log'].append({
        "activity": activity_name,
        "duration": activity['duration'],
        "effects": {
            "rest": activity['rest'],
            "morale": activity['morale']
        }
    })
    
    # Update crew status
    update_crew_status(player, activity['duration'])
    
    return {
        "success": True,
        "message": f"Completed {activity_name}",
        "effects": {
            "rest_gained": activity['rest'],
            "morale_gained": activity['morale'],
            "credits_spent": activity['cost'],
            "duration": activity['duration']
        }
    }

def get_available_activities(player: Dict) -> List[Dict]:
    """Get list of available activities based on current location and resources."""
    available = []
    for name, activity in CREW_ACTIVITIES.items():
        if player['resources']['credits'] >= activity['cost']:
            available.append({
                "name": name,
                "cost": activity['cost'],
                "duration": activity['duration'],
                "description": activity['description']
            })
    return available

def get_crew_status_report(player: Dict) -> Dict:
    """Get a detailed report of crew status."""
    if 'crew' not in player:
        initialize_crew(player)
    
    crew = player['crew']
    status_effect = CREW_STATUS_EFFECTS[crew['status']]
    
    return {
        "morale": crew['morale'],
        "rest": crew['rest'],
        "status": crew['status'],
        "hours_since_rest": crew['hours_since_rest'],
        "performance_modifier": status_effect['performance_mod'],
        "recent_activities": crew['activity_log'][-3:] if crew['activity_log'] else [],
        "current_effects": {
            "morale_mod": status_effect['morale_mod'],
            "performance_mod": status_effect['performance_mod']
        }
    }

def display_crew_status(player: Dict) -> None:
    """Display formatted crew status information."""
    report = get_crew_status_report(player)
    
    print("\n=== Crew Status Report ===")
    print(f"Status: {report['status']}")
    print(f"Morale: {report['morale']:.1f}%")
    print(f"Rest: {report['rest']:.1f}%")
    print(f"Hours Since Last Rest: {report['hours_since_rest']}")
    print(f"Performance Modifier: {report['performance_modifier']:.1f}x")
    
    if report['recent_activities']:
        print("\nRecent Activities:")
        for activity in report['recent_activities']:
            print(f"- {activity['activity']} "
                  f"(Rest: {activity['effects']['rest']:+d}, "
                  f"Morale: {activity['effects']['morale']:+d})")
    
    # Show available activities
    available = get_available_activities(player)
    if available:
        print("\nAvailable Activities:")
        for i, activity in enumerate(available, 1):
            print(f"{i}. {activity['name']} - {activity['description']}")
            print(f"   Cost: {activity['cost']} credits, Duration: {activity['duration']} hours")
