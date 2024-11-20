from combat_system import CombatSystem, CombatEntity, Ability
import json
import os
from dotenv import load_dotenv
import random

def main():
    # Load API key and initialize combat system
    load_dotenv()
    api_key = os.getenv('MISTRAL_API_KEY')
    combat_system = CombatSystem(api_key)

    print("Generating combat scenario...\n")
    scenario = combat_system.generate_combat_scenario({}, "Dragon")
    print("Scenario:")
    print("-" * 50)
    print(json.dumps(scenario, indent=2))
    print("-" * 50 + "\n")

    # Create player and enemy
    player = CombatEntity(
        name="Eamon the Warrior",
        max_health=300,
        current_health=300,
        abilities={
            "Sword Strike": Ability(
                name="Sword Strike",
                damage_range=(30, 60),
                description="A powerful sword attack"
            ),
            "Shield Bash": Ability(
                name="Shield Bash",
                damage_range=(20, 40),
                cooldown=3,
                special_effects={"stun": 1},
                description="A stunning shield attack"
            ),
            "War Cry": Ability(
                name="War Cry",
                damage_range=(0, 0),
                cooldown=4,
                special_effects={
                    "buff": {
                        "name": "damage_boost",
                        "effect": {"damage_multiplier": 1.2},
                        "duration": 2
                    }
                },
                description="Boost damage for 2 turns"
            )
        }
    )

    enemy_data = scenario["enemy"]
    enemy = combat_system.create_combat_entity(enemy_data)

    print(f"Combat begins between {player.name} and {enemy.name}!")
    print(f"Location: {scenario['environment']}\n")

    turn = 1
    while player.is_alive() and enemy.is_alive():
        print(f"\nTurn {turn}")
        print("-" * 20)
        print(f"{player.name} HP: {player.current_health}/{player.max_health}")
        print(f"{enemy.name} HP: {enemy.current_health}/{enemy.max_health}\n")

        # Show available abilities and their status
        print("Available options:")
        print("Combat abilities:")
        for name, ability in player.abilities.items():
            status = "Ready" if ability.current_cooldown == 0 else f"Cooldown: {ability.current_cooldown}"
            print(f"{name}: {ability.description} ({status})")
        print("\nOther options:")
        print("Talk: Speak with the enemy")
        print("Status: Check detailed status\n")

        # Get player action
        while True:
            action = input("Choose your action: ").strip()
            
            if action.lower() == "talk":
                message = input("What would you like to say? ")
                response = combat_system.generate_dialogue_response(message, enemy, scenario)
                print(f"\n{enemy.name}: {response}\n")
                continue
            elif action.lower() == "status":
                print("\nDetailed Status:")
                print(f"{player.name}:")
                print(f"- Health: {player.current_health}/{player.max_health}")
                print(f"- Status Effects: {', '.join(player.status_effects) or 'None'}")
                print(f"- Active Buffs: {', '.join(player.buffs) or 'None'}")
                print(f"\n{enemy.name}:")
                print(f"- Health: {enemy.current_health}/{enemy.max_health}")
                print(f"- Status Effects: {', '.join(enemy.status_effects) or 'None'}")
                print(f"- Active Buffs: {', '.join(enemy.buffs) or 'None'}\n")
                continue
            elif action in player.abilities:
                ability = player.abilities[action]
                if ability.current_cooldown > 0:
                    print(f"{action} is on cooldown for {ability.current_cooldown} more turns")
                    continue
                break
            else:
                print("Invalid action, try again.")
                continue

        if action.lower() not in ["talk", "status"]:
            # Execute player turn
            result = combat_system.execute_turn(player, enemy, action)
            narrative = combat_system.generate_combat_narrative(result, turn)
            print(f"\n{narrative}")

            # Execute enemy turn if they're alive
            if enemy.is_alive():
                # Simple AI: randomly choose an available ability
                available_abilities = [name for name, ability in enemy.abilities.items() 
                                    if ability.current_cooldown == 0]
                enemy_action = random.choice(available_abilities)
                result = combat_system.execute_turn(enemy, player, enemy_action)
                narrative = combat_system.generate_combat_narrative(result, turn)
                print(f"\n{narrative}")

            turn += 1

    # Combat end
    print("\nVictory!" if enemy.current_health <= 0 else "\nDefeat!")
    print(f"{enemy.name} has been {'defeated' if enemy.current_health <= 0 else 'victorious'}!")
    print(f"\nFinal Status:")
    print(f"{player.name}: {player.current_health}/{player.max_health} HP")
    print(f"{enemy.name}: {enemy.current_health}/{enemy.max_health} HP")

if __name__ == "__main__":
    main()
