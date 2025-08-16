# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Sisteama** is a modular framework for orchestrating agentic workflows that combine deterministic logic with AI models. The first implementation is **Tale Keeper**, a D&D 5e narrative engine and gameplay adjudicator.

## Architecture

The system follows a three-layer architecture:

1. **Core Components** (`core/`):
   - `dice_engine.py` - Deterministic D&D dice mechanics and combat calculations
   - `database.py` - SQLite-based persistence for characters, encounters, and game state
   - `lm_studio_client.py` - HTTP client for local LM Studio server for narrative generation
   - `mcp_server.py` - Model Context Protocol server exposing D&D tools

2. **Flow Orchestrator** (`flows/`):
   - `talekeeper.py` - Main orchestrator coordinating all components and providing high-level game logic

3. **Entry Points**:
   - `main.py` - Basic entry point (currently minimal)
   - `run_mcp_server.py` - MCP server startup script
   - `test_system.py` - Comprehensive system testing

## Key Design Patterns

- **Deterministic Core**: All dice mechanics and rule calculations are pure Python functions without AI dependencies
- **AI-Enhanced Narrative**: LM Studio integration provides rich descriptions while maintaining gameplay integrity
- **MCP Integration**: Tools are exposed via Model Context Protocol for external agent interaction
- **Database-First**: All game state persists in SQLite with JSON columns for flexible data storage

## Development Commands

### Running the System
```bash
# Run system tests (recommended first step)
python test_system.py

# Run the main TaleKeeper demo
python flows/talekeeper.py

# Start MCP server for external clients
python run_mcp_server.py

# Test MCP server with inspector (requires uv)
uv run mcp dev run_mcp_server.py
```

### Testing
- Primary test file: `test_system.py`
- Test databases are created automatically (e.g., `test_talekeeper.db`, `test_integration.db`)
- Tests cover dice engine, database operations, LM Studio integration, and full system orchestration

### Database Management
- Main database: `data/talekeeper.db`
- Test databases: `test_*.db` files
- Schema auto-initializes on first connection
- Characters, encounters, experience, and combat logs are tracked

## Core Components Deep Dive

### Dice Engine (`core/dice_engine.py`)
- Pure deterministic implementation of D&D 5e mechanics
- Handles advantage/disadvantage, critical hits, saving throws, initiative
- Parses dice notation (e.g., "2d6+3", "1d8")
- No external dependencies beyond Python standard library

### Database Layer (`core/database.py`)
- SQLite with JSON columns for flexible character stats
- Character lifecycle: creation, HP management, experience tracking
- Encounter management with initiative order and combat logging
- Foreign key constraints ensure data integrity

### LM Studio Integration (`core/lm_studio_client.py`)
- Connects to local LM Studio server (default: http://localhost:1234)
- Generates combat descriptions, damage/healing narratives, NPC dialogue
- Graceful degradation with fallback responses when LM Studio unavailable
- Specialized prompts for different D&D scenarios

### TaleKeeper Orchestrator (`flows/talekeeper.py`)
- Main coordination layer combining all components
- High-level operations: character creation, combat processing, XP awards
- Narrative generation integrated with mechanical outcomes
- Party status tracking and encounter management

## MCP Server Tools

The MCP server (`core/mcp_server.py`) exposes these tools:
- `roll_d20` - D20 rolls with modifiers and advantage
- `roll_damage` - Damage dice parsing and rolling
- `roll_attack` - Complete attack sequence with narrative
- `create_character` - Full D&D character creation
- `get_character` / `list_characters` - Character data retrieval
- `damage_character` / `heal_character` - HP management
- `start_combat` - Combat encounter initialization
- `roll_saving_throw` - Saving throw mechanics
- `add_experience` - XP tracking

## Dependencies and External Services

### Required Dependencies
- `sqlite3` (built-in)
- `requests` (for LM Studio HTTP calls)
- `mcp` library (for server functionality)
- `fastmcp` (for MCP server framework)
- `pydantic` (for structured responses)

### Optional External Services
- **LM Studio**: Local LLM server for narrative generation (fallback responses if unavailable)
- **uv**: Package manager for MCP development tools

## Database Schema Notes

Characters store:
- Core D&D stats (STR, DEX, CON, INT, WIS, CHA) as JSON
- Calculated modifiers and proficiency bonuses
- Equipment and spells as JSON arrays
- HP, AC, level, and other mechanical data

Encounters track:
- Active/inactive state
- Round and turn management
- Initiative order as JSON
- Participant character IDs

Experience and combat logs provide audit trails for all game actions.

## Integration Points

The system is designed for external integration via:
1. **MCP Protocol**: Standard interface for AI agents
2. **HTTP API**: LM Studio provides narrative enhancement
3. **Database Layer**: Direct SQLite access for custom tools
4. **Python API**: Import `TaleKeeper` class for programmatic use

## File Structure Context

- `agents/` - Contains LLM context and MCP documentation
- `data/` - Database files and persistent storage
- `prompts/` - Reserved for prompt templates (currently empty)
- `venv/` - Python virtual environment (gitignored in practice)