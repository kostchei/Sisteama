"""
Database layer for TaleKeeper - manages characters, encounters, and game state.
Uses SQLite for persistence with JSON columns for flexible data storage.
"""

import sqlite3
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Character:
    """Character data structure"""
    id: str
    name: str
    player_name: str
    character_class: str
    level: int
    hp_current: int
    hp_max: int
    ac: int
    stats: Dict[str, int]  # STR, DEX, CON, INT, WIS, CHA
    modifiers: Dict[str, int]  # Calculated modifiers
    proficiency_bonus: int
    saving_throws: Dict[str, int]
    skills: Dict[str, int]
    equipment: List[str]
    spells: List[str]
    background: str
    alignment: str
    notes: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Encounter:
    """Combat encounter data"""
    id: str
    name: str
    description: str
    active: bool
    round_number: int
    current_turn: int
    participants: List[str]  # Character IDs
    initiative_order: List[Tuple[str, int]]  # (character_id, initiative)
    created_at: datetime
    updated_at: datetime


@dataclass
class ExperienceEntry:
    """Experience point tracking"""
    id: str
    character_id: str
    encounter_id: Optional[str]
    xp_gained: int
    source: str  # "combat", "quest", "roleplay", etc.
    description: str
    timestamp: datetime


class DatabaseManager:
    """Manages SQLite database operations for TaleKeeper"""
    
    def __init__(self, db_path: str = "data/talekeeper.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Characters table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    player_name TEXT NOT NULL,
                    character_class TEXT NOT NULL,
                    level INTEGER NOT NULL DEFAULT 1,
                    hp_current INTEGER NOT NULL,
                    hp_max INTEGER NOT NULL,
                    ac INTEGER NOT NULL DEFAULT 10,
                    stats TEXT NOT NULL,  -- JSON: {STR: 10, DEX: 10, ...}
                    modifiers TEXT NOT NULL,  -- JSON: calculated modifiers
                    proficiency_bonus INTEGER NOT NULL DEFAULT 2,
                    saving_throws TEXT NOT NULL,  -- JSON: {STR: 0, DEX: 2, ...}
                    skills TEXT NOT NULL,  -- JSON: {Acrobatics: 2, ...}
                    equipment TEXT NOT NULL DEFAULT '[]',  -- JSON array
                    spells TEXT NOT NULL DEFAULT '[]',  -- JSON array
                    background TEXT NOT NULL DEFAULT '',
                    alignment TEXT NOT NULL DEFAULT 'True Neutral',
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Encounters table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS encounters (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    active BOOLEAN NOT NULL DEFAULT 0,
                    round_number INTEGER NOT NULL DEFAULT 1,
                    current_turn INTEGER NOT NULL DEFAULT 0,
                    participants TEXT NOT NULL DEFAULT '[]',  -- JSON array of character IDs
                    initiative_order TEXT NOT NULL DEFAULT '[]',  -- JSON array of [id, initiative]
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Experience tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experience_log (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    encounter_id TEXT,
                    xp_gained INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (character_id) REFERENCES characters (id),
                    FOREIGN KEY (encounter_id) REFERENCES encounters (id)
                )
            """)
            
            # Combat log for detailed action tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS combat_log (
                    id TEXT PRIMARY KEY,
                    encounter_id TEXT NOT NULL,
                    character_id TEXT,
                    action_type TEXT NOT NULL,  -- 'attack', 'damage', 'heal', 'spell', etc.
                    target_id TEXT,
                    roll_data TEXT,  -- JSON: dice roll details
                    damage INTEGER DEFAULT 0,
                    description TEXT NOT NULL,
                    round_number INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (encounter_id) REFERENCES encounters (id),
                    FOREIGN KEY (character_id) REFERENCES characters (id)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def create_character(self, character_data: Dict[str, Any]) -> Character:
        """Create a new character"""
        char_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Calculate modifiers from stats
        stats = character_data.get('stats', {})
        modifiers = {stat: (value - 10) // 2 for stat, value in stats.items()}
        
        # Default saving throws (base modifiers, no proficiency)
        saving_throws = modifiers.copy()
        
        # Default skills (DEX-based skills as examples)
        skills = {
            'Acrobatics': modifiers.get('DEX', 0),
            'Athletics': modifiers.get('STR', 0),
            'Insight': modifiers.get('WIS', 0),
            'Investigation': modifiers.get('INT', 0),
            'Perception': modifiers.get('WIS', 0),
            'Persuasion': modifiers.get('CHA', 0),
            'Stealth': modifiers.get('DEX', 0),
        }
        
        character = Character(
            id=char_id,
            name=character_data['name'],
            player_name=character_data['player_name'],
            character_class=character_data['character_class'],
            level=character_data.get('level', 1),
            hp_current=character_data['hp_max'],
            hp_max=character_data['hp_max'],
            ac=character_data.get('ac', 10),
            stats=stats,
            modifiers=modifiers,
            proficiency_bonus=2 + ((character_data.get('level', 1) - 1) // 4),
            saving_throws=saving_throws,
            skills=skills,
            equipment=character_data.get('equipment', []),
            spells=character_data.get('spells', []),
            background=character_data.get('background', ''),
            alignment=character_data.get('alignment', 'True Neutral'),
            notes=character_data.get('notes', ''),
            created_at=now,
            updated_at=now
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO characters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                character.id, character.name, character.player_name, character.character_class,
                character.level, character.hp_current, character.hp_max, character.ac,
                json.dumps(character.stats), json.dumps(character.modifiers),
                character.proficiency_bonus, json.dumps(character.saving_throws),
                json.dumps(character.skills), json.dumps(character.equipment),
                json.dumps(character.spells), character.background, character.alignment,
                character.notes, character.created_at, character.updated_at
            ))
            conn.commit()
        
        logger.info(f"Created character: {character.name} (ID: {char_id})")
        return character
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """Get character by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_character(row)
    
    def get_character_by_name(self, name: str) -> Optional[Character]:
        """Get character by name"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM characters WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_character(row)
    
    def list_characters(self) -> List[Character]:
        """List all characters"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM characters ORDER BY name")
            return [self._row_to_character(row) for row in cursor.fetchall()]
    
    def update_character_hp(self, character_id: str, new_hp: int) -> bool:
        """Update character's current HP"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE characters 
                SET hp_current = ?, updated_at = ? 
                WHERE id = ?
            """, (new_hp, datetime.now(), character_id))
            
            success = cursor.rowcount > 0
            if success:
                conn.commit()
                logger.info(f"Updated character {character_id} HP to {new_hp}")
            
            return success
    
    def damage_character(self, character_id: str, damage: int) -> Tuple[bool, int]:
        """Apply damage to character, returns (success, new_hp)"""
        character = self.get_character(character_id)
        if not character:
            return False, 0
        
        new_hp = max(0, character.hp_current - damage)
        success = self.update_character_hp(character_id, new_hp)
        
        return success, new_hp
    
    def heal_character(self, character_id: str, healing: int) -> Tuple[bool, int]:
        """Heal character, returns (success, new_hp)"""
        character = self.get_character(character_id)
        if not character:
            return False, 0
        
        new_hp = min(character.hp_max, character.hp_current + healing)
        success = self.update_character_hp(character_id, new_hp)
        
        return success, new_hp
    
    def create_encounter(self, name: str, description: str = "", participants: List[str] = None) -> Encounter:
        """Create a new encounter"""
        encounter_id = str(uuid.uuid4())
        now = datetime.now()
        
        encounter = Encounter(
            id=encounter_id,
            name=name,
            description=description,
            active=True,
            round_number=1,
            current_turn=0,
            participants=participants or [],
            initiative_order=[],
            created_at=now,
            updated_at=now
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO encounters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                encounter.id, encounter.name, encounter.description, encounter.active,
                encounter.round_number, encounter.current_turn,
                json.dumps(encounter.participants), json.dumps(encounter.initiative_order),
                encounter.created_at, encounter.updated_at
            ))
            conn.commit()
        
        logger.info(f"Created encounter: {name} (ID: {encounter_id})")
        return encounter
    
    def get_active_encounter(self) -> Optional[Encounter]:
        """Get the currently active encounter"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM encounters WHERE active = 1 LIMIT 1")
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_encounter(row)
    
    def add_experience(self, character_id: str, xp_gained: int, source: str, 
                      description: str = "", encounter_id: str = None) -> ExperienceEntry:
        """Add experience points to a character"""
        entry_id = str(uuid.uuid4())
        now = datetime.now()
        
        entry = ExperienceEntry(
            id=entry_id,
            character_id=character_id,
            encounter_id=encounter_id,
            xp_gained=xp_gained,
            source=source,
            description=description,
            timestamp=now
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO experience_log VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id, entry.character_id, entry.encounter_id,
                entry.xp_gained, entry.source, entry.description, entry.timestamp
            ))
            conn.commit()
        
        logger.info(f"Added {xp_gained} XP to character {character_id} from {source}")
        return entry
    
    def log_combat_action(self, encounter_id: str, character_id: str, action_type: str,
                         description: str, roll_data: Dict = None, damage: int = 0,
                         target_id: str = None, round_number: int = 1):
        """Log a combat action"""
        action_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO combat_log VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                action_id, encounter_id, character_id, action_type, target_id,
                json.dumps(roll_data or {}), damage, description, round_number,
                datetime.now()
            ))
            conn.commit()
    
    def get_combat_log(self, encounter_id: str) -> List[Dict]:
        """Get combat log for an encounter"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT cl.*, c.name as character_name
                FROM combat_log cl
                LEFT JOIN characters c ON cl.character_id = c.id
                WHERE cl.encounter_id = ?
                ORDER BY cl.timestamp
            """, (encounter_id,))
            
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]
    
    def _row_to_character(self, row) -> Character:
        """Convert database row to Character object"""
        return Character(
            id=row[0], name=row[1], player_name=row[2], character_class=row[3],
            level=row[4], hp_current=row[5], hp_max=row[6], ac=row[7],
            stats=json.loads(row[8]), modifiers=json.loads(row[9]),
            proficiency_bonus=row[10], saving_throws=json.loads(row[11]),
            skills=json.loads(row[12]), equipment=json.loads(row[13]),
            spells=json.loads(row[14]), background=row[15], alignment=row[16],
            notes=row[17], created_at=row[18], updated_at=row[19]
        )
    
    def _row_to_encounter(self, row) -> Encounter:
        """Convert database row to Encounter object"""
        return Encounter(
            id=row[0], name=row[1], description=row[2], active=bool(row[3]),
            round_number=row[4], current_turn=row[5],
            participants=json.loads(row[6]), initiative_order=json.loads(row[7]),
            created_at=row[8], updated_at=row[9]
        )


if __name__ == "__main__":
    # Example usage
    db = DatabaseManager("test_talekeeper.db")
    
    print("=== Database Test ===")
    
    # Create a test character
    char_data = {
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
    
    character = db.create_character(char_data)
    print(f"Created: {character.name} (Level {character.level} {character.character_class})")
    print(f"HP: {character.hp_current}/{character.hp_max}, AC: {character.ac}")
    print(f"Stats: {character.stats}")
    print(f"Modifiers: {character.modifiers}")
    
    # Test damage
    success, new_hp = db.damage_character(character.id, 8)
    print(f"Damaged for 8 HP: {character.hp_current} → {new_hp}")
    
    # Test healing
    success, new_hp = db.heal_character(character.id, 5)
    print(f"Healed for 5 HP: → {new_hp}")
    
    # Create encounter
    encounter = db.create_encounter("Goblin Ambush", "Party encounters goblins on the road", [character.id])
    print(f"Created encounter: {encounter.name}")
    
    # Add experience
    xp_entry = db.add_experience(character.id, 150, "combat", "Defeated goblin patrol", encounter.id)
    print(f"Added {xp_entry.xp_gained} XP for {xp_entry.source}")
