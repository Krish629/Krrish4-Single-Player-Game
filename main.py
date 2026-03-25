import pygame
import random
import math
import sys
import array
import json
import os
import socket
import threading
import time
import select
from enum import Enum
from datetime import datetime
import queue
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Krrish 4 Game - Online Multiplayer")
sys.is_web = hasattr(sys, 'is_web') and sys.is_web
PORT = 5555
MAX_PLAYERS = 4
SERVER_IP = "localhost"
BUFFER_SIZE = 4096
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_BLUE = (0, 0, 139)
ORANGE = (255, 165, 0)
TRANSPARENT_BLACK = (0, 0, 0, 180)
CYAN = (0, 255, 255)
FIRE_ORANGE = (255, 100, 0)
FIRE_RED = (255, 50, 0)
LIGHT_GREEN = (144, 238, 144)
DARK_RED = (139, 0, 0)
LIGHT_YELLOW = (255, 255, 224)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
ICE_BLUE = (173, 216, 230)
ELECTRIC_PURPLE = (128, 0, 255)
DARK_GRAY = (64, 64, 64)
UFO_BLUE = (0, 100, 255)
LIGHT_BLUE = (100, 150, 255)
BEAM_BLUE = (0, 150, 255)
GRASS_GREEN = (34, 139, 34)
DARK_GRASS_GREEN = (0, 100, 0)
LIGHT_GRASS_GREEN = (50, 205, 50)
SPACE_DARK = (5, 5, 15)
SPACE_MEDIUM = (10, 10, 30)
STAR_COLORS = [WHITE, (200, 200, 255), (255, 255, 200), (200, 255, 200)]
NEBULA_COLORS = [
    (50, 0, 100, 50),
    (0, 50, 100, 50),
    (100, 0, 50, 50),
    (0, 100, 50, 50)
]
SAVE_FILE = "krrish4_save.json"
HIGH_SCORE_FILE = "krrish4_highscores.json"
DIFFICULTY_EASY = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD = 2
DIFFICULTY_NAMES = ["Easy", "Normal", "Hard"]
if not os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, 'w') as f:
        json.dump({}, f)
if not os.path.exists(HIGH_SCORE_FILE):
    with open(HIGH_SCORE_FILE, 'w') as f:
        json.dump({"easy": [], "normal": [], "hard": []}, f)
MSG_TYPE_CONNECT = "connect"
MSG_TYPE_DISCONNECT = "disconnect"
MSG_TYPE_PLAYER_UPDATE = "player_update"
MSG_TYPE_ENEMY_UPDATE = "enemy_update"
MSG_TYPE_PROJECTILE_UPDATE = "projectile_update"
MSG_TYPE_POWERUP_UPDATE = "powerup_update"
MSG_TYPE_GAME_STATE = "game_state"
MSG_TYPE_CHAT = "chat"
MSG_TYPE_PLAYER_JOINED = "player_joined"
MSG_TYPE_PLAYER_LEFT = "player_left"
MSG_TYPE_GAME_START = "game_start"
MSG_TYPE_GAME_OVER = "game_over"
MSG_TYPE_LEVEL_UP = "level_up"
START_SCREEN = 0
DIFFICULTY_SELECT = 1
TRANSITIONING = 2
PLAYING = 3
PAUSED = 4
GAME_OVER = 5
UPGRADE_MENU = 6
HIGH_SCORES = 7
LEADERBOARD = 8
NETWORK_LOBBY = 9
NETWORK_CONNECTING = 10
NETWORK_PLAYING = 11
ROLE_NONE = 0
ROLE_SERVER = 1
ROLE_CLIENT = 2
def generate_jump_sound():
    sample_rate = 22050
    duration = 0.2
    frequency = 440
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    for i in range(frames):
        t = float(i) / sample_rate
        freq = frequency * (1 + 2 * t)
        value = int(32767.0 * math.sin(2.0 * math.pi * freq * t) * (1 - t))
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
def generate_shoot_sound():
    sample_rate = 22050
    duration = 0.1
    frequency = 880
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    for i in range(frames):
        t = float(i) / sample_rate
        value = int(32767.0 * math.sin(2.0 * math.pi * frequency * t) * math.exp(-10 * t))
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
def generate_damage_sound():
    sample_rate = 22050
    duration = 0.3
    frequency = 110
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    for i in range(frames):
        t = float(i) / sample_rate
        value = int(32767.0 * math.sin(2.0 * math.pi * frequency * t) * (1 - t/2))
        noise = random.randint(-1000, 1000)
        samples[i*2] = value + noise
        samples[i*2+1] = value + noise
    
    return pygame.sndarray.make_sound(samples)
def generate_powerup_sound():
    sample_rate = 22050
    duration = 0.4
    start_freq = 523.25
    end_freq = 1046.50
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    for i in range(frames):
        t = float(i) / sample_rate
        freq = start_freq + (end_freq - start_freq) * t
        value = int(32767.0 * math.sin(2.0 * math.pi * freq * t) * math.sin(math.pi * t))
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
def generate_enemy_shoot_sound():
    sample_rate = 22050
    duration = 0.15
    frequency = 220
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    for i in range(frames):
        t = float(i) / sample_rate
        value = int(32767.0 * math.sin(2.0 * math.pi * frequency * t) * math.exp(-15 * t))
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
def generate_explosion_sound():
    sample_rate = 22050
    duration = 0.5
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    for i in range(frames):
        t = float(i) / sample_rate
        value = int(32767.0 * (1 - t) * random.uniform(-1, 1))
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
def generate_levelup_sound():
    sample_rate = 22050
    duration = 0.6
    frequencies = [523.25, 659.25, 783.99, 1046.50]
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    current_note = 0
    note_start_time = 0
    
    for i in range(frames):
        t = float(i) / sample_rate
        note_index = min(int(t * 8), len(frequencies) - 1)
        freq = frequencies[note_index]
        value = int(32767.0 * math.sin(2.0 * math.pi * freq * t) * (1 - t/2))
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
def generate_background_music():
    sample_rate = 22050
    duration = 4.0
    notes = [
        (523.25, 0.5),
        (587.33, 0.5),
        (659.25, 0.5),
        (698.46, 0.5),
        (783.99, 0.5),
        (880.00, 0.5),
        (987.77, 0.5),
        (1046.50, 0.5)
    ]
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    current_note = 0
    note_start_time = 0
    
    for i in range(frames):
        t = float(i) / sample_rate
        
        if t - note_start_time >= notes[current_note][1]:
            current_note = (current_note + 1) % len(notes)
            note_start_time = t
        
        freq = notes[current_note][0]
        
        value = int(32767.0 * 0.3 * (
            math.sin(2.0 * math.pi * freq * t) +
            0.5 * math.sin(2.0 * math.pi * (freq * 1.5) * t) +
            0.25 * math.sin(2.0 * math.pi * (freq * 2) * t)
        ))
        
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
def generate_boss_music():
    sample_rate = 22050
    duration = 4.0
    notes = [
        (220.00, 0.25),
        (220.00, 0.25),
        (246.94, 0.25),
        (261.63, 0.25),
        (293.66, 0.5),
        (329.63, 0.5),
        (349.23, 0.5),
        (392.00, 1.0)
    ]
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    current_note = 0
    note_start_time = 0
    
    for i in range(frames):
        t = float(i) / sample_rate
        
        if t - note_start_time >= notes[current_note][1]:
            current_note = (current_note + 1) % len(notes)
            note_start_time = t
        
        freq = notes[current_note][0]
        
        value = int(32767.0 * 0.4 * (
            math.sin(2.0 * math.pi * freq * t) +
            0.3 * math.sin(2.0 * math.pi * (freq * 2) * t) +
            0.2 * math.sin(2.0 * math.pi * (freq * 0.5) * t)
        ))
        
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
def generate_combo_sound():
    sample_rate = 22050
    duration = 0.2
    frequencies = [523.25, 659.25, 783.99]
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    for i in range(frames):
        t = float(i) / sample_rate
        value = 0
        for freq in frequencies:
            value += int(32767.0 * 0.3 * math.sin(2.0 * math.pi * freq * t))
        
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
def generate_dash_sound():
    sample_rate = 22050
    duration = 0.3
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    for i in range(frames):
        t = float(i) / sample_rate
        noise = random.uniform(-1, 1)
        value = int(32767.0 * noise * (1 - t/2))
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
def generate_wall_jump_sound():
    sample_rate = 22050
    duration = 0.2
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    for i in range(frames):
        t = float(i) / sample_rate
        value = int(32767.0 * math.sin(2.0 * math.pi * 110 * t) * (1 - t))
        noise = random.randint(-1000, 1000)
        samples[i*2] = value + noise
        samples[i*2+1] = value + noise
    
    return pygame.sndarray.make_sound(samples)
def generate_shield_sound():
    sample_rate = 22050
    duration = 0.5
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    for i in range(frames):
        t = float(i) / sample_rate
        value = int(32767.0 * 0.3 * (
            math.sin(2.0 * math.pi * 440 * t) +
            0.5 * math.sin(2.0 * math.pi * 880 * t) +
            0.25 * math.sin(2.0 * math.pi * 1320 * t)
        ))
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
def generate_dynamic_background_music():
    sample_rate = 22050
    duration = 8.0
    
    notes = [
        (523.25, 0.5),
        (587.33, 0.5),
        (659.25, 0.5),
        (698.46, 0.5),
        (783.99, 0.5),
        (880.00, 0.5),
        (987.77, 0.5),
        (1046.50, 0.5)
    ]
    
    bass_notes = [
        (261.63, 1.0),
        (293.66, 1.0),
        (329.63, 1.0),
        (349.23, 1.0),
        (392.00, 1.0),
        (440.00, 1.0),
        (493.88, 1.0),
        (523.25, 1.0)
    ]
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    current_note = 0
    note_start_time = 0
    current_bass = 0
    bass_start_time = 0
    
    for i in range(frames):
        t = float(i) / sample_rate
        
        if t - note_start_time >= notes[current_note][1]:
            current_note = (current_note + 1) % len(notes)
            note_start_time = t
        
        if t - bass_start_time >= bass_notes[current_bass][1]:
            current_bass = (current_bass + 1) % len(bass_notes)
            bass_start_time = t
        
        freq = notes[current_note][0]
        bass_freq = bass_notes[current_bass][0]
        
        melody = int(32767.0 * 0.2 * math.sin(2.0 * math.pi * freq * t))
        harmony = int(32767.0 * 0.1 * math.sin(2.0 * math.pi * (freq * 1.5) * t))
        bass = int(32767.0 * 0.3 * math.sin(2.0 * math.pi * bass_freq * t))
        
        value = melody + harmony + bass
        
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
def generate_combat_music():
    sample_rate = 22050
    duration = 6.0
    
    notes = [
        (440.00, 0.25),
        (440.00, 0.25),
        (493.88, 0.25),
        (523.25, 0.25),
        (587.33, 0.5),
        (659.25, 0.5),
        (698.46, 0.5),
        (783.99, 1.0)
    ]
    
    drum_beats = [
        (0.0, 0.1),
        (0.5, 0.1),
        (1.0, 0.1),
    ]
    
    frames = int(duration * sample_rate)
    samples = array.array('h', [0] * (frames * 2))
    
    current_note = 0
    note_start_time = 0
    
    for i in range(frames):
        t = float(i) / sample_rate
        
        if t - note_start_time >= notes[current_note][1]:
            current_note = (current_note + 1) % len(notes)
            note_start_time = t
        
        freq = notes[current_note][0]
        
        melody = int(32767.0 * 0.3 * math.sin(2.0 * math.pi * freq * t))
        harmony = int(32767.0 * 0.2 * math.sin(2.0 * math.pi * (freq * 1.5) * t))
        
        drum = 0
        for beat_time, beat_duration in drum_beats:
            beat_time_mod = beat_time % duration
            if t >= beat_time_mod and t < beat_time_mod + beat_duration:
                drum = int(32767.0 * 0.5 * random.uniform(-1, 1))
                break
        
        value = melody + harmony + drum
        
        samples[i*2] = value
        samples[i*2+1] = value
    
    return pygame.sndarray.make_sound(samples)
try:
    jump_sound = generate_jump_sound()
    shoot_sound = generate_shoot_sound()
    damage_sound = generate_damage_sound()
    powerup_sound = generate_powerup_sound()
    enemy_shoot_sound = generate_enemy_shoot_sound()
    explosion_sound = generate_explosion_sound()
    levelup_sound = generate_levelup_sound()
    background_music = generate_dynamic_background_music()
    boss_music = generate_boss_music()
    combo_sound = generate_combo_sound()
    dash_sound = generate_dash_sound()
    wall_jump_sound = generate_wall_jump_sound()
    shield_sound = generate_shield_sound()
    combat_music = generate_combat_music()
    
    jump_sound.set_volume(0.7)
    shoot_sound.set_volume(0.6)
    damage_sound.set_volume(0.8)
    powerup_sound.set_volume(0.9)
    enemy_shoot_sound.set_volume(0.5)
    explosion_sound.set_volume(0.7)
    levelup_sound.set_volume(0.8)
    background_music.set_volume(0.3)
    boss_music.set_volume(0.4)
    combo_sound.set_volume(0.7)
    dash_sound.set_volume(0.6)
    wall_jump_sound.set_volume(0.7)
    shield_sound.set_volume(0.5)
    combat_music.set_volume(0.4)
    
    background_music.play(-1)
except:
    jump_sound = None
    shoot_sound = None
    damage_sound = None
    powerup_sound = None
    enemy_shoot_sound = None
    explosion_sound = None
    levelup_sound = None
    background_music = None
    boss_music = None
    combo_sound = None
    dash_sound = None
    wall_jump_sound = None
    shield_sound = None
    combat_music = None
clock = pygame.time.Clock()
FPS = 60
score = 0
game_over = False
font = pygame.font.SysFont('Arial', 30)
small_font = pygame.font.SysFont('Arial', 20)
title_font = pygame.font.SysFont('Arial', 80, bold=True)
network_role = ROLE_NONE
server_socket = None
client_socket = None
clients = {}
players = {}
player_id = None
network_messages = queue.Queue()
network_thread = None
chat_messages = []
chat_input = ""
chat_active = False
game_state = START_SCREEN
transition_alpha = 0
transition_direction = 1
transition_speed = 5
transition_complete = False
previous_state = START_SCREEN
level = 1
enemies_defeated = 0
enemies_per_level = 10
level_up_threshold = 100
upgrade_points = 0
upgrades_available = 0
upgrades = {
    "damage": {"level": 1, "max": 5, "cost": 1, "name": "Damage Boost"},
    "speed": {"level": 1, "max": 5, "cost": 1, "name": "Movement Speed"},
    "health": {"level": 1, "max": 5, "cost": 1, "name": "Max Health"},
    "fire_rate": {"level": 1, "max": 5, "cost": 1, "name": "Fire Rate"},
    "double_jump": {"level": 0, "max": 1, "cost": 3, "name": "Double Jump"},
    "shield": {"level": 0, "max": 1, "cost": 3, "name": "Energy Shield"},
    "multi_shot": {"level": 0, "max": 3, "cost": 2, "name": "Multi-Shot"},
    "piercing": {"level": 0, "max": 1, "cost": 3, "name": "Piercing Shots"}
}
skill_trees = {
    "combat": {
        "name": "Combat Tree",
        "description": "Improve your combat abilities",
        "skills": {
            "precision": {"name": "Precision", "description": "Increase bullet damage", "level": 0, "max": 5, "cost": 1, "requires": None},
            "rapid_fire": {"name": "Rapid Fire", "description": "Increase fire rate", "level": 0, "max": 5, "cost": 1, "requires": None},
            "multi_shot": {"name": "Multi-Shot", "description": "Fire multiple projectiles", "level": 0, "max": 3, "cost": 2, "requires": None},
            "piercing_shot": {"name": "Piercing Shot", "description": "Bullets pierce enemies", "level": 0, "max": 1, "cost": 3, "requires": "precision"},
            "explosive_shot": {"name": "Explosive Shot", "description": "Bullets create explosions", "level": 0, "max": 1, "cost": 3, "requires": "rapid_fire"},
            "mega_blast": {"name": "Mega Blast", "description": "Super powerful blast", "level": 0, "max": 1, "cost": 5, "requires": "piercing_shot"}
        }
    },
    "mobility": {
        "name": "Mobility Tree",
        "description": "Improve your movement abilities",
        "skills": {
            "speed": {"name": "Speed", "description": "Increase movement speed", "level": 0, "max": 5, "cost": 1, "requires": None},
            "jump": {"name": "Jump", "description": "Increase jump height", "level": 0, "max": 3, "cost": 1, "requires": None},
            "double_jump": {"name": "Double Jump", "description": "Jump again in mid-air", "level": 0, "max": 1, "cost": 3, "requires": "jump"},
            "wall_jump": {"name": "Wall Jump", "description": "Jump off walls", "level": 0, "max": 1, "cost": 3, "requires": "speed"},
            "dash": {"name": "Dash", "description": "Quick evasive maneuver", "level": 0, "max": 1, "cost": 5, "requires": "double_jump"}
        }
    },
    "defense": {
        "name": "Defense Tree",
        "description": "Improve your defensive abilities",
        "skills": {
            "health": {"name": "Health", "description": "Increase maximum health", "level": 0, "max": 5, "cost": 1, "requires": None},
            "shield": {"name": "Shield", "description": "Activate energy shield", "level": 0, "max": 1, "cost": 3, "requires": None},
            "regeneration": {"name": "Regeneration", "description": "Regenerate health over time", "level": 0, "max": 3, "cost": 2, "requires": "health"},
            "resistance": {"name": "Resistance", "description": "Reduce damage taken", "level": 0, "max": 3, "cost": 2, "requires": "shield"},
            "immunity": {"name": "Immunity", "description": "Brief immunity after taking damage", "level": 0, "max": 1, "cost": 5, "requires": "resistance"}
        }
    }
}
player_colors = {
    "default": {
        "coat": BLACK,
        "lining": RED,
        "boots": ORANGE,
        "mask": BLACK
    },
    "blue": {
        "coat": DARK_BLUE,
        "lining": CYAN,
        "boots": BLUE,
        "mask": DARK_BLUE
    },
    "green": {
        "coat": DARK_GREEN,
        "lining": LIGHT_GREEN,
        "boots": GREEN,
        "mask": DARK_GREEN
    },
    "purple": {
        "coat": PURPLE,
        "lining": (200, 150, 255),
        "boots": (150, 100, 200),
        "mask": PURPLE
    },
    "gold": {
        "coat": (100, 80, 0),
        "lining": GOLD,
        "boots": (180, 150, 0),
        "mask": (100, 80, 0)
    }
}
current_color_scheme = "default"
combo_count = 0
combo_timer = 0
combo_threshold = 120
difficulty = DIFFICULTY_NORMAL
hazards = []
MINIMAP_WIDTH = int(SCREEN_WIDTH * 0.2)
MINIMAP_HEIGHT = int(SCREEN_HEIGHT * 0.2)
MINIMAP_PLAYER_SIZE = 4
MINIMAP_ENEMY_SIZE = 3
MINIMAP_POWERUP_SIZE = 3
MINIMAP_HAZARD_SIZE = 3
MINIMAP_BOSS_SIZE = 6
MINIMAP_UFO_SIZE = 5
minimap_explored = [[False for _ in range(MINIMAP_WIDTH)] for _ in range(MINIMAP_HEIGHT)]
exploration_radius = 10
boss_active = False
boss_level = 5
weather_type = "clear"
weather_particles = []
weather_timer = 0
weather_duration = 600
day_night_timer = 0
day_night_cycle = 3600
is_day = True
achievements = {
    "first_blood": {"name": "First Blood", "description": "Defeat your first enemy", "unlocked": False},
    "combo_master": {"name": "Combo Master", "description": "Achieve a 10x combo", "unlocked": False},
    "survivor": {"name": "Survivor", "description": "Complete a level without taking damage", "unlocked": False},
    "boss_slayer": {"name": "Boss Slayer", "description": "Defeat your first boss", "unlocked": False},
    "level_10": {"name": "Experienced", "description": "Reach level 10", "unlocked": False},
    "perfect_shield": {"name": "Perfect Shield", "description": "Block 100 damage with a single shield", "unlocked": False}
}
new_achievement = None
achievement_timer = 0
side_quests = []
active_quest = None
quest_completed = False
quest_timer = 0
class Quest:
    def __init__(self, quest_id, name, description, objective_type, target_count, reward_score, reward_upgrades):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.objective_type = objective_type
        self.target_count = target_count
        self.current_count = 0
        self.reward_score = reward_score
        self.reward_upgrades = reward_upgrades
        self.completed = False
        self.active = False
def initialize_quests():
    global side_quests
    
    side_quests = [
        Quest("kill_enemies", "Enemy Hunter", "Defeat 10 enemies", "kill", 10, 50, 1),
        Quest("collect_powerups", "Power Collector", "Collect 5 power-ups", "collect", 5, 75, 1),
        Quest("survive_time", "Survivor", "Survive for 2 minutes", "survive", 7200, 100, 2),
        Quest("kill_boss", "Boss Slayer", "Defeat a boss", "kill", 1, 150, 3),
        Quest("combo_master", "Combo Master", "Achieve a 15x combo", "combo", 15, 125, 2),
        Quest("no_damage", "Untouchable", "Complete a level without taking damage", "no_damage", 1, 200, 3)
    ]
screen_shake_intensity = 0
screen_shake_duration = 0
screen_shake_offset_x = 0
screen_shake_offset_y = 0
slow_motion_active = False
slow_motion_factor = 0.3
slow_motion_duration = 0
slow_motion_timer = 0
screen_flash_color = None
screen_flash_duration = 0
graphics_settings = {
    "particle_density": 1.0,
    "background_detail": 1.0,
    "weather_effects": True,
    "screen_shake": True,
    "slow_motion_effects": True,
    "show_minimap": True
}
stars_far = []
stars_mid = []
stars_near = []
stars_twinkle = []
asteroids = []
for _ in range(200):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT - 50)
    size = random.uniform(0.5, 1.5)
    brightness = random.uniform(0.3, 0.7)
    color = random.choice(STAR_COLORS)
    speed = random.uniform(0.05, 0.15)
    twinkle_speed = random.uniform(0.01, 0.05)
    twinkle_phase = random.uniform(0, 2 * math.pi)
    stars_far.append([x, y, size, brightness, color, speed, twinkle_speed, twinkle_phase])
for _ in range(150):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT - 50)
    size = random.uniform(1.0, 2.5)
    brightness = random.uniform(0.5, 0.9)
    color = random.choice(STAR_COLORS)
    speed = random.uniform(0.1, 0.3)
    twinkle_speed = random.uniform(0.02, 0.08)
    twinkle_phase = random.uniform(0, 2 * math.pi)
    stars_mid.append([x, y, size, brightness, color, speed, twinkle_speed, twinkle_phase])
for _ in range(100):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT - 50)
    size = random.uniform(2.0, 4.0)
    brightness = random.uniform(0.7, 1.0)
    color = random.choice(STAR_COLORS)
    speed = random.uniform(0.2, 0.5)
    twinkle_speed = random.uniform(0.03, 0.1)
    twinkle_phase = random.uniform(0, 2 * math.pi)
    stars_near.append([x, y, size, brightness, color, speed, twinkle_speed, twinkle_phase])
for _ in range(50):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT - 50)
    size = random.uniform(1.5, 3.0)
    base_brightness = random.uniform(0.5, 1.0)
    color = random.choice(STAR_COLORS)
    twinkle_speed = random.uniform(0.05, 0.15)
    twinkle_phase = random.uniform(0, 2 * math.pi)
    stars_twinkle.append([x, y, size, base_brightness, color, twinkle_speed, twinkle_phase])
for _ in range(10):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(50, SCREEN_HEIGHT - 150)
    size = random.randint(15, 30)
    color = random.choice([(100, 100, 100), (150, 150, 150), (80, 80, 80)])
    speed = random.uniform(0.3, 0.8)
    vertical_speed = random.uniform(-0.1, 0.1)
    asteroids.append([x, y, size, color, speed, vertical_speed])
planets = []
for _ in range(3):
    x = random.randint(100, SCREEN_WIDTH - 100)
    y = random.randint(50, SCREEN_HEIGHT - 150)
    size = random.randint(20, 50)
    color = random.choice([(100, 50, 150), (150, 100, 50), (50, 100, 150)])
    speed = random.uniform(0.02, 0.08)
    planets.append([x, y, size, color, speed])
nebulae = []
for _ in range(3):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT - 100)
    width = random.randint(200, 400)
    height = random.randint(100, 200)
    color = random.choice(NEBULA_COLORS)
    rotation = random.uniform(0, 2 * math.pi)
    rotation_speed = random.uniform(-0.005, 0.005)
    nebulae.append([x, y, width, height, color, rotation, rotation_speed])
shooting_stars = []
for _ in range(3):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT // 2)
    length = random.randint(20, 50)
    speed = random.uniform(5, 15)
    angle = random.uniform(math.pi/4, 3*math.pi/4)
    active = False
    timer = random.randint(0, 300)
    shooting_stars.append([x, y, length, speed, angle, active, timer])
galaxies = []
for _ in range(2):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT // 2)
    size = random.randint(30, 60)
    color = random.choice([(100, 100, 255, 30), (255, 100, 100, 30), (100, 255, 100, 30)])
    rotation = random.uniform(0, 2 * math.pi)
    rotation_speed = random.uniform(-0.002, 0.002)
    galaxies.append([x, y, size, color, rotation, rotation_speed])
class NetworkManager:
    def __init__(self):
        self.role = ROLE_NONE
        self.server_socket = None
        self.client_socket = None
        self.clients = {}
        self.players = {}
        self.player_id = None
        self.running = False
        self.message_queue = queue.Queue()
        self.thread = None
        
    def start_server(self):
        self.role = ROLE_SERVER
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', PORT))
        self.server_socket.listen(MAX_PLAYERS)
        self.running = True
        
        self.thread = threading.Thread(target=self.server_loop)
        self.thread.daemon = True
        self.thread.start()
        
        print(f"Server started on port {PORT}")
        return True
    
    def connect_to_server(self, ip=SERVER_IP):
        self.role = ROLE_CLIENT
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.client_socket.connect((ip, PORT))
            self.running = True
            
            self.thread = threading.Thread(target=self.client_loop)
            self.thread.daemon = True
            self.thread.start()
            
            self.send_message({
                "type": "connect",
                "name": "Player",
                "color": current_color_scheme
            })
            
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def server_loop(self):
        while self.running:
            try:
                readable, _, _ = select.select([self.server_socket] + list(self.clients.keys()), [], [], 0.01)
                
                for s in readable:
                    if s is self.server_socket:
                        client_socket, addr = self.server_socket.accept()
                        client_id = len(self.clients)
                        self.clients[client_socket] = {
                            "id": client_id,
                            "socket": client_socket,
                            "addr": addr
                        }
                        
                        self.send_to_client(client_socket, {
                            "type": "player_id",
                            "id": client_id
                        })
                        
                        self.broadcast({
                            "type": "player_joined",
                            "id": client_id
                        }, exclude=client_socket)
                        
                        print(f"Player {client_id} connected from {addr}")
                    else:
                        try:
                            data = s.recv(BUFFER_SIZE)
                            if data:
                                message = json.loads(data.decode('utf-8'))
                                self.handle_server_message(s, message)
                            else:
                                self.disconnect_client(s)
                        except:
                            self.disconnect_client(s)
                
                while not self.message_queue.empty():
                    message = self.message_queue.get()
                    self.broadcast(message)
                
            except Exception as e:
                print(f"Server error: {e}")
                break
        
        for client_socket in list(self.clients.keys()):
            client_socket.close()
        self.server_socket.close()
    
    def client_loop(self):
        while self.running:
            try:
                readable, _, _ = select.select([self.client_socket], [], [], 0.01)
                
                if readable:
                    data = self.client_socket.recv(BUFFER_SIZE)
                    if data:
                        message = json.loads(data.decode('utf-8'))
                        self.handle_client_message(message)
                    else:
                        self.running = False
                        break
                
                while not self.message_queue.empty():
                    message = self.message_queue.get()
                    self.send_to_server(message)
                
            except Exception as e:
                print(f"Client error: {e}")
                break
        
        if self.client_socket:
            self.client_socket.close()
    
    def handle_server_message(self, client_socket, message):
        msg_type = message.get("type")
        client_id = self.clients[client_socket]["id"]
        
        if msg_type == "player_update":
            if client_id in self.players:
                self.players[client_id].update(message)
            else:
                self.players[client_id] = NetworkPlayer(client_id, message)
            
            self.broadcast({
                "type": "player_update",
                "id": client_id,
                "data": message
            }, exclude=client_socket)
        
        elif msg_type == "chat":
            self.broadcast({
                "type": "chat",
                "id": client_id,
                "message": message.get("message", "")
            })
        
        elif msg_type == "game_start":
            self.broadcast({
                "type": "game_start"
            })
    
    def handle_client_message(self, message):
        msg_type = message.get("type")
        
        if msg_type == "player_id":
            self.player_id = message.get("id")
            print(f"Received player ID: {self.player_id}")
        
        elif msg_type == "player_update":
            player_id = message.get("id")
            if player_id != self.player_id and player_id in self.players:
                self.players[player_id].update(message.get("data", {}))
        
        elif msg_type == "player_joined":
            player_id = message.get("id")
            self.players[player_id] = NetworkPlayer(player_id, {})
            chat_messages.append(f"Player {player_id} joined the game")
        
        elif msg_type == "player_left":
            player_id = message.get("id")
            if player_id in self.players:
                del self.players[player_id]
            chat_messages.append(f"Player {player_id} left the game")
        
        elif msg_type == "chat":
            player_id = message.get("id")
            msg = message.get("message", "")
            if player_id in self.players:
                name = self.players[player_id].name
                chat_messages.append(f"{name}: {msg}")
            else:
                chat_messages.append(f"Player {player_id}: {msg}")
        
        elif msg_type == "game_start":
            global game_state
            game_state = NETWORK_PLAYING
            chat_messages.append("Game started!")
    
    def send_message(self, message):
        self.message_queue.put(message)
    
    def send_to_server(self, message):
        if self.client_socket:
            try:
                data = json.dumps(message).encode('utf-8')
                self.client_socket.send(data)
            except:
                pass
    
    def send_to_client(self, client_socket, message):
        try:
            data = json.dumps(message).encode('utf-8')
            client_socket.send(data)
        except:
            pass
    
    def broadcast(self, message, exclude=None):
        for client_socket in list(self.clients.keys()):
            if client_socket != exclude:
                self.send_to_client(client_socket, message)
    
    def disconnect_client(self, client_socket):
        if client_socket in self.clients:
            client_id = self.clients[client_socket]["id"]
            del self.clients[client_socket]
            
            if client_id in self.players:
                del self.players[client_id]
            
            self.broadcast({
                "type": "player_left",
                "id": client_id
            })
            
            client_socket.close()
            print(f"Player {client_id} disconnected")
    
    def update_player(self, data):
        if self.role == ROLE_CLIENT:
            self.send_message({
                "type": "player_update",
                "data": data
            })
    
    def send_chat(self, message):
        self.send_message({
            "type": "chat",
            "message": message
        })
    
    def start_game(self):
        if self.role == ROLE_SERVER:
            self.broadcast({
                "type": "game_start"
            })
    
    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        if self.server_socket:
            self.server_socket.close()
        
        if self.client_socket:
            self.client_socket.close()
class NetworkPlayer:
    def __init__(self, player_id, data):
        self.id = player_id
        self.name = data.get("name", f"Player{player_id}")
        self.color = data.get("color", "default")
        self.x = data.get("x", SCREEN_WIDTH // 2)
        self.y = data.get("y", SCREEN_HEIGHT - 100)
        self.health = data.get("health", 100)
        self.facing_right = data.get("facing_right", True)
        self.animation_state = data.get("animation_state", "idle")
        self.score = data.get("score", 0)
        self.ready = data.get("ready", False)
    
    def update(self, data):
        self.x = data.get("x", self.x)
        self.y = data.get("y", self.y)
        self.health = data.get("health", self.health)
        self.facing_right = data.get("facing_right", self.facing_right)
        self.animation_state = data.get("animation_state", self.animation_state)
        self.score = data.get("score", self.score)
        self.ready = data.get("ready", self.ready)
class AdvancedParticle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, size, speed, direction, lifetime, particle_type="normal"):
        super().__init__()
        self.particle_type = particle_type
        self.size = size
        self.color = color
        self.speed = speed
        self.direction = direction
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 0.1
        self.fade_rate = 5
        
        self.create_image()
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.vx = math.cos(direction) * speed
        self.vy = math.sin(direction) * speed
        
    def create_image(self):
        if self.particle_type == "energy":
            self.image = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size * 2, self.size * 2), self.size)
            pygame.draw.circle(self.image, (255, 255, 255), (self.size * 2, self.size * 2), self.size // 2)
        elif self.particle_type == "fire":
            self.image = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size * 1.5, self.size * 1.5), self.size)
        elif self.particle_type == "smoke":
            self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (100, 100, 100, 150), (self.size, self.size), self.size)
        else:
            self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
    
    def update(self):
        if self.particle_type in ["fire", "smoke"]:
            self.vy += self.gravity
        
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        self.lifetime -= 1
        
        if self.max_lifetime > 0:
            alpha = max(0, 255 - (self.max_lifetime - self.lifetime) * self.fade_rate)
        else:
            alpha = 255
        
        self.create_image()
        self.image.set_alpha(alpha)
        
        if self.lifetime <= 0:
            self.kill()
def create_krrish_idle_image():
    surf = pygame.Surface((40, 60), pygame.SRCALPHA)
    
    colors = player_colors[current_color_scheme]
    
    for i in range(5):
        flame_height = random.randint(5, 15)
        flame_x = random.randint(5, 35)
        flame_y = 55 - flame_height
        flame_color = random.choice([FIRE_ORANGE, FIRE_RED, YELLOW])
        pygame.draw.polygon(surf, flame_color, 
                          [(flame_x, flame_y), 
                           (flame_x - 3, flame_y + flame_height), 
                           (flame_x + 3, flame_y + flame_height)])
    
    pygame.draw.rect(surf, colors["coat"], (10, 20, 20, 30))
    pygame.draw.polygon(surf, colors["lining"], [(10, 20), (15, 25), (15, 45), (10, 50)])
    
    pygame.draw.polygon(surf, colors["coat"], [(8, 25), (12, 20), (28, 20), (32, 25), (30, 50), (10, 50)])
    pygame.draw.polygon(surf, colors["lining"], [(12, 20), (15, 25), (15, 45), (12, 50)])
    
    pygame.draw.rect(surf, colors["boots"], (10, 50, 8, 10))
    pygame.draw.rect(surf, colors["boots"], (22, 50, 8, 10))
    
    pygame.draw.circle(surf, (255, 220, 177), (20, 15), 8)
    
    pygame.draw.ellipse(surf, colors["mask"], (12, 12, 16, 6))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(10, 13, 5, 4))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(25, 13, 5, 4))
    
    pygame.draw.rect(surf, (255, 220, 177), (5, 25, 8, 15))
    pygame.draw.rect(surf, (255, 220, 177), (27, 25, 8, 15))
    
    pygame.draw.circle(surf, (255, 220, 177), (9, 42), 4)
    pygame.draw.circle(surf, (255, 220, 177), (31, 42), 4)
    
    pygame.draw.line(surf, YELLOW, (20, 30), (20, 40), 2)
    pygame.draw.line(surf, YELLOW, (15, 35), (25, 35), 2)
    
    return surf
def create_krrish_walk1_image():
    surf = pygame.Surface((40, 60), pygame.SRCALPHA)
    
    colors = player_colors[current_color_scheme]
    
    for i in range(3):
        flame_height = random.randint(5, 15)
        flame_x = random.randint(5, 35)
        flame_y = 55 - flame_height
        flame_color = random.choice([FIRE_ORANGE, FIRE_RED, YELLOW])
        pygame.draw.polygon(surf, flame_color, 
                          [(flame_x, flame_y), 
                           (flame_x - 3, flame_y + flame_height), 
                           (flame_x + 3, flame_y + flame_height)])
    
    pygame.draw.rect(surf, colors["coat"], (10, 20, 20, 30))
    pygame.draw.polygon(surf, colors["lining"], [(10, 20), (15, 25), (15, 45), (10, 50)])
    
    pygame.draw.polygon(surf, colors["coat"], [(8, 25), (12, 20), (28, 20), (32, 25), (30, 50), (10, 50)])
    pygame.draw.polygon(surf, colors["lining"], [(12, 20), (15, 25), (15, 45), (12, 50)])
    
    pygame.draw.rect(surf, colors["boots"], (8, 50, 8, 10))
    pygame.draw.rect(surf, colors["boots"], (24, 50, 8, 10))
    
    pygame.draw.circle(surf, (255, 220, 177), (20, 15), 8)
    
    pygame.draw.ellipse(surf, colors["mask"], (12, 12, 16, 6))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(10, 13, 5, 4))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(25, 13, 5, 4))
    
    pygame.draw.rect(surf, (255, 220, 177), (5, 25, 8, 15))
    pygame.draw.rect(surf, (255, 220, 177), (27, 25, 8, 15))
    
    pygame.draw.circle(surf, (255, 220, 177), (9, 42), 4)
    pygame.draw.circle(surf, (255, 220, 177), (31, 42), 4)
    
    pygame.draw.line(surf, YELLOW, (20, 30), (20, 40), 2)
    pygame.draw.line(surf, YELLOW, (15, 35), (25, 35), 2)
    
    return surf
def create_krrish_walk2_image():
    surf = pygame.Surface((40, 60), pygame.SRCALPHA)
    
    colors = player_colors[current_color_scheme]
    
    for i in range(3):
        flame_height = random.randint(5, 15)
        flame_x = random.randint(5, 35)
        flame_y = 55 - flame_height
        flame_color = random.choice([FIRE_ORANGE, FIRE_RED, YELLOW])
        pygame.draw.polygon(surf, flame_color, 
                          [(flame_x, flame_y), 
                           (flame_x - 3, flame_y + flame_height), 
                           (flame_x + 3, flame_y + flame_height)])
    
    pygame.draw.rect(surf, colors["coat"], (10, 20, 20, 30))
    pygame.draw.polygon(surf, colors["lining"], [(10, 20), (15, 25), (15, 45), (10, 50)])
    
    pygame.draw.polygon(surf, colors["coat"], [(8, 25), (12, 20), (28, 20), (32, 25), (30, 50), (10, 50)])
    pygame.draw.polygon(surf, colors["lining"], [(12, 20), (15, 25), (15, 45), (12, 50)])
    
    pygame.draw.rect(surf, colors["boots"], (12, 50, 8, 10))
    pygame.draw.rect(surf, colors["boots"], (20, 50, 8, 10))
    
    pygame.draw.circle(surf, (255, 220, 177), (20, 15), 8)
    
    pygame.draw.ellipse(surf, colors["mask"], (12, 12, 16, 6))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(10, 13, 5, 4))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(25, 13, 5, 4))
    
    pygame.draw.rect(surf, (255, 220, 177), (5, 25, 8, 15))
    pygame.draw.rect(surf, (255, 220, 177), (27, 25, 8, 15))
    
    pygame.draw.circle(surf, (255, 220, 177), (9, 42), 4)
    pygame.draw.circle(surf, (255, 220, 177), (31, 42), 4)
    
    pygame.draw.line(surf, YELLOW, (20, 30), (20, 40), 2)
    pygame.draw.line(surf, YELLOW, (15, 35), (25, 35), 2)
    
    return surf
def create_krrish_run1_image():
    surf = pygame.Surface((40, 60), pygame.SRCALPHA)
    
    colors = player_colors[current_color_scheme]
    
    for i in range(4):
        flame_height = random.randint(5, 15)
        flame_x = random.randint(5, 35)
        flame_y = 55 - flame_height
        flame_color = random.choice([FIRE_ORANGE, FIRE_RED, YELLOW])
        pygame.draw.polygon(surf, flame_color, 
                          [(flame_x, flame_y), 
                           (flame_x - 3, flame_y + flame_height), 
                           (flame_x + 3, flame_y + flame_height)])
    
    pygame.draw.rect(surf, colors["coat"], (10, 20, 20, 30))
    pygame.draw.polygon(surf, colors["lining"], [(10, 20), (15, 25), (15, 45), (10, 50)])
    
    pygame.draw.polygon(surf, colors["coat"], [(8, 25), (12, 20), (28, 20), (32, 25), (30, 50), (10, 50)])
    pygame.draw.polygon(surf, colors["lining"], [(12, 20), (15, 25), (15, 45), (12, 50)])
    
    pygame.draw.rect(surf, colors["boots"], (8, 50, 8, 10))
    pygame.draw.rect(surf, colors["boots"], (24, 50, 8, 10))
    
    pygame.draw.circle(surf, (255, 220, 177), (20, 15), 8)
    
    pygame.draw.ellipse(surf, colors["mask"], (12, 12, 16, 6))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(10, 13, 5, 4))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(25, 13, 5, 4))
    
    pygame.draw.rect(surf, (255, 220, 177), (5, 20, 8, 15))
    pygame.draw.rect(surf, (255, 220, 177), (27, 25, 8, 15))
    
    pygame.draw.circle(surf, (255, 220, 177), (9, 37), 4)
    pygame.draw.circle(surf, (255, 220, 177), (35, 42), 4)
    
    pygame.draw.line(surf, YELLOW, (20, 30), (20, 40), 2)
    pygame.draw.line(surf, YELLOW, (15, 35), (25, 35), 2)
    
    pygame.draw.line(surf, WHITE, (30, 25), (20, 25), 1)
    pygame.draw.line(surf, WHITE, (30, 30), (20, 30), 1)
    
    return surf
def create_krrish_run2_image():
    surf = pygame.Surface((40, 60), pygame.SRCALPHA)
    
    colors = player_colors[current_color_scheme]
    
    for i in range(4):
        flame_height = random.randint(5, 15)
        flame_x = random.randint(5, 35)
        flame_y = 55 - flame_height
        flame_color = random.choice([FIRE_ORANGE, FIRE_RED, YELLOW])
        pygame.draw.polygon(surf, flame_color, 
                          [(flame_x, flame_y), 
                           (flame_x - 3, flame_y + flame_height), 
                           (flame_x + 3, flame_y + flame_height)])
    
    pygame.draw.rect(surf, colors["coat"], (10, 20, 20, 30))
    pygame.draw.polygon(surf, colors["lining"], [(10, 20), (15, 25), (15, 45), (10, 50)])
    
    pygame.draw.polygon(surf, colors["coat"], [(8, 25), (12, 20), (28, 20), (32, 25), (30, 50), (10, 50)])
    pygame.draw.polygon(surf, colors["lining"], [(12, 20), (15, 25), (15, 45), (12, 50)])
    
    pygame.draw.rect(surf, colors["boots"], (12, 50, 8, 10))
    pygame.draw.rect(surf, colors["boots"], (20, 50, 8, 10))
    
    pygame.draw.circle(surf, (255, 220, 177), (20, 15), 8)
    
    pygame.draw.ellipse(surf, colors["mask"], (12, 12, 16, 6))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(10, 13, 5, 4))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(25, 13, 5, 4))
    
    pygame.draw.rect(surf, (255, 220, 177), (5, 25, 8, 15))
    pygame.draw.rect(surf, (255, 220, 177), (27, 20, 8, 15))
    
    pygame.draw.circle(surf, (255, 220, 177), (9, 42), 4)
    pygame.draw.circle(surf, (255, 220, 177), (35, 37), 4)
    
    pygame.draw.line(surf, YELLOW, (20, 30), (20, 40), 2)
    pygame.draw.line(surf, YELLOW, (15, 35), (25, 35), 2)
    
    pygame.draw.line(surf, WHITE, (5, 25), (15, 25), 1)
    pygame.draw.line(surf, WHITE, (5, 30), (15, 30), 1)
    
    return surf
def create_krrish_jump_image():
    surf = pygame.Surface((40, 60), pygame.SRCALPHA)
    
    colors = player_colors[current_color_scheme]
    
    for i in range(7):
        flame_height = random.randint(5, 20)
        flame_x = random.randint(5, 35)
        flame_y = 55 - flame_height
        flame_color = random.choice([FIRE_ORANGE, FIRE_RED, YELLOW])
        pygame.draw.polygon(surf, flame_color, 
                          [(flame_x, flame_y), 
                           (flame_x - 3, flame_y + flame_height), 
                           (flame_x + 3, flame_y + flame_height)])
    
    pygame.draw.rect(surf, colors["coat"], (10, 20, 20, 30))
    pygame.draw.polygon(surf, colors["lining"], [(10, 20), (15, 25), (15, 45), (10, 50)])
    
    pygame.draw.polygon(surf, colors["coat"], [(8, 25), (12, 20), (28, 20), (32, 25), (30, 50), (10, 50)])
    pygame.draw.polygon(surf, colors["lining"], [(12, 20), (15, 25), (15, 45), (12, 50)])
    
    pygame.draw.rect(surf, colors["boots"], (10, 50, 8, 10))
    pygame.draw.rect(surf, colors["boots"], (22, 50, 8, 10))
    
    pygame.draw.circle(surf, (255, 220, 177), (20, 15), 8)
    
    pygame.draw.ellipse(surf, colors["mask"], (12, 12, 16, 6))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(10, 13, 5, 4))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(25, 13, 5, 4))
    
    pygame.draw.rect(surf, (255, 220, 177), (5, 20, 8, 15))
    pygame.draw.rect(surf, (255, 220, 177), (27, 20, 8, 15))
    
    pygame.draw.circle(surf, (255, 220, 177), (9, 37), 4)
    pygame.draw.circle(surf, (255, 220, 177), (31, 37), 4)
    
    pygame.draw.line(surf, YELLOW, (20, 30), (20, 40), 2)
    pygame.draw.line(surf, YELLOW, (15, 35), (25, 35), 2)
    
    return surf
def create_krrish_shoot_image():
    surf = pygame.Surface((40, 60), pygame.SRCALPHA)
    
    colors = player_colors[current_color_scheme]
    
    for i in range(5):
        flame_height = random.randint(5, 15)
        flame_x = random.randint(5, 35)
        flame_y = 55 - flame_height
        flame_color = random.choice([FIRE_ORANGE, FIRE_RED, YELLOW])
        pygame.draw.polygon(surf, flame_color, 
                          [(flame_x, flame_y), 
                           (flame_x - 3, flame_y + flame_height), 
                           (flame_x + 3, flame_y + flame_height)])
    
    pygame.draw.rect(surf, colors["coat"], (10, 20, 20, 30))
    pygame.draw.polygon(surf, colors["lining"], [(10, 20), (15, 25), (15, 45), (10, 50)])
    
    pygame.draw.polygon(surf, colors["coat"], [(8, 25), (12, 20), (28, 20), (32, 25), (30, 50), (10, 50)])
    pygame.draw.polygon(surf, colors["lining"], [(12, 20), (15, 25), (15, 45), (12, 50)])
    
    pygame.draw.rect(surf, colors["boots"], (10, 50, 8, 10))
    pygame.draw.rect(surf, colors["boots"], (22, 50, 8, 10))
    
    pygame.draw.circle(surf, (255, 220, 177), (20, 15), 8)
    
    pygame.draw.ellipse(surf, colors["mask"], (12, 12, 16, 6))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(10, 13, 5, 4))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(25, 13, 5, 4))
    
    pygame.draw.rect(surf, (255, 220, 177), (5, 25, 8, 15))
    pygame.draw.rect(surf, (255, 220, 177), (27, 25, 15, 5))
    
    pygame.draw.circle(surf, (255, 220, 177), (9, 42), 4)
    pygame.draw.circle(surf, (255, 220, 177), (42, 27), 4)
    
    pygame.draw.circle(surf, GREEN, (42, 27), 6, 1)
    pygame.draw.circle(surf, YELLOW, (42, 27), 4, 1)
    
    pygame.draw.line(surf, YELLOW, (20, 30), (20, 40), 2)
    pygame.draw.line(surf, YELLOW, (15, 35), (25, 35), 2)
    
    return surf
def create_krrish_attack_image():
    surf = pygame.Surface((50, 60), pygame.SRCALPHA)
    
    colors = player_colors[current_color_scheme]
    
    for i in range(7):
        flame_height = random.randint(5, 20)
        flame_x = random.randint(5, 45)
        flame_y = 55 - flame_height
        flame_color = random.choice([FIRE_ORANGE, FIRE_RED, YELLOW])
        pygame.draw.polygon(surf, flame_color, 
                          [(flame_x, flame_y), 
                           (flame_x - 3, flame_y + flame_height), 
                           (flame_x + 3, flame_y + flame_height)])
    
    pygame.draw.rect(surf, colors["coat"], (10, 20, 20, 30))
    pygame.draw.polygon(surf, colors["lining"], [(10, 20), (15, 25), (15, 45), (10, 50)])
    
    pygame.draw.polygon(surf, colors["coat"], [(8, 25), (12, 20), (28, 20), (32, 25), (30, 50), (10, 50)])
    pygame.draw.polygon(surf, colors["lining"], [(12, 20), (15, 25), (15, 45), (12, 50)])
    
    pygame.draw.rect(surf, colors["boots"], (10, 50, 8, 10))
    pygame.draw.rect(surf, colors["boots"], (22, 50, 8, 10))
    
    pygame.draw.circle(surf, (255, 220, 177), (20, 15), 8)
    
    pygame.draw.ellipse(surf, colors["mask"], (12, 12, 16, 6))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(10, 13, 5, 4))
    pygame.draw.ellipse(surf, colors["mask"], pygame.Rect(25, 13, 5, 4))
    
    pygame.draw.rect(surf, (255, 220, 177), (5, 25, 8, 15))
    pygame.draw.rect(surf, (255, 220, 177), (27, 25, 15, 5))
    
    pygame.draw.circle(surf, (255, 220, 177), (9, 42), 4)
    pygame.draw.circle(surf, (255, 220, 177), (42, 27), 4)
    
    pygame.draw.circle(surf, GREEN, (42, 27), 6, 1)
    pygame.draw.circle(surf, YELLOW, (42, 27), 4, 1)
    
    pygame.draw.line(surf, WHITE, (30, 25), (20, 25), 1)
    pygame.draw.line(surf, WHITE, (30, 30), (20, 30), 1)
    
    pygame.draw.line(surf, YELLOW, (20, 30), (20, 40), 2)
    pygame.draw.line(surf, YELLOW, (15, 35), (25, 35), 2)
    
    return surf
def create_basic_enemy_image():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.rect(surf, PURPLE, (5, 10, 30, 25))
    pygame.draw.circle(surf, BLACK, (20, 10), 8)
    pygame.draw.circle(surf, RED, (15, 8), 3)
    pygame.draw.circle(surf, RED, (25, 8), 3)
    return surf
def create_ranged_enemy_image():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.rect(surf, DARK_BLUE, (5, 10, 30, 25))
    pygame.draw.circle(surf, BLACK, (20, 10), 8)
    pygame.draw.circle(surf, CYAN, (15, 8), 3)
    pygame.draw.circle(surf, CYAN, (25, 8), 3)
    pygame.draw.rect(surf, GRAY, (30, 15, 10, 5))
    return surf
def create_tank_enemy_image():
    surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.rect(surf, DARK_RED, (5, 15, 40, 30))
    pygame.draw.circle(surf, BLACK, (25, 15), 10)
    pygame.draw.circle(surf, RED, (20, 12), 4)
    pygame.draw.circle(surf, RED, (30, 12), 4)
    pygame.draw.rect(surf, GRAY, (10, 20, 30, 5))
    pygame.draw.rect(surf, GRAY, (10, 30, 30, 5))
    return surf
def create_fast_enemy_image():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.rect(surf, ORANGE, (5, 8, 20, 18))
    pygame.draw.circle(surf, BLACK, (15, 8), 6)
    pygame.draw.circle(surf, YELLOW, (12, 6), 2)
    pygame.draw.circle(surf, YELLOW, (18, 6), 2)
    pygame.draw.line(surf, YELLOW, (0, 15), (5, 15), 2)
    pygame.draw.line(surf, YELLOW, (25, 15), (30, 15), 2)
    return surf
def create_boss_image():
    surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    pygame.draw.rect(surf, DARK_RED, (20, 40, 80, 60))
    
    pygame.draw.circle(surf, BLACK, (60, 30), 25)
    
    pygame.draw.circle(surf, RED, (45, 25), 8)
    pygame.draw.circle(surf, RED, (75, 25), 8)
    
    pygame.draw.rect(surf, GRAY, (30, 50, 60, 10))
    pygame.draw.rect(surf, GRAY, (30, 70, 60, 10))
    
    pygame.draw.rect(surf, DARK_RED, (0, 50, 20, 40))
    pygame.draw.rect(surf, DARK_RED, (100, 50, 20, 40))
    
    pygame.draw.rect(surf, DARK_RED, (30, 100, 20, 20))
    pygame.draw.rect(surf, DARK_RED, (70, 100, 20, 20))
    
    pygame.draw.polygon(surf, YELLOW, [(60, 60), (50, 80), (70, 80)])
    
    return surf
def create_energy_blast_image():
    surf = pygame.Surface((15, 15), pygame.SRCALPHA)
    pygame.draw.circle(surf, GREEN, (7, 7), 7)
    pygame.draw.circle(surf, YELLOW, (7, 7), 4)
    return surf
def create_enemy_projectile_image():
    surf = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(surf, RED, (5, 5), 5)
    pygame.draw.circle(surf, YELLOW, (5, 5), 3)
    return surf
def create_ufo_image():
    surf = pygame.Surface((80, 40), pygame.SRCALPHA)
    
    pygame.draw.ellipse(surf, BLACK, (5, 15, 70, 20))
    
    pygame.draw.arc(surf, UFO_BLUE, (20, 5, 40, 20), math.pi, 0, 0)
    pygame.draw.arc(surf, LIGHT_BLUE, (20, 5, 40, 20), math.pi, 0, 2)
    
    for i in range(5):
        x = 15 + i * 12
        pygame.draw.circle(surf, UFO_BLUE, (x, 15), 3)
        pygame.draw.circle(surf, LIGHT_BLUE, (x, 15), 2)
    
    pygame.draw.ellipse(surf, UFO_BLUE, (5, 30, 70, 10), 2)
    
    pygame.draw.arc(surf, LIGHT_BLUE, (25, 10, 30, 10), math.pi, 0, 1)
    
    return surf
def create_fire_powerup_image():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    pygame.draw.polygon(surf, FIRE_ORANGE, [(15, 5), (10, 15), (5, 25), (15, 20), (25, 25), (20, 15)])
    pygame.draw.polygon(surf, FIRE_RED, [(15, 5), (10, 15), (15, 10), (20, 15)])
    
    pygame.draw.circle(surf, YELLOW, (15, 12), 3)
    
    return surf
def create_shield_powerup_image():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    pygame.draw.circle(surf, CYAN, (15, 15), 12, 2)
    pygame.draw.circle(surf, LIGHT_BLUE, (15, 15), 8, 2)
    
    pygame.draw.circle(surf, WHITE, (15, 15), 4)
    
    return surf
def create_speed_powerup_image():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    pygame.draw.polygon(surf, ELECTRIC_PURPLE, [(15, 5), (10, 15), (15, 15), (10, 25), (20, 15), (15, 15), (20, 5)])
    
    pygame.draw.circle(surf, WHITE, (15, 15), 3)
    
    return surf
def create_invincibility_powerup_image():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    points = []
    for i in range(10):
        angle = math.pi * i / 5
        if i % 2 == 0:
            radius = 12
        else:
            radius = 6
        x = 15 + radius * math.cos(angle - math.pi/2)
        y = 15 + radius * math.sin(angle - math.pi/2)
        points.append((x, y))
    
    pygame.draw.polygon(surf, GOLD, points)
    pygame.draw.polygon(surf, YELLOW, points, 2)
    
    return surf
def create_hazard_spike_image():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    pygame.draw.polygon(surf, GRAY, [(15, 5), (5, 25), (25, 25)])
    
    return surf
def draw_parallax_background(surface):
    for star in stars_far:
        star[0] -= star[5]
        if star[0] < 0:
            star[0] = SCREEN_WIDTH
            star[1] = random.randint(0, SCREEN_HEIGHT - 50)
        
        pygame.draw.circle(surface, star[4], (int(star[0]), int(star[1])), int(star[2]))
    
    for asteroid in asteroids:
        asteroid[0] -= asteroid[4]
        asteroid[1] += asteroid[5]
        if asteroid[0] < -asteroid[2]:
            asteroid[0] = SCREEN_WIDTH + asteroid[2]
            asteroid[1] = random.randint(50, SCREEN_HEIGHT - 150)
        
        pygame.draw.circle(surface, asteroid[3], (int(asteroid[0]), int(asteroid[1])), asteroid[2])
        detail_x = int(asteroid[0]) - asteroid[2] // 4
        detail_y = int(asteroid[1]) - asteroid[2] // 4
        detail_size = asteroid[2] // 6
        pygame.draw.circle(surface, (50, 50, 50), (detail_x, detail_y), detail_size)
    
    for planet in planets:
        planet[0] -= planet[4]
        if planet[0] < -planet[2]:
            planet[0] = SCREEN_WIDTH + planet[2]
            planet[1] = random.randint(50, SCREEN_HEIGHT - 150)
        
        pygame.draw.circle(surface, planet[3], (int(planet[0]), int(planet[1])), planet[2])
        highlight_x = int(planet[0]) - planet[2] // 3
        highlight_y = int(planet[1]) - planet[2] // 3
        highlight_size = planet[2] // 4
        highlight_color = (
            min(255, planet[3][0] + 50),
            min(255, planet[3][1] + 50),
            min(255, planet[3][2] + 50)
        )
        pygame.draw.circle(surface, highlight_color, (highlight_x, highlight_y), highlight_size)
def draw_space_background(surface):
    temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    if is_day:
        for y in range(SCREEN_HEIGHT - 50):
            color_value = int(20 + (y / (SCREEN_HEIGHT - 50)) * 50)
            color = (color_value, color_value, color_value + 20)
            pygame.draw.line(temp_surface, color, (0, y), (SCREEN_WIDTH, y))
    else:
        for y in range(SCREEN_HEIGHT - 50):
            color_value = int(5 + (y / (SCREEN_HEIGHT - 50)) * 25)
            color = (color_value, color_value, color_value + 10)
            pygame.draw.line(temp_surface, color, (0, y), (SCREEN_WIDTH, y))
    
    if graphics_settings['background_detail'] > 0.5:
        for nebula in nebulae:
            nebula[5] += nebula[6]
            
            nebula_surface = pygame.Surface((nebula[2], nebula[3]), pygame.SRCALPHA)
            
            center_x = nebula[2] // 2
            center_y = nebula[3] // 2
            
            step = 5 if graphics_settings['background_detail'] > 0.75 else 10
            
            for i in range(0, nebula[2], step):
                for j in range(0, nebula[3], step):
                    dx = i - center_x
                    dy = j - center_y
                    distance = math.sqrt(dx**2 + dy**2)
                    max_distance = math.sqrt(center_x**2 + center_y**2)
                    
                    alpha = int(nebula[4][3] * (1 - distance / max_distance))
                    alpha += random.randint(-10, 10)
                    alpha = max(0, min(255, alpha))
                    
                    color = (nebula[4][0], nebula[4][1], nebula[4][2], alpha)
                    pygame.draw.rect(nebula_surface, color, (i, j, step, step))
            
            rotated_nebula = pygame.transform.rotate(nebula_surface, math.degrees(nebula[5]))
            
            temp_surface.blit(rotated_nebula, (nebula[0] - rotated_nebula.get_width() // 2, 
                                          nebula[1] - rotated_nebula.get_height() // 2))
    
    if graphics_settings['background_detail'] > 0.7:
        for galaxy in galaxies:
            galaxy[4] += galaxy[5]
            
            galaxy_surface = pygame.Surface((galaxy[2] * 2, galaxy[2] * 2), pygame.SRCALPHA)
            
            center_x = galaxy[2]
            center_y = galaxy[2]
            
            num_stars = int(100 * graphics_settings['background_detail'])
            
            for i in range(num_stars):
                angle = i * 0.2 + galaxy[4]
                distance = i * 0.3
                
                x = center_x + math.cos(angle) * distance
                y = center_y + math.sin(angle) * distance
                
                size = max(1, 3 - distance / 30)
                
                alpha = int(galaxy[3][3] * (1 - distance / (galaxy[2])))
                alpha = max(0, min(255, alpha))
                
                color = (galaxy[3][0], galaxy[3][1], galaxy[3][2], alpha)
                pygame.draw.circle(galaxy_surface, color, (int(x), int(y)), size)
            
            temp_surface.blit(galaxy_surface, (galaxy[0] - galaxy[2], galaxy[1] - galaxy[2]))
    
    far_star_count = int(200 * graphics_settings['background_detail'])
    mid_star_count = int(150 * graphics_settings['background_detail'])
    near_star_count = int(100 * graphics_settings['background_detail'])
    
    for i, star in enumerate(stars_far[:far_star_count]):
        star[0] -= star[5]
        star[7] += star[6]
        
        if star[0] < 0:
            star[0] = SCREEN_WIDTH
            star[1] = random.randint(0, SCREEN_HEIGHT - 50)
        
        twinkle_factor = 0.5 + 0.5 * math.sin(star[7])
        current_brightness = star[3] * twinkle_factor
        
        adjusted_color = (
            int(star[4][0] * current_brightness),
            int(star[4][1] * current_brightness),
            int(star[4][2] * current_brightness)
        )
        pygame.draw.circle(temp_surface, adjusted_color, (int(star[0]), int(star[1])), int(star[2]))
    
    for i, star in enumerate(stars_mid[:mid_star_count]):
        star[0] -= star[5]
        star[7] += star[6]
        
        if star[0] < 0:
            star[0] = SCREEN_WIDTH
            star[1] = random.randint(0, SCREEN_HEIGHT - 50)
        
        twinkle_factor = 0.5 + 0.5 * math.sin(star[7])
        current_brightness = star[3] * twinkle_factor
        
        adjusted_color = (
            int(star[4][0] * current_brightness),
            int(star[4][1] * current_brightness),
            int(star[4][2] * current_brightness)
        )
        pygame.draw.circle(temp_surface, adjusted_color, (int(star[0]), int(star[1])), int(star[2]))
    
    for i, star in enumerate(stars_near[:near_star_count]):
        star[0] -= star[5]
        star[7] += star[6]
        
        if star[0] < 0:
            star[0] = SCREEN_WIDTH
            star[1] = random.randint(0, SCREEN_HEIGHT - 50)
        
        twinkle_factor = 0.5 + 0.5 * math.sin(star[7])
        current_brightness = star[3] * twinkle_factor
        
        adjusted_color = (
            int(star[4][0] * current_brightness),
            int(star[4][1] * current_brightness),
            int(star[4][2] * current_brightness)
        )
        pygame.draw.circle(temp_surface, adjusted_color, (int(star[0]), int(star[1])), int(star[2]))
    
    for star in stars_twinkle:
        star[5] += star[6]
        
        twinkle_factor = 0.5 + 0.5 * math.sin(star[5])
        current_brightness = star[3] * twinkle_factor
        
        adjusted_color = (
            int(star[4][0] * current_brightness),
            int(star[4][1] * current_brightness),
            int(star[4][2] * current_brightness)
        )
        pygame.draw.circle(temp_surface, adjusted_color, (int(star[0]), int(star[1])), int(star[2]))
    
    for planet in planets:
        planet[0] -= planet[4]
        if planet[0] < -planet[2]:
            planet[0] = SCREEN_WIDTH + planet[2]
            planet[1] = random.randint(50, SCREEN_HEIGHT - 150)
        
        pygame.draw.circle(temp_surface, planet[3], (int(planet[0]), int(planet[1])), planet[2])
        highlight_x = int(planet[0]) - planet[2] // 3
        highlight_y = int(planet[1]) - planet[2] // 3
        highlight_size = planet[2] // 4
        highlight_color = (
            min(255, planet[3][0] + 50),
            min(255, planet[3][1] + 50),
            min(255, planet[3][2] + 50)
        )
        pygame.draw.circle(temp_surface, highlight_color, (highlight_x, highlight_y), highlight_size)
    
    for shooting_star in shooting_stars:
        shooting_star[6] -= 1
        
        if shooting_star[6] <= 0 and not shooting_star[5]:
            shooting_star[5] = True
            shooting_star[0] = random.randint(0, SCREEN_WIDTH // 2)
            shooting_star[1] = random.randint(0, SCREEN_HEIGHT // 2)
        
        if shooting_star[5]:
            shooting_star[0] += math.cos(shooting_star[4]) * shooting_star[3]
            shooting_star[1] += math.sin(shooting_star[4]) * shooting_star[3]
            
            end_x = shooting_star[0] - math.cos(shooting_star[4]) * shooting_star[2]
            end_y = shooting_star[1] - math.sin(shooting_star[4]) * shooting_star[2]
            
            for i in range(int(shooting_star[2])):
                factor = i / shooting_star[2]
                alpha = int(255 * (1 - factor))
                color = (255, 255, 255, alpha)
                
                tail_x = shooting_star[0] - math.cos(shooting_star[4]) * i
                tail_y = shooting_star[1] - math.sin(shooting_star[4]) * i
                
                pygame.draw.circle(temp_surface, color, (int(tail_x), int(tail_y)), 2)
            
            pygame.draw.circle(temp_surface, WHITE, (int(shooting_star[0]), int(shooting_star[1])), 3)
            
            if (shooting_star[0] < 0 or shooting_star[0] > SCREEN_WIDTH or 
                shooting_star[1] < 0 or shooting_star[1] > SCREEN_HEIGHT - 50):
                shooting_star[5] = False
                shooting_star[6] = random.randint(100, 300)
    
    surface.blit(temp_surface, (screen_shake_offset_x, screen_shake_offset_y))
def draw_grass_ground(surface):
    pygame.draw.rect(surface, GRASS_GREEN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    
    for x in range(0, SCREEN_WIDTH, 2):
        blade_height = random.randint(5, 15)
        blade_x = x + random.randint(0, 1)
        pygame.draw.line(surface, DARK_GRASS_GREEN, 
                         (blade_x, SCREEN_HEIGHT - 50), 
                         (blade_x, SCREEN_HEIGHT - 50 - blade_height), 1)
    
    for _ in range(100):
        highlight_x = random.randint(0, SCREEN_WIDTH)
        highlight_y = random.randint(SCREEN_HEIGHT - 50, SCREEN_HEIGHT - 5)
        highlight_size = random.randint(1, 3)
        pygame.draw.circle(surface, LIGHT_GRASS_GREEN, 
                          (highlight_x, highlight_y), highlight_size)
def draw_weather_effects(surface):
    global weather_particles, weather_timer, weather_type
    
    if not graphics_settings['weather_effects']:
        return
    
    weather_timer += 1
    
    if weather_timer >= weather_duration:
        weather_timer = 0
        weather_types = ["clear", "rain", "snow", "wind"]
        weather_type = random.choice(weather_types)
        weather_particles = []
    
    if weather_type == "rain":
        for _ in range(3):
            x = random.randint(0, SCREEN_WIDTH)
            y = -10
            speed = random.uniform(5, 10)
            length = random.randint(5, 15)
            weather_particles.append([x, y, speed, length])
        
        for i in range(len(weather_particles) - 1, -1, -1):
            particle = weather_particles[i]
            particle[1] += particle[2]
            
            pygame.draw.line(surface, ICE_BLUE, 
                            (particle[0], particle[1]), 
                            (particle[0], particle[1] + particle[3]), 1)
            
            if particle[1] > SCREEN_HEIGHT:
                weather_particles.pop(i)
    
    elif weather_type == "snow":
        for _ in range(2):
            x = random.randint(0, SCREEN_WIDTH)
            y = -10
            speed = random.uniform(1, 3)
            size = random.randint(2, 5)
            drift = random.uniform(-1, 1)
            weather_particles.append([x, y, speed, size, drift])
        
        for i in range(len(weather_particles) - 1, -1, -1):
            particle = weather_particles[i]
            particle[1] += particle[2]
            particle[0] += particle[4]
            
            pygame.draw.circle(surface, WHITE, (int(particle[0]), int(particle[1])), particle[3])
            
            if particle[1] > SCREEN_HEIGHT:
                weather_particles.pop(i)
    
    elif weather_type == "wind":
        for _ in range(5):
            x = -10
            y = random.randint(0, SCREEN_HEIGHT - 50)
            speed = random.uniform(5, 15)
            length = random.randint(10, 30)
            weather_particles.append([x, y, speed, length])
        
        for i in range(len(weather_particles) - 1, -1, -1):
            particle = weather_particles[i]
            particle[0] += particle[2]
            
            pygame.draw.line(surface, (200, 200, 255, 100), 
                            (particle[0], particle[1]), 
                            (particle[0] + particle[3], particle[1]), 2)
            
            if particle[0] > SCREEN_WIDTH:
                weather_particles.pop(i)
def draw_minimap(surface, player_pos, enemies, powerups):
    if not graphics_settings['show_minimap']:
        return
    
    minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA)
    minimap_surface.fill((0, 0, 0, 180))
    
    pygame.draw.rect(minimap_surface, WHITE, (0, 0, MINIMAP_WIDTH, MINIMAP_HEIGHT), 2)
    
    player_x = int(player_pos[0] * 0.2)
    player_y = int(player_pos[1] * 0.2)
    
    player_x = max(0, min(player_x, MINIMAP_WIDTH - 1))
    player_y = max(0, min(player_y, MINIMAP_HEIGHT - 1))
    
    for y in range(max(0, player_y - exploration_radius), min(MINIMAP_HEIGHT, player_y + exploration_radius)):
        for x in range(max(0, player_x - exploration_radius), min(MINIMAP_WIDTH, player_x + exploration_radius)):
            distance = math.sqrt((x - player_x)**2 + (y - player_y)**2)
            if distance <= exploration_radius:
                minimap_explored[y][x] = True
    
    for y in range(MINIMAP_HEIGHT):
        for x in range(MINIMAP_WIDTH):
            if minimap_explored[y][x]:
                pygame.draw.rect(minimap_surface, (50, 50, 50, 100), (x, y, 1, 1))
    
    grid_spacing = 20
    for i in range(0, MINIMAP_WIDTH, grid_spacing):
        pygame.draw.line(minimap_surface, (100, 100, 100, 50), (i, 0), (i, MINIMAP_HEIGHT))
    for i in range(0, MINIMAP_HEIGHT, grid_spacing):
        pygame.draw.line(minimap_surface, (100, 100, 100, 50), (0, i), (MINIMAP_WIDTH, i))
    
    pygame.draw.circle(minimap_surface, GREEN, (player_x, player_y), MINIMAP_PLAYER_SIZE)
    
    if player.facing_right:
        pygame.draw.line(minimap_surface, GREEN, (player_x, player_y), (player_x + 8, player_y), 2)
    else:
        pygame.draw.line(minimap_surface, GREEN, (player_x, player_y), (player_x - 8, player_y), 2)
    
    for enemy in enemies:
        enemy_x = int(enemy.rect.centerx * 0.2)
        enemy_y = int(enemy.rect.centery * 0.2)
        
        enemy_x = max(0, min(enemy_x, MINIMAP_WIDTH - 1))
        enemy_y = max(0, min(enemy_y, MINIMAP_HEIGHT - 1))
        
        if minimap_explored[enemy_y][enemy_x]:
            if hasattr(enemy, 'enemy_type'):
                if enemy.enemy_type == "basic":
                    color = RED
                elif enemy.enemy_type == "ranged":
                    color = CYAN
                elif enemy.enemy_type == "tank":
                    color = DARK_RED
                elif enemy.enemy_type == "fast":
                    color = ORANGE
                elif enemy.enemy_type == "flying":
                    color = PURPLE
                else:
                    color = RED
            else:
                color = DARK_RED
                
            size = MINIMAP_BOSS_SIZE if hasattr(enemy, 'boss_type') else MINIMAP_ENEMY_SIZE
            pygame.draw.circle(minimap_surface, color, (enemy_x, enemy_y), size)
    
    for powerup in powerups:
        powerup_x = int(powerup.rect.centerx * 0.2)
        powerup_y = int(powerup.rect.centery * 0.2)
        
        powerup_x = max(0, min(powerup_x, MINIMAP_WIDTH - 1))
        powerup_y = max(0, min(powerup_y, MINIMAP_HEIGHT - 1))
        
        if minimap_explored[powerup_y][powerup_x]:
            if powerup.type == "health":
                color = RED
            elif powerup.type == "power":
                color = YELLOW
            elif powerup.type == "shield":
                color = CYAN
            elif powerup.type == "speed":
                color = GREEN
            elif powerup.type == "fire":
                color = FIRE_ORANGE
            elif powerup.type == "invincibility":
                color = GOLD
            else:
                color = YELLOW
                
            pygame.draw.circle(minimap_surface, color, (powerup_x, powerup_y), MINIMAP_POWERUP_SIZE)
    
    for hazard in hazards:
        hazard_x = int(hazard.rect.centerx * 0.2)
        hazard_y = int(hazard.rect.centery * 0.2)
        
        hazard_x = max(0, min(hazard_x, MINIMAP_WIDTH - 1))
        hazard_y = max(0, min(hazard_y, MINIMAP_HEIGHT - 1))
        
        if minimap_explored[hazard_y][hazard_x]:
            pygame.draw.circle(minimap_surface, GRAY, (hazard_x, hazard_y), MINIMAP_HAZARD_SIZE)
    
    for obj in destructible_object_group:
        obj_x = int(obj.rect.centerx * 0.2)
        obj_y = int(obj.rect.centery * 0.2)
        
        obj_x = max(0, min(obj_x, MINIMAP_WIDTH - 1))
        obj_y = max(0, min(obj_y, MINIMAP_HEIGHT - 1))
        
        if minimap_explored[obj_y][obj_x]:
            if obj.obj_type == "crate":
                color = (139, 69, 19)
            elif obj.obj_type == "barrel":
                color = (50, 50, 50)
            else:
                color = GRAY
                
            pygame.draw.rect(minimap_surface, color, (obj_x - 2, obj_y - 2, 4, 4))
    
    for ufo in ufo_entity_group:
        ufo_x = int(ufo.rect.centerx * 0.2)
        ufo_y = int(ufo.rect.centery * 0.2)
        
        ufo_x = max(0, min(ufo_x, MINIMAP_WIDTH - 1))
        ufo_y = max(0, min(ufo_y, MINIMAP_HEIGHT - 1))
        
        if minimap_explored[ufo_y][ufo_x]:
            pygame.draw.circle(minimap_surface, UFO_BLUE, (ufo_x, ufo_y), MINIMAP_UFO_SIZE)
    
    view_distance = 50
    view_angle = math.pi / 3
    
    if player.facing_right:
        start_angle = -view_angle / 2
    else:
        start_angle = math.pi - view_angle / 2
    
    points = [(player_x, player_y)]
    for i in range(5):
        angle = start_angle + (i / 4) * view_angle
        end_x = player_x + math.cos(angle) * view_distance
        end_y = player_y + math.sin(angle) * view_distance
        points.append((end_x, end_y))
    
    pygame.draw.polygon(minimap_surface, (0, 255, 0, 30), points)
    
    surface.blit(minimap_surface, (SCREEN_WIDTH - MINIMAP_WIDTH - 10, 10))
    
    minimap_title = small_font.render("MINIMAP", True, WHITE)
    surface.blit(minimap_title, (SCREEN_WIDTH - MINIMAP_WIDTH - 10, MINIMAP_HEIGHT + 15))
def trigger_screen_flash(color, duration=10):
    global screen_flash_color, screen_flash_duration
    screen_flash_color = color
    screen_flash_duration = duration
def draw_screen_flash(surface):
    global screen_flash_duration
    if screen_flash_duration > 0:
        flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        flash_surface.fill((*screen_flash_color, min(100, screen_flash_duration * 10)))
        surface.blit(flash_surface, (0, 0))
        screen_flash_duration -= 1
def draw_slow_motion_effect(surface):
    global slow_motion_active, slow_motion_timer
    if slow_motion_active:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((100, 100, 255, 30))
        surface.blit(overlay, (0, 0))
        
        slow_text = font.render("SLOW MOTION", True, WHITE)
        surface.blit(slow_text, (SCREEN_WIDTH//2 - slow_text.get_width()//2, 50))
        
        slow_motion_timer -= 1
        if slow_motion_timer <= 0:
            slow_motion_active = False
def draw_health_bar(surface, x, y, health_percentage, color=RED, width=100, height=10):
    pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))
    
    fill = (health_percentage / 100) * width
    pygame.draw.rect(surface, color, (x, y, fill, height))
    
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2)
    
    pygame.draw.rect(surface, (255, 255, 255, 100), (x, y, fill, height // 2))
def draw_energy_bar(surface, x, y, energy_percentage, color=BLUE, width=100, height=10):
    pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))
    
    fill = (energy_percentage / 100) * width
    for i in range(fill):
        color_value = int(255 * (i / fill))
        gradient_color = (color[0], color[1], min(255, color[2] + color_value))
        pygame.draw.rect(surface, gradient_color, (x + i, y, 1, height))
    
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2)
    
    if energy_percentage > 70:
        glow_surface = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*color, 50), (0, 0, width + 10, height + 10))
        surface.blit(glow_surface, (x - 5, y - 5))
def draw_button(surface, x, y, width, height, text, color, text_color=BLACK):
    for i in range(height):
        color_value = int(50 * (i / height))
        gradient_color = (min(255, color[0] + color_value), 
                          min(255, color[1] + color_value), 
                          min(255, color[2] + color_value))
        pygame.draw.line(surface, gradient_color, (x, y + i), (x + width, y + i))
    
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2)
    
    button_text = font.render(text, True, text_color)
    surface.blit(button_text, (x + width//2 - button_text.get_width()//2, 
                               y + height//2 - button_text.get_height()//2))
    
    return pygame.Rect(x, y, width, height)
def create_energy_particles(x, y, count=20):
    for _ in range(count):
        size = random.randint(2, 5)
        speed = random.uniform(1, 4)
        direction = random.uniform(0, 2 * math.pi)
        lifetime = random.randint(20, 40)
        
        particle_color = random.choice([GREEN, CYAN, YELLOW])
        particle = AdvancedParticle(x, y, particle_color, size, speed, direction, lifetime, "energy")
        particle_group.add(particle)
def create_fire_particles(x, y, count=30):
    for _ in range(count):
        size = random.randint(3, 8)
        speed = random.uniform(1, 5)
        direction = random.uniform(math.pi/4, 3*math.pi/4)
        lifetime = random.randint(15, 30)
        
        particle_color = random.choice([FIRE_ORANGE, FIRE_RED, YELLOW])
        particle = AdvancedParticle(x, y, particle_color, size, speed, direction, lifetime, "fire")
        particle_group.add(particle)
def create_smoke_particles(x, y, count=15):
    for _ in range(count):
        size = random.randint(5, 15)
        speed = random.uniform(0.5, 2)
        direction = random.uniform(math.pi/3, 2*math.pi/3)
        lifetime = random.randint(30, 60)
        
        particle = AdvancedParticle(x, y, (100, 100, 100), size, speed, direction, lifetime, "smoke")
        particle_group.add(particle)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.idle_image = create_krrish_idle_image()
        self.walk1_image = create_krrish_walk1_image()
        self.walk2_image = create_krrish_walk2_image()
        self.run1_image = create_krrish_run1_image()
        self.run2_image = create_krrish_run2_image()
        self.jump_image = create_krrish_jump_image()
        self.shoot_image = create_krrish_shoot_image()
        self.attack_image = create_krrish_attack_image()
        
        self.image = self.idle_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        
        self.animation_state = "idle"
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5
        self.facing_right = True
        
        self.vel_y = 0
        self.jumping = False
        self.double_jump_available = False
        self.shoot_cooldown = 0
        self.health = 100
        self.speed = 5
        self.max_health = 100
        self.bullet_damage = 10
        self.shield_active = False
        self.shield_timer = 0
        self.invincible = False
        self.invincible_timer = 0
        self.speed_boost = False
        self.speed_boost_timer = 0
        
        self.wall_sliding = False
        self.wall_jump_cooldown = 0
        self.dash_cooldown = 0
        self.dash_duration = 0
        self.dash_direction = (0, 0)
        
        self.regen_timer = 0
        self.regen_interval = 300
        self.damage_resistance = 0
        self.immunity_timer = 0
        self.immunity_duration = 120
        
        self.blast_type = "normal"
        self.blast_types = ["normal", "homing", "spread", "laser"]
        self.current_blast_index = 0
        
        self.color_scheme = "default"
        
    def update(self):
        keys = pygame.key.get_pressed()
        moving = False
        
        current_speed = self.speed
        if self.speed_boost:
            current_speed *= 1.5
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= current_speed
            self.facing_right = False
            moving = True
        if keys[pygame.K_RIGHT]:
            self.rect.x += current_speed
            self.facing_right = True
            moving = True
            
        self.wall_sliding = False
        if self.jumping and self.wall_jump_cooldown <= 0:
            if self.rect.left <= 0:
                self.wall_sliding = True
                self.facing_right = True
                if self.vel_y > 0:
                    self.vel_y *= 0.8
            elif self.rect.right >= SCREEN_WIDTH:
                self.wall_sliding = True
                self.facing_right = False
                if self.vel_y > 0:
                    self.vel_y *= 0.8
        
        if self.wall_jump_cooldown > 0:
            self.wall_jump_cooldown -= 1
            
        if self.dash_duration > 0:
            self.dash_duration -= 1
            self.rect.x += self.dash_direction[0] * 15
            self.rect.y += self.dash_direction[1] * 15
            
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > SCREEN_HEIGHT - 50:
                self.rect.bottom = SCREEN_HEIGHT - 50
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
            
        if keys[pygame.K_SPACE]:
            if not self.jumping:
                jump_height = 15
                if skill_trees["mobility"]["skills"]["jump"]["level"] > 0:
                    jump_height += 2 * skill_trees["mobility"]["skills"]["jump"]["level"]
                
                self.vel_y = -jump_height
                self.jumping = True
                if jump_sound:
                    jump_sound.play()
            elif self.double_jump_available and skill_trees["mobility"]["skills"]["double_jump"]["level"] > 0:
                self.vel_y = -12
                self.double_jump_available = False
                if jump_sound:
                    jump_sound.play()
            elif self.wall_sliding:
                self.vel_y = -12
                self.wall_jump_cooldown = 20
                self.jumping = True
                self.double_jump_available = True
                if wall_jump_sound:
                    wall_jump_sound.play()
            
        self.vel_y += 0.8
        self.rect.y += self.vel_y
        
        if self.rect.bottom > SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.vel_y = 0
            self.jumping = False
            self.double_jump_available = True
            
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
            
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        if self.speed_boost:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer <= 0:
                self.speed_boost = False
        
        if skill_trees["defense"]["skills"]["regeneration"]["level"] > 0:
            self.regen_timer += 1
            if self.regen_timer >= self.regen_interval:
                self.regen_timer = 0
                heal_amount = 5 * skill_trees["defense"]["skills"]["regeneration"]["level"]
                self.heal(heal_amount)
        
        if self.immunity_timer > 0:
            self.immunity_timer -= 1
            
        self.update_animation(moving)
        
    def update_animation(self, moving):
        if self.shoot_cooldown > 15:
            self.animation_state = "shooting"
            self.animation_frame = 0
        elif self.jumping:
            self.animation_state = "jumping"
            self.animation_frame = 0
        elif moving:
            if self.animation_state != "walking":
                self.animation_state = "walking"
                self.animation_frame = 0
        else:
            if self.animation_state != "idle":
                self.animation_state = "idle"
                self.animation_frame = 0
                
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            
            if self.animation_state == "walking":
                self.animation_frame = (self.animation_frame + 1) % 2
            elif self.animation_state == "shooting":
                if self.animation_frame == 0:
                    self.animation_frame = 1
                else:
                    self.animation_state = "idle"
                    self.animation_frame = 0
                    
        if self.animation_state == "idle":
            self.image = self.idle_image
        elif self.animation_state == "walking":
            if self.animation_frame == 0:
                self.image = self.walk1_image
            else:
                self.image = self.walk2_image
        elif self.animation_state == "jumping":
            self.image = self.jump_image
        elif self.animation_state == "shooting":
            self.image = self.shoot_image
            
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
            
    def shoot(self, direction):
        if self.shoot_cooldown == 0:
            if direction == "left":
                dx, dy = -1, 0
            elif direction == "right":
                dx, dy = 1, 0
            elif direction == "down":
                dx, dy = 0, 1
            elif direction == "up":
                dx, dy = 0, -1
            elif direction == "up-left":
                dx, dy = -1, -1
            elif direction == "up-right":
                dx, dy = 1, -1
            elif direction == "down-left":
                dx, dy = -1, 1
            elif direction == "down-right":
                dx, dy = 1, 1
            else:
                dx = 1 if self.facing_right else -1
                dy = 0
                
            length = math.sqrt(dx**2 + dy**2)
            if length > 0:
                dx /= length
                dy /= length
                
            if self.blast_type == "normal":
                multi_shot_level = skill_trees["combat"]["skills"]["multi_shot"]["level"]
                if multi_shot_level > 0:
                    num_shots = 1 + multi_shot_level
                    spread = 0.2
                    
                    for i in range(num_shots):
                        angle_offset = spread * (i - (num_shots - 1) / 2)
                        
                        new_dx = dx * math.cos(angle_offset) - dy * math.sin(angle_offset)
                        new_dy = dx * math.sin(angle_offset) + dy * math.cos(angle_offset)
                        
                        blast = EnergyBlast(self.rect.centerx, self.rect.centery, new_dx, new_dy, self.bullet_damage)
                        energy_blast_group.add(blast)
                        
                        create_energy_particles(self.rect.centerx, self.rect.centery, 5)
                else:
                    blast = EnergyBlast(self.rect.centerx, self.rect.centery, dx, dy, self.bullet_damage)
                    energy_blast_group.add(blast)
                    
                    create_energy_particles(self.rect.centerx, self.rect.centery, 10)
                    
            elif self.blast_type == "homing":
                target = None
                min_distance = float('inf')
                
                for enemy in enemy_group:
                    distance = math.sqrt((enemy.rect.centerx - self.rect.centerx)**2 + 
                                        (enemy.rect.centery - self.rect.centery)**2)
                    if distance < min_distance:
                        min_distance = distance
                        target = enemy
                
                missile = HomingMissile(self.rect.centerx, self.rect.centery, dx, dy, self.bullet_damage, target)
                energy_blast_group.add(missile)
                
                create_energy_particles(self.rect.centerx, self.rect.centery, 15)
                
            elif self.blast_type == "spread":
                num_shots = 5
                spread = 0.3
                
                for i in range(num_shots):
                    angle_offset = spread * (i - (num_shots - 1) / 2)
                    
                    new_dx = dx * math.cos(angle_offset) - dy * math.sin(angle_offset)
                    new_dy = dx * math.sin(angle_offset) + dy * math.cos(angle_offset)
                    
                    shot = SpreadShot(self.rect.centerx, self.rect.centery, new_dx, new_dy, self.bullet_damage, angle_offset)
                    energy_blast_group.add(shot)
                    
                    create_energy_particles(self.rect.centerx, self.rect.centery, 5)
                    
            elif self.blast_type == "laser":
                laser = LaserBeam(self.rect.centerx, self.rect.centery, dx, dy, self.bullet_damage * 1.5)
                energy_blast_group.add(laser)
                
                create_energy_particles(self.rect.centerx, self.rect.centery, 20)
                
                trigger_screen_flash((0, 255, 255), 5)
            
            base_cooldown = 20
            cooldown_reduction = (skill_trees["combat"]["skills"]["rapid_fire"]["level"] - 1) * 3
            self.shoot_cooldown = max(5, base_cooldown - cooldown_reduction)
            
            if shoot_sound:
                shoot_sound.play()
                
    def take_damage(self, amount):
        if self.invincible or self.immunity_timer > 0:
            return
        elif self.shield_active:
            shield_absorbed = min(amount, self.shield_timer // 10)
            self.shield_timer -= shield_absorbed * 10
            
            if shield_absorbed >= 10 and not achievements["perfect_shield"]["unlocked"]:
                achievements["perfect_shield"]["unlocked"] = True
                unlock_achievement("perfect_shield")
                
            if self.shield_timer <= 0:
                self.shield_active = False
                
            remaining_damage = amount - shield_absorbed
            if remaining_damage > 0:
                if skill_trees["defense"]["skills"]["resistance"]["level"] > 0:
                    resistance_percent = 0.1 * skill_trees["defense"]["skills"]["resistance"]["level"]
                    remaining_damage = int(remaining_damage * (1 - resistance_percent))
                
                self.health -= remaining_damage
                if self.health < 0:
                    self.health = 0
                
                trigger_screen_shake(5, 10)
                
                if skill_trees["defense"]["skills"]["immunity"]["level"] > 0:
                    self.immunity_timer = self.immunity_duration
        else:
            if skill_trees["defense"]["skills"]["resistance"]["level"] > 0:
                resistance_percent = 0.1 * skill_trees["defense"]["skills"]["resistance"]["level"]
                amount = int(amount * (1 - resistance_percent))
            
            self.health -= amount
            if self.health < 0:
                self.health = 0
            
            trigger_screen_shake(5, 10)
            
            if skill_trees["defense"]["skills"]["immunity"]["level"] > 0:
                self.immunity_timer = self.immunity_duration
                
        if damage_sound:
            damage_sound.play()
            
    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
            
    def activate_shield(self):
        if skill_trees["defense"]["skills"]["shield"]["level"] > 0:
            self.shield_active = True
            self.shield_timer = 300
            if shield_sound:
                shield_sound.play()
            
    def activate_invincibility(self, duration):
        self.invincible = True
        self.invincible_timer = duration
            
    def activate_speed_boost(self, duration):
        self.speed_boost = True
        self.speed_boost_timer = duration
            
    def switch_blast_type(self):
        self.current_blast_index = (self.current_blast_index + 1) % len(self.blast_types)
        self.blast_type = self.blast_types[self.current_blast_index]
        
        if powerup_sound:
            powerup_sound.play()
            
    def dash(self, direction):
        if self.dash_cooldown == 0 and skill_trees["mobility"]["skills"]["dash"]["level"] > 0:
            self.dash_cooldown = 120
            self.dash_duration = 10
            
            if direction == "left":
                self.dash_direction = (-1, 0)
            elif direction == "right":
                self.dash_direction = (1, 0)
            elif direction == "up":
                self.dash_direction = (0, -1)
            elif direction == "down":
                self.dash_direction = (0, 1)
            elif direction == "up-left":
                self.dash_direction = (-0.7, -0.7)
            elif direction == "up-right":
                self.dash_direction = (0.7, -0.7)
            elif direction == "down-left":
                self.dash_direction = (-0.7, 0.7)
            elif direction == "down-right":
                self.dash_direction = (0.7, 0.7)
            else:
                self.dash_direction = (1 if self.facing_right else -1, 0)
            
            if dash_sound:
                dash_sound.play()
                
    def change_color_scheme(self, scheme_name):
        if scheme_name in player_colors:
            self.color_scheme = scheme_name
            current_color_scheme = scheme_name
            
            self.idle_image = create_krrish_idle_image()
            self.walk1_image = create_krrish_walk1_image()
            self.walk2_image = create_krrish_walk2_image()
            self.run1_image = create_krrish_run1_image()
            self.run2_image = create_krrish_run2_image()
            self.jump_image = create_krrish_jump_image()
            self.shoot_image = create_krrish_shoot_image()
            self.attack_image = create_krrish_attack_image()
            
            if powerup_sound:
                powerup_sound.play()
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="basic"):
        super().__init__()
        self.enemy_type = enemy_type
        
        if enemy_type == "basic":
            self.image = create_basic_enemy_image()
            self.health = 10 + (level - 1) * 5
            self.speed = 1.5 + (level - 1) * 0.1
            self.damage = 10
            self.score_value = 10
            self.color = PURPLE
        elif enemy_type == "ranged":
            self.image = create_ranged_enemy_image()
            self.health = 15 + (level - 1) * 7
            self.speed = 1.0 + (level - 1) * 0.05
            self.damage = 15
            self.score_value = 20
            self.color = DARK_BLUE
            self.shoot_cooldown = 0
            self.shoot_interval = 120 - min(level * 5, 60)
        elif enemy_type == "tank":
            self.image = create_tank_enemy_image()
            self.health = 30 + (level - 1) * 10
            self.speed = 0.8 + (level - 1) * 0.03
            self.damage = 20
            self.score_value = 30
            self.color = DARK_RED
        elif enemy_type == "fast":
            self.image = create_fast_enemy_image()
            self.health = 5 + (level - 1) * 2
            self.speed = 3.0 + (level - 1) * 0.2
            self.damage = 5
            self.score_value = 15
            self.color = ORANGE
            
        if difficulty == DIFFICULTY_EASY:
            self.health = int(self.health * 0.8)
            self.speed *= 0.9
            self.damage = int(self.damage * 0.8)
        elif difficulty == DIFFICULTY_HARD:
            self.health = int(self.health * 1.5)
            self.speed *= 1.2
            self.damage = int(self.damage * 1.3)
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.max_health = self.health
        
        self.group_behavior = None
        self.group_leader = None
        self.formation_offset = (0, 0)
        self.tactic_timer = 0
        self.tactic_interval = 180
        
    def update(self, player_pos):
        self.tactic_timer += 1
        
        if self.tactic_timer >= self.tactic_interval and not self.group_behavior:
            nearby_enemies = []
            for enemy in enemy_group:
                if enemy != self and not enemy.group_behavior:
                    distance = math.sqrt((enemy.rect.centerx - self.rect.centerx)**2 + 
                                        (enemy.rect.centery - self.rect.centery)**2)
                    if distance < 200:
                        nearby_enemies.append(enemy)
            
            if len(nearby_enemies) >= 2:
                self.group_behavior = "formation"
                self.group_leader = self
                
                formation_types = ["line", "circle", "v"]
                formation = random.choice(formation_types)
                
                if formation == "line":
                    for i, enemy in enumerate(nearby_enemies[:3]):
                        enemy.group_behavior = "formation"
                        enemy.group_leader = self
                        enemy.formation_offset = ((i + 1) * 50, 0)
                elif formation == "circle":
                    for i, enemy in enumerate(nearby_enemies[:4]):
                        angle = (i / 4) * 2 * math.pi
                        radius = 80
                        enemy.group_behavior = "formation"
                        enemy.group_leader = self
                        enemy.formation_offset = (radius * math.cos(angle), radius * math.sin(angle))
                elif formation == "v":
                    for i, enemy in enumerate(nearby_enemies[:3]):
                        offset_x = (i + 1) * 40
                        offset_y = (i + 1) * 30
                        if i % 2 == 0:
                            offset_x = -offset_x
                        enemy.group_behavior = "formation"
                        enemy.group_leader = self
                        enemy.formation_offset = (offset_x, offset_y)
                
                self.tactic_timer = 0
        
        if self.group_behavior == "formation" and self.group_leader:
            target_x = self.group_leader.rect.centerx + self.formation_offset[0]
            target_y = self.group_leader.rect.centery + self.formation_offset[1]
            
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 5:
                dx /= distance
                dy /= distance
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed
            
            if self.group_leader == self:
                dx = player_pos[0] - self.rect.centerx
                dy = player_pos[1] - self.rect.centery
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0:
                    dx /= distance
                    dy /= distance
                    
                    self.rect.x += dx * self.speed
                    self.rect.y += dy * self.speed
                    
                    if self.enemy_type == "ranged":
                        self.shoot(player_pos)
                        self.shoot_cooldown = 0
        else:
            if self.enemy_type == "ranged":
                dx = player_pos[0] - self.rect.centerx
                dy = player_pos[1] - self.rect.centery
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 200:
                    if distance > 0:
                        dx /= distance
                        dy /= distance
                        self.rect.x += dx * self.speed
                        self.rect.y += dy * self.speed
                elif distance < 150:
                    if distance > 0:
                        dx /= distance
                        dy /= distance
                        self.rect.x -= dx * self.speed
                        self.rect.y -= dy * self.speed
                
                self.shoot_cooldown += 1
                if self.shoot_cooldown >= self.shoot_interval:
                    self.shoot(player_pos)
                    self.shoot_cooldown = 0
            else:
                dx = player_pos[0] - self.rect.centerx
                dy = player_pos[1] - self.rect.centery
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0:
                    dx /= distance
                    dy /= distance
                    
                    self.rect.x += dx * self.speed
                    self.rect.y += dy * self.speed
                    
            if self.group_leader and (self.group_leader not in enemy_group or 
                                      math.sqrt((self.rect.centerx - self.group_leader.rect.centerx)**2 + 
                                               (self.rect.centery - self.group_leader.rect.centery)**2) > 300):
                self.group_behavior = None
                self.group_leader = None
                
    def shoot(self, player_pos):
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            
            projectile = EnemyProjectile(self.rect.centerx, self.rect.centery, dx, dy, self.damage)
            enemy_projectile_group.add(projectile)
            
            if enemy_shoot_sound:
                enemy_shoot_sound.play()
            
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            create_enemy_particles(self.rect.centerx, self.rect.centery, self.color)
            self.kill()
            return True
        return False
class FlyingEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        
        pygame.draw.ellipse(self.image, (100, 100, 100), (5, 10, 30, 15))
        pygame.draw.ellipse(self.image, (150, 150, 150), (5, 10, 30, 15), 2)
        
        pygame.draw.circle(self.image, (50, 50, 50), (10, 10), 5)
        pygame.draw.circle(self.image, (50, 50, 50), (30, 10), 5)
        pygame.draw.circle(self.image, (50, 50, 50), (10, 25), 5)
        pygame.draw.circle(self.image, (50, 50, 50), (30, 25), 5)
        
        pygame.draw.circle(self.image, RED, (20, 17), 3)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.health = 20 + (level - 1) * 8
        self.speed = 2.0 + (level - 1) * 0.15
        self.damage = 15
        self.score_value = 25
        self.color = (100, 100, 100)
        self.max_health = self.health
        self.shoot_cooldown = 0
        self.shoot_interval = 150 - min(level * 5, 75)
        self.hover_offset = random.uniform(0, 2 * math.pi)
        self.hover_amplitude = random.uniform(5, 15)
        self.hover_speed = random.uniform(0.05, 0.1)
        self.base_y = y
        
        if difficulty == DIFFICULTY_EASY:
            self.health = int(self.health * 0.8)
            self.speed *= 0.9
            self.damage = int(self.damage * 0.8)
        elif difficulty == DIFFICULTY_HARD:
            self.health = int(self.health * 1.5)
            self.speed *= 1.2
            self.damage = int(self.damage * 1.3)
    
    def update(self, player_pos):
        self.hover_offset += self.hover_speed
        self.rect.y = self.base_y + math.sin(self.hover_offset) * self.hover_amplitude
        
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            
            self.rect.x += dx * self.speed
            
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
        
        self.shoot_cooldown += 1
        if self.shoot_cooldown >= self.shoot_interval:
            self.shoot(player_pos)
            self.shoot_cooldown = 0
    
    def shoot(self, player_pos):
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            
            projectile = EnemyProjectile(self.rect.centerx, self.rect.centery, dx, dy, self.damage)
            enemy_projectile_group.add(projectile)
            
            if enemy_shoot_sound:
                enemy_shoot_sound.play()
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            create_enemy_particles(self.rect.centerx, self.rect.centery, self.color)
            self.kill()
            return True
        return False
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_boss_image()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.health = 100 + (level - 1) * 20
        self.speed = 1.0 + (level - 1) * 0.05
        self.damage = 25 + (level - 1) * 5
        self.score_value = 100 * level
        self.color = DARK_RED
        self.max_health = self.health
        self.boss_type = True
        
        self.attack_pattern = 0
        self.attack_timer = 0
        self.attack_interval = 120
        self.movement_pattern = 0
        self.movement_timer = 0
        self.movement_interval = 180
        
        if difficulty == DIFFICULTY_EASY:
            self.health = int(self.health * 0.8)
            self.speed *= 0.9
            self.damage = int(self.damage * 0.8)
        elif difficulty == DIFFICULTY_HARD:
            self.health = int(self.health * 1.5)
            self.speed *= 1.2
            self.damage = int(self.damage * 1.3)
            
    def update(self, player_pos):
        self.attack_timer += 1
        if self.attack_timer >= self.attack_interval:
            self.attack_timer = 0
            self.attack_pattern = (self.attack_pattern + 1) % 3
            
            trigger_screen_shake(7, 15)
            
            if self.attack_pattern == 0:
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    dx = math.cos(rad)
                    dy = math.sin(rad)
                    projectile = EnemyProjectile(self.rect.centerx, self.rect.centery, dx, dy, self.damage)
                    enemy_projectile_group.add(projectile)
            elif self.attack_pattern == 1:
                dx = player_pos[0] - self.rect.centerx
                dy = player_pos[1] - self.rect.centery
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0:
                    dx /= distance
                    dy /= distance
                    
                    for offset in [-0.2, 0, 0.2]:
                        new_dx = dx * math.cos(offset) - dy * math.sin(offset)
                        new_dy = dx * math.sin(offset) + dy * math.cos(offset)
                        projectile = EnemyProjectile(self.rect.centerx, self.rect.centery, new_dx, new_dy, self.damage)
                        enemy_projectile_group.add(projectile)
            elif self.attack_pattern == 2:
                for i in range(12):
                    angle = (i / 12) * 2 * math.pi
                    dx = math.cos(angle)
                    dy = math.sin(angle)
                    projectile = EnemyProjectile(self.rect.centerx, self.rect.centery, dx, dy, self.damage)
                    enemy_projectile_group.add(projectile)
            
            if enemy_shoot_sound:
                enemy_shoot_sound.play()
        
        self.movement_timer += 1
        if self.movement_timer >= self.movement_interval:
            self.movement_timer = 0
            self.movement_pattern = (self.movement_pattern + 1) % 2
        
        if self.movement_pattern == 0:
            self.rect.x += self.speed
            if self.rect.left <= 100:
                self.speed *= -1
            elif self.rect.right >= SCREEN_WIDTH - 100:
                self.speed *= -1
        else:
            self.rect.y += self.speed
            if self.rect.top <= 100:
                self.speed *= -1
            elif self.rect.bottom >= SCREEN_HEIGHT - 150:
                self.speed *= -1
                
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            create_boss_explosion(self.rect.centerx, self.rect.centery)
            
            trigger_slow_motion(120)
            
            self.kill()
            return True
        return False
class EnergyBlast(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, damage):
        super().__init__()
        self.image = create_energy_blast_image()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dx = dx
        self.dy = dy
        self.speed = 10
        self.damage = damage
        self.piercing = skill_trees["combat"]["skills"]["piercing_shot"]["level"] > 0
        self.hit_enemies = []
        
    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()
class HomingMissile(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, damage, target):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 100, 0), (7, 7), 7)
        pygame.draw.circle(self.image, (255, 200, 0), (7, 7), 4)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dx = dx
        self.dy = dy
        self.speed = 7
        self.damage = damage
        self.target = target
        self.lifetime = 120
        self.piercing = skill_trees["combat"]["skills"]["piercing_shot"]["level"] > 0
        self.hit_enemies = []
        
    def update(self):
        if self.target and self.target.alive():
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                dx /= distance
                dy /= distance
                
                self.dx = self.dx * 0.9 + dx * 0.1
                self.dy = self.dy * 0.9 + dy * 0.1
                
                length = math.sqrt(self.dx**2 + self.dy**2)
                if length > 0:
                    self.dx /= length
                    self.dy /= length
        
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        
        self.lifetime -= 1
        if self.lifetime <= 0 or (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or 
                                  self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()
class SpreadShot(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, damage, spread_angle):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 255), (5, 5), 5)
        pygame.draw.circle(self.image, (255, 255, 255), (5, 5), 3)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        cos_angle = math.cos(spread_angle)
        sin_angle = math.sin(spread_angle)
        self.dx = dx * cos_angle - dy * sin_angle
        self.dy = dx * sin_angle + dy * cos_angle
        
        self.speed = 10
        self.damage = damage
        self.piercing = skill_trees["combat"]["skills"]["piercing_shot"]["level"] > 0
        self.hit_enemies = []
        
    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()
class LaserBeam(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, damage):
        super().__init__()
        self.image = pygame.Surface((40, 5), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 0, 255), (0, 0, 40, 5))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dx = dx
        self.dy = dy
        self.speed = 15
        self.damage = damage
        self.piercing = True
        self.hit_enemies = []
        
    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()
class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, damage):
        super().__init__()
        self.image = create_enemy_projectile_image()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dx = dx
        self.dy = dy
        self.speed = 5
        self.damage = damage
        
    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        
        if type == "health":
            pygame.draw.circle(self.image, RED, (10, 10), 10)
            pygame.draw.rect(self.image, WHITE, (8, 6, 4, 8))
            pygame.draw.rect(self.image, WHITE, (6, 8, 8, 4))
        elif type == "power":
            pygame.draw.circle(self.image, YELLOW, (10, 10), 10)
            pygame.draw.polygon(self.image, BLACK, [(10, 5), (15, 15), (5, 15)])
        elif type == "fire":
            self.image = create_fire_powerup_image()
        elif type == "shield":
            self.image = create_shield_powerup_image()
        elif type == "speed":
            self.image = create_speed_powerup_image()
        elif type == "invincibility":
            self.image = create_invincibility_powerup_image()
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 1
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
class UFOEntity(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = create_ufo_image()
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, 50)
        self.speed = 2
        self.direction = 1
        self.drop_timer = 0
        self.drop_interval = random.randint(180, 300)
        self.super_drop_timer = 0
        self.super_drop_interval = random.randint(600, 900)
        self.beam_active = False
        self.beam_timer = 0
        self.beam_y = 0
        
    def update(self):
        self.rect.x += self.speed * self.direction
        
        if self.rect.left <= 0:
            self.direction = 1
        elif self.rect.right >= SCREEN_WIDTH:
            self.direction = -1
            
        self.drop_timer += 1
        self.super_drop_timer += 1
        
        if self.beam_active:
            self.beam_timer -= 1
            self.beam_y += 5
            
            if self.beam_timer <= 0:
                self.beam_active = False
        
        if self.drop_timer >= self.drop_interval:
            self.drop_powerup()
            self.drop_timer = 0
            self.drop_interval = random.randint(180, 300)
            
        if self.super_drop_timer >= self.super_drop_interval:
            self.drop_super_power()
            self.super_drop_timer = 0
            self.super_drop_interval = random.randint(600, 900)
            
    def drop_powerup(self):
        self.beam_active = True
        self.beam_timer = 30
        self.beam_y = self.rect.bottom
        
        powerup_type = random.choice(["health", "power", "shield", "speed"])
        powerup = PowerUp(self.rect.centerx, self.rect.bottom, powerup_type)
        powerup_group.add(powerup)
        
    def drop_super_power(self):
        self.beam_active = True
        self.beam_timer = 30
        self.beam_y = self.rect.bottom
        
        powerup_types = ["fire", "invincibility"]
        powerup_type = random.choice(powerup_types)
        powerup = PowerUp(self.rect.centerx, self.rect.bottom, powerup_type)
        powerup_group.add(powerup)
    
    def draw_beam(self, surface):
        if self.beam_active:
            beam_width = 30
            beam_height = min(self.beam_y - self.rect.bottom, SCREEN_HEIGHT - self.rect.bottom - 50)
            
            beam_surface = pygame.Surface((beam_width, beam_height), pygame.SRCALPHA)
            
            for i in range(beam_height):
                alpha = 255 - int((i / beam_height) * 200)
                color = (*BEAM_BLUE, alpha)
                pygame.draw.line(beam_surface, color, (0, i), (beam_width, i))
            
            surface.blit(beam_surface, (self.rect.centerx - beam_width // 2, self.rect.bottom))
            
            glow_radius = min(40, self.beam_timer * 2)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            
            for r in range(glow_radius, 0, -1):
                alpha = int(150 * (r / glow_radius))
                color = (*LIGHT_BLUE, alpha)
                pygame.draw.circle(glow_surface, color, (glow_radius, glow_radius), r)
            
            surface.blit(glow_surface, (self.rect.centerx - glow_radius, self.beam_y - glow_radius))
class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, hazard_type="spike"):
        super().__init__()
        self.hazard_type = hazard_type
        
        if hazard_type == "spike":
            self.image = create_hazard_spike_image()
            self.damage = 20
        elif hazard_type == "pit":
            self.image = pygame.Surface((60, 20), pygame.SRCALPHA)
            pygame.draw.rect(self.image, BLACK, (0, 0, 60, 20))
            self.damage = 999
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
    def update(self):
        pass
class DestructibleObject(pygame.sprite.Sprite):
    def __init__(self, x, y, obj_type="crate"):
        super().__init__()
        self.obj_type = obj_type
        
        if obj_type == "crate":
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (139, 69, 19), (0, 0, 40, 40))
            pygame.draw.rect(self.image, (101, 67, 33), (0, 0, 40, 40), 2)
            pygame.draw.line(self.image, (101, 67, 33), (0, 20), (40, 20), 2)
            pygame.draw.line(self.image, (101, 67, 33), (20, 0), (20, 40), 2)
            self.health = 30
            self.drop_chance = 0.3
        elif obj_type == "barrel":
            self.image = pygame.Surface((30, 40), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (50, 50, 50), (5, 0, 20, 40))
            pygame.draw.rect(self.image, (30, 30, 30), (5, 0, 20, 40), 2)
            pygame.draw.line(self.image, (30, 30, 30), (5, 10), (25, 10), 2)
            pygame.draw.line(self.image, (30, 30, 30), (5, 20), (25, 20), 2)
            pygame.draw.line(self.image, (30, 30, 30), (5, 30), (25, 30), 2)
            self.health = 20
            self.drop_chance = 0.2
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.max_health = self.health
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            for _ in range(15):
                size = random.randint(2, 5)
                speed = random.uniform(1, 3)
                direction = random.uniform(0, 2 * math.pi)
                lifetime = random.randint(20, 40)
                
                particle_color = (139, 69, 19) if self.obj_type == "crate" else (50, 50, 50)
                particle = Particle(self.rect.centerx, self.rect.centery, 
                                  particle_color, size, speed, direction, lifetime)
                particle_group.add(particle)
            
            if random.random() < self.drop_chance:
                powerup_type = random.choice(["health", "power", "shield", "speed"])
                powerup = PowerUp(self.rect.centerx, self.rect.centery, powerup_type)
                powerup_group.add(powerup)
            
            self.kill()
            return True
        return False
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, size, speed, direction, lifetime):
        super().__init__()
        self.size = size
        self.color = color
        self.speed = speed
        self.direction = direction
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size, size), size)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
    def update(self):
        self.rect.x += math.cos(self.direction) * self.speed
        self.rect.y += math.sin(self.direction) * self.speed
        
        self.size = max(1, self.size * 0.95)
        
        self.lifetime -= 1
        
        if self.max_lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
        else:
            alpha = 255
        
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*self.color, alpha), (self.size, self.size), self.size)
        
        if self.lifetime <= 0:
            self.kill()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
energy_blast_group = pygame.sprite.Group()
enemy_projectile_group = pygame.sprite.Group()
powerup_group = pygame.sprite.Group()
ufo_entity_group = pygame.sprite.Group()
hazard_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()
destructible_object_group = pygame.sprite.Group()
player = Player()
player_group.add(player)
ufo_entity = UFOEntity()
ufo_entity_group.add(ufo_entity)
network_manager = NetworkManager()
def create_enemy_particles(x, y, color=PURPLE):
    num_particles = int(20 * graphics_settings['particle_density'])
    for _ in range(num_particles):
        size = random.randint(2, 6)
        speed = random.uniform(1, 4)
        direction = random.uniform(0, 2 * math.pi)
        lifetime = random.randint(20, 40)
        
        particle_color = (
            max(0, min(255, color[0] + random.randint(-30, 30))),
            max(0, min(255, color[1] + random.randint(-30, 30))),
            max(0, min(255, color[2] + random.randint(-30, 30)))
        )
        
        particle = Particle(x, y, particle_color, size, speed, direction, lifetime)
        particle_group.add(particle)
def create_boss_explosion(x, y):
    num_particles = int(100 * graphics_settings['particle_density'])
    for _ in range(num_particles):
        size = random.randint(5, 15)
        speed = random.uniform(2, 8)
        direction = random.uniform(0, 2 * math.pi)
        lifetime = random.randint(40, 80)
        
        particle_color = random.choice([FIRE_ORANGE, FIRE_RED, YELLOW, GOLD])
        particle = Particle(x, y, particle_color, size, speed, direction, lifetime)
        particle_group.add(particle)
    
    trigger_screen_shake(10, 30)
    
    if explosion_sound:
        explosion_sound.play()
def draw_fire_explosion(x, y):
    explosion_radius = 150
    for i in range(20):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, explosion_radius)
        size = random.randint(5, 15)
        speed_x = math.cos(angle) * distance / 10
        speed_y = math.sin(angle) * distance / 10
        
        particle_x = x + speed_x * 5
        particle_y = y + speed_y * 5
        particle_color = random.choice([FIRE_ORANGE, FIRE_RED, YELLOW])
        pygame.draw.circle(screen, particle_color, (int(particle_x), int(particle_y)), size)
def spawn_enemies():
    spawn_chance = max(1, 60 - level * 5)
    
    if random.randint(1, spawn_chance) == 1 and len(enemy_group) < 8 + level:
        if level < 3:
            enemy_types = ["basic"]
        elif level < 5:
            enemy_types = ["basic", "ranged"]
        elif level < 7:
            enemy_types = ["basic", "ranged", "fast", "flying"]
        else:
            enemy_types = ["basic", "ranged", "tank", "fast", "flying"]
            
        enemy_type = random.choice(enemy_types)
        
        side = random.randint(0, 3)
        if side == 0:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = -50
        elif side == 1:
            x = SCREEN_WIDTH + 50
            y = random.randint(50, SCREEN_HEIGHT - 150)
        elif side == 2:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = SCREEN_HEIGHT + 50
        else:
            x = -50
            y = random.randint(50, SCREEN_HEIGHT - 150)
        
        if enemy_type == "flying":
            y = random.randint(100, SCREEN_HEIGHT - 200)
            enemy = FlyingEnemy(x, y)
        else:
            enemy = Enemy(x, y, enemy_type)
        
        enemy_group.add(enemy)
def spawn_boss():
    global boss_active
    
    enemy_group.empty()
    
    boss = Boss(SCREEN_WIDTH // 2, 150)
    boss_group.add(boss)
    boss_active = True
    
    if background_music and boss_music:
        background_music.stop()
        boss_music.play(-1)
def spawn_powerup():
    if random.randint(1, 300) == 1:
        x = random.randint(20, SCREEN_WIDTH - 20)
        y = -20
        type = random.choice(["health", "power", "shield", "speed"])
        powerup = PowerUp(x, y, type)
        powerup_group.add(powerup)
def spawn_hazards():
    if level >= 3 and len(hazard_group) < 3 + level // 2:
        x = random.randint(60, SCREEN_WIDTH - 60)
        y = SCREEN_HEIGHT - 50
        hazard_type = "spike"
        hazard = Hazard(x, y, hazard_type)
        hazard_group.add(hazard)
def spawn_destructible_objects():
    if level >= 2 and len(destructible_object_group) < 5 + level:
        x = random.randint(60, SCREEN_WIDTH - 60)
        y = SCREEN_HEIGHT - 90
        obj_type = random.choice(["crate", "barrel"])
        obj = DestructibleObject(x, y, obj_type)
        destructible_object_group.add(obj)
def check_level_up():
    global level, enemies_defeated, enemies_per_level, boss_active
    
    if enemies_defeated >= enemies_per_level and not boss_active:
        level += 1
        enemies_defeated = 0
        enemies_per_level = 10 + level * 2
        
        if level % boss_level == 0:
            spawn_boss()
        else:
            if levelup_sound:
                levelup_sound.play()
            
            for _ in range(50):
                size = random.randint(3, 8)
                speed = random.uniform(2, 6)
                direction = random.uniform(0, 2 * math.pi)
                lifetime = random.randint(30, 60)
                
                particle_color = random.choice([YELLOW, GOLD, LIGHT_YELLOW])
                particle = Particle(player.rect.centerx, player.rect.centery, 
                                   particle_color, size, speed, direction, lifetime)
                particle_group.add(particle)
            
            if level >= 10 and not achievements["level_10"]["unlocked"]:
                achievements["level_10"]["unlocked"] = True
                unlock_achievement("level_10")
def update_combo():
    global combo_count, combo_timer
    
    if combo_timer > 0:
        combo_timer -= 1
    else:
        combo_count = 0
    
    if combo_count >= 10 and not achievements["combo_master"]["unlocked"]:
        achievements["combo_master"]["unlocked"] = True
        unlock_achievement("combo_master")
def increase_combo():
    global combo_count, combo_timer
    
    combo_count += 1
    combo_timer = combo_threshold
    
    if combo_count in [10, 20, 30]:
        trigger_slow_motion(60)
    
    if combo_count in [5, 10, 15, 20]:
        if combo_sound:
            combo_sound.play()
def apply_upgrades():
    if skill_trees["combat"]["skills"]["precision"]["level"] > 0:
        player.bullet_damage = 10 + (skill_trees["combat"]["skills"]["precision"]["level"] - 1) * 5
    
    if skill_trees["mobility"]["skills"]["speed"]["level"] > 0:
        player.speed = 5 + (skill_trees["mobility"]["skills"]["speed"]["level"] - 1) * 1
    
    if skill_trees["defense"]["skills"]["health"]["level"] > 0:
        player.max_health = 100 + (skill_trees["defense"]["skills"]["health"]["level"] - 1) * 20
        if player.health > player.max_health:
            player.health = player.max_health
def unlock_achievement(achievement_id):
    global new_achievement, achievement_timer
    
    achievement = achievements[achievement_id]
    new_achievement = achievement
    achievement_timer = 180
    
    global upgrade_points
    upgrade_points += 2
    
    if powerup_sound:
        powerup_sound.play()
def save_game():
    save_data = {
        "level": level,
        "score": score,
        "upgrade_points": upgrade_points,
        "upgrades": {key: value["level"] for key, value in upgrades.items()},
        "skill_trees": {
            tree_id: {skill_id: skill["level"] for skill_id, skill in tree["skills"].items()}
            for tree_id, tree in skill_trees.items()
        },
        "achievements": {key: value["unlocked"] for key, value in achievements.items()},
        "difficulty": difficulty,
        "color_scheme": player.color_scheme
    }
    
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(save_data, f)
        return True
    except:
        return False
def load_game():
    try:
        with open(SAVE_FILE, 'r') as f:
            save_data = json.load(f)
        
        global level, score, upgrade_points, difficulty
        
        level = save_data.get("level", 1)
        score = save_data.get("score", 0)
        upgrade_points = save_data.get("upgrade_points", 0)
        difficulty = save_data.get("difficulty", DIFFICULTY_NORMAL)
        
        loaded_upgrades = save_data.get("upgrades", {})
        for key, value in loaded_upgrades.items():
            if key in upgrades:
                upgrades[key]["level"] = value
        
        loaded_skill_trees = save_data.get("skill_trees", {})
        for tree_id, tree_data in loaded_skill_trees.items():
            if tree_id in skill_trees:
                for skill_id, skill_level in tree_data.items():
                    if skill_id in skill_trees[tree_id]["skills"]:
                        skill_trees[tree_id]["skills"][skill_id]["level"] = skill_level
        
        loaded_achievements = save_data.get("achievements", {})
        for key, value in loaded_achievements.items():
            if key in achievements:
                achievements[key]["unlocked"] = value
        
        player_color_scheme = save_data.get("color_scheme", "default")
        player.change_color_scheme(player_color_scheme)
        
        apply_upgrades()
        
        return True
    except:
        return False
def save_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            high_scores = json.load(f)
    except:
        high_scores = {"easy": [], "normal": [], "hard": []}
    
    difficulty_name = DIFFICULTY_NAMES[difficulty].lower()
    high_score_entry = {
        "score": score,
        "level": level,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    high_scores[difficulty_name].append(high_score_entry)
    high_scores[difficulty_name].sort(key=lambda x: x["score"], reverse=True)
    
    high_scores[difficulty_name] = high_scores[difficulty_name][:10]
    
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(high_scores, f)
        return True
    except:
        return False
def draw_start_screen():
    draw_space_background(screen)
    
    title_text = "Krrish4"
    title_surface = title_font.render(title_text, True, GRAY)
    
    shadow_surface = title_font.render(title_text, True, BLACK)
    screen.blit(shadow_surface, (SCREEN_WIDTH//2 - title_surface.get_width()//2 + 5, 100 + 5))
    
    screen.blit(title_surface, (SCREEN_WIDTH//2 - title_surface.get_width()//2, 100))
    
    button_width = 200
    button_height = 60
    button_spacing = 20
    start_y = SCREEN_HEIGHT//2 - 50
    
    play_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y, button_width, button_height)
    pygame.draw.rect(screen, YELLOW, play_button_rect)
    pygame.draw.rect(screen, BLACK, play_button_rect, 3)
    
    play_text = font.render("PLAY", True, BLACK)
    screen.blit(play_text, (play_button_rect.x + button_width//2 - play_text.get_width()//2, 
                           play_button_rect.y + button_height//2 - play_text.get_height()//2))
    
    multiplayer_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y + button_height + button_spacing, button_width, button_height)
    pygame.draw.rect(screen, CYAN, multiplayer_button_rect)
    pygame.draw.rect(screen, BLACK, multiplayer_button_rect, 3)
    
    multiplayer_text = font.render("MULTIPLAYER", True, BLACK)
    screen.blit(multiplayer_text, (multiplayer_button_rect.x + button_width//2 - multiplayer_text.get_width()//2, 
                                   multiplayer_button_rect.y + button_height//2 - multiplayer_text.get_height()//2))
    
    load_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y + 2*(button_height + button_spacing), button_width, button_height)
    pygame.draw.rect(screen, GREEN, load_button_rect)
    pygame.draw.rect(screen, BLACK, load_button_rect, 3)
    
    load_text = font.render("LOAD", True, BLACK)
    screen.blit(load_text, (load_button_rect.x + button_width//2 - load_text.get_width()//2, 
                           load_button_rect.y + button_height//2 - load_text.get_height()//2))
    
    high_scores_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y + 3*(button_height + button_spacing), button_width, button_height)
    pygame.draw.rect(screen, PURPLE, high_scores_button_rect)
    pygame.draw.rect(screen, BLACK, high_scores_button_rect, 3)
    
    high_scores_text = font.render("HIGH SCORES", True, WHITE)
    screen.blit(high_scores_text, (high_scores_button_rect.x + button_width//2 - high_scores_text.get_width()//2, 
                                   high_scores_button_rect.y + button_height//2 - high_scores_text.get_height()//2))
    
    settings_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y + 4*(button_height + button_spacing), button_width, button_height)
    pygame.draw.rect(screen, PURPLE, settings_button_rect)
    pygame.draw.rect(screen, BLACK, settings_button_rect, 3)
    
    settings_text = font.render("SETTINGS", True, WHITE)
    screen.blit(settings_text, (settings_button_rect.x + button_width//2 - settings_text.get_width()//2, 
                              settings_button_rect.y + button_height//2 - settings_text.get_height()//2))
    
    return play_button_rect, multiplayer_button_rect, load_button_rect, high_scores_button_rect, settings_button_rect
def draw_difficulty_select_screen():
    draw_space_background(screen)
    
    title_text = "Select Difficulty"
    title_surface = font.render(title_text, True, WHITE)
    screen.blit(title_surface, (SCREEN_WIDTH//2 - title_surface.get_width()//2, 100))
    
    button_width = 200
    button_height = 60
    button_spacing = 20
    start_y = SCREEN_HEIGHT//2 - 100
    
    easy_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y, button_width, button_height)
    pygame.draw.rect(screen, GREEN, easy_button_rect)
    pygame.draw.rect(screen, BLACK, easy_button_rect, 3)
    
    easy_text = font.render("EASY", True, BLACK)
    screen.blit(easy_text, (easy_button_rect.x + button_width//2 - easy_text.get_width()//2, 
                           easy_button_rect.y + button_height//2 - easy_text.get_height()//2))
    
    normal_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y + button_height + button_spacing, button_width, button_height)
    pygame.draw.rect(screen, YELLOW, normal_button_rect)
    pygame.draw.rect(screen, BLACK, normal_button_rect, 3)
    
    normal_text = font.render("NORMAL", True, BLACK)
    screen.blit(normal_text, (normal_button_rect.x + button_width//2 - normal_text.get_width()//2, 
                             normal_button_rect.y + button_height//2 - normal_text.get_height()//2))
    
    hard_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y + 2*(button_height + button_spacing), button_width, button_height)
    pygame.draw.rect(screen, RED, hard_button_rect)
    pygame.draw.rect(screen, BLACK, hard_button_rect, 3)
    
    hard_text = font.render("HARD", True, BLACK)
    screen.blit(hard_text, (hard_button_rect.x + button_width//2 - hard_text.get_width()//2, 
                           hard_button_rect.y + button_height//2 - hard_text.get_height()//2))
    
    back_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y + 3*(button_height + button_spacing), button_width, button_height)
    pygame.draw.rect(screen, GRAY, back_button_rect)
    pygame.draw.rect(screen, WHITE, back_button_rect, 3)
    
    back_text = font.render("BACK", True, WHITE)
    screen.blit(back_text, (back_button_rect.x + button_width//2 - back_text.get_width()//2, 
                           back_button_rect.y + button_height//2 - back_text.get_height()//2))
    
    return easy_button_rect, normal_button_rect, hard_button_rect, back_button_rect
def draw_network_lobby():
    draw_space_background(screen)
    
    title_text = "Multiplayer Lobby"
    title_surface = font.render(title_text, True, WHITE)
    screen.blit(title_surface, (SCREEN_WIDTH//2 - title_surface.get_width()//2, 50))
    
    y_offset = 120
    for player_id, player in network_manager.players.items():
        color = player.color
        name = player.name
        ready = getattr(player, 'ready', False)
        
        status = "Ready" if ready else "Not Ready"
        status_color = GREEN if ready else RED
        
        player_text = font.render(f"{name}: {status}", True, color)
        screen.blit(player_text, (SCREEN_WIDTH//2 - player_text.get_width()//2, y_offset))
        
        y_offset += 40
    
    instructions = [
        "Press ENTER when ready",
        "Press T to chat",
        "Press ESC to return to menu"
    ]
    
    y_offset = SCREEN_HEIGHT - 150
    for instruction in instructions:
        instruction_text = small_font.render(instruction, True, WHITE)
        screen.blit(instruction_text, (SCREEN_WIDTH//2 - instruction_text.get_width()//2, y_offset))
        y_offset += 25
    
    y_offset = SCREEN_HEIGHT - 250
    for message in chat_messages[-5:]:
        message_text = small_font.render(message, True, WHITE)
        screen.blit(message_text, (20, y_offset))
        y_offset += 20
    
    if chat_active:
        pygame.draw.rect(screen, GRAY, (20, SCREEN_HEIGHT - 30, 300, 25))
        pygame.draw.rect(screen, WHITE, (20, SCREEN_HEIGHT - 30, 300, 25), 2)
        
        input_text = small_font.render(chat_input, True, WHITE)
        screen.blit(input_text, (25, SCREEN_HEIGHT - 25))
    
    if len(network_manager.players) >= 2 and all(getattr(p, 'ready', False) for p in network_manager.players.values()):
        start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        pygame.draw.rect(screen, GREEN, start_button_rect)
        pygame.draw.rect(screen, BLACK, start_button_rect, 3)
        
        start_text = font.render("START GAME", True, BLACK)
        screen.blit(start_text, (start_button_rect.x + start_button_rect.width//2 - start_text.get_width()//2, 
                               start_button_rect.y + start_button_rect.height//2 - start_text.get_height()//2))
        
        return start_button_rect
    
    return None
def draw_network_connecting():
    draw_space_background(screen)
    
    title_text = "Connecting to Server..."
    title_surface = font.render(title_text, True, WHITE)
    screen.blit(title_surface, (SCREEN_WIDTH//2 - title_surface.get_width()//2, SCREEN_HEIGHT//2 - 50))
    
    ip_text = font.render(f"Server IP: {SERVER_IP}", True, WHITE)
    screen.blit(ip_text, (SCREEN_WIDTH//2 - ip_text.get_width()//2, SCREEN_HEIGHT//2))
    
    instructions = [
        "Press ESC to cancel",
        "Waiting for connection..."
    ]
    
    y_offset = SCREEN_HEIGHT//2 + 50
    for instruction in instructions:
        instruction_text = small_font.render(instruction, True, WHITE)
        screen.blit(instruction_text, (SCREEN_WIDTH//2 - instruction_text.get_width()//2, y_offset))
        y_offset += 25
def draw_pause_button():
    button_size = 40
    button_x = SCREEN_WIDTH - button_size - 10
    button_y = 10
    button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
    
    pygame.draw.rect(screen, GRAY, button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 2)
    
    bar_width = 6
    bar_height = 20
    bar1_x = button_x + button_size//3 - bar_width//2
    bar2_x = button_x + 2*button_size//3 - bar_width//2
    bar_y = button_y + button_size//2 - bar_height//2
    
    pygame.draw.rect(screen, WHITE, (bar1_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, WHITE, (bar2_x, bar_y, bar_width, bar_height))
    
    return button_rect
def draw_pause_menu():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(TRANSPARENT_BLACK)
    screen.blit(overlay, (0, 0))
    
    menu_width = 300
    menu_height = 300
    menu_x = SCREEN_WIDTH//2 - menu_width//2
    menu_y = SCREEN_HEIGHT//2 - menu_height//2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    
    pygame.draw.rect(screen, GRAY, menu_rect)
    pygame.draw.rect(screen, WHITE, menu_rect, 3)
    
    pause_text = title_font.render("PAUSED", True, WHITE)
    screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, menu_y + 20))
    
    button_width = 200
    button_height = 50
    button_spacing = 20
    start_y = menu_y + 100
    
    resume_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y, button_width, button_height)
    pygame.draw.rect(screen, GREEN, resume_rect)
    pygame.draw.rect(screen, WHITE, resume_rect, 2)
    resume_text = font.render("RESUME", True, BLACK)
    screen.blit(resume_text, (resume_rect.x + button_width//2 - resume_text.get_width()//2, 
                             resume_rect.y + button_height//2 - resume_text.get_height()//2))
    
    save_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y + button_height + button_spacing, button_width, button_height)
    pygame.draw.rect(screen, YELLOW, save_rect)
    pygame.draw.rect(screen, WHITE, save_rect, 2)
    save_text = font.render("SAVE", True, BLACK)
    screen.blit(save_text, (save_rect.x + button_width//2 - save_text.get_width()//2, 
                           save_rect.y + button_height//2 - save_text.get_height()//2))
    
    restart_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y + 2*(button_height + button_spacing), button_width, button_height)
    pygame.draw.rect(screen, YELLOW, restart_rect)
    pygame.draw.rect(screen, WHITE, restart_rect, 2)
    restart_text = font.render("RESTART", True, BLACK)
    screen.blit(restart_text, (restart_rect.x + button_width//2 - restart_text.get_width()//2, 
                             restart_rect.y + button_height//2 - restart_text.get_height()//2))
    
    menu_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, start_y + 3*(button_height + button_spacing), button_width, button_height)
    pygame.draw.rect(screen, RED, menu_button_rect)
    pygame.draw.rect(screen, WHITE, menu_button_rect, 2)
    menu_button_text = font.render("MAIN MENU", True, WHITE)
    screen.blit(menu_button_text, (menu_button_rect.x + menu_button_rect.width//2 - menu_button_text.get_width()//2, 
                                  menu_button_rect.y + menu_button_rect.height//2 - menu_button_text.get_height()//2))
    
    return resume_rect, save_rect, restart_rect, menu_button_rect
def draw_upgrade_menu():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(TRANSPARENT_BLACK)
    screen.blit(overlay, (0, 0))
    
    menu_width = 700
    menu_height = 600
    menu_x = SCREEN_WIDTH//2 - menu_width//2
    menu_y = SCREEN_HEIGHT//2 - menu_height//2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    
    pygame.draw.rect(screen, GRAY, menu_rect)
    pygame.draw.rect(screen, WHITE, menu_rect, 3)
    
    title_text = font.render("SKILL TREES", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, menu_y + 20))
    
    points_text = font.render(f"Skill Points: {upgrade_points}", True, YELLOW)
    screen.blit(points_text, (SCREEN_WIDTH//2 - points_text.get_width()//2, menu_y + 80))
    
    tree_width = menu_width - 100
    tree_height = 400
    tree_y = menu_y + 120
    
    tab_width = tree_width // 3
    tab_rects = []
    
    tabs = [
        ("all", "All Quests"),
        ("active", "Active"),
        ("completed", "Completed")
    ]
    
    for i, (tree_id, tree) in enumerate(skill_trees.items()):
        tab_x = menu_x + 50 + i * tab_width
        tab_rect = pygame.Rect(tab_x, tree_y - 30, tab_width - 10, 30)
        tab_rects.append((tab_rect, tree_id))
        
        if tree_id == "combat":
            tab_color = DARK_BLUE
        elif tree_id == "mobility":
            tab_color = DARK_GREEN
        else:
            tab_color = DARK_RED
            
        pygame.draw.rect(screen, tab_color, tab_rect)
        pygame.draw.rect(screen, WHITE, tab_rect, 2)
        
        tab_text = small_font.render(tree["name"], True, WHITE)
        screen.blit(tab_text, (tab_rect.x + tab_rect.width//2 - tab_text.get_width()//2, 
                               tab_rect.y + tab_rect.height//2 - tab_text.get_height()//2))
    
    skill_rects = []
    for i, (tree_id, tree) in enumerate(skill_trees.items()):
        desc_text = small_font.render(tree["description"], True, WHITE)
        screen.blit(desc_text, (menu_x + 50 + i * tab_width, tree_y))
        
        for j, (skill_id, skill) in enumerate(tree["skills"].items()):
            skill_x = menu_x + 50 + i * tab_width + 20
            skill_y = tree_y + 40 + j * 60
            
            skill_rect = pygame.Rect(skill_x, skill_y, tab_width - 50, 50)
            
            if skill["level"] >= skill["max"]:
                box_color = DARK_BLUE
            elif skill["level"] > 0:
                box_color = BLUE
            elif skill["requires"] is None or skill_trees[tree_id]["skills"][skill["requires"]]["level"] > 0:
                if upgrade_points >= skill["cost"]:
                    box_color = GREEN
                else:
                    box_color = GRAY
            else:
                box_color = DARK_GRAY
            
            pygame.draw.rect(screen, box_color, skill_rect)
            pygame.draw.rect(screen, WHITE, skill_rect, 2)
            
            skill_name = small_font.render(skill["name"], True, WHITE)
            skill_level = small_font.render(f"Lv.{skill['level']}/{skill['max']}", True, WHITE)
            skill_cost = small_font.render(f"Cost: {skill['cost']}", True, WHITE)
            
            screen.blit(skill_name, (skill_rect.x + 10, skill_rect.y + 5))
            screen.blit(skill_level, (skill_rect.x + skill_rect.width - 50, skill_rect.y + 5))
            screen.blit(skill_cost, (skill_rect.x + 10, skill_rect.y + 25))
            
            desc_text = small_font.render(skill["description"], True, WHITE)
            screen.blit(desc_text, (skill_rect.x + 10, skill_rect.y + 40))
            
            if skill["requires"] and skill["level"] == 0:
                req_text = small_font.render(f"Requires: {skill_trees[tree_id]['skills'][skill['requires']]['name']}", True, RED)
                screen.blit(req_text, (skill_rect.x + 10, skill_rect.y + 55))
            
            skill_rects.append((skill_rect, tree_id, skill_id))
    
    continue_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, menu_y + menu_height - 60, 200, 40)
    pygame.draw.rect(screen, YELLOW, continue_rect)
    pygame.draw.rect(screen, WHITE, continue_rect, 2)
    continue_text = font.render("CONTINUE", True, BLACK)
    screen.blit(continue_text, (continue_rect.x + continue_rect.width//2 - continue_text.get_width()//2, 
                                continue_rect.y + continue_rect.height//2 - continue_text.get_height()//2))
    
    return skill_rects, continue_rect
def draw_customization_menu():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(TRANSPARENT_BLACK)
    screen.blit(overlay, (0, 0))
    
    menu_width = 600
    menu_height = 500
    menu_x = SCREEN_WIDTH//2 - menu_width//2
    menu_y = SCREEN_HEIGHT//2 - menu_height//2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    
    pygame.draw.rect(screen, GRAY, menu_rect)
    pygame.draw.rect(screen, WHITE, menu_rect, 3)
    
    title_text = font.render("CHARACTER CUSTOMIZATION", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, menu_y + 20))
    
    color_rects = []
    options_per_row = 3
    option_width = 150
    option_height = 150
    option_spacing = 20
    start_x = menu_x + (menu_width - (options_per_row * option_width + (options_per_row - 1) * option_spacing)) // 2
    start_y = menu_y + 100
    
    for i, (scheme_name, colors) in enumerate(player_colors.items()):
        row = i // options_per_row
        col = i % options_per_row
        
        x = start_x + col * (option_width + option_spacing)
        y = start_y + row * (option_height + option_spacing)
        
        option_rect = pygame.Rect(x, y, option_width, option_height)
        
        if scheme_name == player.color_scheme:
            pygame.draw.rect(screen, YELLOW, option_rect, 3)
        else:
            pygame.draw.rect(screen, WHITE, option_rect, 2)
        
        preview_surf = pygame.Surface((40, 60), pygame.SRCALPHA)
        
        pygame.draw.rect(preview_surf, colors["coat"], (10, 20, 20, 30))
        pygame.draw.polygon(preview_surf, colors["lining"], [(10, 20), (15, 25), (15, 45), (10, 50)])
        pygame.draw.rect(preview_surf, colors["boots"], (10, 50, 8, 10))
        pygame.draw.circle(preview_surf, (255, 220, 177), (20, 15), 8)
        pygame.draw.ellipse(preview_surf, colors["mask"], (12, 12, 16, 6))
        
        preview_surf = pygame.transform.scale(preview_surf, (30, 45))
        
        screen.blit(preview_surf, (x + option_width//2 - 15, y + 20))
        
        name_text = small_font.render(scheme_name.capitalize(), True, WHITE)
        screen.blit(name_text, (x + option_width//2 - name_text.get_width()//2, y + 80))
        
        color_rects.append((option_rect, scheme_name))
    
    back_rect = pygame.Rect(SCREEN_WIDTH//2 - 50, menu_y + menu_height - 60, 100, 40)
    pygame.draw.rect(screen, YELLOW, back_rect)
    pygame.draw.rect(screen, WHITE, back_rect, 2)
    back_text = font.render("BACK", True, BLACK)
    screen.blit(back_text, (back_rect.x + back_rect.width//2 - back_text.get_width()//2, 
                           back_rect.y + back_rect.height//2 - back_text.get_height()//2))
    
    return color_rects, back_rect
def draw_graphics_settings_menu():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(TRANSPARENT_BLACK)
    screen.blit(overlay, (0, 0))
    
    menu_width = 600
    menu_height = 500
    menu_x = SCREEN_WIDTH//2 - menu_width//2
    menu_y = SCREEN_HEIGHT//2 - menu_height//2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    
    pygame.draw.rect(screen, GRAY, menu_rect)
    pygame.draw.rect(screen, WHITE, menu_rect, 3)
    
    title_text = font.render("GRAPHICS SETTINGS", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, menu_y + 20))
    
    option_rects = []
    y_offset = menu_y + 80
    
    particle_text = small_font.render(f"Particle Density: {int(graphics_settings['particle_density'] * 100)}%", True, WHITE)
    screen.blit(particle_text, (menu_x + 20, y_offset))
    
    particle_slider_rect = pygame.Rect(menu_x + 250, y_offset, 200, 20)
    pygame.draw.rect(screen, GRAY, particle_slider_rect)
    pygame.draw.rect(screen, WHITE, particle_slider_rect, 2)
    
    handle_x = menu_x + 250 + int(graphics_settings['particle_density'] * 200)
    pygame.draw.circle(screen, WHITE, (handle_x, y_offset + 10), 8)
    
    option_rects.append((particle_slider_rect, "particle_density"))
    
    y_offset += 40
    
    bg_text = small_font.render(f"Background Detail: {int(graphics_settings['background_detail'] * 100)}%", True, WHITE)
    screen.blit(bg_text, (menu_x + 20, y_offset))
    
    bg_slider_rect = pygame.Rect(menu_x + 250, y_offset, 200, 20)
    pygame.draw.rect(screen, GRAY, bg_slider_rect)
    pygame.draw.rect(screen, WHITE, bg_slider_rect, 2)
    
    handle_x = menu_x + 250 + int(graphics_settings['background_detail'] * 200)
    pygame.draw.circle(screen, WHITE, (handle_x, y_offset + 10), 8)
    
    option_rects.append((bg_slider_rect, "background_detail"))
    
    y_offset += 40
    
    weather_text = small_font.render("Weather Effects", True, WHITE)
    screen.blit(weather_text, (menu_x + 20, y_offset))
    
    weather_toggle_rect = pygame.Rect(menu_x + 250, y_offset, 60, 20)
    pygame.draw.rect(screen, GREEN if graphics_settings['weather_effects'] else RED, weather_toggle_rect)
    pygame.draw.rect(screen, WHITE, weather_toggle_rect, 2)
    
    toggle_text = small_font.render("ON" if graphics_settings['weather_effects'] else "OFF", True, WHITE)
    screen.blit(toggle_text, (weather_toggle_rect.x + weather_toggle_rect.width//2 - toggle_text.get_width()//2, 
                             weather_toggle_rect.y + weather_toggle_rect.height//2 - toggle_text.get_height()//2))
    
    option_rects.append((weather_toggle_rect, "weather_effects"))
    
    y_offset += 40
    
    shake_text = small_font.render("Screen Shake", True, WHITE)
    screen.blit(shake_text, (menu_x + 20, y_offset))
    
    shake_toggle_rect = pygame.Rect(menu_x + 250, y_offset, 60, 20)
    pygame.draw.rect(screen, GREEN if graphics_settings['screen_shake'] else RED, shake_toggle_rect)
    pygame.draw.rect(screen, WHITE, shake_toggle_rect, 2)
    
    toggle_text = small_font.render("ON" if graphics_settings['screen_shake'] else "OFF", True, WHITE)
    screen.blit(toggle_text, (shake_toggle_rect.x + shake_toggle_rect.width//2 - toggle_text.get_width()//2, 
                             shake_toggle_rect.y + shake_toggle_rect.height//2 - toggle_text.get_height()//2))
    
    option_rects.append((shake_toggle_rect, "screen_shake"))
    
    y_offset += 40
    
    slow_text = small_font.render("Slow Motion Effects", True, WHITE)
    screen.blit(slow_text, (menu_x + 20, y_offset))
    
    slow_toggle_rect = pygame.Rect(menu_x + 250, y_offset, 60, 20)
    pygame.draw.rect(screen, GREEN if graphics_settings['slow_motion_effects'] else RED, slow_toggle_rect)
    pygame.draw.rect(screen, WHITE, slow_toggle_rect, 2)
    
    toggle_text = small_font.render("ON" if graphics_settings['slow_motion_effects'] else "OFF", True, WHITE)
    screen.blit(toggle_text, (slow_toggle_rect.x + slow_toggle_rect.width//2 - toggle_text.get_width()//2, 
                             slow_toggle_rect.y + slow_toggle_rect.height//2 - toggle_text.get_height()//2))
    
    option_rects.append((slow_toggle_rect, "slow_motion_effects"))
    
    y_offset += 40
    
    minimap_text = small_font.render("Show Minimap", True, WHITE)
    screen.blit(minimap_text, (menu_x + 20, y_offset))
    
    minimap_toggle_rect = pygame.Rect(menu_x + 250, y_offset, 60, 20)
    pygame.draw.rect(screen, GREEN if graphics_settings['show_minimap'] else RED, minimap_toggle_rect)
    pygame.draw.rect(screen, WHITE, minimap_toggle_rect, 2)
    
    toggle_text = small_font.render("ON" if graphics_settings['show_minimap'] else "OFF", True, WHITE)
    screen.blit(toggle_text, (minimap_toggle_rect.x + minimap_toggle_rect.width//2 - toggle_text.get_width()//2, 
                             minimap_toggle_rect.y + minimap_toggle_rect.height//2 - toggle_text.get_height()//2))
    
    option_rects.append((minimap_toggle_rect, "show_minimap"))
    
    preset_y = menu_y + menu_height - 120
    
    low_button_rect = pygame.Rect(menu_x + 50, preset_y, 100, 40)
    pygame.draw.rect(screen, RED, low_button_rect)
    pygame.draw.rect(screen, WHITE, low_button_rect, 2)
    low_text = font.render("LOW", True, WHITE)
    screen.blit(low_text, (low_button_rect.x + low_button_rect.width//2 - low_text.get_width()//2, 
                          low_button_rect.y + low_button_rect.height//2 - low_text.get_height()//2))
    
    med_button_rect = pygame.Rect(menu_x + 200, preset_y, 100, 40)
    pygame.draw.rect(screen, YELLOW, med_button_rect)
    pygame.draw.rect(screen, WHITE, med_button_rect, 2)
    med_text = font.render("MEDIUM", True, BLACK)
    screen.blit(med_text, (med_button_rect.x + med_button_rect.width//2 - med_text.get_width()//2, 
                          med_button_rect.y + med_button_rect.height//2 - med_text.get_height()//2))
    
    high_button_rect = pygame.Rect(menu_x + 350, preset_y, 100, 40)
    pygame.draw.rect(screen, GREEN, high_button_rect)
    pygame.draw.rect(screen, WHITE, high_button_rect, 2)
    high_text = font.render("HIGH", True, BLACK)
    screen.blit(high_text, (high_button_rect.x + high_button_rect.width//2 - high_text.get_width()//2, 
                           high_button_rect.y + high_button_rect.height//2 - high_text.get_height()//2))
    
    preset_rects = [(low_button_rect, "low"), (med_button_rect, "medium"), (high_button_rect, "high")]
    
    back_rect = pygame.Rect(SCREEN_WIDTH//2 - 50, menu_y + menu_height - 60, 100, 40)
    pygame.draw.rect(screen, YELLOW, back_rect)
    pygame.draw.rect(screen, WHITE, back_rect, 2)
    back_text = font.render("BACK", True, BLACK)
    screen.blit(back_text, (back_rect.x + back_rect.width//2 - back_text.get_width()//2, 
                           back_rect.y + back_rect.height//2 - back_text.get_height()//2))
    
    return option_rects, preset_rects, back_rect
def draw_high_scores_screen():
    draw_space_background(screen)
    
    title_text = "HIGH SCORES"
    title_surface = title_font.render(title_text, True, WHITE)
    screen.blit(title_surface, (SCREEN_WIDTH//2 - title_surface.get_width()//2, 50))
    
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            high_scores = json.load(f)
    except:
        high_scores = {"easy": [], "normal": [], "hard": []}
    
    difficulties = ["easy", "normal", "hard"]
    difficulty_colors = [GREEN, YELLOW, RED]
    
    for i, diff in enumerate(difficulties):
        diff_text = font.render(f"{DIFFICULTY_NAMES[i].upper()}", True, difficulty_colors[i])
        screen.blit(diff_text, (150, 150 + i * 150))
        
        scores = high_scores.get(diff, [])[:5]
        for j, score_entry in enumerate(scores):
            score_text = small_font.render(
                f"{j+1}. Score: {score_entry['score']} - Level: {score_entry['level']} - {score_entry['date']}", 
                True, WHITE
            )
            screen.blit(score_text, (150, 190 + i * 150 + j * 25))
    
    button_width = 200
    button_height = 50
    back_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, SCREEN_HEIGHT - 100, button_width, button_height)
    pygame.draw.rect(screen, GRAY, back_button_rect)
    pygame.draw.rect(screen, WHITE, back_button_rect, 2)
    
    back_text = font.render("BACK", True, WHITE)
    screen.blit(back_text, (back_button_rect.x + button_width//2 - back_text.get_width()//2, 
                           back_button_rect.y + button_height//2 - back_text.get_height()//2))
    
    return back_button_rect
def draw_quest_journal():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(TRANSPARENT_BLACK)
    screen.blit(overlay, (0, 0))
    
    menu_width = 600
    menu_height = 600
    menu_x = SCREEN_WIDTH//2 - menu_width//2
    menu_y = SCREEN_HEIGHT//2 - menu_height//2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    
    pygame.draw.rect(screen, GRAY, menu_rect)
    pygame.draw.rect(screen, WHITE, menu_rect, 3)
    
    title_text = font.render("QUEST JOURNAL", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, menu_y + 20))
    
    active_tab = "all"
    tab_rects = []
    
    tabs = [
        ("all", "All Quests"),
        ("active", "Active"),
        ("completed", "Completed")
    ]
    
    tab_width = menu_width // 3
    for i, (tab_id, tab_name) in enumerate(tabs):
        tab_x = menu_x + i * tab_width
        tab_rect = pygame.Rect(tab_x, menu_y + 60, tab_width - 10, 30)
        tab_rects.append((tab_rect, tab_id))
        
        pygame.draw.rect(screen, DARK_BLUE if tab_id == active_tab else GRAY, tab_rect)
        pygame.draw.rect(screen, WHITE, tab_rect, 2)
        
        tab_text = small_font.render(tab_name, True, WHITE)
        screen.blit(tab_text, (tab_rect.x + tab_rect.width//2 - tab_text.get_width()//2, 
                               tab_rect.y + tab_rect.height//2 - tab_text.get_height()//2))
    
    y_offset = menu_y + 110
    quests_to_show = []
    
    if active_tab == "all":
        quests_to_show = side_quests
    elif active_tab == "active":
        quests_to_show = [q for q in side_quests if q.active and not q.completed]
    elif active_tab == "completed":
        quests_to_show = [q for q in side_quests if q.completed]
    
    for quest in quests_to_show:
        quest_color = GREEN if quest.completed else YELLOW if quest.active else WHITE
        name_text = small_font.render(quest.name, True, quest_color)
        screen.blit(name_text, (menu_x + 20, y_offset))
        
        desc_text = small_font.render(quest.description, True, WHITE)
        screen.blit(desc_text, (menu_x + 20, y_offset + 20))
        
        if quest.active and not quest.completed:
            progress_text = small_font.render(f"Progress: {quest.current_count}/{quest.target_count}", True, WHITE)
            screen.blit(progress_text, (menu_x + 20, y_offset + 40))
            
            BAR_LENGTH = 200
            BAR_HEIGHT = 8
            progress = min(1.0, quest.current_count / quest.target_count)
            fill = int(progress * BAR_LENGTH)
            outline_rect = pygame.Rect(menu_x + 20, y_offset + 60, BAR_LENGTH, BAR_HEIGHT)
            fill_rect = pygame.Rect(menu_x + 20, y_offset + 60, fill, BAR_HEIGHT)
            pygame.draw.rect(screen, GREEN, fill_rect)
            pygame.draw.rect(screen, WHITE, outline_rect, 2)
        elif quest.completed:
            status_text = small_font.render("COMPLETED", True, GREEN)
            screen.blit(status_text, (menu_x + 20, y_offset + 40))
            
            reward_text = small_font.render(f"Reward: {quest.reward_score} Score, {quest.reward_upgrades} Upgrades", True, YELLOW)
            screen.blit(reward_text, (menu_x + 20, y_offset + 60))
        
        y_offset += 90
    
    close_rect = pygame.Rect(SCREEN_WIDTH//2 - 50, menu_y + menu_height - 60, 100, 40)
    pygame.draw.rect(screen, RED, close_rect)
    pygame.draw.rect(screen, WHITE, close_rect, 2)
    close_text = font.render("CLOSE", True, WHITE)
    screen.blit(close_text, (close_rect.x + close_rect.width//2 - close_text.get_width()//2, 
                            close_rect.y + close_rect.height//2 - close_text.get_height()//2))
    
    return close_rect, tab_rects
def complete_quest():
    global active_quest, quest_completed, quest_timer, score, upgrade_points
    
    if active_quest and not active_quest.completed:
        active_quest.completed = True
        quest_completed = True
        quest_timer = 180
        
        score += active_quest.reward_score
        upgrade_points += active_quest.reward_upgrades
        upgrades_available += active_quest.reward_upgrades
        
        if levelup_sound:
            levelup_sound.play()
        
        active_quest = None
def trigger_screen_shake(intensity, duration):
    if graphics_settings['screen_shake']:
        global screen_shake_intensity, screen_shake_duration
        screen_shake_intensity = intensity
        screen_shake_duration = duration
def trigger_slow_motion(duration):
    if graphics_settings['slow_motion_effects']:
        global slow_motion_active, slow_motion_duration, slow_motion_timer
        slow_motion_active = True
        slow_motion_duration = duration
        slow_motion_timer = duration
def reset_game():
    global score, game_over, level, enemies_defeated, enemies_per_level, upgrade_points, upgrades_available
    global boss_active, combo_count, combo_timer, hazards, weather_particles, weather_type, weather_timer
    global day_night_timer, is_day, active_quest, quest_completed, quest_timer
    
    score = 0
    game_over = False
    level = 1
    enemies_defeated = 0
    enemies_per_level = 10
    upgrade_points = 0
    upgrades_available = 0
    boss_active = False
    combo_count = 0
    combo_timer = 0
    
    weather_particles = []
    weather_type = "clear"
    weather_timer = 0
    
    day_night_timer = 0
    is_day = True
    
    hazards = []
    hazard_group.empty()
    
    active_quest = None
    quest_completed = False
    quest_timer = 0
    initialize_quests()
    
    for key in upgrades:
        upgrades[key]["level"] = 1 if key != "double_jump" and key != "shield" and key != "multi_shot" and key != "piercing" else 0
    
    for tree_id, tree in skill_trees.items():
        for skill_id, skill in tree["skills"].items():
            skill["level"] = 0
    
    player.health = player.max_health
    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    player.vel_y = 0
    player.jumping = False
    player.double_jump_available = False
    player.shoot_cooldown = 0
    player.facing_right = True
    player.animation_state = "idle"
    player.animation_frame = 0
    player.animation_timer = 0
    player.shield_active = False
    player.shield_timer = 0
    player.invincible = False
    player.invincible_timer = 0
    player.speed_boost = False
    player.speed_boost_timer = 0
    player.wall_sliding = False
    player.wall_jump_cooldown = 0
    player.dash_cooldown = 0
    player.dash_duration = 0
    player.regen_timer = 0
    player.damage_resistance = 0
    player.immunity_timer = 0
    
    apply_upgrades()
    
    enemy_group.empty()
    boss_group.empty()
    energy_blast_group.empty()
    enemy_projectile_group.empty()
    powerup_group.empty()
    particle_group.empty()
    destructible_object_group.empty()
    
    ufo_entity.rect.center = (SCREEN_WIDTH // 2, 50)
    ufo_entity.direction = 1
    ufo_entity.drop_timer = 0
    ufo_entity.drop_interval = random.randint(180, 300)
    ufo_entity.super_drop_timer = 0
    ufo_entity.super_drop_interval = random.randint(600, 900)
    ufo_entity.beam_active = False
    ufo_entity.beam_timer = 0
    
    for key in achievements:
        if key not in ["first_blood", "combo_master", "boss_slayer", "level_10", "perfect_shield"]:
            achievements[key]["unlocked"] = False
def start_transition():
    global game_state, transition_alpha, transition_direction, transition_complete, previous_state
    previous_state = game_state
    game_state = TRANSITIONING
    transition_alpha = 0
    transition_direction = 1
    transition_complete = False
def game_loop():
    global running, game_state, game_over, score, level, enemies_defeated, enemies_per_level
    global upgrade_points, upgrades_available, transition_alpha, transition_direction, transition_complete
    global boss_active, combo_count, combo_timer, new_achievement, achievement_timer
    global day_night_timer, is_day, active_quest, quest_completed, quest_timer
    global level_damage_taken, network_role, network_manager, player_id, chat_messages, chat_input, chat_active
    global SERVER_IP
    
    running = True
    play_button_rect = None
    multiplayer_button_rect = None
    load_button_rect = None
    high_scores_button_rect = None
    settings_button_rect = None
    easy_button_rect = None
    normal_button_rect = None
    hard_button_rect = None
    back_button_rect = None
    pause_button_rect = None
    explosion_timer = 0
    explosion_pos = None
    
    level_damage_taken = False
    
    initialize_quests()
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if game_state == START_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_rect and play_button_rect.collidepoint(event.pos):
                        game_state = DIFFICULTY_SELECT
                    elif multiplayer_button_rect and multiplayer_button_rect.collidepoint(event.pos):
                        game_state = NETWORK_CONNECTING
                        SERVER_IP = "localhost"
                    elif load_button_rect and load_button_rect.collidepoint(event.pos):
                        if load_game():
                            start_transition()
                    elif high_scores_button_rect and high_scores_button_rect.collidepoint(event.pos):
                        game_state = HIGH_SCORES
                    elif settings_button_rect and settings_button_rect.collidepoint(event.pos):
                        option_rects, preset_rects, back_rect = draw_graphics_settings_menu()
                        
                        waiting_for_selection = True
                        dragging_slider = None
                        
                        while waiting_for_selection:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    running = False
                                    waiting_for_selection = False
                                elif event.type == pygame.MOUSEBUTTONDOWN:
                                    for rect, setting_id in option_rects:
                                        if rect.collidepoint(event.pos):
                                            if setting_id in ["particle_density", "background_detail"]:
                                                dragging_slider = setting_id
                                            else:
                                                graphics_settings[setting_id] = not graphics_settings[setting_id]
                                                option_rects, preset_rects, back_rect = draw_graphics_settings_menu()
                                    
                                    for rect, preset in preset_rects:
                                        if rect.collidepoint(event.pos):
                                            if preset == "low":
                                                graphics_settings = {
                                                    "particle_density": 0.5,
                                                    "background_detail": 0.5,
                                                    "weather_effects": False,
                                                    "screen_shake": False,
                                                    "slow_motion_effects": False,
                                                    "show_minimap": True
                                                }
                                            elif preset == "medium":
                                                graphics_settings = {
                                                    "particle_density": 0.75,
                                                    "background_detail": 0.75,
                                                    "weather_effects": True,
                                                    "screen_shake": True,
                                                    "slow_motion_effects": True,
                                                    "show_minimap": True
                                                }
                                            elif preset == "high":
                                                graphics_settings = {
                                                    "particle_density": 1.0,
                                                    "background_detail": 1.0,
                                                    "weather_effects": True,
                                                    "screen_shake": True,
                                                    "slow_motion_effects": True,
                                                    "show_minimap": True
                                                }
                                            
                                            option_rects, preset_rects, back_rect = draw_graphics_settings_menu()
                                    
                                    if back_rect.collidepoint(event.pos):
                                        waiting_for_selection = False
                                        
                                elif event.type == pygame.MOUSEMOTION:
                                    if dragging_slider:
                                        for rect, setting_id in option_rects:
                                            if setting_id == dragging_slider:
                                                relative_x = event.pos[0] - rect.x
                                                new_value = max(0.0, min(1.0, relative_x / rect.width))
                                                graphics_settings[setting_id] = new_value
                                                option_rects, preset_rects, back_rect = draw_graphics_settings_menu()
                                                break
                                                
                                elif event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_ESCAPE:
                                        waiting_for_selection = False
                            
                            draw_start_screen()
                            option_rects, preset_rects, back_rect = draw_graphics_settings_menu()
                            
                            pygame.display.flip()
                            clock.tick(FPS)
                        
            elif game_state == DIFFICULTY_SELECT:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if easy_button_rect and easy_button_rect.collidepoint(event.pos):
                        difficulty = DIFFICULTY_EASY
                        start_transition()
                    elif normal_button_rect and normal_button_rect.collidepoint(event.pos):
                        difficulty = DIFFICULTY_NORMAL
                        start_transition()
                    elif hard_button_rect and hard_button_rect.collidepoint(event.pos):
                        difficulty = DIFFICULTY_HARD
                        start_transition()
                    elif back_button_rect and back_button_rect.collidepoint(event.pos):
                        game_state = START_SCREEN
                        
            elif game_state == NETWORK_CONNECTING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = START_SCREEN
                    elif event.key == pygame.K_RETURN:
                        if network_manager.connect_to_server(SERVER_IP):
                            game_state = NETWORK_LOBBY
                            chat_messages.append("Connected to server!")
                        else:
                            chat_messages.append("Failed to connect to server")
                    elif event.key == pygame.K_BACKSPACE:
                        SERVER_IP = SERVER_IP[:-1]
                    else:
                        SERVER_IP += event.unicode
                        
            elif game_state == NETWORK_LOBBY:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        network_manager.stop()
                        game_state = START_SCREEN
                    elif event.key == pygame.K_ENTER:
                        if network_manager.player_id is not None:
                            ready = not network_manager.players.get(network_manager.player_id, {}).get("ready", False)
                            network_manager.send_message({
                                "type": "ready",
                                "ready": ready
                            })
                    elif event.key == pygame.K_t and not chat_active:
                        chat_active = True
                        chat_input = ""
                        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    start_button_rect = None
                    if len(network_manager.players) >= 2 and all(getattr(p, 'ready', False) for p in network_manager.players.values()):
                        start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
                        if start_button_rect.collidepoint(event.pos):
                            network_manager.start_game()
                            game_state = NETWORK_PLAYING
                            chat_messages.append("Game started!")
                            
            elif game_state == NETWORK_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = NETWORK_LOBBY
                    elif event.key == pygame.K_a:
                        player.shoot("left")
                    elif event.key == pygame.K_s:
                        player.shoot("down")
                    elif event.key == pygame.K_d:
                        player.shoot("right")
                    elif event.key == pygame.K_w:
                        player.shoot("up")
                    elif event.key == pygame.K_q:
                        player.shoot("up-left")
                    elif event.key == pygame.K_e:
                        player.shoot("up-right")
                    elif event.key == pygame.K_z:
                        player.shoot("down-left")
                    elif event.key == pygame.K_c:
                        player.shoot("down-right")
                    elif event.key == pygame.K_SPACE:
                        player.shoot("right" if player.facing_right else "left")
                        
                if chat_active:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if chat_input:
                                network_manager.send_chat(chat_input)
                                chat_messages.append(f"You: {chat_input}")
                            chat_active = False
                            chat_input = ""
                        elif event.key == pygame.K_BACKSPACE:
                            chat_input = chat_input[:-1]
                        else:
                            chat_input += event.unicode
                        
            elif game_state == TRANSITIONING:
                pass
                
            elif game_state == PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pause_button_rect and pause_button_rect.collidepoint(event.pos):
                        game_state = PAUSED
                        
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        player.shoot("left")
                    elif event.key == pygame.K_s:
                        player.shoot("down")
                    elif event.key == pygame.K_d:
                        player.shoot("right")
                    elif event.key == pygame.K_w:
                        player.shoot("up")
                    elif event.key == pygame.K_q:
                        player.shoot("up-left")
                    elif event.key == pygame.K_e:
                        player.shoot("up-right")
                    elif event.key == pygame.K_z:
                        player.shoot("down-left")
                    elif event.key == pygame.K_c:
                        player.shoot("down-right")
                    elif event.key == pygame.K_p:
                        game_state = PAUSED
                    elif event.key == pygame.K_u and upgrades_available > 0:
                        game_state = UPGRADE_MENU
                    elif event.key == pygame.K_x and skill_trees["defense"]["skills"]["shield"]["level"] > 0:
                        player.activate_shield()
                    elif event.key == pygame.K_TAB:
                        player.switch_blast_type()
                    elif event.key == pygame.K_LSHIFT:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LEFT]:
                            player.dash("left")
                        elif keys[pygame.K_RIGHT]:
                            player.dash("right")
                        elif keys[pygame.K_UP]:
                            player.dash("up")
                        elif keys[pygame.K_DOWN]:
                            player.dash("down")
                        else:
                            player.dash("default")
                        
            elif game_state == PAUSED:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    resume_rect, save_rect, restart_rect, menu_button_rect = draw_pause_menu()
                    if resume_rect.collidepoint(event.pos):
                        game_state = PLAYING
                    elif save_rect.collidepoint(event.pos):
                        save_game()
                    elif restart_rect.collidepoint(event.pos):
                        start_transition()
                    elif menu_button_rect.collidepoint(event.pos):
                        game_state = START_SCREEN
                        
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        game_state = PLAYING
                        
            elif game_state == UPGRADE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    skill_rects, continue_rect = draw_upgrade_menu()
                    
                    # Define menu_y and menu_height for customization_button_rect
                    menu_width = 700
                    menu_height = 600
                    menu_y = SCREEN_HEIGHT//2 - menu_height//2

                    for rect, tree_id, skill_id in skill_rects:
                        if rect.collidepoint(event.pos):
                            skill = skill_trees[tree_id]["skills"][skill_id]
                            if skill["level"] < skill["max"] and upgrade_points >= skill["cost"]:
                                if skill["requires"] is None or skill_trees[tree_id]["skills"][skill["requires"]]["level"] > 0:
                                    upgrade_points -= skill["cost"]
                                    skill["level"] += 1
                                    apply_upgrades()
                                    
                                    if powerup_sound:
                                        powerup_sound.play()
                    
                    if continue_rect.collidepoint(event.pos):
                        upgrades_available = 0
                        game_state = PLAYING
                        
                    customization_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, menu_y + menu_height - 60, 200, 40)
                    if customization_button_rect.collidepoint(event.pos):
                        color_rects, back_rect = draw_customization_menu()
                        
                        waiting_for_selection = True
                        
                        while waiting_for_selection:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    running = False
                                    waiting_for_selection = False
                                elif event.type == pygame.MOUSEBUTTONDOWN:
                                    for rect, scheme_name in color_rects:
                                        if rect.collidepoint(event.pos):
                                            player.change_color_scheme(scheme_name)
                                            waiting_for_selection = False
                                    
                                    if back_rect.collidepoint(event.pos):
                                        waiting_for_selection = False
                                        
                                elif event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_ESCAPE:
                                        waiting_for_selection = False
                            
                            draw_upgrade_menu()
                            color_rects, back_rect = draw_customization_menu()
                            
                            pygame.display.flip()
                            clock.tick(FPS)
                        
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        upgrades_available = 0
                        game_state = PLAYING
                        
            elif game_state == HIGH_SCORES:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    back_button_rect = draw_high_scores_screen()
                    if back_button_rect.collidepoint(event.pos):
                        game_state = START_SCREEN
                        
            elif game_state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        start_transition()
                    elif event.key == pygame.K_m:
                        game_state = START_SCREEN
        
        if game_state == TRANSITIONING:
            transition_alpha += transition_speed * transition_direction
            
            if transition_direction == 1 and transition_alpha >= 255:
                reset_game()
                game_state = PLAYING
                transition_direction = -1
            
            elif transition_direction == -1 and transition_alpha <= 0:
                transition_complete = True
                transition_alpha = 0
                game_state = PLAYING
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, transition_alpha))
            screen.blit(overlay, (0, 0))
        
        if game_state == START_SCREEN:
            play_button_rect, multiplayer_button_rect, load_button_rect, high_scores_button_rect, settings_button_rect = draw_start_screen()
            
        elif game_state == DIFFICULTY_SELECT:
            easy_button_rect, normal_button_rect, hard_button_rect, back_button_rect = draw_difficulty_select_screen()
            
        elif game_state == NETWORK_CONNECTING:
            draw_network_connecting()
            
        elif game_state == NETWORK_LOBBY:
            start_button_rect = draw_network_lobby()
            
        elif game_state == NETWORK_PLAYING or game_state == PLAYING:
            day_night_timer += 1
            if day_night_timer >= day_night_cycle:
                day_night_timer = 0
                is_day = not is_day
            
            spawn_enemies()
            spawn_powerup()
            spawn_hazards()
            spawn_destructible_objects()
            
            if active_quest and active_quest.objective_type == "survive":
                active_quest.current_count += 1
                if active_quest.current_count >= active_quest.target_count:
                    complete_quest()
            
            player_pos = (player.rect.centerx, player.rect.centery)
            player_group.update()
            enemy_group.update(player_pos)
            boss_group.update(player_pos)
            energy_blast_group.update()
            enemy_projectile_group.update()
            powerup_group.update()
            ufo_entity_group.update()
            hazard_group.update()
            particle_group.update()
            destructible_object_group.update()
            
            update_combo()
            
            for blast in energy_blast_group:
                enemies_hit = pygame.sprite.spritecollide(blast, enemy_group, False)
                for enemy in enemies_hit:
                    if blast.piercing:
                        if enemy not in blast.hit_enemies:
                            if enemy.take_damage(blast.damage):
                                score += enemy.score_value
                                enemies_defeated += 1
                                increase_combo()
                                check_level_up()
                            blast.hit_enemies.append(enemy)
                    else:
                        if enemy.take_damage(blast.damage):
                            score += enemy.score_value
                            enemies_defeated += 1
                            increase_combo()
                            check_level_up()
                        blast.kill()
            
            for blast in energy_blast_group:
                objects_hit = pygame.sprite.spritecollide(blast, destructible_object_group, False)
                for obj in objects_hit:
                    if obj.take_damage(blast.damage):
                        pass
                    if not blast.piercing:
                        blast.kill()
            
            for blast in energy_blast_group:
                bosses_hit = pygame.sprite.spritecollide(blast, boss_group, False)
                for boss in bosses_hit:
                    if boss.take_damage(blast.damage):
                        score += boss.score_value
                        check_level_up()
                        boss_active = False
                        
                        if boss_music and background_music:
                            boss_music.stop()
                            background_music.play(-1)
                        
                        if not achievements["boss_slayer"]["unlocked"]:
                            achievements["boss_slayer"]["unlocked"] = True
                            unlock_achievement("boss_slayer")
                    blast.kill()
            
            projectiles_hit = pygame.sprite.spritecollide(player, enemy_projectile_group, True)
            if projectiles_hit:
                player.take_damage(projectiles_hit[0].damage)
                level_damage_taken = True
                combo_count = 0
                if player.health <= 0:
                    game_over = True
                    game_state = GAME_OVER
                    save_high_score()
            
            enemies_hit = pygame.sprite.spritecollide(player, enemy_group, True)
            if enemies_hit:
                player.take_damage(enemies_hit[0].damage)
                level_damage_taken = True
                combo_count = 0
                if player.health <= 0:
                    game_over = True
                    game_state = GAME_OVER
                    save_high_score()
            
            hazards_hit = pygame.sprite.spritecollide(player, hazard_group, False)
            for hazard in hazards_hit:
                player.take_damage(hazard.damage)
                level_damage_taken = True
                combo_count = 0
                if player.health <= 0:
                    game_over = True
                    game_state = GAME_OVER
                    save_high_score()
            
            powerups_hit = pygame.sprite.spritecollide(player, powerup_group, True)
            for powerup in powerups_hit:
                if powerup.type == "health":
                    player.heal(20)
                    if powerup_sound:
                        powerup_sound.play()
                elif powerup.type == "power":
                    player.shoot_cooldown = 0
                    score += 5
                    upgrade_points += 1
                    upgrades_available += 1
                    if powerup_sound:
                        powerup_sound.play()
                elif powerup.type == "fire":
                    explosion_pos = (player.rect.centerx, player.rect.centery)
                    explosion_timer = 30
                    
                    for enemy in enemy_group:
                        enemy.kill()
                        score += enemy.score_value
                        enemies_defeated += 1
                    check_level_up()
                    if powerup_sound:
                        powerup_sound.play()
                elif powerup.type == "shield":
                    player.activate_shield()
                    if powerup_sound:
                        powerup_sound.play()
                elif powerup.type == "speed":
                    player.activate_speed_boost(300)
                    if powerup_sound:
                        powerup_sound.play()
                elif powerup.type == "invincibility":
                    player.activate_invincibility(180)
                    if powerup_sound:
                        powerup_sound.play()
                
                if active_quest and active_quest.objective_type == "collect":
                    active_quest.current_count += 1
                    if active_quest.current_count >= active_quest.target_count:
                        complete_quest()
            
            if enemies_defeated >= 1 and not achievements["first_blood"]["unlocked"]:
                achievements["first_blood"]["unlocked"] = True
                unlock_achievement("first_blood")
            
            if enemies_defeated >= enemies_per_level and not level_damage_taken and not achievements["survivor"]["unlocked"]:
                achievements["survivor"]["unlocked"] = True
                unlock_achievement("survivor")
            
            if enemies_defeated >= enemies_per_level and not level_damage_taken and active_quest and active_quest.objective_type == "no_damage":
                active_quest.current_count = 1
                if active_quest.current_count >= active_quest.target_count:
                    complete_quest()
            
            if active_quest and active_quest.objective_type == "combo" and combo_count >= active_quest.target_count:
                active_quest.current_count = combo_count
                if active_quest.current_count >= active_quest.target_count:
                    complete_quest()
            
            if active_quest and active_quest.objective_type == "kill" and active_quest.name == "Boss Slayer":
                active_quest.current_count = 1
                if active_quest.current_count >= active_quest.target_count:
                    complete_quest()
            
            if not active_quest and random.randint(1, 600) == 1:
                available_quests = [q for q in side_quests if not q.completed and not q.active]
                
                if available_quests:
                    active_quest = random.choice(available_quests)
                    active_quest.active = True
                    active_quest.current_count = 0
                    
                    if active_quest.objective_type == "survive":
                        active_quest.current_count = 0
                    
                    if powerup_sound:
                        powerup_sound.play()
            
            draw_space_background(screen)
            draw_grass_ground(screen)
            draw_weather_effects(screen)
            
            for ufo in ufo_entity_group:
                ufo.draw_beam(screen)
            
            ufo_entity_group.draw(screen)
            hazard_group.draw(screen)
            destructible_object_group.draw(screen)
            player_group.draw(screen)
            enemy_group.draw(screen)
            boss_group.draw(screen)
            energy_blast_group.draw(screen)
            enemy_projectile_group.draw(screen)
            powerup_group.draw(screen)
            particle_group.draw(screen)
            
            if explosion_timer > 0 and explosion_pos:
                draw_fire_explosion(explosion_pos[0], explosion_pos[1])
                explosion_timer -= 1
            
            if player.shield_active:
                shield_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
                pygame.draw.circle(shield_surface, (0, 200, 255, 100), (40, 40), 35, 3)
                screen.blit(shield_surface, (player.rect.centerx - 40, player.rect.centery - 40))
            
            if player.invincible:
                invinc_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.circle(invinc_surface, (255, 255, 0, 50), (30, 30), 25, 2)
                screen.blit(invinc_surface, (player.rect.centerx - 30, player.rect.centery - 30))
            
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            
            level_text = font.render(f"Level: {level}", True, YELLOW)
            screen.blit(level_text, (10, 50))
            
            if combo_count > 1:
                combo_text = font.render(f"Combo: {combo_count}x", True, GOLD)
                screen.blit(combo_text, (10, 90))
            
            draw_health_bar(screen, 10, 130, player.health)
            health_text = small_font.render("Health", True, WHITE)
            screen.blit(health_text, (10, 145))
            
            if boss_active:
                for boss in boss_group:
                    boss_health_percent = (boss.health / boss.max_health) * 100
                    draw_health_bar(screen, SCREEN_WIDTH // 2 - 100, 20, boss_health_percent, DARK_RED)
                    boss_text = font.render("BOSS", True, RED)
                    screen.blit(boss_text, (SCREEN_WIDTH // 2 - boss_text.get_width() // 2, 35))
            
            if upgrades_available > 0:
                upgrade_text = font.render(f"Upgrades Available! ({upgrades_available})", True, GOLD)
                screen.blit(upgrade_text, (SCREEN_WIDTH//2 - upgrade_text.get_width()//2, 10))
            
            blast_type_text = small_font.render(f"Blast: {player.blast_type.capitalize()}", True, WHITE)
            screen.blit(blast_type_text, (10, 170))
            
            if skill_trees["defense"]["skills"]["shield"]["level"] > 0:
                shield_text = small_font.render("Shield: X", True, CYAN if player.shield_active else GRAY)
                screen.blit(shield_text, (10, 190))
            
            if active_quest:
                quest_text = small_font.render(f"Quest: {active_quest.name}", True, YELLOW)
                screen.blit(quest_text, (10, 220))
                
                progress_text = small_font.render(f"Progress: {active_quest.current_count}/{active_quest.target_count}", True, WHITE)
                screen.blit(progress_text, (10, 240))
                
                BAR_LENGTH = 200
                BAR_HEIGHT = 10
                progress = min(1.0, active_quest.current_count / active_quest.target_count)
                fill = int(progress * BAR_LENGTH)
                outline_rect = pygame.Rect(10, 260, BAR_LENGTH, BAR_HEIGHT)
                fill_rect = pygame.Rect(10, 260, fill, BAR_HEIGHT)
                pygame.draw.rect(screen, GREEN, fill_rect)
                pygame.draw.rect(screen, WHITE, outline_rect, 2)
            
            draw_minimap(screen, player.rect.center, list(enemy_group) + list(boss_group), list(powerup_group))
            
            weather_text = small_font.render(f"Weather: {weather_type.capitalize()}", True, WHITE)
            screen.blit(weather_text, (10, SCREEN_HEIGHT - 30))
            
            time_text = small_font.render(f"Time: {'Day' if is_day else 'Night'}", True, WHITE)
            screen.blit(time_text, (10, SCREEN_HEIGHT - 50))
            
            if new_achievement and achievement_timer > 0:
                achievement_surface = pygame.Surface((400, 80), pygame.SRCALPHA)
                achievement_surface.fill((0, 0, 0, 200))
                pygame.draw.rect(achievement_surface, GOLD, (0, 0, 400, 80), 3)
                
                achievement_title = small_font.render("Achievement Unlocked!", True, GOLD)
                achievement_name = font.render(new_achievement["name"], True, WHITE)
                achievement_desc = small_font.render(new_achievement["description"], True, WHITE)
                
                achievement_surface.blit(achievement_title, (200 - achievement_title.get_width() // 2, 10))
                achievement_surface.blit(achievement_name, (200 - achievement_name.get_width() // 2, 35))
                achievement_surface.blit(achievement_desc, (200 - achievement_desc.get_width() // 2, 55))
                
                screen.blit(achievement_surface, (SCREEN_WIDTH // 2 - 200, 100))
                achievement_timer -= 1
            
            if quest_completed and quest_timer > 0:
                quest_surface = pygame.Surface((400, 100), pygame.SRCALPHA)
                quest_surface.fill((0, 0, 0, 200))
                pygame.draw.rect(quest_surface, GREEN, (0, 0, 400, 100), 3)
                
                quest_title = small_font.render("Quest Completed!", True, GREEN)
                quest_name = font.render(active_quest.name if active_quest else "Quest", True, WHITE)
                quest_reward = small_font.render(f"Reward: {active_quest.reward_score} Score, {active_quest.reward_upgrades} Upgrades", True, YELLOW)
                
                quest_surface.blit(quest_title, (200 - quest_title.get_width() // 2, 10))
                quest_surface.blit(quest_name, (200 - quest_name.get_width() // 2, 40))
                quest_surface.blit(quest_reward, (200 - quest_reward.get_width() // 2, 70))
                
                screen.blit(quest_surface, (SCREEN_WIDTH // 2 - 200, 200))
                quest_timer -= 1
            
            if slow_motion_active:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((100, 100, 255, 30))
                screen.blit(overlay, (0, 0))
                
                slow_text = font.render("SLOW MOTION", True, WHITE)
                screen.blit(slow_text, (SCREEN_WIDTH//2 - slow_text.get_width()//2, 50))
            
            draw_screen_flash(screen)
            
            y_offset = SCREEN_HEIGHT - 150
            for message in chat_messages[-5:]:
                message_text = small_font.render(message, True, WHITE)
                screen.blit(message_text, (20, y_offset))
                y_offset += 20
            
            if chat_active:
                pygame.draw.rect(screen, GRAY, (20, SCREEN_HEIGHT - 30, 300, 25))
                pygame.draw.rect(screen, WHITE, (20, SCREEN_HEIGHT - 30, 300, 25), 2)
                
                input_text = small_font.render(chat_input, True, WHITE)
                screen.blit(input_text, (25, SCREEN_HEIGHT - 25))
            
            pause_button_rect = draw_pause_button()
            
        elif game_state == PAUSED:
            draw_space_background(screen)
            draw_grass_ground(screen)
            draw_weather_effects(screen)
            
            for ufo in ufo_entity_group:
                ufo.draw_beam(screen)
            
            ufo_entity_group.draw(screen)
            hazard_group.draw(screen)
            destructible_object_group.draw(screen)
            player_group.draw(screen)
            enemy_group.draw(screen)
            boss_group.draw(screen)
            energy_blast_group.draw(screen)
            enemy_projectile_group.draw(screen)
            powerup_group.draw(screen)
            particle_group.draw(screen)
            
            if player.shield_active:
                shield_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
                pygame.draw.circle(shield_surface, (0, 200, 255, 100), (40, 40), 35, 3)
                screen.blit(shield_surface, (player.rect.centerx - 40, player.rect.centery - 40))
            
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            
            level_text = font.render(f"Level: {level}", True, YELLOW)
            screen.blit(level_text, (10, 50))
            
            draw_health_bar(screen, 10, 90, player.health)
            health_text = small_font.render("Health", True, WHITE)
            screen.blit(health_text, (10, 105))
            
            draw_pause_menu()
            
        elif game_state == UPGRADE_MENU:
            draw_space_background(screen)
            draw_grass_ground(screen)
            draw_weather_effects(screen)
            
            for ufo in ufo_entity_group:
                ufo.draw_beam(screen)
            
            ufo_entity_group.draw(screen)
            hazard_group.draw(screen)
            destructible_object_group.draw(screen)
            player_group.draw(screen)
            enemy_group.draw(screen)
            boss_group.draw(screen)
            energy_blast_group.draw(screen)
            enemy_projectile_group.draw(screen)
            powerup_group.draw(screen)
            particle_group.draw(screen)
            
            if player.shield_active:
                shield_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
                pygame.draw.circle(shield_surface, (0, 200, 255, 100), (40, 40), 35, 3)
                screen.blit(shield_surface, (player.rect.centerx - 40, player.rect.centery - 40))
            
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            
            level_text = font.render(f"Level: {level}", True, YELLOW)
            screen.blit(level_text, (10, 50))
            
            draw_health_bar(screen, 10, 90, player.health)
            health_text = small_font.render("Health", True, WHITE)
            screen.blit(health_text, (10, 105))
            
            draw_upgrade_menu()
            
        elif game_state == HIGH_SCORES:
            draw_high_scores_screen()
            
        elif game_state == GAME_OVER:
            draw_space_background(screen)
            draw_grass_ground(screen)
            draw_weather_effects(screen)
            
            for ufo in ufo_entity_group:
                ufo.draw_beam(screen)
            
            ufo_entity_group.draw(screen)
            hazard_group.draw(screen)
            destructible_object_group.draw(screen)
            player_group.draw(screen)
            enemy_group.draw(screen)
            boss_group.draw(screen)
            energy_blast_group.draw(screen)
            enemy_projectile_group.draw(screen)
            powerup_group.draw(screen)
            particle_group.draw(screen)
            
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            
            level_text = font.render(f"Level: {level}", True, YELLOW)
            screen.blit(level_text, (10, 50))
            
            draw_health_bar(screen, 10, 90, player.health)
            health_text = small_font.render("Health", True, WHITE)
            screen.blit(health_text, (10, 105))
            
            game_over_text = font.render("GAME OVER", True, RED)
            restart_text = small_font.render("Press R to Restart", True, WHITE)
            menu_text = small_font.render("Press M for Main Menu", True, WHITE)
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            final_level_text = font.render(f"Level Reached: {level}", True, YELLOW)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 120))
            screen.blit(final_score_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 80))
            screen.blit(final_level_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 40))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - 90, SCREEN_HEIGHT//2 + 20))
            screen.blit(menu_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50))
        
        if game_state == PLAYING or game_state == PAUSED or game_state == GAME_OVER or game_state == NETWORK_PLAYING:
            controls = [
                "Controls:",
                "Arrow Keys - Move",
                "Space - Jump",
                "A - Shoot Left",
                "S - Shoot Down",
                "D - Shoot Right",
                "W - Shoot Up",
                "Q - Shoot Up-Left",
                "E - Shoot Up-Right",
                "Z - Shoot Down-Left",
                "C - Shoot Down-Right",
                "P - Pause Game",
                "U - Upgrade Menu",
                "X - Activate Shield",
                "Tab - Switch Blast Type",
                "Shift - Dash",
                "R - Restart Game",
            ]
            y_offset = SCREEN_HEIGHT - 300
            for control in controls:
                control_text = small_font.render(control, True, WHITE)
                screen.blit(control_text, (SCREEN_WIDTH - 220, y_offset))
                y_offset += 20
        
        if slow_motion_active:
            effective_fps = int(FPS * slow_motion_factor)
            clock.tick(effective_fps)
        else:
            clock.tick(FPS)
        
        pygame.display.flip()
    
    if not hasattr(sys, 'is_web') or not sys.is_web:
        pygame.quit()
        sys.exit()
if __name__ == "__main__":
    game_loop()