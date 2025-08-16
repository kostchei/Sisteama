/**
 * Main D&D Game Application
 * 
 * AI Agents: This is the root component. Add new screens to the router.
 * Game flow: Main Menu -> Character Creation/Load -> Game -> Combat/Rest/Town
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import './styles/main.css';

// Import components
import MainMenu from './components/MainMenu';
import CharacterCreator from './components/CharacterCreator';
import CharacterSheet from './components/CharacterSheet';
import CombatScreen from './components/CombatScreen';
import RestScreen from './components/RestScreen';
import TownScreen from './components/TownScreen';
import GameScreen from './components/GameScreen';

// Import services
import { gameAPI } from './services/api';
import { useGameStore } from './services/gameStore';

function App() {
  const { 
    character, 
    setCharacter, 
    gameState, 
    setGameState,
    isLoading,
    setLoading 
  } = useGameStore();

  useEffect(() => {
    // Check for existing save on mount
    checkExistingSaves();
  }, []);

  const checkExistingSaves = async () => {
    try {
      setLoading(true);
      const saves = await gameAPI.getSaveSlots();
      // AI Agents: Handle auto-load of last played character here
      console.log('Available saves:', saves);
    } catch (error) {
      console.error('Error checking saves:', error);
    } finally {
      setLoading(false);
    }
  };

  // Loading screen
  if (isLoading) {
    return (
      <div className="app loading-screen">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading D&D Game...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="app">
        {/* Toast notifications for game events */}
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#2a2a2a',
              color: '#fff',
              border: '1px solid #444',
            },
            success: {
              iconTheme: {
                primary: '#4ade80',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />

        {/* Main routing */}
        <Routes>
          {/* Main Menu - Entry point */}
          <Route path="/" element={<MainMenu />} />
          
          {/* Character Creation */}
          <Route path="/create-character" element={<CharacterCreator />} />
          
          {/* Main Game Screen - Hub for all game activities */}
          <Route path="/game" element={
            character ? <GameScreen /> : <Navigate to="/" />
          } />
          
          {/* Combat Screen */}
          <Route path="/combat" element={
            character && gameState?.inCombat ? 
              <CombatScreen /> : 
              <Navigate to="/game" />
          } />
          
          {/* Rest Screen */}
          <Route path="/rest" element={
            character ? <RestScreen /> : <Navigate to="/" />
          } />
          
          {/* Town Screen - Shop, Train, Long Rest */}
          <Route path="/town" element={
            character ? <TownScreen /> : <Navigate to="/" />
          } />
          
          {/* Character Sheet - View/Edit character */}
          <Route path="/character" element={
            character ? <CharacterSheet /> : <Navigate to="/" />
          } />
          
          {/* Catch all - redirect to main menu */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>

        {/* Global UI Elements */}
        {character && (
          <div className="global-hud">
            {/* Quick stats display */}
            <div className="quick-stats">
              <span className="stat-hp">
                HP: {character.currentHp}/{character.maxHp}
              </span>
              <span className="stat-level">
                Level {character.level}
              </span>
              <span className="stat-xp">
                XP: {character.experience}
              </span>
            </div>
          </div>
        )}
      </div>
    </Router>
  );
}

export default App;