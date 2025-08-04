"""
TaleKeeper MCP Server - Provides D&D tools via Model Context Protocol
Integrates dice engine, database, and LM Studio for complete D&D gameplay
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from dice_engine import DiceEngine, AdvantageType, AttackResult, DiceResult
from database import DatabaseManager, Character
from lm_studio_client import LMStudioClient


class AttackResultResponse(BaseModel):
    """Structured response for attack rolls"""
    hit: bool
    attack_total: int
    attack_roll: int
    attack_modifier: int
    damage_total: Optional[int] = None
    damage_rolls: Optional[List[int]] = None
    critical_hit: bool = False
    target_ac: int
    description: str


class CharacterResponse(BaseModel):
    """Structured response for character data"""
    id: str
    name: str
    character_class: str
    level: int
    hp_current: int
    hp_max: int
    ac: int
    stats: Dict[str, int]


class DiceRollResponse(BaseModel):
    """Structured response for dice rolls"""
    total: int
    rolls: List[int]
    modifier: int
    dice_type: str
    description: str
    critical: bool = False


# Initialize components
dice_engine = DiceEngine()
database = DatabaseManager()
lm_client = LMStudioClient()

# Create FastMCP server
mcp = FastMCP("TaleKeeper")


@mcp.tool()
def roll_d20(modifier: int = 0, advantage: str = "normal") -> DiceRollResponse:
    """
    Roll a d20 with optional modifier and advantage/disadvantage
    
    Args:
        modifier: Bonus or penalty to add to the roll
        advantage: "normal", "advantage", or "disadvantage"
    """
    adv_type = AdvantageType(advantage.lower())
    result = dice_engine.roll_d20(modifier, adv_type)
    
    return DiceRollResponse(
        total=result.total,
        rolls=result.rolls,
        modifier=result.modifier,
        dice_type=result.dice_type,
        description=result.description,
        critical=result.critical
    )


@mcp.tool()
def roll_damage(dice_string: str, bonus_modifier: int = 0) -> DiceRollResponse:
    """
    Roll damage dice from notation like '2d6+3'
    
    Args:
        dice_string: Dice notation (e.g., '2d6+3', '1d8', '4d6+2')
        bonus_modifier: Additional modifier beyond what's in the string
    """
    result = dice_engine.roll_damage(dice_string, bonus_modifier)
    
    return DiceRollResponse(
        total=result.total,
        rolls=result.rolls,
        modifier=result.modifier,
        dice_type=result.dice_type,
        description=result.description
    )


@mcp.tool()
def roll_attack(character_name: str, target_ac: int, attack_bonus: int,
               damage_dice: str, advantage: str = "normal") -> AttackResultResponse:
    """
    Roll an attack for a character against a target AC with damage
    
    Args:
        character_name: Name of attacking character
        target_ac: Target's Armor Class
        attack_bonus: Total attack bonus (ability + proficiency + magic)
        damage_dice: Damage dice notation (e.g., '1d8+4')
        advantage: "normal", "advantage", or "disadvantage"
    """
    adv_type = AdvantageType(advantage.lower())
    
    # Roll attack
    attack_result = dice_engine.calculate_attack(attack_bonus, target_ac, adv_type)
    
    damage_total = None
    damage_rolls = None
    
    # If hit, roll damage
    if attack_result.hit:
        if attack_result.critical_hit:
            damage_result = dice_engine.roll_critical_damage(damage_dice)
        else:
            damage_result = dice_engine.roll_damage(damage_dice)
        
        damage_total = damage_result.total
        damage_rolls = damage_result.rolls
        attack_result.damage_roll = damage_result
    
    # Generate narrative description
    context = {
        "attacker": character_name,
        "hit": attack_result.hit,
        "critical": attack_result.critical_hit,
        "attack_roll": attack_result.attack_roll.total,
        "target_ac": target_ac,
        "damage": damage_total
    }
    
    description = lm_client.generate_combat_description(context)
    
    return AttackResultResponse(
        hit=attack_result.hit,
        attack_total=attack_result.attack_roll.total,
        attack_roll=attack_result.attack_roll.rolls[0],
        attack_modifier=attack_result.attack_roll.modifier,
        damage_total=damage_total,
        damage_rolls=damage_rolls,
        critical_hit=attack_result.critical_hit,
        target_ac=target_ac,
        description=description
    )


@mcp.tool()
def create_character(name: str, player_name: str, character_class: str,
                    level: int, hp_max: int, ac: int,
                    strength: int, dexterity: int, constitution: int,
                    intelligence: int, wisdom: int, charisma: int,
                    background: str = "", alignment: str = "True Neutral") -> CharacterResponse:
    """
    Create a new D&D character
    
    Args:
        name: Character name
        player_name: Player's name
        character_class: Character class (Fighter, Wizard, etc.)
        level: Character level (1-20)
        hp_max: Maximum hit points
        ac: Armor Class
        strength: Strength ability score (1-20)
        dexterity: Dexterity ability score (1-20)
        constitution: Constitution ability score (1-20)
        intelligence: Intelligence ability score (1-20)
        wisdom: Wisdom ability score (1-20)
        charisma: Charisma ability score (1-20)
        background: Character background
        alignment: Character alignment
    """
    char_data = {
        'name': name,
        'player_name': player_name,
        'character_class': character_class,
        'level': level,
        'hp_max': hp_max,
        'ac': ac,
        'stats': {
            'STR': strength,
            'DEX': dexterity,
            'CON': constitution,
            'INT': intelligence,
            'WIS': wisdom,
            'CHA': charisma
        },
        'background': background,
        'alignment': alignment
    }
    
    character = database.create_character(char_data)
    
    return CharacterResponse(
        id=character.id,
        name=character.name,
        character_class=character.character_class,
        level=character.level,
        hp_current=character.hp_current,
        hp_max=character.hp_max,
        ac=character.ac,
        stats=character.stats
    )


@mcp.tool()
def get_character(character_name: str) -> Optional[CharacterResponse]:
    """
    Get character information by name
    
    Args:
        character_name: Name of the character to retrieve
    """
    character = database.get_character_by_name(character_name)
    
    if not character:
        return None
    
    return CharacterResponse(
        id=character.id,
        name=character.name,
        character_class=character.character_class,
        level=character.level,
        hp_current=character.hp_current,
        hp_max=character.hp_max,
        ac=character.ac,
        stats=character.stats
    )


@mcp.tool()
def list_characters() -> List[CharacterResponse]:
    """List all characters in the database"""
    characters = database.list_characters()
    
    return [CharacterResponse(
        id=char.id,
        name=char.name,
        character_class=char.character_class,
        level=char.level,
        hp_current=char.hp_current,
        hp_max=char.hp_max,
        ac=char.ac,
        stats=char.stats
    ) for char in characters]


@mcp.tool()
def damage_character(character_name: str, damage: int, damage_type: str = "physical") -> Dict[str, Any]:
    """
    Apply damage to a character
    
    Args:
        character_name: Name of character taking damage
        damage: Amount of damage
        damage_type: Type of damage (for narrative purposes)
    """
    character = database.get_character_by_name(character_name)
    
    if not character:
        return {"success": False, "error": f"Character '{character_name}' not found"}
    
    success, new_hp = database.damage_character(character.id, damage)
    
    if not success:
        return {"success": False, "error": "Failed to apply damage"}
    
    # Generate narrative description
    context = {
        "character": character_name,
        "damage": damage,
        "damage_type": damage_type,
        "old_hp": character.hp_current,
        "new_hp": new_hp,
        "unconscious": new_hp <= 0
    }
    
    description = lm_client.generate_damage_description(context)
    
    return {
        "success": True,
        "character": character_name,
        "damage_taken": damage,
        "old_hp": character.hp_current,
        "new_hp": new_hp,
        "unconscious": new_hp <= 0,
        "description": description
    }


@mcp.tool()
def heal_character(character_name: str, healing: int, heal_type: str = "magical") -> Dict[str, Any]:
    """
    Heal a character
    
    Args:
        character_name: Name of character being healed
        healing: Amount of healing
        heal_type: Type of healing (for narrative purposes)
    """
    character = database.get_character_by_name(character_name)
    
    if not character:
        return {"success": False, "error": f"Character '{character_name}' not found"}
    
    success, new_hp = database.heal_character(character.id, healing)
    
    if not success:
        return {"success": False, "error": "Failed to apply healing"}
    
    # Generate narrative description
    context = {
        "character": character_name,
        "healing": healing,
        "heal_type": heal_type,
        "old_hp": character.hp_current,
        "new_hp": new_hp,
        "max_hp": character.hp_max
    }
    
    description = lm_client.generate_healing_description(context)
    
    return {
        "success": True,
        "character": character_name,
        "healing_received": healing,
        "old_hp": character.hp_current,
        "new_hp": new_hp,
        "description": description
    }


@mcp.tool()
def start_combat(encounter_name: str, participants: List[str], description: str = "") -> Dict[str, Any]:
    """
    Start a new combat encounter
    
    Args:
        encounter_name: Name of the encounter
        participants: List of character names participating
        description: Description of the encounter
    """
    # Validate all participants exist
    character_ids = []
    for name in participants:
        character = database.get_character_by_name(name)
        if not character:
            return {"success": False, "error": f"Character '{name}' not found"}
        character_ids.append(character.id)
    
    encounter = database.create_encounter(encounter_name, description, character_ids)
    
    # Generate initiative order (simplified - could be expanded)
    initiative_order = []
    for name in participants:
        character = database.get_character_by_name(name)
        dex_mod = character.modifiers.get('DEX', 0)
        initiative_roll = dice_engine.roll_initiative(dex_mod)
        initiative_order.append((character.id, initiative_roll.total))
    
    # Sort by initiative (highest first)
    initiative_order.sort(key=lambda x: x[1], reverse=True)
    
    return {
        "success": True,
        "encounter_id": encounter.id,
        "encounter_name": encounter_name,
        "participants": participants,
        "initiative_order": initiative_order,
        "current_round": 1,
        "description": f"Combat begins! {description}"
    }


@mcp.tool()
def roll_saving_throw(character_name: str, save_type: str, dc: int, advantage: str = "normal") -> Dict[str, Any]:
    """
    Roll a saving throw for a character
    
    Args:
        character_name: Name of character making the save
        save_type: Type of save ("STR", "DEX", "CON", "INT", "WIS", "CHA")
        dc: Difficulty Class to beat
        advantage: "normal", "advantage", or "disadvantage"
    """
    character = database.get_character_by_name(character_name)
    
    if not character:
        return {"success": False, "error": f"Character '{character_name}' not found"}
    
    save_bonus = character.saving_throws.get(save_type.upper(), 0)
    adv_type = AdvantageType(advantage.lower())
    
    success, roll_result = dice_engine.calculate_saving_throw(save_bonus, dc, adv_type)
    
    return {
        "success": True,
        "character": character_name,
        "save_type": save_type.upper(),
        "dc": dc,
        "roll_total": roll_result.total,
        "roll_result": roll_result.rolls[0],
        "save_bonus": save_bonus,
        "passed": success,
        "description": f"{character_name} rolls {save_type} save: {roll_result.description} vs DC {dc} - {'SUCCESS' if success else 'FAILURE'}"
    }


@mcp.tool()
def add_experience(character_name: str, xp_amount: int, source: str = "adventure") -> Dict[str, Any]:
    """
    Add experience points to a character
    
    Args:
        character_name: Name of character gaining XP
        xp_amount: Amount of XP to add
        source: Source of the XP (combat, quest, roleplay, etc.)
    """
    character = database.get_character_by_name(character_name)
    
    if not character:
        return {"success": False, "error": f"Character '{character_name}' not found"}
    
    xp_entry = database.add_experience(character.id, xp_amount, source)
    
    return {
        "success": True,
        "character": character_name,
        "xp_gained": xp_amount,
        "source": source,
        "description": f"{character_name} gains {xp_amount} XP from {source}!"
    }


# Resource for character sheets
@mcp.resource("character://{character_name}")
def get_character_sheet(character_name: str) -> str:
    """Get a full character sheet as a resource"""
    character = database.get_character_by_name(character_name)
    
    if not character:
        return f"Character '{character_name}' not found"
    
    # Format character sheet
    sheet = f"""
# {character.name}
**Class:** {character.character_class} (Level {character.level})
**Player:** {character.player_name}
**Background:** {character.background}
**Alignment:** {character.alignment}

## Combat Stats
- **HP:** {character.hp_current}/{character.hp_max}
- **AC:** {character.ac}
- **Proficiency Bonus:** +{character.proficiency_bonus}

## Ability Scores
- **STR:** {character.stats.get('STR', 10)} ({character.modifiers.get('STR', 0):+d})
- **DEX:** {character.stats.get('DEX', 10)} ({character.modifiers.get('DEX', 0):+d})
- **CON:** {character.stats.get('CON', 10)} ({character.modifiers.get('CON', 0):+d})
- **INT:** {character.stats.get('INT', 10)} ({character.modifiers.get('INT', 0):+d})
- **WIS:** {character.stats.get('WIS', 10)} ({character.modifiers.get('WIS', 0):+d})
- **CHA:** {character.stats.get('CHA', 10)} ({character.modifiers.get('CHA', 0):+d})

## Equipment
{chr(10).join(f"- {item}" for item in character.equipment)}

## Notes
{character.notes}
"""
    
    return sheet


# Prompt for combat scenarios
@mcp.prompt()
def combat_scenario(encounter_type: str = "random", difficulty: str = "medium") -> str:
    """Generate a combat scenario prompt"""
    return f"""
You are a D&D Dungeon Master creating a {difficulty} difficulty {encounter_type} encounter.

Please describe:
1. The setting and environment
2. The enemies or challenges
3. Any special terrain or environmental hazards
4. Tactical considerations for the players

Make it engaging and appropriate for the current party level and composition.
"""


if __name__ == "__main__":
    print("Starting TaleKeeper MCP Server...")
    print("Available tools:")
    print("- roll_d20: Roll a d20 with modifiers and advantage")
    print("- roll_damage: Roll damage dice")
    print("- roll_attack: Complete attack roll with damage")
    print("- create_character: Create a new D&D character")
    print("- get_character: Get character information")
    print("- list_characters: List all characters")
    print("- damage_character: Apply damage to a character")
    print("- heal_character: Heal a character")
    print("- start_combat: Begin a combat encounter")
    print("- roll_saving_throw: Roll saving throws")
    print("- add_experience: Award experience points")
    print("\nUse 'uv run mcp dev core/mcp_server.py' to test with inspector")
