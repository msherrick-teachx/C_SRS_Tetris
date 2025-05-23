import pygame
import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import time
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
VISIBLE_HEIGHT = 20
BUFFER_HEIGHT = 20
TOTAL_HEIGHT = VISIBLE_HEIGHT + BUFFER_HEIGHT
CELL_SIZE = 25
BOARD_X = 250
BOARD_Y = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Piece colors
PIECE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

# SRS+ piece data
PIECES = {
    'I': [
        [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
        [[0,0,1,0], [0,0,1,0], [0,0,1,0], [0,0,1,0]],
        [[0,0,0,0], [0,0,0,0], [1,1,1,1], [0,0,0,0]],
        [[0,1,0,0], [0,1,0,0], [0,1,0,0], [0,1,0,0]]
    ],
    'O': [
        [[1,1], [1,1]],
        [[1,1], [1,1]],
        [[1,1], [1,1]],
        [[1,1], [1,1]]
    ],
    'T': [
        [[0,1,0], [1,1,1], [0,0,0]],
        [[0,1,0], [0,1,1], [0,1,0]],
        [[0,0,0], [1,1,1], [0,1,0]],
        [[0,1,0], [1,1,0], [0,1,0]]
    ],
    'S': [
        [[0,1,1], [1,1,0], [0,0,0]],
        [[0,1,0], [0,1,1], [0,0,1]],
        [[0,0,0], [0,1,1], [1,1,0]],
        [[1,0,0], [1,1,0], [0,1,0]]
    ],
    'Z': [
        [[1,1,0], [0,1,1], [0,0,0]],
        [[0,0,1], [0,1,1], [0,1,0]],
        [[0,0,0], [1,1,0], [0,1,1]],
        [[0,1,0], [1,1,0], [1,0,0]]
    ],
    'J': [
        [[1,0,0], [1,1,1], [0,0,0]],
        [[0,1,1], [0,1,0], [0,1,0]],
        [[0,0,0], [1,1,1], [0,0,1]],
        [[0,1,0], [0,1,0], [1,1,0]]
    ],
    'L': [
        [[0,0,1], [1,1,1], [0,0,0]],
        [[0,1,0], [0,1,0], [0,1,1]],
        [[0,0,0], [1,1,1], [1,0,0]],
        [[1,1,0], [0,1,0], [0,1,0]]
    ]
}

# SRS+ wall kicks
WALL_KICKS = {
    'JLSTZ': {
        (0, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (1, 0): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        (1, 2): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        (2, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (2, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        (3, 2): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (3, 0): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (0, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]
    },
    'I': {
        (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        (1, 0): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        (2, 1): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        (2, 3): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        (3, 0): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]
    }
}

class InputKey(Enum):
    LEFT = "left"
    RIGHT = "right"
    SOFT_DROP = "soft_drop"
    HARD_DROP = "hard_drop"
    ROTATE_CW = "rotate_cw"
    ROTATE_CCW = "rotate_ccw"
    ROTATE_180 = "rotate_180"
    HOLD = "hold"
    PAUSE = "pause"
    RESTART = "restart"

@dataclass
class Settings:
    das: int = 100  # Delayed Auto Shift (ms)
    arr: int = 0    # Auto Repeat Rate (ms)
    sdf: int = 5    # Soft Drop Factor
    gravity: float = 1.0
    lock_delay: int = 500  # ms
    
    keybinds: Dict[InputKey, int] = None
    
    def __post_init__(self):
        if self.keybinds is None:
            self.keybinds = {
                InputKey.LEFT: pygame.K_LEFT,
                InputKey.RIGHT: pygame.K_RIGHT,
                InputKey.SOFT_DROP: pygame.K_DOWN,
                InputKey.HARD_DROP: pygame.K_SPACE,
                InputKey.ROTATE_CW: pygame.K_UP,
                InputKey.ROTATE_CCW: pygame.K_z,
                InputKey.ROTATE_180: pygame.K_a,
                InputKey.HOLD: pygame.K_c,
                InputKey.PAUSE: pygame.K_ESCAPE,
                InputKey.RESTART: pygame.K_r
            }
    
    def save(self, filename="settings.json"):
        data = {
            "das": self.das,
            "arr": self.arr,
            "sdf": self.sdf,
            "gravity": self.gravity,
            "lock_delay": self.lock_delay,
            "keybinds": {k.value: v for k, v in self.keybinds.items()}
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filename="settings.json"):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                self.das = data.get("das", self.das)
                self.arr = data.get("arr", self.arr)
                self.sdf = data.get("sdf", self.sdf)
                self.gravity = data.get("gravity", self.gravity)
                self.lock_delay = data.get("lock_delay", self.lock_delay)
                
                if "keybinds" in data:
                    self.keybinds = {
                        InputKey(k): v for k, v in data["keybinds"].items()
                    }

class Piece:
    def __init__(self, piece_type: str, x: int = 3, y: int = 18):
        self.type = piece_type
        self.x = x
        self.y = y
        self.rotation = 0
        self.shape = PIECES[piece_type]
        self.color = PIECE_COLORS[piece_type]
        
    def get_current_shape(self):
        return self.shape[self.rotation]
    
    def get_blocks(self):
        blocks = []
        shape = self.get_current_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    blocks.append((self.x + x, self.y + y))
        return blocks

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(BOARD_WIDTH)] for _ in range(TOTAL_HEIGHT)]
        self.current_piece = None
        self.hold_piece = None
        self.can_hold = True
        self.next_pieces = []
        self.bag = []
        self.game_over = False
        
        # Stats
        self.lines_cleared = 0
        self.level = 1
        self.score = 0
        self.pieces_placed = 0
        self.attack_sent = 0
        self.b2b_count = 0
        self.combo_count = 0
        
        # Timing
        self.gravity_timer = 0
        self.lock_timer = 0
        self.is_locking = False
        self.lock_moves = 0
        self.max_lock_moves = 15
        
        # Initialize piece queue
        self._refill_bag()
        self.next_pieces = [self._get_next_from_bag() for _ in range(5)]
        self.spawn_piece()
    
    def _refill_bag(self):
        self.bag = list(PIECES.keys())
        random.shuffle(self.bag)
    
    def _get_next_from_bag(self):
        if not self.bag:
            self._refill_bag()
        return self.bag.pop()
    
    def spawn_piece(self):
        piece_type = self.next_pieces.pop(0)
        self.next_pieces.append(self._get_next_from_bag())
        
        # SRS+ spawn position - spawn near top of grid (which appears at bottom after display flip)
        spawn_x = 3
        spawn_y = 38  # Near top of total grid
        
        self.current_piece = Piece(piece_type, spawn_x, spawn_y)
        self.can_hold = True
        self.is_locking = False
        self.lock_timer = 0
        self.lock_moves = 0
        
        # Check game over
        if not self.is_valid_position(self.current_piece):
            self.game_over = True
    
    def is_valid_position(self, piece: Piece, dx: int = 0, dy: int = 0) -> bool:
        for block_x, block_y in piece.get_blocks():
            new_x = block_x + dx
            new_y = block_y + dy
            
            # Check boundaries
            if new_x < 0 or new_x >= BOARD_WIDTH:
                return False
            if new_y < 0 or new_y >= TOTAL_HEIGHT:
                return False
            # Check collision with placed pieces
            if self.grid[new_y][new_x] is not None:
                return False
        
        return True
    
    def move_piece(self, dx: int, dy: int) -> bool:
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            
            # Reset lock timer on successful move
            if self.is_locking and dy == 0:
                self.lock_moves += 1
                if self.lock_moves < self.max_lock_moves:
                    self.lock_timer = 0
            
            return True
        return False
    
    def rotate_piece(self, direction: int) -> bool:
        """Rotate piece with SRS+ wall kicks"""
        if not self.current_piece:
            return False
        
        old_rotation = self.current_piece.rotation
        new_rotation = (old_rotation + direction) % 4
        
        # Try basic rotation
        self.current_piece.rotation = new_rotation
        if self.is_valid_position(self.current_piece):
            if self.is_locking:
                self.lock_moves += 1
                if self.lock_moves < self.max_lock_moves:
                    self.lock_timer = 0
            return True
        
        # Try wall kicks
        kick_table = WALL_KICKS['I'] if self.current_piece.type == 'I' else WALL_KICKS['JLSTZ']
        kicks = kick_table.get((old_rotation, new_rotation), [])
        
        for kick_x, kick_y in kicks:
            if self.is_valid_position(self.current_piece, kick_x, kick_y):
                self.current_piece.x += kick_x
                self.current_piece.y += kick_y
                if self.is_locking:
                    self.lock_moves += 1
                    if self.lock_moves < self.max_lock_moves:
                        self.lock_timer = 0
                return True
        
        # Rotation failed
        self.current_piece.rotation = old_rotation
        return False
    
    def rotate_180(self) -> bool:
        """180 degree rotation"""
        if self.rotate_piece(1):
            return self.rotate_piece(1)
        return False
    
    def hard_drop(self):
        drop_distance = 0
        while self.move_piece(0, -1):  # Move down (decrease Y)
            drop_distance += 1
        
        # Score for hard drop
        self.score += drop_distance * 2
        self.lock_piece()
    
    def soft_drop(self) -> int:
        if self.move_piece(0, -1):  # Move down (decrease Y)
            self.score += 1
            return 1
        return 0
    
    def hold(self):
        if not self.can_hold or not self.current_piece:
            return
        
        self.can_hold = False
        current_type = self.current_piece.type
        
        if self.hold_piece is None:
            self.hold_piece = current_type
            self.spawn_piece()
        else:
            self.hold_piece, temp = current_type, self.hold_piece
            self.current_piece = Piece(temp, 3, 38)
    
    def lock_piece(self):
        if not self.current_piece:
            return
        
        # Place piece on board
        for x, y in self.current_piece.get_blocks():
            if 0 <= y < TOTAL_HEIGHT:
                self.grid[y][x] = self.current_piece.color
        
        self.pieces_placed += 1
        
        # Clear lines and calculate attack
        lines_cleared = self.clear_lines()
        attack = self.calculate_attack(lines_cleared)
        self.attack_sent += attack
        
        # Update combo
        if lines_cleared > 0:
            self.combo_count += 1
        else:
            self.combo_count = 0
        
        # Spawn next piece
        self.spawn_piece()
    
    def clear_lines(self) -> int:
        lines_to_clear = []
        
        # Check all rows for completed lines
        for y in range(TOTAL_HEIGHT):
            if all(self.grid[y][x] is not None for x in range(BOARD_WIDTH)):
                lines_to_clear.append(y)
        
        # Remove cleared lines and shift everything down
        for y in sorted(lines_to_clear, reverse=True):
            del self.grid[y]
        
        # Add new empty lines at the top (buffer zone)
        for _ in range(len(lines_to_clear)):
            self.grid.append([None for _ in range(BOARD_WIDTH)])
        
        lines_cleared = len(lines_to_clear)
        self.lines_cleared += lines_cleared
        
        # Update level
        self.level = 1 + self.lines_cleared // 10
        
        # Score calculation
        if lines_cleared > 0:
            base_score = [0, 100, 300, 500, 800][lines_cleared]
            self.score += base_score * self.level
        
        return lines_cleared
    
    def calculate_attack(self, lines: int) -> int:
        """Calculate attack based on modern Tetris attack table"""
        if lines == 0:
            return 0
        
        # Base attack values
        attack_table = {
            1: 0,  # Single
            2: 1,  # Double
            3: 2,  # Triple
            4: 4   # Tetris
        }
        
        base_attack = attack_table.get(lines, 0)
        
        # Perfect clear bonus
        if all(self.grid[y][x] is None for y in range(TOTAL_HEIGHT) for x in range(BOARD_WIDTH)):
            base_attack += 10
        
        # B2B bonus for Tetris and T-spins
        if lines == 4:
            if self.b2b_count > 0:
                base_attack += 1
            self.b2b_count += 1
        else:
            self.b2b_count = 0
        
        # Combo bonus
        combo_table = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 5]
        if self.combo_count > 0 and self.combo_count < len(combo_table):
            base_attack += combo_table[self.combo_count]
        elif self.combo_count >= len(combo_table):
            base_attack += 5
        
        return base_attack
    
    def update(self, dt: float, settings: Settings):
        if self.game_over or not self.current_piece:
            return
        
        # Gravity (pieces fall down visually, decreasing Y in grid)
        self.gravity_timer += dt * settings.gravity * self.level
        
        while self.gravity_timer >= 1000:
            self.gravity_timer -= 1000
            if not self.move_piece(0, -1):  # Move down (decrease Y)
                self.is_locking = True
        
        # Lock delay
        if self.is_locking:
            self.lock_timer += dt
            if self.lock_timer >= settings.lock_delay or self.lock_moves >= self.max_lock_moves:
                self.lock_piece()
                
        # Check if piece should start locking (touching ground or other pieces)
        if not self.is_locking and not self.is_valid_position(self.current_piece, 0, -1):
            self.is_locking = True

class InputHandler:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.key_states = {}
        self.key_timers = {}
        self.das_charged = {}
        
        for key in InputKey:
            self.key_states[key] = False
            self.key_timers[key] = 0
            self.das_charged[key] = False
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            for input_key, key_code in self.settings.keybinds.items():
                if event.key == key_code:
                    self.key_states[input_key] = True
                    self.key_timers[input_key] = 0
                    self.das_charged[input_key] = False
                    return input_key
        
        elif event.type == pygame.KEYUP:
            for input_key, key_code in self.settings.keybinds.items():
                if event.key == key_code:
                    self.key_states[input_key] = False
                    self.key_timers[input_key] = 0
                    self.das_charged[input_key] = False
        
        return None
    
    def update(self, dt: float):
        actions = []
        
        for input_key in [InputKey.LEFT, InputKey.RIGHT, InputKey.SOFT_DROP]:
            if self.key_states[input_key]:
                self.key_timers[input_key] += dt
                
                if not self.das_charged[input_key]:
                    if self.key_timers[input_key] >= self.settings.das:
                        self.das_charged[input_key] = True
                        self.key_timers[input_key] = 0
                        actions.append(input_key)
                else:
                    if self.settings.arr == 0:
                        actions.append(input_key)
                    elif self.key_timers[input_key] >= self.settings.arr:
                        self.key_timers[input_key] -= self.settings.arr
                        actions.append(input_key)
        
        return actions

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris SRS+")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        self.settings = Settings()
        self.settings.load()
        
        self.board = Board()
        self.input_handler = InputHandler(self.settings)
        
        self.paused = False
        self.running = True
        
        # Timing stats
        self.start_time = time.time()
        self.frame_times = []
    
    def calculate_stats(self):
        elapsed_time = time.time() - self.start_time
        
        # PPS (Pieces Per Second)
        pps = self.board.pieces_placed / elapsed_time if elapsed_time > 0 else 0
        
        # APM (Attack Per Minute)
        apm = (self.board.attack_sent / elapsed_time) * 60 if elapsed_time > 0 else 0
        
        return {
            "time": elapsed_time,
            "pps": pps,
            "apm": apm,
            "lines": self.board.lines_cleared,
            "attack": self.board.attack_sent,
            "level": self.board.level,
            "score": self.board.score,
            "combo": self.board.combo_count,
            "b2b": self.board.b2b_count
        }
    
    def draw_board(self):
        # Draw board background
        board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH * CELL_SIZE, VISIBLE_HEIGHT * CELL_SIZE)
        pygame.draw.rect(self.screen, DARK_GRAY, board_rect)
        pygame.draw.rect(self.screen, WHITE, board_rect, 2)
        
        # Draw grid lines
        for x in range(BOARD_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY, 
                           (BOARD_X + x * CELL_SIZE, BOARD_Y),
                           (BOARD_X + x * CELL_SIZE, BOARD_Y + VISIBLE_HEIGHT * CELL_SIZE), 1)
        
        for y in range(VISIBLE_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY,
                           (BOARD_X, BOARD_Y + y * CELL_SIZE),
                           (BOARD_X + BOARD_WIDTH * CELL_SIZE, BOARD_Y + y * CELL_SIZE), 1)
        
        # Draw placed pieces
        for y in range(TOTAL_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board.grid[y][x] is not None:
                    # Convert from grid coordinates to screen coordinates
                    screen_y = TOTAL_HEIGHT - 1 - y
                    if screen_y < VISIBLE_HEIGHT:
                        rect = pygame.Rect(BOARD_X + x * CELL_SIZE + 1,
                                         BOARD_Y + screen_y * CELL_SIZE + 1,
                                         CELL_SIZE - 2, CELL_SIZE - 2)
                        pygame.draw.rect(self.screen, self.board.grid[y][x], rect)
        
        # Draw ghost piece
        if self.board.current_piece:
            ghost_y = self.board.current_piece.y
            while self.board.is_valid_position(self.board.current_piece, 0, ghost_y - self.board.current_piece.y - 1):
                ghost_y -= 1
            
            for x, y in self.board.current_piece.get_blocks():
                final_y = y + (ghost_y - self.board.current_piece.y)
                screen_y = TOTAL_HEIGHT - 1 - final_y
                if 0 <= screen_y < VISIBLE_HEIGHT:
                    rect = pygame.Rect(BOARD_X + x * CELL_SIZE + 1,
                                     BOARD_Y + screen_y * CELL_SIZE + 1,
                                     CELL_SIZE - 2, CELL_SIZE - 2)
                    s = pygame.Surface((CELL_SIZE - 2, CELL_SIZE - 2))
                    s.set_alpha(64)
                    s.fill(self.board.current_piece.color)
                    self.screen.blit(s, rect)
        
        # Draw current piece
        if self.board.current_piece:
            for x, y in self.board.current_piece.get_blocks():
                screen_y = TOTAL_HEIGHT - 1 - y
                if 0 <= screen_y < VISIBLE_HEIGHT:
                    rect = pygame.Rect(BOARD_X + x * CELL_SIZE + 1,
                                     BOARD_Y + screen_y * CELL_SIZE + 1,
                                     CELL_SIZE - 2, CELL_SIZE - 2)
                    pygame.draw.rect(self.screen, self.board.current_piece.color, rect)
    
    def draw_next_pieces(self):
        next_x = BOARD_X + BOARD_WIDTH * CELL_SIZE + 30
        next_y = BOARD_Y
        
        text = self.font.render("NEXT", True, WHITE)
        self.screen.blit(text, (next_x, next_y))
        
        y_offset = 30
        for piece_type in self.board.next_pieces[:5]:
            shape = PIECES[piece_type][0]
            color = PIECE_COLORS[piece_type]
            
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(next_x + x * 20, next_y + y_offset + y * 20, 18, 18)
                        pygame.draw.rect(self.screen, color, rect)
            
            y_offset += 80
    
    def draw_hold_piece(self):
        hold_x = BOARD_X - 120
        hold_y = BOARD_Y
        
        text = self.font.render("HOLD", True, WHITE)
        self.screen.blit(text, (hold_x, hold_y))
        
        if self.board.hold_piece:
            shape = PIECES[self.board.hold_piece][0]
            color = PIECE_COLORS[self.board.hold_piece]
            
            if not self.board.can_hold:
                color = GRAY
            
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(hold_x + x * 20, hold_y + 30 + y * 20, 18, 18)
                        pygame.draw.rect(self.screen, color, rect)
    
    def draw_stats(self):
        stats = self.calculate_stats()
        stats_x = 20
        stats_y = 200
        
        stats_text = [
            f"Time: {int(stats['time'])}s",
            f"Score: {stats['score']:,}",
            f"Level: {stats['level']}",
            f"Lines: {stats['lines']}",
            f"",
            f"PPS: {stats['pps']:.2f}",
            f"APM: {stats['apm']:.1f}",
            f"Attack: {stats['attack']}",
            f"",
            f"Combo: {stats['combo']}",
            f"B2B: {stats['b2b']}"
        ]
        
        for i, text in enumerate(stats_text):
            if text:
                rendered = self.small_font.render(text, True, WHITE)
                self.screen.blit(rendered, (stats_x, stats_y + i * 20))
    
    def draw_controls(self):
        controls_x = 20
        controls_y = 450
        
        controls_text = [
            "Controls:",
            "← → - Move",
            "↓ - Soft Drop",
            "Space - Hard Drop",
            "↑ - Rotate CW",
            "Z - Rotate CCW",
            "A - Rotate 180°",
            "C - Hold",
            "ESC - Pause",
            "R - Restart"
        ]
        
        for i, text in enumerate(controls_text):
            rendered = self.small_font.render(text, True, LIGHT_GRAY)
            self.screen.blit(rendered, (controls_x, controls_y + i * 18))
    
    def draw(self):
        self.screen.fill(BLACK)
        
        self.draw_board()
        self.draw_next_pieces()
        self.draw_hold_piece()
        self.draw_stats()
        self.draw_controls()
        
        if self.paused:
            pause_text = self.font.render("PAUSED", True, WHITE)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, text_rect)
        
        if self.board.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            restart_text = self.small_font.render("Press R to restart", True, WHITE)
            
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def handle_input(self, dt: float):
        # Get continuous actions from input handler
        actions = self.input_handler.update(dt)
        
        for action in actions:
            if action == InputKey.LEFT:
                self.board.move_piece(-1, 0)
            elif action == InputKey.RIGHT:
                self.board.move_piece(1, 0)
            elif action == InputKey.SOFT_DROP:
                # Apply SDF multiplier
                for _ in range(self.settings.sdf):
                    if self.board.soft_drop() == 0:
                        break
    
    def run(self):
        while self.running:
            dt = self.clock.tick(60)  # 60 FPS
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Handle single-press actions
                action = self.input_handler.handle_event(event)
                
                if action == InputKey.PAUSE:
                    self.paused = not self.paused
                elif action == InputKey.RESTART:
                    self.board = Board()
                    self.start_time = time.time()
                    self.paused = False
                
                if not self.paused and not self.board.game_over:
                    # These actions should trigger on key press
                    if action == InputKey.LEFT:
                        self.board.move_piece(-1, 0)
                    elif action == InputKey.RIGHT:
                        self.board.move_piece(1, 0)
                    elif action == InputKey.SOFT_DROP:
                        self.board.soft_drop()
                    elif action == InputKey.HARD_DROP:
                        self.board.hard_drop()
                    elif action == InputKey.ROTATE_CW:
                        self.board.rotate_piece(1)
                    elif action == InputKey.ROTATE_CCW:
                        self.board.rotate_piece(-1)
                    elif action == InputKey.ROTATE_180:
                        self.board.rotate_180()
                    elif action == InputKey.HOLD:
                        self.board.hold()
            
            # Update game state
            if not self.paused and not self.board.game_over:
                self.handle_input(dt)
                self.board.update(dt, self.settings)
            
            # Draw everything
            self.draw()
        
        # Save settings on exit
        self.settings.save()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()