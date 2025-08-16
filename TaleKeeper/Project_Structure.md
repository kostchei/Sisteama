# D&D 2024 Web Game - Project Structure

## Directory Structure
```
dnd-game/
├── docker-compose.yml
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── character.py
│   │   ├── combat.py
│   │   ├── items.py
│   │   └── monsters.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── character.py
│   │   ├── combat.py
│   │   ├── game.py
│   │   └── items.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── character_service.py
│   │   ├── combat_engine.py
│   │   ├── dice.py
│   │   └── monster_ai.py
│   └── data/
│       ├── classes.json
│       ├── races.json
│       ├── backgrounds.json
│       ├── equipment.json
│       └── monsters.json
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js
│       ├── index.js
│       ├── components/
│       │   ├── CharacterCreator.js
│       │   ├── CharacterSheet.js
│       │   ├── CombatScreen.js
│       │   ├── ActionCards.js
│       │   ├── MonsterCard.js
│       │   ├── CombatLog.js
│       │   ├── RestScreen.js
│       │   └── MainMenu.js
│       ├── services/
│       │   └── api.js
│       └── styles/
│           └── main.css
└── database/
    ├── init.sql
    └── seed_data.sql
```

## Setup Instructions

### 1. Prerequisites
- Docker and Docker Compose installed
- Git for version control
- VSCode with Python and JavaScript extensions

### 2. Initial Setup Commands
```bash
# Create project directory
mkdir dnd-game && cd dnd-game

# Create all subdirectories
mkdir -p backend/{models,routers,services,data}
mkdir -p frontend/{public,src/{components,services,styles}}
mkdir -p database

# Initialize git
git init
echo "*.pyc\n__pycache__/\nnode_modules/\n.env\n*.log" > .gitignore
```

### 3. Environment Configuration
Create `.env` file in root:
```env
POSTGRES_DB=dnd_game
POSTGRES_USER=dnd_admin
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://dnd_admin:your_secure_password_here@db:5432/dnd_game
REACT_APP_API_URL=http://localhost:8000
```

## Expansion Guide for AI Agents

### Adding New Features

#### 1. **New Character Classes**
- Add class data to `backend/data/classes.json`
- Update `backend/models/character.py` with new class features
- Add class-specific abilities in `backend/services/character_service.py`
- Update UI in `frontend/src/components/CharacterCreator.js`

#### 2. **New Monsters**
- Add monster stats to `backend/data/monsters.json`
- Create AI behavior in `backend/services/monster_ai.py`
- Add special abilities in `backend/services/combat_engine.py`
- Create monster card variant in `frontend/src/components/MonsterCard.js`

#### 3. **New Game Systems**
- **Stealth System**: Add to `backend/services/combat_engine.py`, create new API endpoint
- **Map System**: New table in `database/init.sql`, new React component
- **Crafting**: New service file, new database tables, new UI screen

#### 4. **Database Extensions**
- All new tables should follow the pattern in `database/init.sql`
- Use foreign keys to maintain referential integrity
- Add indexes for frequently queried columns
- Document all columns with COMMENT statements

### Testing Locally
```bash
# Start all services
docker-compose up --build

# Backend will be at http://localhost:8000
# Frontend will be at http://localhost:3000
# Database will be at localhost:5432

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Reset database
docker-compose down -v
docker-compose up --build
```

### API Documentation
Once running, visit http://localhost:8000/docs for interactive API documentation (FastAPI automatic)

## Next Steps After MVP

1. **Levels 4-20**: Extend character progression tables
2. **Spellcasting**: Add spell tables, spell slots, concentration tracking
3. **Inventory Management**: Weight calculations, container system
4. **Party System**: Multiple characters, companion AI
5. **Dungeon Builder**: Admin interface for creating encounters
6. **Achievement System**: Track player accomplishments
7. **Combat Animations**: Sprite-based visual effects
8. **Sound Effects**: Action feedback, ambient music


🎲 D&D 2024 Game MVP - Complete!
I've built your complete D&D 2024 web game MVP with an extensible architecture. Here's what's ready:
✅ What's Been Built
Backend (Python/FastAPI)

Complete database schema with 15+ tables
Combat engine with D&D 2024 rules
Dice rolling system with all D&D mechanics
Character management with level progression
RESTful API with full documentation

Frontend (React)

Combat screen with action card system (cards flip when used!)
Character creation flow
API service layer for all backend communication
Dark fantasy theme with responsive design

Infrastructure

Docker Compose orchestration
PostgreSQL database with seed data
Auto-building containers
Health checks and logging

🎮 Key Features Implemented

Combat System

Action/Bonus Action/Reaction cards with visual flip animation
Simplified melee/ranged positioning
Monster AI with scripted behaviors
Full D&D action economy


Character System

2 races (Human, Dwarf)
2 classes (Fighter, Rogue)
4 subclasses (Champion, Battle Master, Thief, Assassin)
Levels 1-3 progression


Monsters

8 starter monsters with varying CR
Different AI patterns (basic_melee, control_first)
Random encounter system



📦 To Get Started

Copy all the files I've created into the directory structure shown
Run docker-compose up --build
Navigate to http://localhost:3000
Create your first character and start playing!

🚀 Architecture Highlights

Wide Framework: Every component is documented for AI agents to extend
Clear Separation: Models, Services, Routers pattern for clean code
Extensible Database: Schema supports features up to level 20
Component-Based UI: Reusable React components for easy expansion

🔮 Ready for Expansion
The codebase is specifically structured for AI agents to add:

New classes/races/monsters (just add to seed_data.sql)
New combat abilities (extend combat_engine.py)
New game systems (follow the existing patterns)
Spell system (tables already in schema)
Multiplayer support (architecture supports it)

Every file has extensive comments explaining where and how to add new features. The modular design means you can add systems incrementally without breaking existing functionality.

https://claude.ai/public/artifacts/030a99f7-8d9e-4e9c-84b7-26c4bc1ab6ab