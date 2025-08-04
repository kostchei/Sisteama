"""
Test script for TaleKeeper system components.
Tests dice engine, database, and basic orchestration.
"""

import sys
from pathlib import Path

# Add core directory to path
sys.path.append(str(Path(__file__).parent / "core"))
sys.path.append(str(Path(__file__).parent / "flows"))

from dice_engine import DiceEngine, AdvantageType
from database import DatabaseManager
from lm_studio_client import LMStudioClient
from talekeeper import TaleKeeper


def test_dice_engine():
    """Test the dice engine functionality"""
    print("=== Testing Dice Engine ===")
    
    dice = DiceEngine()
    
    # Test basic d20 roll
    result = dice.roll_d20(5)
    print(f"d20 + 5: {result.description} = {result.total}")
    assert 6 <= result.total <= 25, f"d20+5 should be 6-25, got {result.total}"
    
    # Test advantage
    result = dice.roll_d20(3, AdvantageType.ADVANTAGE)
    print(f"d20 + 3 (Advantage): {result.description} = {result.total}")
    
    # Test damage roll
    damage = dice.roll_damage("2d6+3")
    print(f"Damage: {damage.description} = {damage.total}")
    assert 5 <= damage.total <= 15, f"2d6+3 should be 5-15, got {damage.total}"
    
    # Test attack
    attack = dice.calculate_attack(8, 15)
    print(f"Attack (+8 vs AC 15): {attack.attack_roll.description} = {'HIT' if attack.hit else 'MISS'}")
    
    print("[PASS] Dice engine tests passed!\n")


def test_database():
    """Test the database functionality"""
    print("=== Testing Database ===")
    
    # Use test database
    db = DatabaseManager("test_talekeeper.db")
    
    # Create test character
    char_data = {
        'name': 'Test Character',
        'player_name': 'Test Player',
        'character_class': 'Rogue',
        'level': 2,
        'hp_max': 16,
        'ac': 14,
        'stats': {'STR': 12, 'DEX': 16, 'CON': 14, 'INT': 13, 'WIS': 11, 'CHA': 10},
        'background': 'Criminal'
    }
    
    character = db.create_character(char_data)
    print(f"Created character: {character.name} (ID: {character.id[:8]}...)")
    
    # Test character retrieval
    retrieved = db.get_character_by_name("Test Character")
    assert retrieved is not None, "Failed to retrieve character"
    assert retrieved.name == "Test Character", "Character name mismatch"
    print(f"Retrieved: {retrieved.name} - {retrieved.character_class} Level {retrieved.level}")
    
    # Test damage/healing
    success, new_hp = db.damage_character(character.id, 5)
    assert success, "Failed to apply damage"
    print(f"Applied 5 damage: {character.hp_current} -> {new_hp}")
    
    success, healed_hp = db.heal_character(character.id, 3)
    assert success, "Failed to apply healing"
    print(f"Applied 3 healing: {new_hp} -> {healed_hp}")
    
    # Test encounter creation
    encounter = db.create_encounter("Test Fight", "Testing encounter", [character.id])
    print(f"Created encounter: {encounter.name} (ID: {encounter.id[:8]}...)")
    
    # Test experience
    xp_entry = db.add_experience(character.id, 100, "testing")
    print(f"Added 100 XP from {xp_entry.source}")
    
    print("[PASS] Database tests passed!\n")


def test_lm_studio_client():
    """Test LM Studio client (may fail if LM Studio not running)"""
    print("=== Testing LM Studio Client ===")
    
    client = LMStudioClient()
    
    # Test fallback functionality (should work even without LM Studio)
    context = {
        "attacker": "Test Hero",
        "hit": True,
        "critical": False,
        "attack_roll": 18,
        "target_ac": 15,
        "damage": 8
    }
    
    description = client.generate_combat_description(context)
    print(f"Combat description: {description}")
    assert len(description) > 0, "Should generate some description"
    
    # Test damage description
    damage_context = {
        "character": "Test Character",
        "damage": 5,
        "damage_type": "slashing",
        "old_hp": 16,
        "new_hp": 11,
        "unconscious": False
    }
    
    damage_desc = client.generate_damage_description(damage_context)
    print(f"Damage description: {damage_desc}")
    
    print("[PASS] LM Studio client tests passed!\n")


def test_talekeeper_integration():
    """Test the full TaleKeeper integration"""
    print("=== Testing TaleKeeper Integration ===")
    
    # Initialize with test database
    talekeeper = TaleKeeper("test_integration.db")
    
    # Create a test character
    char_data = {
        'name': 'Integration Hero',
        'player_name': 'Test User',
        'character_class': 'Paladin',
        'level': 1,
        'hp_max': 12,
        'ac': 18,
        'stats': {'STR': 15, 'DEX': 10, 'CON': 14, 'INT': 11, 'WIS': 13, 'CHA': 16},
        'background': 'Noble'
    }
    
    character = talekeeper.create_character(char_data)
    print(f"Created character through TaleKeeper: {character.name}")
    
    # Test party status
    status = talekeeper.get_party_status()
    print(f"Party status: {status['party_size']} characters")
    for char in status['characters']:
        print(f"  - {char['name']}: {char['hp_current']}/{char['hp_max']} HP")
    
    # Test saving throw
    save_result = talekeeper.process_saving_throw("Integration Hero", "wis", 12)
    print(f"Saving throw: {save_result['success']} (rolled {save_result['roll_total']})")
    
    # Test XP award
    xp_result = talekeeper.award_experience(["Integration Hero"], 50, "testing")
    print(f"XP awarded: {xp_result['total_xp']} points")
    
    print("[PASS] TaleKeeper integration tests passed!\n")


def main():
    """Run all tests"""
    print("=== Starting TaleKeeper System Tests ===\n")
    
    try:
        test_dice_engine()
        test_database()
        test_lm_studio_client()
        test_talekeeper_integration()
        
        print("*** All tests passed! System is ready for use. ***")
        
    except Exception as e:
        print(f"*** Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
