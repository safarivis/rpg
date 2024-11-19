import random

def generate_npc():
    """Generate an NPC with dynamic attributes and motivations."""
    npc_pool = [
        {"name": "Eva", "role": "Loyal Crew Member and lover", "motivation": "Freedom"},
        {"name": "Varok", "role": "Rival Pirate Captain", "motivation": "Revenge"},
        {"name": "Eliara", "role": "Mysterious Informant", "motivation": "Profit"},
        {"name": "Drakos", "role": "Mercenary Leader", "motivation": "Power"},
        {"name": "Ardin", "role": "Disgraced Scientist", "motivation": "Redemption"}
    ]

    npc = random.choice(npc_pool)
    # Assign dynamic traits to make NPCs unique each time
    npc["loyalty"] = random.randint(-20, 20)  # -20 (hostile) to 20 (friendly)
    npc["skills"] = random.sample(["Combat", "Negotiation", "Strategy", "Stealth"], 2)
    npc["status"] = "Ally" if npc["loyalty"] > 0 else "Rival"
    return npc

def display_npc(npc):
    """Display details about the generated NPC."""
    print("\nGenerated NPC:")
    print(f"Name: {npc['name']}")
    print(f"Role: {npc['role']}")
    print(f"Motivation: {npc['motivation']}")
    print(f"Loyalty: {npc['loyalty']}")
    print(f"Status: {npc['status']}")
    print(f"Skills: {', '.join(npc['skills'])}")
