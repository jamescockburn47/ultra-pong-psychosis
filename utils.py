# utils.py — Utility Functions (Added resource_path)

import pygame
import random
import math
import sys # Needed for sys.frozen and sys._MEIPASS
import os  # Needed for path joining

from config import * # Import all constants

# --- Resource Path Helper ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # sys.frozen will be True if running as a bundled exe
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
            # print(f"Running bundled, MEIPASS: {base_path}") # Optional debug print
        else:
            # Running as a normal script, use the script's directory
            base_path = os.path.abspath(".")
            # print(f"Running as script, base path: {base_path}") # Optional debug print

        # Join the base path with the relative path provided
        full_path = os.path.join(base_path, relative_path)
        # print(f"Resolved path for '{relative_path}': {full_path}") # Optional debug print
        return full_path

    except Exception as e:
        print(f"Error getting resource path for '{relative_path}': {e}")
        # Fallback to just the relative path if something goes wrong
        return relative_path

# --- Other Utility Functions ---

def get_random_crazy_color(alpha=255):
    """Generates a random vibrant color."""
    r = random.randint(50, 255)
    g = random.randint(50, 255)
    b = random.randint(50, 255)
    return (r, g, b, alpha)

def draw_psychedelic_background(surface, current_time_tick):
    """Draws a dynamic, psychedelic background effect."""
    global_hue_offset = (current_time_tick * PSYCHEDELIC_HUE_SHIFT_SPEED * 10) % 360
    band_height = 15
    for y_pos in range(0, SCREEN_HEIGHT, band_height):
        hue = (global_hue_offset + y_pos * 0.4 + current_time_tick * 30) % 360
        saturation = 70 + math.sin(current_time_tick * 0.2 + y_pos * 0.02) * 30
        value = 60 + math.cos(current_time_tick * 0.3 - y_pos * 0.03) * 20
        color = pygame.Color(0)
        color.hsva = (hue, max(40, min(100, saturation)), max(40, min(100, value)), 100)
        pygame.draw.rect(surface, color, (0, y_pos, SCREEN_WIDTH, band_height))

def draw_text_adv(surface, text, size, x, y, base_color, font_type="Verdana", center_aligned=False,
                  shadow_color=(30,30,30), shadow_offset=(2,2),
                  hover_color=None, mouse_pos=None, click_rect_ref=None):
    """Draws text with advanced options like font, alignment, shadow, and hover."""
    try:
        font = pygame.font.SysFont(font_type, size, bold=True)
    except pygame.error:
        font = pygame.font.Font(None, size) # Fallback to default font

    is_hovering = False
    if isinstance(click_rect_ref, pygame.Rect) and hover_color and mouse_pos and click_rect_ref.collidepoint(mouse_pos):
        is_hovering = True

    current_color = hover_color if is_hovering else base_color

    text_surface_main = font.render(text, True, current_color)
    text_rect = text_surface_main.get_rect()

    if center_aligned:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)

    if shadow_color and shadow_offset: # Only draw shadow if specified
        text_surface_shadow = font.render(text, True, shadow_color)
        surface.blit(text_surface_shadow, (text_rect.x + shadow_offset[0], text_rect.y + shadow_offset[1]))

    surface.blit(text_surface_main, text_rect)
    return text_rect # Return rect for click detection

# Function to create impact particles
def create_impact_particles(x, y, particle_group, impact_type="generic", custom_color_func=None):
    """Creates particle effects at a given position with type-specific or custom colors."""
    # Import Particle class locally to avoid circular dependency with sprites.py
    from sprites import Particle

    num_particles = PARTICLE_COUNT_IMPACT
    speed_range = (1, PARTICLE_SPEED_IMPACT)
    lifespan_mod = 0

    # Default color function
    color_func = lambda: get_random_crazy_color(random.randint(180,255))

    if custom_color_func:
        color_func = custom_color_func
    elif impact_type == "wall":
        color_func = lambda: (random.randint(100,200), random.randint(100,200), random.randint(200,255), random.randint(150,220))
    elif impact_type == "paddle":
        color_func = lambda: (random.randint(200,255), random.randint(100,200), random.randint(50,150), random.randint(180,255))
    elif impact_type == "goal":
        num_particles = PARTICLE_COUNT_IMPACT * 2
        speed_range = (2, PARTICLE_SPEED_IMPACT * 1.5)
        color_func = lambda: (random.randint(200,255), random.randint(200,255), random.randint(50,150), random.randint(200,255)) # More vibrant for goal
    elif impact_type == "teleport_vanish":
        num_particles = PARTICLE_COUNT_IMPACT // 2
        color_func = lambda: (random.randint(80,150), random.randint(200,255), random.randint(80,150), random.randint(100,180)) # Greenish hues
        lifespan_mod = -10 # Shorter lifespan
    elif impact_type == "teleport_appear":
        num_particles = PARTICLE_COUNT_IMPACT // 2
        color_func = lambda: (random.randint(100,180), random.randint(220,255), random.randint(100,180), random.randint(150,220)) # Brighter greenish
        lifespan_mod = 5

    for _ in range(num_particles):
        particle_group.add(Particle(x, y, color_func, speed_range=speed_range, lifespan_mod=lifespan_mod))
