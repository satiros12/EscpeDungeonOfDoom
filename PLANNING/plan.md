# EscapeDoom - Project Reorganization Plan

## Overview

Transform the existing DOOM-style-Game into a modular uv project with clear MVC architecture, a visual map editor, and main menu system.

---

## 1. Architecture

### 1.1 Directory Structure

```
EscapeDoom/
├── src/
│   ├── data/                    # DATA LAYER (pure data, no pygame)
│   │   ├── __init__.py
│   │   ├── config.py            # Game constants
│   │   ├── map.py               # MapData class (JSON serialization)
│   │   └── entity.py            # EntityDef, NPCDef, StaticDef
│   │
│   ├── engine/                  # ENGINE LAYER (game logic)
│   │   ├── __init__.py
│   │   ├── core.py              # Game class, State machine
│   │   ├── player.py            # Player controller
│   │   ├── raycaster.py         # 3D rendering engine
│   │   ├── pathfinding.py       # A* + patrol/chase logic
│   │   ├── physics.py           # Collision detection
│   │   └── entity_manager.py    # Entity spawning/updating
│   │
│   └── view/                    # VIEW LAYER (rendering & UI)
│       ├── __init__.py
│       ├── renderer.py          # 3D view + sprite rendering
│       ├── menu.py              # Main menu (Start/Editor/Quit)
│       ├── hud.py               # Health, ammo, weapon
│       └── resources/           # Textures, sprites, sounds
│
├── editor/                      # MAP EDITOR APPLICATION
│   ├── __init__.py
│   ├── editor.py                # Editor main window
│   ├── map_canvas.py            # Tile painting (grid-based)
│   ├── entity_panel.py          # Palette: NPC types, objects
│   ├── path_editor.py           # Click waypoints to define patrol
│   └── preview.py               # 3D preview mode
│
├── maps/                        # JSON map files
│   └── level1.json
│
├── main.py                      # Game entry: Menu -> Game
├── editor_main.py               # Editor entry
└── pyproject.toml
```

### 1.2 Layer Responsibilities

| Layer | Responsibility | Dependencies |
|-------|----------------|--------------|
| data | Data structures, JSON, constants | None (pure Python) |
| engine | Game logic, physics, AI | data |
| view | Rendering, UI, menus | engine, data |
| editor | Map editing tools | data, view |

### 1.3 State Machine

```
[Main Menu] --start--> [Game] --ESC--> [Main Menu]
      |
      +----[Editor] -----> [Preview] --> [Editor]
```

---

## 2. Data Layer

### 2.1 Config (src/data/config.py)

```python
# Display
RES = (1600, 900)
FPS = 60

# Player
PLAYER_SPEED = 0.004
PLAYER_ROT_SPEED = 0.002
PLAYER_MAX_HEALTH = 100

# Raycasting
FOV = pi / 3
MAX_DEPTH = 20

# NPC
NPC_DETECTION_RANGE = 5  # tiles
NPC_ATTACK_RANGE = 2
```

### 2.2 Map Data (src/data/map.py)

```python
@dataclass
class MapData:
    name: str
    width: int
    height: int
    tiles: List[List[int]]      # 0=floor, 1+=wall types
    entities: List[EntityDef]
    player_start: Tuple[float, float, float]  # x, y, angle

    def save(self, path: str):      # JSON
    def load(cls, path) -> MapData: # from JSON
```

### 2.3 Entity Definitions (src/data/entity.py)

```python
@dataclass
class NPCDef:
    type: str           # "soldier", "caco_demon", "cyber_demon"
    x: float
    y: float
    patrol: List[Tuple[float, float]]  # sequential waypoints

@dataclass
class StaticDef:
    sprite: str         # "candlebra", "barrel", etc.
    x: float
    y: float
    animated: bool = False

EntityDef = Union[NPCDef, StaticDef]
```

### 2.4 Map JSON Format (maps/level1.json)

```json
{
  "name": "level1",
  "width": 16,
  "height": 16,
  "tiles": [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            ...],
  "entities": [
    {"type": "soldier", "x": 10.5, "y": 5.5, "patrol": [[10,5], [12,5], [12,8], [10,8]]},
    {"type": "caco_demon", "x": 5.5, "y": 14.5, "patrol": []},
    {"type": "static", "sprite": "candlebra", "x": 3.5, "y": 7.5}
  ],
  "player_start": [1.5, 5, 0]
}
```

---

## 3. Engine Layer

### 3.1 Core (src/engine/core.py)

```python
class Game:
    def __init__(self):
        self.state = "menu"  # menu | game | editor | preview
        self.map: MapData = None
        
    def load_map(self, path: str):
    def set_state(self, state: str):
    def run(self):
        while True:
            if self.state == "menu": self.menu.update()
            elif self.state == "game": self.game_loop()
```

### 3.2 Player (src/engine/player.py)

- Movement (WASD + mouse look)
- Shooting (left click)
- Health system
- ESC returns to menu

### 3.3 Pathfinding (src/engine/pathfinding.py)

```python
class PathFinding:
    def get_path(self, start, target) -> Tuple[int, int]:  # A*
    
    def get_npc_state(self, npc, player_pos, patrol_points):
        # State machine:
        # 1. PATROL: follow waypoints sequentially
        # 2. CHASE: if player in detection range, abandon patrol and chase
        # 3. RETURN: if player escapes, return to nearest waypoint then resume patrol
```

### 3.4 Entity Manager (src/engine/entity_manager.py)

```python
class EntityManager:
    def spawn_npc(self, npc_def: NPCDef) -> NPC
    def spawn_static(self, static_def: StaticDef) -> Sprite
    def update(self, dt):
    def get_visible_objects(self, player) -> List[ObjectToRender]
```

---

## 4. View Layer

### 4.1 Menu (src/view/menu.py)

```python
class Menu:
    def __init__(self, game):
        self.options = ["Start Game", "Map Editor", "Quit"]
        self.selected = 0
    
    def handle_input(self, event):
        # Arrow keys to navigate
        # Enter to select
    
    def draw(self, screen):
        # Render menu with title and options
        # Highlight selected option
```

### 4.2 Renderer (src/view/renderer.py)

- Raycasted 3D walls
- Sprite billboarding for NPCs/objects
- Weapon rendering
- HUD overlay

### 4.3 HUD (src/view/hud.py)

- Health bar
- Ammo count

---

## 5. Editor

### 5.1 Map Canvas (editor/map_canvas.py)

- Tile painting: Left-click to place selected tile
- Grid: Shows wall, floor, numbered variants

### 5.2 Entity Panel (editor/entity_panel.py)

- NPCs: Soldier, Caco Demon, Cyber Demon
- Objects: Candle, Barrel, Light
- Drag onto canvas

### 5.3 Path Editor (editor/path_editor.py)

- Select NPC on map
- Click waypoints in sequence (shows lines connecting them)
- Right-click to remove last waypoint
- Visual: numbered circles connected by lines

### 5.4 Preview (editor/preview.py)

- Toggle into 3D view
- Walk around with WASD
- Test NPC patrol paths
- Press ESC to return to editor

---

## 6. Main Entry Points

### 6.1 main.py

```python
if __name__ == "__main__":
    game = Game()
    game.run()
```

### 6.2 editor_main.py

```python
if __name__ == "__main__":
    editor = Editor()
    editor.run()
```

---

## 7. Implementation Order

```
Phase 1: Data Layer
  1.1 config.py
  1.2 map.py (MapData)
  1.3 entity.py (NPCDef, StaticDef)

Phase 2: Engine Layer  
  2.1 core.py (Game skeleton)
  2.2 player.py
  2.3 raycaster.py
  2.4 pathfinding.py (A* + patrol logic)
  2.5 physics.py
  2.6 entity_manager.py

Phase 3: View Layer
  3.1 menu.py
  3.2 renderer.py
  3.3 hud.py

Phase 4: Integration
  4.1 Wire Menu -> Game transition
  4.2 ESC returns to menu

Phase 5: Editor
  5.1 editor.py (main window)
  5.2 map_canvas.py
  5.3 entity_panel.py
  5.4 path_editor.py
  5.5 preview.py

Phase 6: Documentation
  6.1 README.md
```

---

## 8. Dependencies

- pygame >= 2.6.1 (already in pyproject.toml)

---

## 9. Migration Notes

- Keep existing sprite resources (resources/)
- Keep existing sound files (resources/sound/)
- Convert hardcoded map to maps/level1.json
- Convert hardcoded NPC spawns to JSON entities
