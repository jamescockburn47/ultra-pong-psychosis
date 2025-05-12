# config.py — Updated Game Configuration Constants

import pygame

# --- Colors ---
BLACK = (0,0,0); WHITE = (255,255,255); RED = (255,0,0); YELLOW = (255,255,0); ORANGE = (255,165,0)
CYAN = (0,255,255); LIGHT_BLUE = (173,216,230); PURPLE = (128,0,128); BLUE = (0,0,255)
LASER_SHOT_COLOR = (255,50,50); TELEPORT_COLOR = (100,255,100)

# --- Game Element Colors ---
COLOR_PADDLE_BASE = (50,200,255); COLOR_BALL_BASE = (255,255,0)
COLOR_DUCK = (255,230,0); COLOR_SHIELD = (60,120,255)

# --- Screen ---
# *** ADJUSTED SCREEN SIZE (Approx 15% smaller) ***
SCREEN_WIDTH = 850
SCREEN_HEIGHT = 638

# --- Paddle ---
# Note: Paddle/Ball sizes and speeds were previously adjusted for a larger screen.
# Consider if these need further tweaking for the new 850x638 size.
PADDLE_WIDTH = 15
PADDLE_HEIGHT_NORMAL = 100 # Reverted closer to original, adjust as needed
PADDLE_BORDER_WIDTH = 2
PADDLE_SPEED = 8 # Slightly reduced speed for smaller screen
PLAYER_2_PADDLE_SPEED = 8 # Slightly reduced speed for smaller screen
AI_PADDLE_SPEED_EASY = 4.5
AI_PADDLE_SPEED_MEDIUM = 6.0
AI_PADDLE_SPEED_HARD = 7.5

PADDLE_SPIN_FACTOR = 0.20
PADDLE_EDGE_SPIN_FACTOR = 0.45

PADDLE_FREEZE_DURATION = 120; PADDLE_SLOW_FACTOR = 0.5
PADDLE_CONFUSE_CONTROLS_DURATION = 200; PADDLE_STUN_DURATION_DUCK = 0

SHIELD_SIZE = (PADDLE_WIDTH, PADDLE_HEIGHT_NORMAL + 20); SHIELD_OFFSET = 5
POWERUP_PADDLE_HEIGHT_BIG = 150 # Adjusted for new normal height
POWERUP_PADDLE_HEIGHT_SMALL = 60 # Adjusted for new normal height
OPPONENT_PADDLE_SHRINK_DURATION = 240; OPPONENT_PADDLE_SHRINK_HEIGHT = 40 # Adjusted

# --- Ball ---
BALL_RADIUS_NORMAL = 9 # Slightly reduced radius for smaller screen
BALL_RADIUS_BIG = 14
BALL_RADIUS_SMALL = 5
BALL_INITIAL_SPEED_X = 4.5 # Slightly reduced initial speed
BALL_SPEED_INCREMENT_RALLY = 0.005
BALL_SPEED_INCREMENT_HIT = 0.05
BALL_MAX_SPEED_X = 14.0 # Reduced max speed

BALL_SPIN_DECAY = 0.980
BALL_SPIN_EFFECT_ON_CURVE = 0.13
BALL_MAX_SPIN = 8.0 # Slightly reduced max spin
BALL_LAST_HIT_TIMER_DURATION = 45

BALL_SPEED_BOOST_MULTIPLIER = 1.7; BALL_INVISIBILITY_ALPHA = 40
BALL_INVISIBILITY_FLICKER_RATE = 3; STICKY_BALL_DURATION = 240
LASER_SHOT_SPEED_MULTIPLIER = 2.2; GHOST_BALL_ALPHA = 70; GHOST_BALL_DURATION = 240

# --- Power-up System ---
POWERUP_SIZE = 30 # Slightly smaller powerups
POWERUP_SPAWN_CHANCE = 0.0040 # Spawn chance might need adjustment based on game feel
MAX_POWERUPS_ONSCREEN = 4
POWERUP_GENERAL_DURATION = 300; POWERUP_SHORT_DURATION = 180
POWERUP_MULTIBALL_COUNT = 2; POWERUP_MAGNET_RANGE = 130; POWERUP_MAGNET_SPEED = 1.6 # Adjusted range/speed
REPEL_FIELD_DURATION = 240; REPEL_FIELD_RADIUS_FACTOR = 1.3; REPEL_FIELD_STRENGTH = 2.8

ALL_POWERUP_TYPES = [
    "paddle_big_self", "paddle_small_self", "multi_ball", "ball_fast_all",
    "opp_freeze", "ball_invis_all", "shield_self", "slow_opponent",
    "sticky_paddle_self", "curve_ball_self", "laser_shot_self",
    "confuse_opponent_controls", "point_shield_self",
    "ball_size_toggle_all", "rainbow_ball_all", "opponent_paddle_shrink",
    "ball_ghost_self", "paddle_teleport_self", "repel_field_self",
    "ball_split_self", "ball_teleport_all"
]
# Display names remain the same
POWERUP_DISPLAY_NAMES = {
    "paddle_big_self": "BIG PADDLE!", "paddle_small_self": "SMALL PADDLE!",
    "multi_ball": "MULTIBALL!", "ball_fast_all": "SPEED BOOST!",
    "opp_freeze": "OPP FROZE!", "freeze": "FROZEN!",
    "ball_invis_all": "INVISIBLE BALL!",
    "shield_self": "SHIELD UP!", "shield": "SHIELD UP!",
    "slow_opponent": "OPP SLOWED!", "slow": "SLOWED!",
    "sticky_paddle_self": "STICKY PADDLE!", "sticky": "STICKY PADDLE!",
    "curve_ball_self": "CURVE READY!", "curve_shot_ready": "CURVE READY!",
    "laser_shot_self": "LASER ACTIVE!", "laser_shot": "LASER ACTIVE!",
    "confuse_opponent_controls": "OPP CONFUSED!", "confused_controls": "CONFUSED!",
    "point_shield_self": "POINT SHIELD!", "point_shield": "POINT SHIELD!",
    "ball_size_toggle_all": "BALL SIZE +/-!",
    "rainbow_ball_all": "RAINBOW BALL!",
    "opponent_paddle_shrink": "SHRINK OPP!", "shrunken_by_opponent": "SHRUNKEN!",
    "ball_ghost_self": "GHOST READY!", "ghost_shot_ready": "GHOST READY!",
    "paddle_teleport_self": "PADDLE WARP!",
    "repel_field_self": "REPEL FIELD!", "repel_field": "REPEL FIELD!",
    "ball_split_self": "SPLIT READY!", "ball_split_ready": "SPLIT READY!",
    "ball_teleport_all": "BALL TELEPORT!",
    "stunned_by_duck": "STUNNED!"
}

# --- Visual Effects ---
PSYCHEDELIC_BACKGROUND_SPEED = 0.08; PSYCHEDELIC_HUE_SHIFT_SPEED = 0.5
SCREEN_WOBBLE_AMPLITUDE = 3 # Slightly reduced wobble for smaller screen
SCREEN_WOBBLE_SPEED = 0.15
BALL_TRAIL_LENGTH_GHOST = 20 # Slightly shorter trail
PARTICLE_COUNT_IMPACT = 25 # Fewer particles
PARTICLE_LIFESPAN_IMPACT = 28; PARTICLE_SPEED_IMPACT = 4.5 # Slightly slower/shorter particles

# --- Distractors ---
DISTRACTOR_SPAWN_CHANCE_TOTAL = 0.005
CRAZY_DUCK_SPAWN_CHANCE_RATIO = 0.4
DISTRACTOR_MAX_ONSCREEN_TOTAL = 3
MAX_DUCKS_ONSCREEN = 1

DISTRACTOR_SPEED_RANGE = (1.3, 3.2) # Slightly slower distractors

# Crazy Duck Specifics
CRAZY_DUCK_VERTICAL_SPEED_RANGE = (1.8, 3.8)
CRAZY_DUCK_HIT_STRENGTH_Y = 3.3
CRAZY_DUCK_HIT_SPIN = 2.3

# --- UI & Game Flow ---
GOAL_FLASH_DURATION_INTENSE = 15; GOAL_FLASH_ALPHA_INTENSE = 180
COUNTDOWN_INITIAL_VALUE = 3; COUNTDOWN_FRAMES_PER_NUMBER = 60
COUNTDOWN_TEXT_COLOR = (255,255,255); COUNTDOWN_GO_TEXT_COLOR = (0,255,0)
SUDDEN_DEATH_SCORE_THRESHOLD = 6; SUDDEN_DEATH_FLASH_SPEED = 0.05; SUDDEN_DEATH_FLASH_ALPHA_MAX = 150
WINNING_SCORE = 7

# --- Game Modes & States ---
GAME_MODE_AI = 0; GAME_MODE_2P = 1
DIFFICULTY_EASY = 0; DIFFICULTY_MEDIUM = 1; DIFFICULTY_HARD = 2
STATE_START_MENU = 0; STATE_MODE_SELECT = 1; STATE_AI_DIFFICULTY_SELECT = 1.5
STATE_COUNTDOWN = 1.25; STATE_PLAYING = 2; STATE_GAME_OVER = 3
STATE_INSTRUCTIONS = 4; STATE_PAUSED = 5
