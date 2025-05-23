import pygame
import json
import sys
from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum

# Import from main game
from tetris_main import Settings, InputKey, SCREEN_WIDTH, SCREEN_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (100, 100, 255)

class SettingsMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Settings Configuration")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        self.settings = Settings()
        self.settings.load()
        
        self.running = True
        self.selected_option = 0
        self.editing_keybind = None
        self.message = ""
        self.message_timer = 0
        
        # Menu options
        self.options = [
            ("DAS (ms)", "das", 0, 500, 10),
            ("ARR (ms)", "arr", 0, 100, 5),
            ("SDF", "sdf", 1, 40, 1),
            ("Gravity", "gravity", 0.1, 20.0, 0.1),
            ("Lock Delay (ms)", "lock_delay", 100, 2000, 50),
            ("", None, 0, 0, 0),  # Separator
            ("Move Left", InputKey.LEFT),
            ("Move Right", InputKey.RIGHT),
            ("Soft Drop", InputKey.SOFT_DROP),
            ("Hard Drop", InputKey.HARD_DROP),
            ("Rotate CW", InputKey.ROTATE_CW),
            ("Rotate CCW", InputKey.ROTATE_CCW),
            ("Rotate 180°", InputKey.ROTATE_180),
            ("Hold", InputKey.HOLD),
            ("Pause", InputKey.PAUSE),
            ("Restart", InputKey.RESTART),
            ("", None, 0, 0, 0),  # Separator
            ("Save Settings", "save"),
            ("Reset to Default", "reset"),
            ("Return to Game", "exit")
        ]
    
    def get_key_name(self, key_code: int) -> str:
        """Convert pygame key code to readable name"""
        if key_code == pygame.K_SPACE:
            return "SPACE"
        elif key_code == pygame.K_LEFT:
            return "LEFT"
        elif key_code == pygame.K_RIGHT:
            return "RIGHT"
        elif key_code == pygame.K_UP:
            return "UP"
        elif key_code == pygame.K_DOWN:
            return "DOWN"
        elif key_code == pygame.K_ESCAPE:
            return "ESC"
        else:
            return pygame.key.name(key_code).upper()
    
    def handle_navigation(self, direction: int):
        """Navigate through menu options"""
        self.selected_option += direction
        
        # Skip separators
        while (0 <= self.selected_option < len(self.options) and 
               self.options[self.selected_option][1] is None):
            self.selected_option += direction
        
        # Wrap around
        if self.selected_option < 0:
            self.selected_option = len(self.options) - 1
            while self.options[self.selected_option][1] is None:
                self.selected_option -= 1
        elif self.selected_option >= len(self.options):
            self.selected_option = 0
            while self.options[self.selected_option][1] is None:
                self.selected_option += 1
    
    def handle_value_change(self, direction: int):
        """Change numeric values"""
        option = self.options[self.selected_option]
        
        if len(option) == 5:  # Numeric option
            name, attr, min_val, max_val, step = option
            current_value = getattr(self.settings, attr)
            
            if isinstance(current_value, float):
                new_value = current_value + (step * direction)
                new_value = round(new_value, 1)
            else:
                new_value = current_value + (step * direction)
            
            new_value = max(min_val, min(max_val, new_value))
            setattr(self.settings, attr, new_value)
    
    def show_message(self, message: str, duration: int = 2000):
        """Display a temporary message"""
        self.message = message
        self.message_timer = duration
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Title
        title = self.font.render("SETTINGS CONFIGURATION", True, WHITE)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH // 2, y=30)
        self.screen.blit(title, title_rect)
        
        # Draw options
        y_offset = 100
        
        for i, option in enumerate(self.options):
            if option[1] is None:  # Separator
                continue
            
            # Highlight selected option
            if i == self.selected_option:
                if self.editing_keybind:
                    color = RED
                else:
                    color = GREEN
                pygame.draw.rect(self.screen, color, 
                               (50, y_offset - 5, SCREEN_WIDTH - 100, 30), 2)
            
            # Draw option name
            text = self.small_font.render(option[0], True, WHITE)
            self.screen.blit(text, (100, y_offset))
            
            # Draw value
            if len(option) == 5:  # Numeric option
                value = getattr(self.settings, option[1])
                if isinstance(value, float):
                    value_text = f"{value:.1f}"
                else:
                    value_text = str(value)
                
                # Draw arrows
                if i == self.selected_option:
                    left_arrow = self.small_font.render("◄", True, WHITE)
                    right_arrow = self.small_font.render("►", True, WHITE)
                    self.screen.blit(left_arrow, (400, y_offset))
                    self.screen.blit(right_arrow, (500, y_offset))
                
                value_rendered = self.small_font.render(value_text, True, WHITE)
                value_rect = value_rendered.get_rect(centerx=450, y=y_offset)
                self.screen.blit(value_rendered, value_rect)
            
            elif isinstance(option[1], InputKey):  # Keybind option
                key_code = self.settings.keybinds[option[1]]
                key_name = self.get_key_name(key_code)
                
                if i == self.selected_option and self.editing_keybind:
                    key_text = "Press any key..."
                    color = RED
                else:
                    key_text = key_name
                    color = WHITE
                
                key_rendered = self.small_font.render(key_text, True, color)
                self.screen.blit(key_rendered, (450, y_offset))
            
            elif option[1] in ["save", "reset", "exit"]:  # Action buttons
                if i == self.selected_option:
                    button_color = GREEN
                else:
                    button_color = GRAY
                
                pygame.draw.rect(self.screen, button_color,
                               (300, y_offset - 5, 200, 30), 2)
            
            y_offset += 35
        
        # Draw message
        if self.message and self.message_timer > 0:
            msg_rendered = self.font.render(self.message, True, GREEN)
            msg_rect = msg_rendered.get_rect(centerx=SCREEN_WIDTH // 2, y=550)
            self.screen.blit(msg_rendered, msg_rect)
        
        # Instructions
        instructions = [
            "↑/↓ - Navigate",
            "←/→ - Change values",
            "ENTER - Edit keybind / Select action",
            "ESC - Cancel"
        ]
        
        y = 500
        for instruction in instructions:
            text = self.small_font.render(instruction, True, LIGHT_GRAY)
            self.screen.blit(text, (50, y))
            y += 25
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            
            # Update message timer
            if self.message_timer > 0:
                self.message_timer -= dt
                if self.message_timer <= 0:
                    self.message = ""
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.editing_keybind:
                        # Assign new keybind
                        if event.key != pygame.K_ESCAPE:
                            option = self.options[self.selected_option]
                            input_key = option[1]
                            
                            # Check for conflicts
                            conflict = False
                            for key, code in self.settings.keybinds.items():
                                if code == event.key and key != input_key:
                                    self.show_message(f"Key already used for {key.value}")
                                    conflict = True
                                    break
                            
                            if not conflict:
                                self.settings.keybinds[input_key] = event.key
                                self.show_message("Keybind updated!")
                        
                        self.editing_keybind = False
                    
                    else:
                        if event.key == pygame.K_UP:
                            self.handle_navigation(-1)
                        elif event.key == pygame.K_DOWN:
                            self.handle_navigation(1)
                        elif event.key == pygame.K_LEFT:
                            self.handle_value_change(-1)
                        elif event.key == pygame.K_RIGHT:
                            self.handle_value_change(1)
                        elif event.key == pygame.K_RETURN:
                            option = self.options[self.selected_option]
                            
                            if isinstance(option[1], InputKey):
                                self.editing_keybind = True
                            elif option[1] == "save":
                                self.settings.save()
                                self.show_message("Settings saved!")
                            elif option[1] == "reset":
                                self.settings = Settings()
                                self.show_message("Settings reset to default!")
                            elif option[1] == "exit":
                                self.running = False
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False
            
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    menu = SettingsMenu()
    menu.run()