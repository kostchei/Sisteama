"""
Deterministic dice rolling engine for D&D 5e mechanics.
Handles all dice-based calculations with pure logic.
"""

import random
import re
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class AdvantageType(Enum):
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"


@dataclass
class DiceResult:
    """Result of a dice roll with detailed breakdown"""
    total: int
    rolls: List[int]
    modifier: int
    dice_type: str
    advantage_type: AdvantageType = AdvantageType.NORMAL
    critical: bool = False
    description: str = ""


@dataclass
class AttackResult:
    """Result of an attack roll"""
    hit: bool
    attack_roll: DiceResult
    damage_roll: Optional[DiceResult] = None
    critical_hit: bool = False
    target_ac: int = 0


class DiceEngine:
    """Core dice rolling engine for D&D 5e mechanics"""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize with optional seed for reproducible results"""
        if seed is not None:
            random.seed(seed)
    
    def roll_die(self, sides: int) -> int:
        """Roll a single die with given number of sides"""
        return random.randint(1, sides)
    
    def roll_multiple(self, count: int, sides: int) -> List[int]:
        """Roll multiple dice of the same type"""
        return [self.roll_die(sides) for _ in range(count)]
    
    def roll_d20(self, modifier: int = 0, advantage: AdvantageType = AdvantageType.NORMAL) -> DiceResult:
        """
        Roll a d20 with optional modifier and advantage/disadvantage
        
        Args:
            modifier: Bonus or penalty to add to the roll
            advantage: Normal, advantage, or disadvantage
            
        Returns:
            DiceResult with detailed breakdown
        """
        if advantage == AdvantageType.NORMAL:
            rolls = [self.roll_die(20)]
        else:
            # Roll twice for advantage/disadvantage
            roll1 = self.roll_die(20)
            roll2 = self.roll_die(20)
            rolls = [roll1, roll2]
            
            if advantage == AdvantageType.ADVANTAGE:
                rolls = [max(roll1, roll2)]
            else:  # DISADVANTAGE
                rolls = [min(roll1, roll2)]
        
        total = rolls[0] + modifier
        critical = rolls[0] == 20
        
        return DiceResult(
            total=total,
            rolls=rolls,
            modifier=modifier,
            dice_type="d20",
            advantage_type=advantage,
            critical=critical,
            description=self._format_d20_description(rolls, modifier, advantage, critical)
        )
    
    def parse_dice_string(self, dice_string: str) -> Tuple[int, int, int]:
        """
        Parse dice notation like '2d6+3' or '1d8-1'
        
        Returns:
            Tuple of (count, sides, modifier)
        """
        # Clean the string
        dice_string = dice_string.strip().lower().replace(" ", "")
        
        # Pattern: optional count, 'd', sides, optional modifier
        pattern = r'^(\d*)d(\d+)([+-]\d+)?$'
        match = re.match(pattern, dice_string)
        
        if not match:
            raise ValueError(f"Invalid dice notation: {dice_string}")
        
        count_str, sides_str, modifier_str = match.groups()
        
        count = int(count_str) if count_str else 1
        sides = int(sides_str)
        modifier = int(modifier_str) if modifier_str else 0
        
        return count, sides, modifier
    
    def roll_damage(self, dice_string: str, bonus_modifier: int = 0) -> DiceResult:
        """
        Roll damage dice from notation like '2d6+3'
        
        Args:
            dice_string: Dice notation (e.g., '2d6+3', '1d8', '4d6+2')
            bonus_modifier: Additional modifier beyond what's in the string
            
        Returns:
            DiceResult with damage breakdown
        """
        count, sides, string_modifier = self.parse_dice_string(dice_string)
        total_modifier = string_modifier + bonus_modifier
        
        rolls = self.roll_multiple(count, sides)
        total = sum(rolls) + total_modifier
        
        return DiceResult(
            total=total,
            rolls=rolls,
            modifier=total_modifier,
            dice_type=f"{count}d{sides}",
            description=self._format_damage_description(rolls, total_modifier, dice_string)
        )
    
    def calculate_attack(self, attack_bonus: int, target_ac: int, 
                        advantage: AdvantageType = AdvantageType.NORMAL) -> AttackResult:
        """
        Calculate an attack roll against target AC
        
        Args:
            attack_bonus: Total attack bonus (ability + proficiency + magic)
            target_ac: Target's Armor Class
            advantage: Advantage type for the roll
            
        Returns:
            AttackResult with hit/miss and roll details
        """
        attack_roll = self.roll_d20(attack_bonus, advantage)
        
        # Natural 20 always hits and is critical
        if attack_roll.rolls[0] == 20:
            hit = True
            critical_hit = True
        # Natural 1 always misses
        elif attack_roll.rolls[0] == 1:
            hit = False
            critical_hit = False
        else:
            hit = attack_roll.total >= target_ac
            critical_hit = False
        
        return AttackResult(
            hit=hit,
            attack_roll=attack_roll,
            critical_hit=critical_hit,
            target_ac=target_ac
        )
    
    def roll_critical_damage(self, base_damage: str, bonus_modifier: int = 0) -> DiceResult:
        """
        Roll critical hit damage (double the dice, not the modifier)
        
        Args:
            base_damage: Base damage dice string
            bonus_modifier: Additional modifier
            
        Returns:
            DiceResult with doubled dice damage
        """
        count, sides, string_modifier = self.parse_dice_string(base_damage)
        
        # Double the number of dice for critical hits
        critical_count = count * 2
        total_modifier = string_modifier + bonus_modifier
        
        rolls = self.roll_multiple(critical_count, sides)
        total = sum(rolls) + total_modifier
        
        return DiceResult(
            total=total,
            rolls=rolls,
            modifier=total_modifier,
            dice_type=f"{critical_count}d{sides}",
            critical=True,
            description=f"Critical hit! {critical_count}d{sides} + {total_modifier} = {total}"
        )
    
    def calculate_saving_throw(self, save_bonus: int, dc: int,
                              advantage: AdvantageType = AdvantageType.NORMAL) -> Tuple[bool, DiceResult]:
        """
        Calculate a saving throw against a DC
        
        Args:
            save_bonus: Character's saving throw bonus
            dc: Difficulty Class to beat
            advantage: Advantage type for the roll
            
        Returns:
            Tuple of (success, DiceResult)
        """
        roll = self.roll_d20(save_bonus, advantage)
        success = roll.total >= dc
        
        return success, roll
    
    def roll_initiative(self, dex_modifier: int) -> DiceResult:
        """Roll initiative (d20 + Dex modifier)"""
        return self.roll_d20(dex_modifier)
    
    def roll_ability_scores(self, method: str = "4d6_drop_lowest") -> List[int]:
        """
        Roll ability scores using various methods
        
        Args:
            method: "4d6_drop_lowest", "3d6", or "point_buy"
            
        Returns:
            List of 6 ability scores
        """
        if method == "4d6_drop_lowest":
            scores = []
            for _ in range(6):
                rolls = self.roll_multiple(4, 6)
                # Drop the lowest
                rolls.sort(reverse=True)
                scores.append(sum(rolls[:3]))
            return scores
        
        elif method == "3d6":
            return [sum(self.roll_multiple(3, 6)) for _ in range(6)]
        
        else:
            raise ValueError(f"Unknown ability score method: {method}")
    
    def _format_d20_description(self, rolls: List[int], modifier: int, 
                               advantage: AdvantageType, critical: bool) -> str:
        """Format description for d20 rolls"""
        if advantage == AdvantageType.ADVANTAGE:
            base = f"Advantage: {rolls} -> {max(rolls)}"
        elif advantage == AdvantageType.DISADVANTAGE:
            base = f"Disadvantage: {rolls} -> {min(rolls)}"
        else:
            base = f"Roll: {rolls[0]}"
        
        if modifier != 0:
            base += f" + {modifier}" if modifier > 0 else f" - {abs(modifier)}"
        
        if critical:
            base += " (Critical!)"
            
        return base
    
    def _format_damage_description(self, rolls: List[int], modifier: int, dice_string: str) -> str:
        """Format description for damage rolls"""
        roll_str = " + ".join(map(str, rolls))
        if modifier > 0:
            return f"{dice_string}: [{roll_str}] + {modifier}"
        elif modifier < 0:
            return f"{dice_string}: [{roll_str}] - {abs(modifier)}"
        else:
            return f"{dice_string}: [{roll_str}]"


# Utility functions for common D&D calculations
def get_ability_modifier(ability_score: int) -> int:
    """Calculate ability modifier from ability score"""
    return (ability_score - 10) // 2


def get_proficiency_bonus(level: int) -> int:
    """Calculate proficiency bonus based on character level"""
    return 2 + ((level - 1) // 4)


def calculate_spell_save_dc(level: int, ability_modifier: int) -> int:
    """Calculate spell save DC"""
    return 8 + get_proficiency_bonus(level) + ability_modifier


def calculate_spell_attack_bonus(level: int, ability_modifier: int) -> int:
    """Calculate spell attack bonus"""
    return get_proficiency_bonus(level) + ability_modifier


if __name__ == "__main__":
    # Example usage
    dice = DiceEngine()
    
    print("=== Dice Engine Test ===")
    
    # Test basic d20 roll
    result = dice.roll_d20(5)
    print(f"d20 + 5: {result.description} = {result.total}")
    
    # Test advantage
    result = dice.roll_d20(3, AdvantageType.ADVANTAGE)
    print(f"d20 + 3 (Advantage): {result.description} = {result.total}")
    
    # Test damage roll
    damage = dice.roll_damage("2d6+3")
    print(f"Damage: {damage.description} = {damage.total}")
    
    # Test attack
    attack = dice.calculate_attack(8, 15)
    print(f"Attack (+8 vs AC 15): {attack.attack_roll.description} = {'HIT' if attack.hit else 'MISS'}")
    
    # Test critical damage
    if attack.critical_hit:
        crit_damage = dice.roll_critical_damage("1d8+4")
        print(f"Critical damage: {crit_damage.description} = {crit_damage.total}")
