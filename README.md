# Tetris SRS+ Implementation

A modern Tetris implementation featuring the SRS+ (Super Rotation System Plus) rotation system used in TETR.IO, along with contemporary attack mechanics and customizable controls.

## Features

### Gameplay
- **SRS+ Rotation System**: Advanced piece rotation with wall kicks matching TETR.IO's implementation
- **Modern Attack System**: 
  - Accurate attack calculations based on line clears
  - Back-to-Back (B2B) bonus for consecutive Tetrises
  - Combo system with increasing attack multipliers
  - Perfect clear detection (+10 attack bonus)
- **7-Bag Randomizer**: Standard piece generation system
- **Ghost Piece**: Shows where your piece will land
- **Hold Feature**: Save a piece for later use
- **Lock Delay**: 500ms default with movement reset
- **Next Queue**: Shows next 5 pieces

### Statistics Tracking
- **PPS (Pieces Per Second)**: Real-time piece placement rate
- **APM (Attack Per Minute)**: Attack lines sent per minute
- **Lines Cleared**: Total line count
- **Score**: Points based on line clears and drops
- **Level**: Increases every 10 lines
- **Combo Counter**: Tracks consecutive line clears
- **B2B Counter**: Tracks Back-to-Back special clears

### Customization
- **DAS (Delayed Auto Shift)**: Configure initial movement delay (0-500ms)
- **ARR (Auto Repeat Rate)**: Configure continuous movement speed (0-100ms)
- **SDF (Soft Drop Factor)**: Configure soft drop speed multiplier (1-40)
- **Gravity**: Adjustable falling speed (0.1-20.0)
- **Lock Delay**: Time before piece locks in place (100-2000ms)
- **Custom Keybinds**: Fully remappable controls

## Installation

### Requirements
- Python 3.7+
- PyGame 2.0+

### Setup
```bash
# Install PyGame
pip install pygame

# Clone or download the game files
# Ensure you have both tetris_main.py and tetris_settings.py
```

## How to Play

### Running the Game
```bash
python tetris_main.py
```

### Configuring Settings
```bash
python tetris_settings.py
```

### Default Controls
- **←/→**: Move left/right
- **↓**: Soft drop (faster falling)
- **Space**: Hard drop (instant drop)
- **↑**: Rotate clockwise
- **Z**: Rotate counter-clockwise
- **A**: Rotate 180°
- **C**: Hold piece
- **ESC**: Pause game
- **R**: Restart game

### Game Mechanics

#### Movement System
- **DAS**: When holding a direction, the piece will wait for the DAS duration before beginning repeated movement
- **ARR**: After DAS activates, the piece moves continuously at the ARR rate (0 = instant)
- **SDF**: Soft drop moves the piece down by SDF cells per frame

#### Rotation System (SRS+)
The game uses the SRS+ rotation system with advanced wall kicks:
- Pieces can kick off walls and other blocks when rotating
- Different kick tables for I-piece vs other pieces
- Supports 180° rotations

#### Attack System
Attack lines are calculated based on:
- **Single**: 0 lines
- **Double**: 1 line
- **Triple**: 2 lines
- **Tetris**: 4 lines (+ B2B bonus)
- **Perfect Clear**: +10 bonus
- **Combos**: Additional lines based on combo count

#### Lock System
- Pieces have a 500ms lock delay when touching the stack
- Moving or rotating resets the lock timer (up to 15 moves)
- Lock timer doesn't reset after 15 moves to prevent infinite stalling

## Settings Configuration

### Using the Settings Menu
1. Run `python tetris_settings.py`
2. Navigate with ↑/↓ arrows
3. Adjust values with ←/→ arrows
4. Press Enter to edit keybinds
5. Save your settings before exiting

### Settings Explanation
- **DAS**: Lower = more responsive initial movement, Higher = more deliberate control
- **ARR**: 0 = instant repeated movement, Higher = slower repeated movement
- **SDF**: Higher = faster soft drop
- **Gravity**: Higher = pieces fall faster naturally
- **Lock Delay**: Time you have to move piece before it locks

### Settings File
Settings are saved to `settings.json` and loaded automatically on startup.

## Tips for Optimal Play

### Recommended Settings for Different Playstyles
- **Beginners**: DAS: 150ms, ARR: 20ms, SDF: 10
- **Intermediate**: DAS: 100ms, ARR: 10ms, SDF: 20
- **Advanced**: DAS: 80ms, ARR: 0ms, SDF: 40

### Strategies
1. **Stacking**: Keep your board flat to maintain options
2. **T-Spins**: Look for T-shaped holes to maximize attack
3. **4-Wide**: Leave a 4-block well on one side for Tetrises
4. **Combos**: Continuous line clears multiply attack power
5. **Perfect Clears**: Clearing the entire board gives massive attack bonus

## File Structure
```
tetris_main.py      # Main game implementation
tetris_settings.py  # Settings configuration tool
settings.json       # Saved settings (created after first save)
README.md          # This file
```

## Troubleshooting

### Common Issues
1. **Game won't start**: Ensure PyGame is installed correctly
2. **Controls not responding**: Check for key conflicts in settings
3. **Performance issues**: Try reducing graphical effects or closing other programs

### Debug Information
- FPS is locked at 60
- The game uses double buffering for smooth rendering
- All timings are frame-independent using delta time

## Credits
- Rotation system based on TETR.IO's SRS+ implementation
- Attack system follows modern guideline Tetris rules
- Built with Python and PyGame
