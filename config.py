import pygame

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
BROWN = (139, 69, 19)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 100)
DARK_GRAY = (60, 60, 60)
WIN_GREEN = (0, 150, 0)
LAVA_COLOR = (255, 69, 0)
PHANTOM_COLOR = (150, 150, 200)
ARMORED_COLOR = (100, 100, 100)

FPS = 60
TOWER_SIZE = 40
ENEMY_SIZE = 30

TOWER_SNIPER = 1
TOWER_FLAMETHROWER = 2
TOWER_MORTAR = 3
TOWER_POISON = 4
TOWER_ARMY_BASE = 5
TOWER_FROST = 6
TOWER_FARM = 7

PROJECTILE_HOMING = 1
PROJECTILE_SPLASH = 2
PROJECTILE_FLAME = 3
PROJECTILE_POISON = 4
PROJECTILE_ARMY_BASE = 5
PROJECTILE_FROST = 6
PROJECTILE_FARM = 7

ENEMY_NORMAL = 1
ENEMY_FAST = 2
ENEMY_TANK = 3
ENEMY_LAVA = 4
ENEMY_PHANTOM = 5
ENEMY_ARMORED = 6

TOWERS = {
    TOWER_SNIPER: [
        {'name': 'Снайпер', 'color': BLUE, 'damage': 10, 'range': 300, 'fire_rate': 60, 'projectile_type': PROJECTILE_HOMING, 'upgrade_cost': 200, 'cost': 150},
        {'name': 'Снайпер', 'color': BLUE, 'damage': 15, 'range': 350, 'fire_rate': 50, 'projectile_type': PROJECTILE_HOMING, 'upgrade_cost': 400, 'cost': 150},
        {'name': 'Снайпер', 'color': BLUE, 'damage': 25, 'range': 400, 'fire_rate': 40, 'projectile_type': PROJECTILE_HOMING, 'upgrade_cost': 700, 'cost': 150},
        {'name': 'Снайпер', 'color': BLUE, 'damage': 40, 'range': 450, 'fire_rate': 30, 'projectile_type': PROJECTILE_HOMING, 'upgrade_cost': 0, 'cost': 150},
    ],
    TOWER_FLAMETHROWER: [
        {'name': 'Огнемет', 'color': RED, 'damage': 0.2, 'range': 120, 'fire_rate': 5,
         'projectile_type': PROJECTILE_FLAME, 'splash_radius': 40, 'speed_boost': 1, 'upgrade_cost': 150, 'cost': 100},
        {'name': 'Огнемет', 'color': RED, 'damage': 0.3, 'range': 130, 'fire_rate': 5,
         'projectile_type': PROJECTILE_FLAME, 'splash_radius': 45, 'speed_boost': 0.7, 'upgrade_cost': 300, 'cost': 100},
        {'name': 'Огнемет', 'color': RED, 'damage': 0.5, 'range': 140, 'fire_rate': 5,
         'projectile_type': PROJECTILE_FLAME, 'splash_radius': 50, 'speed_boost': 0.5, 'upgrade_cost': 600, 'cost': 100},
        {'name': 'Огнемет', 'color': RED, 'damage': 1, 'range': 150, 'fire_rate': 5,
         'projectile_type': PROJECTILE_FLAME, 'splash_radius': 60, 'speed_boost': 0.5, 'upgrade_cost': 0, 'cost': 100},
    ],
    TOWER_MORTAR: [
        {'name': 'Миномет', 'color': ORANGE, 'damage': 5, 'range': 200, 'fire_rate': 90, 'projectile_type': PROJECTILE_SPLASH, 'splash_radius': 50, 'upgrade_cost': 250, 'cost': 120},
        {'name': 'Миномет', 'color': ORANGE, 'damage': 10, 'range': 220, 'fire_rate': 75, 'projectile_type': PROJECTILE_SPLASH, 'splash_radius': 60, 'upgrade_cost': 500, 'cost': 120},
        {'name': 'Миномет', 'color': ORANGE, 'damage': 15, 'range': 240, 'fire_rate': 60, 'projectile_type': PROJECTILE_SPLASH, 'splash_radius': 70, 'upgrade_cost': 1000, 'cost': 120},
        {'name': 'Миномет', 'color': ORANGE, 'damage': 25, 'range': 260, 'fire_rate': 50, 'projectile_type': PROJECTILE_SPLASH, 'splash_radius': 80, 'upgrade_cost': 0, 'cost': 120},
    ],
    TOWER_POISON: [
        {'name': 'Яд', 'color': PURPLE, 'damage': 2, 'range': 150, 'fire_rate': 60,
         'projectile_type': PROJECTILE_POISON, 'poison_duration': 3 * FPS, 'poison_damage_per_sec': 0.5, 'upgrade_cost': 200, 'cost': 110},
        {'name': 'Яд', 'color': PURPLE, 'damage': 3, 'range': 170, 'fire_rate': 50,
         'projectile_type': PROJECTILE_POISON, 'poison_duration': 3 * FPS, 'poison_damage_per_sec': 0.7, 'upgrade_cost': 400, 'cost': 110},
        {'name': 'Яд', 'color': PURPLE, 'damage': 4, 'range': 190, 'fire_rate': 40,
         'projectile_type': PROJECTILE_POISON, 'poison_duration': 4 * FPS, 'poison_damage_per_sec': 1.0, 'upgrade_cost': 800, 'cost': 110},
        {'name': 'Яд', 'color': PURPLE, 'damage': 5, 'range': 210, 'fire_rate': 30,
         'projectile_type': PROJECTILE_POISON, 'poison_duration': 5 * FPS, 'poison_damage_per_sec': 1.2, 'upgrade_cost': 0, 'cost': 110},
    ],
    TOWER_ARMY_BASE: [

        {'name': 'База', 'color': BROWN, 'damage': 20, 'range': 0, 'fire_rate': 4 * FPS,
         'projectile_type': PROJECTILE_ARMY_BASE, 'unit_hp': 100, 'unit_speed': 1.0, 'upgrade_cost': 300, 'cost': 200},
        {'name': 'База', 'color': BROWN, 'damage': 30, 'range': 0, 'fire_rate': 3 * FPS,
         'projectile_type': PROJECTILE_ARMY_BASE, 'unit_hp': 150, 'unit_speed': 1.0, 'upgrade_cost': 600, 'cost': 200},
        {'name': 'База', 'color': BROWN, 'damage': 40, 'range': 0, 'fire_rate': 2 * FPS,
         'projectile_type': PROJECTILE_ARMY_BASE, 'unit_hp': 200, 'unit_speed': 1.0, 'upgrade_cost': 1200, 'cost': 200},
        {'name': 'База', 'color': BROWN, 'damage': 50, 'range': 0, 'fire_rate': 1.5 * FPS,
         'projectile_type': PROJECTILE_ARMY_BASE, 'unit_hp': 300, 'unit_speed': 1.0, 'upgrade_cost': 0, 'cost': 200},
    ],
    TOWER_FROST: [
        {'name': 'Заморозка', 'color': LIGHT_BLUE, 'damage': 1, 'range': 200, 'fire_rate': 10,
         'projectile_type': PROJECTILE_FROST, 'slow_factor': 0.5, 'slow_duration': 1 * FPS, 'upgrade_cost': 200, 'cost': 90},
        {'name': 'Заморозка', 'color': LIGHT_BLUE, 'damage': 2, 'range': 220, 'fire_rate': 8,
         'projectile_type': PROJECTILE_FROST, 'slow_factor': 0.6, 'slow_duration': 1.5 * FPS, 'upgrade_cost': 400, 'cost': 90},
        {'name': 'Заморозка', 'color': LIGHT_BLUE, 'damage': 5, 'range': 250, 'fire_rate': 6,
         'projectile_type': PROJECTILE_FROST, 'slow_factor': 0.7, 'slow_duration': 2 * FPS, 'upgrade_cost': 400, 'cost': 90},
        {'name': 'Заморозка', 'color': LIGHT_BLUE, 'damage': 5, 'range': 250, 'fire_rate': 6,
         'projectile_type': PROJECTILE_FROST, 'slow_factor': 0.8, 'slow_duration': 2.5 * FPS, 'upgrade_cost': 0, 'cost': 90},
    ],
}

ENEMIES = {
    ENEMY_NORMAL: {'health': 15, 'speed': 1.0, 'color': GREEN, 'reward': 10},
    ENEMY_FAST: {'health': 10, 'speed': 2.0, 'color': YELLOW, 'reward': 15},
    ENEMY_TANK: {'health': 50, 'speed': 0.5, 'color': RED, 'reward': 30},
    ENEMY_LAVA: {'health': 150, 'speed': 0.8, 'color': LAVA_COLOR, 'reward': 50, 'spawns_on_death': True, 'spawned_hp': 60},
    ENEMY_PHANTOM: {'health': 60, 'speed': 3.0, 'color': PHANTOM_COLOR, 'reward': 20, 'is_phantom': True},
    ENEMY_ARMORED: {'health': 100, 'speed': 1.0, 'color': ARMORED_COLOR, 'reward': 40, 'is_armored': True},
}

DIFFICULTY_EASY = 1
DIFFICULTY_MEDIUM = 2
DIFFICULTY_HARD = 3

ENEMY_PATH_STANDARD = [
    (0, 300), (220, 300), (220, 180), (500, 180),
    (500, 420), (780, 420), (780, 540), (SCREEN_WIDTH, 540)
]

ENEMY_PATH_SHORT_FINAL = [
    (0, SCREEN_HEIGHT // 2 - 10), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10), (SCREEN_WIDTH, SCREEN_HEIGHT // 2 - 10)
]

WAVES_BASE = []
WAVES_BASE.append([(ENEMY_NORMAL, 7), (ENEMY_FAST, 2)])  # 1
WAVES_BASE.append([(ENEMY_NORMAL, 10),(ENEMY_TANK, 4)])  # 2
WAVES_BASE.append([(ENEMY_TANK, 5), (ENEMY_FAST, 7)])  # 3
WAVES_BASE.append([(ENEMY_TANK, 4), (ENEMY_PHANTOM, 3)])  # 4
WAVES_BASE.append([(ENEMY_FAST, 5), (ENEMY_TANK, 5)])  # 5
WAVES_BASE.append([(ENEMY_LAVA, 2), (ENEMY_PHANTOM, 5), (ENEMY_ARMORED, 3)])  # 6

def generate_waves(base_waves, num_waves, scale_factor):
    all_waves = []
    base_len = len(base_waves)
    for i in range(num_waves):
        base_wave = base_waves[i % base_len]
        current_scale = scale_factor * (1 + (i // base_len) * 0.2 + (i / num_waves) * 0.5)
        new_wave = []
        for enemy_type, count in base_wave:
            new_count = max(1, int(count * current_scale))
            new_wave.append((enemy_type, new_count))
        all_waves.append(new_wave)
    return all_waves

WAVES_EASY = generate_waves(WAVES_BASE, 20, 1)
WAVES_MEDIUM = generate_waves(WAVES_BASE, 30, 1.5)
WAVES_HARD = generate_waves(WAVES_BASE, 40, 2)

DIFFICULTY_SETTINGS = {
    DIFFICULTY_EASY: {'name': 'Легкий', 'path': ENEMY_PATH_STANDARD, 'waves': WAVES_EASY, 'lives': 30, 'money': 700},
    DIFFICULTY_MEDIUM: {'name': 'Средний', 'path': ENEMY_PATH_STANDARD, 'waves': WAVES_MEDIUM, 'lives': 20, 'money': 500},
    DIFFICULTY_HARD: {'name': 'Тяжелый', 'path': ENEMY_PATH_SHORT_FINAL, 'waves': WAVES_HARD, 'lives': 10, 'money': 300},
}



