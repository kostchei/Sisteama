/**
 * File: frontend/src/components/CharacterSheet.js
 * Path: /frontend/src/components/CharacterSheet.js
 * 
 * Character Sheet Component
 * 
 * Pseudo Code:
 * 1. Display complete character information and statistics
 * 2. Show equipment, spells, and abilities
 * 3. Handle character progression and leveling
 * 4. Manage inventory and equipment changes
 * 5. Provide character management actions
 * 
 * AI Agents: Full D&D character sheet display and management.
 */

import React from 'react';
import { useGameStore } from '../services/gameStore';

const CharacterSheet = () => {
  const { character } = useGameStore();

  if (!character) {
    return <div>No character loaded</div>;
  }

  return (
    <div className="character-sheet">
      <h1>{character.name}</h1>
      <div className="character-info">
        <p>Race: {character.race}</p>
        <p>Class: {character.characterClass}</p>
        <p>Level: {character.level}</p>
        <p>HP: {character.hp}/{character.maxHp}</p>
      </div>
      <div className="placeholder">
        <p>Character Sheet - Coming Soon</p>
        <p>This will show full character details, stats, equipment, and abilities.</p>
      </div>
    </div>
  );
};

export default CharacterSheet;