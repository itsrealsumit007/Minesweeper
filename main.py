import pygame
import random
import time
import math
import json
import os
from typing import List, Tuple, Set, Dict
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod

pygame.init()

@dataclass
class Particle:
    x: float
    y: float
    dx: float
    dy: float
    lifetime: float
    color: Tuple[int, int, int]
    size: float
    start_time: float

    def update(self) -> bool:
        current_time = time.time()
        progress = (current_time - self.start_time) / self.lifetime
        if progress >= 1:
            return False
        
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.5  # Gravity
        self.size = max(1, self.size * (1 - progress))
        return True

    def draw(self, screen: pygame.Surface, offset_y: int = 100):
        pygame.draw.circle(screen, self.color, 
                         (int(self.x), int(self.y) + offset_y), 
                         int(self.size))

class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []
    
    def add_explosion(self, x: int, y: int, color: Tuple[int, int, int], 
                     count: int = 20, size: float = 3):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append(Particle(
                x=x,
                y=y,
                dx=math.cos(angle) * speed,
                dy=math.sin(angle) * speed - 2,
                lifetime=random.uniform(0.5, 1.0),
                color=color,
                size=size,
                start_time=time.time()
            ))
    
    def update_and_draw(self, screen: pygame.Surface):
        self.particles = [p for p in self.particles if p.update()]
        for particle in self.particles:
            particle.draw(screen)

class Achievement:
    def __init__(self, name: str, description: str, icon: str):
        self.name = name
        self.description = description
        self.icon = icon
        self.unlocked = False
        self.unlock_time = None

    def unlock(self):
        if not self.unlocked:
            self.unlocked = True
            self.unlock_time = time.time()

class AchievementManager:
    def __init__(self):
        self.achievements = {
            'first_win': Achievement('First Victory', 'Win your first game', '🏆'),
            'speed_demon': Achievement('Speed Demon', 'Win in under 30 seconds', '⚡'),
            'combo_master': Achievement('Combo Master', 'Get a 10x combo', '🔥'),
            'perfectionist': Achievement('Perfectionist', 'Win without misplacing any flags', '✨'),
            'theme_explorer': Achievement('Theme Explorer', 'Try all themes', '🎨'),
            'hard_victory': Achievement('Expert', 'Win on hard difficulty', '👑')
        }
        self.recent_unlocks: List[Achievement] = []
    
    def check_achievements(self, game: 'Minesweeper'):
        if game.win:
            self.achievements['first_win'].unlock()
            if game.elapsed_time < 30:
                self.achievements['speed_demon'].unlock()
            if game.difficulty == Difficulty.HARD:
                self.achievements['hard_victory'].unlock()
            if not any(game.misplaced_flags):
                self.achievements['perfectionist'].unlock()
        
        if game.max_combo >= 10:
            self.achievements['combo_master'].unlock()
        
        if game.themes_tried == len(game.themes):
            self.achievements['theme_explorer'].unlock()

class PowerUp(ABC):
    def __init__(self, duration: float = None):
        self.active = False
        self.start_time = None
        self.duration = duration
    
    @abstractmethod
    def activate(self, game: 'Minesweeper', x: int, y: int): pass
    
    @abstractmethod
    def update(self, game: 'Minesweeper'): pass
    
    def is_expired(self) -> bool:
        if not self.active or self.duration is None:
            return False
        return time.time() - self.start_time > self.duration

class RevealAreaPowerUp(PowerUp):
    def activate(self, game: 'Minesweeper', x: int, y: int):
        self.active = True
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < game.GRID_SIZE and 
                    0 <= new_y < game.GRID_SIZE and
                    not game.revealed[new_y][new_x] and
                    game.grid[new_y][new_x] != -1):
                    game.reveal_cell(new_x, new_y)
                    game.particles.add_explosion(
                        new_x * game.CELL_SIZE + game.CELL_SIZE // 2,
                        new_y * game.CELL_SIZE + game.CELL_SIZE // 2,
                        game.theme['BLUE'], 10, 2
                    )
    
    def update(self, game: 'Minesweeper'): pass

class TimeFreezeePowerUp(PowerUp):
    def __init__(self):
        super().__init__(duration=5.0)
        self.frozen_time = 0
    
    def activate(self, game: 'Minesweeper', x: int, y: int):
        self.active = True
        self.start_time = time.time()
        self.frozen_time = game.elapsed_time
    
    def update(self, game: 'Minesweeper'):
        if self.active and not self.is_expired():
            game.elapsed_time = self.frozen_time

class SafetyNetPowerUp(PowerUp):
    def __init__(self):
        super().__init__(duration=10.0)
    
    def activate(self, game: 'Minesweeper', x: int, y: int):
        self.active = True
        self.start_time = time.time()
    
    def update(self, game: 'Minesweeper'):
        if self.active and self.is_expired():
            self.active = False

class Difficulty(Enum):
    EASY = (8, 10)      # 8x8, 10 mines
    MEDIUM = (15, 35)   # 15x15, 35 mines
    HARD = (20, 80)     # 20x20, 80 mines

class Theme:
    CLASSIC = {
        'WHITE': (255, 255, 255),
        'GRAY': (192, 192, 192),
        'DARK_GRAY': (128, 128, 128),
        'BLACK': (0, 0, 0),
        'RED': (255, 0, 0),
        'BLUE': (0, 0, 255),
        'GREEN': (0, 128, 0),
        'NUMBERS': [(0, 0, 255), (0, 128, 0), (255, 0, 0), (0, 0, 128),
                   (128, 0, 0), (0, 128, 128), (0, 0, 0), (128, 128, 128)]
    }
    
    DARK = {
        'WHITE': (200, 200, 200),
        'GRAY': (40, 40, 40),
        'DARK_GRAY': (30, 30, 30),
        'BLACK': (0, 0, 0),
        'RED': (255, 69, 58),
        'BLUE': (10, 132, 255),
        'GREEN': (48, 209, 88),
        'NUMBERS': [(10, 132, 255), (48, 209, 88), (255, 69, 58), (191, 90, 242),
                   (255, 159, 10), (94, 92, 230), (255, 214, 10), (172, 172, 172)]
    }
    
    NATURE = {
        'WHITE': (236, 240, 241),
        'GRAY': (60, 179, 113),
        'DARK_GRAY': (46, 139, 87),
        'BLACK': (0, 100, 0),
        'RED': (220, 20, 60),
        'BLUE': (30, 144, 255),
        'GREEN': (34, 139, 34),
        'NUMBERS': [(30, 144, 255), (34, 139, 34), (220, 20, 60), (147, 112, 219),
                   (218, 165, 32), (72, 61, 139), (210, 105, 30), (119, 136, 153)]
    }

class Animation:
    def __init__(self):
        self.active_cells = []  # [(x, y, start_time, duration, type), ...]
        self.reveal_radius = 0
        self.last_pulse = 0
        self.flag_wave = 0
        
    def add_reveal(self, x: int, y: int, anim_type: str = 'reveal'):
        self.active_cells.append((x, y, time.time(), 0.3, anim_type))
        
    def update(self):
        current_time = time.time()
        self.active_cells = [(x, y, start, duration, atype) for x, y, start, duration, atype in self.active_cells
                            if current_time - start < duration]
        
        # Update pulse effect
        self.reveal_radius = 1 + math.sin(current_time * 2) * 0.1
        # Update flag wave
        self.flag_wave = math.sin(current_time * 4) * 3
        
    def get_cell_scale(self, x: int, y: int) -> float:
        for cell_x, cell_y, start, duration, atype in self.active_cells:
            if cell_x == x and cell_y == y:
                progress = (time.time() - start) / duration
                if atype == 'reveal':
                    if progress < 0.5:
                        return 1.0 + (1.0 - progress * 2) * 0.2
                elif atype == 'chord':
                    return 1.0 + math.sin(progress * math.pi) * 0.1
        return 1.0 * self.reveal_radius

    def get_flag_offset(self) -> float:
        return self.flag_wave

class Minesweeper:
    def __init__(self):
        self.difficulty = Difficulty.MEDIUM
        self.CELL_SIZE = 40
        self.update_grid_size()
        self.theme = Theme.CLASSIC
        self.themes = [Theme.CLASSIC, Theme.DARK, Theme.NATURE]
        self.current_theme = 0
        self.animation = Animation()
        self.high_scores = {diff: float('inf') for diff in Difficulty}
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()
        self.particles = ParticleSystem()
        self.achievements = AchievementManager()
        self.power_ups = {
            'reveal': RevealAreaPowerUp(),
            'freeze': TimeFreezeePowerUp(),
            'safety': SafetyNetPowerUp()
        }
        self.active_power_ups: List[PowerUp] = []
        self.power_up_charges = {name: 3 for name in self.power_ups}
        self.themes_tried = set()
        self.misplaced_flags = []
        self.load_game()

    def update_grid_size(self):
        self.GRID_SIZE, self.MINES = self.difficulty.value
        self.WINDOW_SIZE = self.CELL_SIZE * self.GRID_SIZE
        self.screen = pygame.display.set_mode((self.WINDOW_SIZE, self.WINDOW_SIZE + 100))
        pygame.display.set_caption('Enhanced Minesweeper')

    def reset_game(self):
        self.grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.revealed = [[False for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.flagged = [[False for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.game_over = False
        self.win = False
        self.first_click = True
        self.start_time = None
        self.elapsed_time = 0
        self.mines_left = self.MINES
        self.combo = 0
        self.max_combo = 0
        self.last_reveal_time = 0
        self.animation = Animation()

    def place_mines(self, first_x: int, first_y: int):
        positions = [(x, y) for x in range(self.GRID_SIZE) for y in range(self.GRID_SIZE)
                    if abs(x - first_x) > 1 or abs(y - first_y) > 1]
        mine_positions = random.sample(positions, self.MINES)
        
        for x, y in mine_positions:
            self.grid[y][x] = -1
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < self.GRID_SIZE and 0 <= new_y < self.GRID_SIZE and 
                        self.grid[new_y][new_x] != -1):
                        self.grid[new_y][new_x] += 1

    def reveal_cell(self, x: int, y: int):
        if not (0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE) or self.revealed[y][x] or self.flagged[y][x]:
            return

        current_time = time.time()
        if current_time - self.last_reveal_time < 1.0:
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
        else:
            self.combo = 1
        self.last_reveal_time = current_time

        self.revealed[y][x] = True
        self.animation.add_reveal(x, y)

        if self.grid[y][x] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    self.reveal_cell(x + dx, y + dy)

    def chord_reveal(self, x: int, y: int):
        """Reveal adjacent cells if the correct number of flags are placed."""
        if not self.revealed[y][x] or self.grid[y][x] <= 0:
            return False
        
        # Count adjacent flags
        flag_count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.GRID_SIZE and 
                    0 <= new_y < self.GRID_SIZE and 
                    self.flagged[new_y][new_x]):
                    flag_count += 1
        
        # If flag count matches the number, reveal adjacent cells
        if flag_count == self.grid[y][x]:
            revealed_count = 0
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < self.GRID_SIZE and 
                        0 <= new_y < self.GRID_SIZE and 
                        not self.flagged[new_y][new_x] and
                        not self.revealed[new_y][new_x]):
                        if self.grid[new_y][new_x] == -1:
                            self.game_over = True
                            self.particles.add_explosion(
                                new_x * self.CELL_SIZE + self.CELL_SIZE // 2,
                                new_y * self.CELL_SIZE + self.CELL_SIZE // 2,
                                self.theme['RED'], 30, 4
                            )
                            return True
                        self.reveal_cell(new_x, new_y)
                        revealed_count += 1
                        self.animation.add_reveal(new_x, new_y, 'chord')
            
            if revealed_count > 0:
                self.particles.add_explosion(
                    x * self.CELL_SIZE + self.CELL_SIZE // 2,
                    y * self.CELL_SIZE + self.CELL_SIZE // 2,
                    self.theme['GREEN'], 15, 2
                )
            return True
        return False

    def handle_click(self, pos: Tuple[int, int], right_click: bool = False):
        if self.game_over or self.win:
            return

        x, y = pos[0] // self.CELL_SIZE, (pos[1] - 100) // self.CELL_SIZE
        if not (0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE):
            # Check if clicking difficulty buttons
            if 10 <= pos[1] <= 40:
                if 10 <= pos[0] <= 90:
                    self.difficulty = Difficulty.EASY
                    self.update_grid_size()
                    self.reset_game()
                elif 100 <= pos[0] <= 200:
                    self.difficulty = Difficulty.MEDIUM
                    self.update_grid_size()
                    self.reset_game()
                elif 210 <= pos[0] <= 290:
                    self.difficulty = Difficulty.HARD
                    self.update_grid_size()
                    self.reset_game()
            # Check if clicking theme button
            elif 50 <= pos[1] <= 80 and 10 <= pos[0] <= 100:
                self.current_theme = (self.current_theme + 1) % len(self.themes)
                self.theme = self.themes[self.current_theme]
                self.themes_tried.add(self.current_theme)
            return

        # Handle power-up activation
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1] and self.power_up_charges['reveal'] > 0:
            self.power_ups['reveal'].activate(self, x, y)
            self.power_up_charges['reveal'] -= 1
        elif keys[pygame.K_2] and self.power_up_charges['freeze'] > 0:
            self.power_ups['freeze'].activate(self, x, y)
            self.power_up_charges['freeze'] -= 1
        elif keys[pygame.K_3] and self.power_up_charges['safety'] > 0:
            self.power_ups['safety'].activate(self, x, y)
            self.power_up_charges['safety'] -= 1

        if right_click:
            if not self.revealed[y][x]:
                was_flagged = self.flagged[y][x]
                self.flagged[y][x] = not was_flagged
                self.mines_left += 1 if not was_flagged else -1
                
                # Track misplaced flags
                if self.grid[y][x] != -1 and not was_flagged:
                    self.misplaced_flags.append((x, y))
                elif self.grid[y][x] != -1 and was_flagged:
                    self.misplaced_flags.remove((x, y))
                
                # Add flag animation
                if not was_flagged:
                    self.animation.add_reveal(x, y, 'flag')
            return

        if self.flagged[y][x]:
            return

        # Try to chord reveal if clicking on a revealed number
        if self.revealed[y][x] and self.grid[y][x] > 0:
            if self.chord_reveal(x, y):
                self.check_win()
                return

        if self.first_click:
            self.place_mines(x, y)
            self.first_click = False
            self.start_time = time.time()

        if self.grid[y][x] == -1:
            if any(p.active for p in self.power_ups.values()):
                return  # Power-up protection
            self.game_over = True
            self.particles.add_explosion(
                x * self.CELL_SIZE + self.CELL_SIZE // 2,
                y * self.CELL_SIZE + self.CELL_SIZE // 2,
                self.theme['RED'], 30, 4
            )
            return

        self.reveal_cell(x, y)
        self.check_win()
        if self.grid[y][x] == 0:
            self.particles.add_explosion(
                x * self.CELL_SIZE + self.CELL_SIZE // 2,
                y * self.CELL_SIZE + self.CELL_SIZE // 2,
                self.theme['BLUE'], 15, 2
            )

    def check_win(self):
        unrevealed = sum(1 for y in range(self.GRID_SIZE) for x in range(self.GRID_SIZE)
                        if not self.revealed[y][x])
        if unrevealed == self.MINES:
            self.win = True
            if self.elapsed_time > 0:
                self.high_scores[self.difficulty] = min(self.high_scores[self.difficulty], self.elapsed_time)

    def draw_flag(self, x: int, y: int, offset_y: float = 0):
        """Draw a custom flag using Pygame shapes."""
        # Calculate base position
        base_x = x * self.CELL_SIZE + self.CELL_SIZE // 2
        base_y = y * self.CELL_SIZE + self.CELL_SIZE // 2 + 100 + offset_y
        
        # Draw flag pole
        pygame.draw.line(self.screen, self.theme['BLACK'],
                        (base_x - 2, base_y - 15),
                        (base_x - 2, base_y + 8),
                        3)
        
        # Draw flag triangle
        flag_points = [
            (base_x - 2, base_y - 15),  # Pole top
            (base_x + 12, base_y - 10),  # Triangle tip
            (base_x - 2, base_y - 5)     # Pole middle
        ]
        pygame.draw.polygon(self.screen, self.theme['RED'], flag_points)

    def draw_cell(self, x: int, y: int, rect: Tuple[int, int, int, int]):
        scale = self.animation.get_cell_scale(x, y)
        scaled_size = int(self.CELL_SIZE * scale)
        offset = (self.CELL_SIZE - scaled_size) // 2
        scaled_rect = (rect[0] + offset, rect[1] + offset, scaled_size, scaled_size)
        
        if not self.revealed[y][x]:
            pygame.draw.rect(self.screen, self.theme['DARK_GRAY'], scaled_rect)
            pygame.draw.rect(self.screen, self.theme['WHITE'], scaled_rect, 1)
            if self.flagged[y][x]:
                flag_offset = self.animation.get_flag_offset()
                self.draw_flag(x, y, flag_offset)
        else:
            pygame.draw.rect(self.screen, self.theme['WHITE'], scaled_rect)
            pygame.draw.rect(self.screen, self.theme['GRAY'], scaled_rect, 1)
            
            if self.grid[y][x] > 0:
                number_text = self.font.render(str(self.grid[y][x]), True, 
                                             self.theme['NUMBERS'][self.grid[y][x] - 1])
                number_rect = number_text.get_rect()
                number_rect.center = (x * self.CELL_SIZE + self.CELL_SIZE // 2,
                                    y * self.CELL_SIZE + self.CELL_SIZE // 2 + 100)
                self.screen.blit(number_text, number_rect)
            elif self.grid[y][x] == -1 and self.game_over:
                # Draw a custom mine
                center_x = x * self.CELL_SIZE + self.CELL_SIZE // 2
                center_y = y * self.CELL_SIZE + self.CELL_SIZE // 2 + 100
                radius = self.CELL_SIZE // 4
                
                # Draw main circle
                pygame.draw.circle(self.screen, self.theme['BLACK'], (center_x, center_y), radius)
                
                # Draw spikes
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    start_x = center_x + math.cos(rad) * radius
                    start_y = center_y + math.sin(rad) * radius
                    end_x = center_x + math.cos(rad) * (radius + 4)
                    end_y = center_y + math.sin(rad) * (radius + 4)
                    pygame.draw.line(self.screen, self.theme['BLACK'], 
                                   (start_x, start_y), (end_x, end_y), 2)
                
                # Draw shine
                shine_pos = (center_x - radius//3, center_y - radius//3)
                pygame.draw.circle(self.screen, self.theme['WHITE'], shine_pos, 2)

    def draw(self):
        self.screen.fill(self.theme['GRAY'])
        
        # Draw top bar
        pygame.draw.rect(self.screen, self.theme['DARK_GRAY'], (0, 0, self.WINDOW_SIZE, 100))
        
        # Calculate dynamic spacing based on window size
        button_width = min(80, self.WINDOW_SIZE // 5)
        button_spacing = min(100, self.WINDOW_SIZE // 4)
        
        # Draw difficulty buttons with adjusted spacing
        for i, diff in enumerate([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]):
            color = self.theme['WHITE'] if diff == self.difficulty else self.theme['GRAY']
            button_x = 10 + i * button_spacing
            pygame.draw.rect(self.screen, color, (button_x, 10, button_width, 30))
            text = self.small_font.render(diff.name, True, self.theme['BLACK'])
            text_rect = text.get_rect(center=(button_x + button_width//2, 25))
            self.screen.blit(text, text_rect)

        # Draw theme button
        pygame.draw.rect(self.screen, self.theme['WHITE'], (10, 50, button_width, 30))
        text = self.small_font.render('Theme', True, self.theme['BLACK'])
        text_rect = text.get_rect(center=(10 + button_width//2, 65))
        self.screen.blit(text, text_rect)
        
        # Right-aligned stats (timer and mines)
        right_margin = self.WINDOW_SIZE - 10
        
        # Draw timer
        if self.start_time:
            self.elapsed_time = int(time.time() - self.start_time)
        timer_text = self.font.render(f'Time: {self.elapsed_time}', True, self.theme['WHITE'])
        timer_rect = timer_text.get_rect(right=right_margin, top=15)
        self.screen.blit(timer_text, timer_rect)
        
        # Draw mines counter
        mines_text = self.font.render(f'Mines: {self.mines_left}', True, self.theme['WHITE'])
        mines_rect = mines_text.get_rect(right=right_margin, top=55)
        self.screen.blit(mines_text, mines_rect)

        # Calculate center area for power-ups and combo
        center_start_x = button_width + button_spacing + 20
        center_width = mines_rect.left - center_start_x - 20  # Space between center and right stats
        
        # Draw power-up indicators with dynamic spacing
        power_up_icons = {'reveal': '🔍', 'freeze': '❄️', 'safety': '🛡️'}
        power_up_spacing = min(100, center_width // len(power_up_icons))
        for i, (name, charges) in enumerate(self.power_up_charges.items()):
            # Draw icon
            icon_text = self.font.render(power_up_icons[name], True, self.theme['WHITE'])
            x_pos = center_start_x + i * power_up_spacing
            icon_rect = icon_text.get_rect(centerx=x_pos + 20, centery=25)
            self.screen.blit(icon_text, icon_rect)
            
            # Draw small charge dots below icon
            dot_y = 40
            dot_radius = 3
            for j in range(charges):
                dot_x = x_pos + 20 + (j - 1) * (dot_radius * 3)
                pygame.draw.circle(self.screen, self.theme['WHITE'], 
                                (int(dot_x), dot_y), dot_radius)

        # Draw combo below power-ups
        if self.combo > 1:
            combo_text = self.font.render(f'Combo: {self.combo}!', True, self.theme['RED'])
            combo_rect = combo_text.get_rect(centerx=center_start_x + center_width//2, top=55)
            self.screen.blit(combo_text, combo_rect)
        
        # Draw particles
        self.particles.update_and_draw(self.screen)
        
        # Draw achievement notifications with adjusted positioning
        current_time = time.time()
        y_offset = 150
        for achievement in self.achievements.achievements.values():
            if (achievement.unlocked and achievement.unlock_time and 
                current_time - achievement.unlock_time < 3):
                text = self.font.render(
                    f'{achievement.icon} {achievement.name} unlocked!',
                    True, self.theme['GREEN']
                )
                text_rect = text.get_rect(center=(self.WINDOW_SIZE // 2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 40

        # Draw grid
        self.animation.update()
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                rect = (x * self.CELL_SIZE, y * self.CELL_SIZE + 100, 
                       self.CELL_SIZE, self.CELL_SIZE)
                self.draw_cell(x, y, rect)

        if self.game_over:
            self.draw_game_over()
        elif self.win:
            self.draw_win()

        pygame.display.flip()

    def draw_game_over(self):
        surface = pygame.Surface((self.WINDOW_SIZE, self.WINDOW_SIZE + 100))
        surface.set_alpha(128)
        surface.fill(self.theme['BLACK'])
        self.screen.blit(surface, (0, 0))
        
        text = self.font.render('Game Over! Press R to restart', True, self.theme['WHITE'])
        text_rect = text.get_rect(center=(self.WINDOW_SIZE // 2, self.WINDOW_SIZE // 2))
        self.screen.blit(text, text_rect)
        
        score_text = self.font.render(f'Max Combo: {self.max_combo}', True, self.theme['WHITE'])
        self.screen.blit(score_text, (self.WINDOW_SIZE // 2 - 100, self.WINDOW_SIZE // 2 + 50))

    def draw_win(self):
        surface = pygame.Surface((self.WINDOW_SIZE, self.WINDOW_SIZE + 100))
        surface.set_alpha(128)
        surface.fill(self.theme['GREEN'])
        self.screen.blit(surface, (0, 0))
        
        text = self.font.render(f'You Win! Time: {self.elapsed_time}s', True, self.theme['WHITE'])
        text_rect = text.get_rect(center=(self.WINDOW_SIZE // 2, self.WINDOW_SIZE // 2))
        self.screen.blit(text, text_rect)
        
        if self.elapsed_time == self.high_scores[self.difficulty]:
            high_score_text = self.font.render('New Best Time!', True, self.theme['WHITE'])
            self.screen.blit(high_score_text, (self.WINDOW_SIZE // 2 - 100, self.WINDOW_SIZE // 2 + 50))

    def save_game(self):
        save_data = {
            'high_scores': {diff.name: score for diff, score in self.high_scores.items()},
            'achievements': {name: ach.unlocked for name, ach in self.achievements.achievements.items()},
            'power_up_charges': self.power_up_charges,
            'themes_tried': list(self.themes_tried)
        }
        with open('minesweeper_save.json', 'w') as f:
            json.dump(save_data, f)

    def load_game(self):
        try:
            with open('minesweeper_save.json', 'r') as f:
                save_data = json.load(f)
                for diff_name, score in save_data['high_scores'].items():
                    self.high_scores[Difficulty[diff_name]] = score
                for name, unlocked in save_data['achievements'].items():
                    if unlocked:
                        self.achievements.achievements[name].unlock()
                self.power_up_charges = save_data['power_up_charges']
                self.themes_tried = set(save_data['themes_tried'])
        except FileNotFoundError:
            pass

    def run(self):
        running = True
        last_save = time.time()
        
        while running:
            current_time = time.time()
            if current_time - last_save > 30:  # Auto-save every 30 seconds
                self.save_game()
                last_save = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_game()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in (1, 3):
                        self.handle_click(event.pos, event.button == 3)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_t:
                        self.current_theme = (self.current_theme + 1) % len(self.themes)
                        self.theme = self.themes[self.current_theme]
                        self.themes_tried.add(self.current_theme)

            self.achievements.check_achievements(self)
            self.draw()

        pygame.quit()

if __name__ == '__main__':
    game = Minesweeper()
    game.run()
