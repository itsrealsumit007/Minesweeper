# Enhanced Minesweeper

A modern, feature-rich implementation of the classic Minesweeper game using Python and Pygame. This version includes multiple difficulty levels, themes, power-ups, achievements, and various gameplay enhancements.

## Features

### Core Gameplay
- Three difficulty levels:
  - Easy (8x8 grid, 10 mines)
  - Medium (15x15 grid, 35 mines)
  - Hard (20x20 grid, 80 mines)
- First-click protection (never hit a mine on first click)
- Chord functionality (click numbers to reveal adjacent cells)
- Flag system to mark potential mines
- Timer and mine counter

### Visual Enhancements
- Three beautiful themes:
  - Classic
  - Dark Mode
  - Nature
- Smooth animations and transitions
- Particle effects for various actions
- Flag waving animation
- Modern UI with clear indicators

### Power-Up System
1. 🔍 Reveal Area (Press 1)
   - Safely reveals a 5x5 area around clicked cell
   - 3 charges per game
2. ❄️ Time Freeze (Press 2)
   - Stops the timer for 5 seconds
   - 3 charges per game
3. 🛡️ Safety Net (Press 3)
   - Protects from hitting mines for 10 seconds
   - 3 charges per game

### Achievement System
- 🏆 First Victory: Win your first game
- ⚡ Speed Demon: Win in under 30 seconds
- 🔥 Combo Master: Get a 10x combo
- ✨ Perfectionist: Win without misplacing flags
- 🎨 Theme Explorer: Try all themes
- 👑 Expert: Win on hard difficulty

### Additional Features
- Combo system for quick revelations
- Auto-save system
- High score tracking per difficulty
- Achievement notifications
- Persistent game progress

## Controls

### Mouse Controls
- Left Click: Reveal cell
- Right Click: Place/remove flag
- Left Click on revealed number: Chord (reveal adjacent cells if correct flags are placed)

### Keyboard Controls
- 1: Activate Reveal Area power-up
- 2: Activate Time Freeze power-up
- 3: Activate Safety Net power-up
- R: Restart game
- T: Change theme

### UI Buttons
- Difficulty buttons at the top
- Theme toggle button
- Visual indicators for:
  - Time
  - Remaining mines
  - Current combo
  - Power-up charges
  - Achievements

## Installation

1. Ensure you have Python 3.x installed
2. Install Pygame:
   ```bash
   pip install pygame
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## Requirements
- Python 3.x
- Pygame

## Game Tips
1. Use flags wisely to mark potential mines
2. Build combos by quickly revealing safe cells
3. Use chording (clicking numbers) to quickly reveal multiple cells
4. Save power-ups for challenging situations
5. Try different themes for variety
6. Aim for achievements to track your progress

## Technical Details
- Written in Python using Pygame
- Object-oriented design with clean code structure
- Efficient particle system for visual effects
- Smooth animations using interpolation
- Auto-save system using JSON
- Modular power-up system for easy expansion

