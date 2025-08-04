"""
TaleKeeper - Main orchestrator for the D&D agent flow system.
Coordinates dice engine, database, LM Studio, and MCP server.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sys

# Add core directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "core"))

from dice_engine import DiceEngine, AdvantageType
from database import DatabaseManager, Character
from lm_studio_client import LMStudioClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaleKeeper:
    """
    Main orchestrator for the TaleKeeper D&D system.
    Coordinates all components and provides high-level game logic.
    """
    
    def __init__(self, db_path: str = "data/talekeeper.db", lm_studio_url: str = "http://localhost:1234"):
        """Initialize TaleKeeper with all subsystems"""
        self.dice_engine = DiceEngine()
        self.database = DatabaseManager(db_path)
        self.lm_client = LMStudioClient(lm_studio_url)
        
        logger.info("TaleKeeper initialized successfully")
    
    def create_character(self, character_data: Dict[str, Any]) -> Character:
        """Create a new character with validation and setup"""
        logger.info(f"Creating character: {character_data.get('name')}")
        
        # Validate required fields
        required_fields = ['name', 'player_name', 'character_class', 'hp_max']
        for field in required_fields:
            if field not in character_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create character in database
        character = self.database.create_character(character_data)
        
        # Generate welcome narrative
        context = {
            "character_name": character.name,
            "character_class": character.character_class,
            "background": character.background
        }
        
        welcome_msg = self.lm_client.generate_npc_dialogue(
            "The Narrator", 
            f"Welcome {character.name} the {character.character_class} to our adventure",
            "welcoming"
        )
        
        logger.info(f"Character {character.name} created successfully")
        logger.info(f"Welcome message: {welcome_msg}")
        
        return character
    
    def process_attack(self, attacker_name: str, target_name: str, weapon: str = "sword", 
                      attack_bonus: int = 5, damage_dice: str = "1d8+3", 
                      advantage: str = "normal") -> Dict[str, Any]:
        """
        Process a complete attack sequence with narrative
        
        Returns detailed attack result with narrative description
        """
        logger.info(f"{attacker_name} attacks {target_name} with {weapon}")
        
        # Get characters
        attacker = self.database.get_character_by_name(attacker_name)
        target = self.database.get_character_by_name(target_name)
        
        if not attacker or not target:
            missing = attacker_name if not attacker else target_name
            raise ValueError(f"Character not found: {missing}")
        
        # Roll attack
        adv_type = AdvantageType(advantage.lower())
        target_ac = target.ac
        attack_result = self.dice_engine.calculate_attack(attack_bonus, target_ac, adv_type)
        
        result = {
            "attacker": attacker_name,
            "target": target_name,
            "weapon": weapon,
            "hit": attack_result.hit,
            "attack_roll": attack_result.attack_roll.total,
            "target_ac": target_ac,
            "critical_hit": attack_result.critical_hit,
            "damage": 0,
            "target_hp_before": target.hp_current,
            "target_hp_after": target.hp_current,
            "target_unconscious": False,
            "narrative": ""
        }
        
        # If hit, roll damage and apply it
        if attack_result.hit:
            if attack_result.critical_hit:
                damage_result = self.dice_engine.roll_critical_damage(damage_dice)
            else:
                damage_result = self.dice_engine.roll_damage(damage_dice)
            
            damage_dealt = damage_result.total
            result["damage"] = damage_dealt
            
            # Apply damage to target
            success, new_hp = self.database.damage_character(target.id, damage_dealt)
            if success:
                result["target_hp_after"] = new_hp
                result["target_unconscious"] = new_hp <= 0
                
                # Log combat action
                active_encounter = self.database.get_active_encounter()
                if active_encounter:
                    self.database.log_combat_action(
                        active_encounter.id,
                        attacker.id,
                        "attack",
                        f"{attacker_name} hits {target_name} for {damage_dealt} damage",
                        {
                            "attack_roll": attack_result.attack_roll.total,
                            "damage_roll": damage_result.total,
                            "weapon": weapon
                        },
                        damage_dealt,
                        target.id,
                        active_encounter.round_number
                    )
        
        # Generate narrative description
        narrative_context = {
            "attacker": attacker_name,
            "target": target_name,
            "weapon": weapon,
            "hit": result["hit"],
            "critical": result["critical_hit"],
            "attack_roll": result["attack_roll"],
            "target_ac": target_ac,
            "damage": result["damage"],
            "unconscious": result["target_unconscious"]
        }
        
        result["narrative"] = self.lm_client.generate_combat_description(narrative_context)
        
        logger.info(f"Attack result: {result['narrative']}")
        return result
    
    def start_encounter(self, encounter_name: str, participant_names: List[str], 
                       description: str = "") -> Dict[str, Any]:
        """Start a new combat encounter with initiative"""
        logger.info(f"Starting encounter: {encounter_name}")
        
        # Validate all participants exist
        participants = []
        for name in participant_names:
            character = self.database.get_character_by_name(name)
            if not character:
                raise ValueError(f"Character not found: {name}")
            participants.append(character)
        
        # Create encounter
        participant_ids = [char.id for char in participants]
        encounter = self.database.create_encounter(encounter_name, description, participant_ids)
        
        # Roll initiative for all participants
        initiative_order = []
        for character in participants:
            dex_mod = character.modifiers.get('DEX', 0)
            initiative_roll = self.dice_engine.roll_initiative(dex_mod)
            initiative_order.append({
                "character": character.name,
                "initiative": initiative_roll.total,
                "roll": initiative_roll.rolls[0],
                "modifier": dex_mod
            })
        
        # Sort by initiative (highest first)
        initiative_order.sort(key=lambda x: x["initiative"], reverse=True)
        
        # Generate encounter start narrative
        narrative = self.lm_client.generate_environment_description(
            "combat encounter",
            "tense",
            [f"{char['character']} (Init: {char['initiative']})" for char in initiative_order]
        )
        
        result = {
            "encounter_id": encounter.id,
            "encounter_name": encounter_name,
            "description": description,
            "participants": participant_names,
            "initiative_order": initiative_order,
            "current_round": 1,
            "narrative": narrative
        }
        
        logger.info(f"Encounter started: {narrative}")
        return result
    
    def process_saving_throw(self, character_name: str, save_type: str, dc: int, 
                           advantage: str = "normal") -> Dict[str, Any]:
        """Process a saving throw with narrative"""
        logger.info(f"{character_name} makes a {save_type} saving throw (DC {dc})")
        
        character = self.database.get_character_by_name(character_name)
        if not character:
            raise ValueError(f"Character not found: {character_name}")
        
        save_bonus = character.saving_throws.get(save_type.upper(), 0)
        adv_type = AdvantageType(advantage.lower())
        
        success, roll_result = self.dice_engine.calculate_saving_throw(save_bonus, dc, adv_type)
        
        result = {
            "character": character_name,
            "save_type": save_type.upper(),
            "dc": dc,
            "roll_total": roll_result.total,
            "roll_natural": roll_result.rolls[0],
            "save_bonus": save_bonus,
            "success": success,
            "advantage": advantage
        }
        
        # Generate narrative
        outcome = "succeeds" if success else "fails"
        narrative = f"{character_name} {outcome} their {save_type} saving throw with a {roll_result.total}!"
        
        # Use LM Studio for more detailed narrative
        situation = f"{character_name} rolling {save_type} save against DC {dc} and {outcome}"
        detailed_narrative = self.lm_client.generate_npc_dialogue(
            "The Narrator",
            situation,
            "dramatic"
        )
        
        result["narrative"] = detailed_narrative
        
        logger.info(f"Saving throw result: {detailed_narrative}")
        return result
    
    def award_experience(self, character_names: List[str], xp_amount: int, 
                        source: str = "combat") -> Dict[str, Any]:
        """Award experience points to multiple characters"""
        logger.info(f"Awarding {xp_amount} XP to {len(character_names)} characters")
        
        results = []
        for name in character_names:
            character = self.database.get_character_by_name(name)
            if character:
                self.database.add_experience(character.id, xp_amount, source)
                results.append({
                    "character": name,
                    "xp_gained": xp_amount,
                    "success": True
                })
            else:
                results.append({
                    "character": name,
                    "xp_gained": 0,
                    "success": False,
                    "error": "Character not found"
                })
        
        # Generate celebration narrative
        success_names = [r["character"] for r in results if r["success"]]
        if success_names:
            narrative = self.lm_client.generate_npc_dialogue(
                "The Narrator",
                f"The party gains {xp_amount} experience points for their {source}",
                "celebratory"
            )
        else:
            narrative = "No experience was awarded."
        
        result = {
            "total_xp": xp_amount,
            "source": source,
            "character_results": results,
            "narrative": narrative
        }
        
        logger.info(f"Experience awarded: {narrative}")
        return result
    
    def get_party_status(self) -> Dict[str, Any]:
        """Get current status of all characters"""
        characters = self.database.list_characters()
        
        party_status = []
        for char in characters:
            hp_percentage = (char.hp_current / char.hp_max) * 100
            status = "healthy"
            if hp_percentage <= 0:
                status = "unconscious"
            elif hp_percentage <= 25:
                status = "critical"
            elif hp_percentage <= 50:
                status = "wounded"
            
            party_status.append({
                "name": char.name,
                "class": char.character_class,
                "level": char.level,
                "hp_current": char.hp_current,
                "hp_max": char.hp_max,
                "hp_percentage": round(hp_percentage, 1),
                "status": status,
                "ac": char.ac
            })
        
        return {
            "party_size": len(party_status),
            "characters": party_status,
            "active_encounter": self.database.get_active_encounter() is not None
        }
    
    def generate_quest_hook(self, quest_type: str = "mystery", difficulty: str = "medium") -> str:
        """Generate a quest hook using LM Studio"""
        return self.lm_client.generate_quest_hook(quest_type, difficulty)
    
    def describe_environment(self, location_type: str, mood: str = "neutral", 
                           features: List[str] = None) -> str:
        """Generate environment description using LM Studio"""
        return self.lm_client.generate_environment_description(location_type, mood, features or [])


async def main():
    """Demo function showing TaleKeeper capabilities"""
    print("=== TaleKeeper Demo ===")
    
    # Initialize TaleKeeper
    talekeeper = TaleKeeper()
    
    # Create some demo characters
    print("\n1. Creating Characters...")
    
    thorin_data = {
        'name': 'Thorin Ironbeard',
        'player_name': 'Alice',
        'character_class': 'Fighter',
        'level': 3,
        'hp_max': 28,
        'ac': 16,
        'stats': {'STR': 16, 'DEX': 14, 'CON': 15, 'INT': 10, 'WIS': 12, 'CHA': 8},
        'background': 'Soldier',
        'alignment': 'Lawful Good'
    }
    
    elara_data = {
        'name': 'Elara Moonwhisper',
        'player_name': 'Bob',
        'character_class': 'Wizard',
        'level': 3,
        'hp_max': 18,
        'ac': 12,
        'stats': {'STR': 8, 'DEX': 14, 'CON': 13, 'INT': 16, 'WIS': 12, 'CHA': 11},
        'background': 'Scholar',
        'alignment': 'Chaotic Good'
    }
    
    thorin = talekeeper.create_character(thorin_data)
    elara = talekeeper.create_character(elara_data)
    
    print(f"Created: {thorin.name} (Fighter, {thorin.hp_current}/{thorin.hp_max} HP)")
    print(f"Created: {elara.name} (Wizard, {elara.hp_current}/{elara.hp_max} HP)")
    
    # Start an encounter
    print("\n2. Starting Combat Encounter...")
    encounter = talekeeper.start_encounter(
        "Goblin Ambush",
        ["Thorin Ironbeard", "Elara Moonwhisper"],
        "The party encounters goblins on the forest road"
    )
    print(f"Encounter: {encounter['encounter_name']}")
    print(f"Initiative: {encounter['initiative_order']}")
    print(f"Narrative: {encounter['narrative']}")
    
    # Process an attack
    print("\n3. Combat Action...")
    attack_result = talekeeper.process_attack(
        "Thorin Ironbeard",
        "Elara Moonwhisper",  # Friendly fire for demo
        "longsword",
        attack_bonus=8,
        damage_dice="1d8+4"
    )
    print(f"Attack result: {attack_result['narrative']}")
    print(f"Damage: {attack_result['damage']}, Target HP: {attack_result['target_hp_after']}")
    
    # Saving throw
    print("\n4. Saving Throw...")
    save_result = talekeeper.process_saving_throw(
        "Elara Moonwhisper",
        "dex",
        15,
        "advantage"
    )
    print(f"Save result: {save_result['narrative']}")
    
    # Award XP
    print("\n5. Experience Award...")
    xp_result = talekeeper.award_experience(
        ["Thorin Ironbeard", "Elara Moonwhisper"],
        200,
        "combat"
    )
    print(f"XP Award: {xp_result['narrative']}")
    
    # Party status
    print("\n6. Party Status...")
    status = talekeeper.get_party_status()
    for char in status['characters']:
        print(f"{char['name']}: {char['hp_current']}/{char['hp_max']} HP ({char['status']})")
    
    # Generate quest hook
    print("\n7. Quest Hook...")
    quest = talekeeper.generate_quest_hook("mystery", "medium")
    print(f"Quest: {quest}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
