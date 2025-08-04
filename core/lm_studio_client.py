"""
LM Studio HTTP Client for narrative generation.
Connects to local LM Studio server for D&D story and combat descriptions.
"""

import requests
import json
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class LMStudioClient:
    """Client for connecting to LM Studio HTTP API"""
    
    def __init__(self, base_url: str = "http://localhost:1234", model: str = None):
        """
        Initialize LM Studio client
        
        Args:
            base_url: LM Studio server URL (default: http://localhost:1234)
            model: Specific model to use (if None, uses loaded model)
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test if LM Studio server is available"""
        try:
            response = self.session.get(f"{self.base_url}/v1/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                logger.info(f"Connected to LM Studio. Available models: {len(models.get('data', []))}")
                return True
            else:
                logger.warning(f"LM Studio responded with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not connect to LM Studio at {self.base_url}: {e}")
            return False
    
    def _generate_text(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> str:
        """
        Generate text using LM Studio API
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.0 = deterministic, 1.0 = very creative)
            
        Returns:
            Generated text or fallback message
        """
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a skilled Dungeon Master narrating a D&D game. Be descriptive but concise."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"LM Studio API error: {response.status_code} - {response.text}")
                return self._fallback_response(prompt)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to LM Studio failed: {e}")
            return self._fallback_response(prompt)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing LM Studio response: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when LM Studio is unavailable"""
        if "attack" in prompt.lower():
            return "The attack strikes with precision!"
        elif "damage" in prompt.lower():
            return "The character takes significant damage."
        elif "heal" in prompt.lower():
            return "Healing energy flows through the character."
        else:
            return "The action unfolds dramatically."
    
    def generate_combat_description(self, context: Dict[str, Any]) -> str:
        """
        Generate a narrative description of a combat action
        
        Args:
            context: Dictionary with combat details
                - attacker: Name of attacking character
                - hit: Whether the attack hit
                - critical: Whether it was a critical hit
                - attack_roll: The attack roll result
                - target_ac: Target's AC
                - damage: Damage dealt (if any)
        """
        attacker = context.get("attacker", "The attacker")
        hit = context.get("hit", False)
        critical = context.get("critical", False)
        attack_roll = context.get("attack_roll", 0)
        target_ac = context.get("target_ac", 10)
        damage = context.get("damage", 0)
        
        if not hit:
            prompt = f"""
            Describe {attacker}'s attack that missed (rolled {attack_roll} vs AC {target_ac}). 
            Make it dramatic but clearly a miss. Keep it to 1-2 sentences.
            """
        elif critical:
            prompt = f"""
            Describe {attacker}'s critical hit attack that dealt {damage} damage! 
            This was a spectacular, devastating blow. Keep it to 1-2 sentences.
            """
        else:
            prompt = f"""
            Describe {attacker}'s successful attack that dealt {damage} damage 
            (rolled {attack_roll} vs AC {target_ac}). Keep it to 1-2 sentences.
            """
        
        return self._generate_text(prompt, max_tokens=100, temperature=0.8)
    
    def generate_damage_description(self, context: Dict[str, Any]) -> str:
        """
        Generate a narrative description of taking damage
        
        Args:
            context: Dictionary with damage details
                - character: Name of character taking damage
                - damage: Amount of damage
                - damage_type: Type of damage
                - old_hp: HP before damage
                - new_hp: HP after damage
                - unconscious: Whether character is now unconscious
        """
        character = context.get("character", "The character")
        damage = context.get("damage", 0)
        damage_type = context.get("damage_type", "physical")
        old_hp = context.get("old_hp", 0)
        new_hp = context.get("new_hp", 0)
        unconscious = context.get("unconscious", False)
        
        if unconscious:
            prompt = f"""
            Describe {character} taking {damage} {damage_type} damage and falling unconscious 
            (from {old_hp} to {new_hp} HP). Make it dramatic but not graphic. 1-2 sentences.
            """
        elif new_hp <= old_hp // 4:  # Severely injured
            prompt = f"""
            Describe {character} taking {damage} {damage_type} damage and being severely wounded 
            (from {old_hp} to {new_hp} HP). Show they're badly hurt. 1-2 sentences.
            """
        else:
            prompt = f"""
            Describe {character} taking {damage} {damage_type} damage 
            (from {old_hp} to {new_hp} HP). 1-2 sentences.
            """
        
        return self._generate_text(prompt, max_tokens=100, temperature=0.7)
    
    def generate_healing_description(self, context: Dict[str, Any]) -> str:
        """
        Generate a narrative description of healing
        
        Args:
            context: Dictionary with healing details
                - character: Name of character being healed
                - healing: Amount of healing
                - heal_type: Type of healing (magical, potion, etc.)
                - old_hp: HP before healing
                - new_hp: HP after healing
                - max_hp: Maximum HP
        """
        character = context.get("character", "The character")
        healing = context.get("healing", 0)
        heal_type = context.get("heal_type", "magical")
        old_hp = context.get("old_hp", 0)
        new_hp = context.get("new_hp", 0)
        max_hp = context.get("max_hp", 100)
        
        if new_hp >= max_hp:
            prompt = f"""
            Describe {character} being fully healed by {heal_type} healing 
            (from {old_hp} to {new_hp} HP). They're completely restored. 1-2 sentences.
            """
        elif old_hp <= max_hp // 4 and new_hp > max_hp // 2:  # Major recovery
            prompt = f"""
            Describe {character} receiving {healing} points of {heal_type} healing, 
            making a major recovery (from {old_hp} to {new_hp} HP). 1-2 sentences.
            """
        else:
            prompt = f"""
            Describe {character} receiving {healing} points of {heal_type} healing 
            (from {old_hp} to {new_hp} HP). 1-2 sentences.
            """
        
        return self._generate_text(prompt, max_tokens=100, temperature=0.7)
    
    def generate_npc_dialogue(self, npc_name: str, situation: str, personality: str = "friendly") -> str:
        """
        Generate NPC dialogue for a given situation
        
        Args:
            npc_name: Name of the NPC
            situation: Current situation or context
            personality: NPC personality (friendly, hostile, mysterious, etc.)
        """
        prompt = f"""
        As {npc_name}, a {personality} NPC, respond to this situation: {situation}
        
        Speak in character with appropriate tone and mannerisms. 
        Keep it to 1-3 sentences and include dialogue in quotes.
        """
        
        return self._generate_text(prompt, max_tokens=150, temperature=0.9)
    
    def generate_environment_description(self, location_type: str, mood: str = "neutral", 
                                       special_features: List[str] = None) -> str:
        """
        Generate description of a location or environment
        
        Args:
            location_type: Type of location (tavern, dungeon, forest, etc.)
            mood: Desired mood (dark, cheerful, mysterious, etc.)
            special_features: List of special features to include
        """
        features_text = ""
        if special_features:
            features_text = f"Include these features: {', '.join(special_features)}. "
        
        prompt = f"""
        Describe a {mood} {location_type} that the party encounters. 
        {features_text}Make it atmospheric and immersive. 
        Keep it to 2-3 sentences, focusing on what the characters see, hear, and smell.
        """
        
        return self._generate_text(prompt, max_tokens=200, temperature=0.8)
    
    def generate_quest_hook(self, quest_type: str = "mystery", difficulty: str = "medium") -> str:
        """
        Generate a quest hook for the party
        
        Args:
            quest_type: Type of quest (mystery, rescue, exploration, etc.)
            difficulty: Quest difficulty level
        """
        prompt = f"""
        Create a {difficulty} difficulty {quest_type} quest hook for a D&D party. 
        Include the problem, potential rewards, and what makes it urgent or interesting. 
        Keep it to 2-3 sentences.
        """
        
        return self._generate_text(prompt, max_tokens=200, temperature=0.9)


if __name__ == "__main__":
    # Test the LM Studio client
    client = LMStudioClient()
    
    print("=== LM Studio Client Test ===")
    
    # Test combat description
    attack_context = {
        "attacker": "Thorin",
        "hit": True,
        "critical": False,
        "attack_roll": 18,
        "target_ac": 15,
        "damage": 8
    }
    
    combat_desc = client.generate_combat_description(attack_context)
    print(f"Combat: {combat_desc}")
    
    # Test damage description
    damage_context = {
        "character": "Elara",
        "damage": 12,
        "damage_type": "fire",
        "old_hp": 25,
        "new_hp": 13,
        "unconscious": False
    }
    
    damage_desc = client.generate_damage_description(damage_context)
    print(f"Damage: {damage_desc}")
    
    # Test NPC dialogue
    dialogue = client.generate_npc_dialogue("Gruff Bartender", "The party asks about local rumors", "grumpy")
    print(f"NPC: {dialogue}")
    
    # Test environment
    environment = client.generate_environment_description("ancient tomb", "ominous", ["glowing runes", "stone statues"])
    print(f"Environment: {environment}")
