# sprites.py — Updated Distractor Shapes

import pygame
import random
import math
from config import *
from utils import create_impact_particles, get_random_crazy_color

# Note: play_sound function is defined in game.py and passed to sprites that need it.
# sounds dictionary and laser_channel are also managed in game.py.

class Effect:
    def __init__(self, name, duration_frames, intensity=None, start_tick=0, display_text=""):
        self.name = name
        self.duration_frames = duration_frames
        self.intensity = intensity
        self.start_tick = start_tick
        self.display_text = display_text
    def is_active(self, current_tick):
        if self.duration_frames <= 0: return True # -1 duration means active until removed
        return current_tick < self.start_tick + self.duration_frames
    def __repr__(self):
        return f"Effect(name='{self.name}', duration={self.duration_frames}, intensity={self.intensity}, start_tick={self.start_tick})"

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color_func, size_range=(2,6), speed_range=(1,PARTICLE_SPEED_IMPACT), lifespan_mod=0):
        super().__init__()
        size = random.randint(*size_range)
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        self.color_val = color_func() if callable(color_func) else color_func
        try:
            initial_color_fill = self.color_val if len(self.color_val) == 4 else self.color_val + (255,)
            self.image.fill(initial_color_fill)
        except (TypeError, ValueError): # Fallback if color_val is not as expected
             self.image.fill((255,255,255,255)) # Default to white

        self.rect = self.image.get_rect(center=(x, y))
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        self.velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
        self.lifespan = PARTICLE_LIFESPAN_IMPACT + random.randint(-5,5) + lifespan_mod
        self.initial_lifespan = max(self.lifespan, 1)

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.lifespan -= 1
        alpha = max(0, int(255 * (self.lifespan / self.initial_lifespan)))
        draw_size = self.image.get_width()
        self.image = pygame.Surface([draw_size, draw_size], pygame.SRCALPHA) # Recreate surface for alpha

        base_color = self.color_val[:3] if isinstance(self.color_val, (list, tuple)) and len(self.color_val) >= 3 else (255, 255, 255) # Default to white
        current_color_tuple = base_color + (alpha,)
        try:
            self.image.fill(current_color_tuple)
        except (TypeError, ValueError):
             self.image.fill((255,255,255,alpha)) # Fallback fill

        if self.lifespan <= 0:
            self.kill()

class DistractorSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(25, 70) # Slightly larger max size possible
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        hue = random.randint(0,360)
        color = pygame.Color(0,0,0,0)
        hsva_alpha = int((random.randint(160, 220) / 255.0) * 100) # HSVA alpha is 0-100, slightly less transparent
        color.hsva = (hue % 360, 100, 100, hsva_alpha) # Corrected HSVA

        # *** MORE SHAPE VARIETY ***
        shape_type = random.choice(["rect", "circle", "poly", "ellipse"]) # Added ellipse

        if shape_type == "rect":
            pygame.draw.rect(self.image, color, (0,0,size,size), border_radius=size//random.randint(3,6)) # Random border radius
        elif shape_type == "circle":
            pygame.draw.circle(self.image, color, (size//2, size//2), size//random.randint(2,3)) # Slightly variable radius
        elif shape_type == "ellipse":
            # Random width/height for ellipse, ensuring it fits within the surface
            ellipse_width = random.randint(size // 2, size)
            ellipse_height = random.randint(size // 2, size)
            ellipse_rect = pygame.Rect( (size - ellipse_width) // 2, (size - ellipse_height) // 2, ellipse_width, ellipse_height)
            pygame.draw.ellipse(self.image, color, ellipse_rect)
        else: # Polygon
            num_points = random.randint(4, 8) # Increased max points
            points = []
            center_x, center_y = size // 2, size // 2
            min_radius = size * 0.2
            max_radius = size * 0.5
            angle_step = (2 * math.pi) / num_points
            # Generate points around a center with varying radius for spikiness
            for i in range(num_points):
                radius = random.uniform(min_radius, max_radius)
                angle = i * angle_step + random.uniform(-angle_step * 0.3, angle_step * 0.3) # Add jitter
                px = center_x + radius * math.cos(angle)
                py = center_y + radius * math.sin(angle)
                points.append((int(px), int(py)))
            # Ensure points are within bounds (simple clamp)
            points = [(max(0, min(size-1, p[0])), max(0, min(size-1, p[1]))) for p in points]
            if len(points) >= 3: # Need at least 3 points for polygon
                pygame.draw.polygon(self.image, color, points)
            else: # Fallback to circle if polygon generation failed
                 pygame.draw.circle(self.image, color, (size//2, size//2), size//3)


        self.rect = self.image.get_rect()
        # Spawning logic remains the same
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top": self.rect.bottom = 0; self.rect.centerx = random.randint(0,SCREEN_WIDTH)
        elif edge == "bottom": self.rect.top = SCREEN_HEIGHT; self.rect.centerx = random.randint(0,SCREEN_WIDTH)
        elif edge == "left": self.rect.right = 0; self.rect.centery = random.randint(0,SCREEN_HEIGHT)
        else: self.rect.left = SCREEN_WIDTH; self.rect.centery = random.randint(0,SCREEN_HEIGHT)

        angle_to_centerish = math.atan2(SCREEN_HEIGHT/2 - self.rect.centery, SCREEN_WIDTH/2 - self.rect.centerx)
        actual_angle = angle_to_centerish + random.uniform(-math.pi/3, math.pi/3)
        speed = random.uniform(*DISTRACTOR_SPEED_RANGE)
        self.velocity = [math.cos(actual_angle) * speed, math.sin(actual_angle) * speed]
        self.rotation_speed = random.uniform(-6, 6) # Slightly faster rotation possible
        self.angle = 0
        self.original_image = self.image.copy()

    def update(self, time_tick=0): # time_tick added for consistency, not used here
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.angle = (self.angle + self.rotation_speed) % 360
        # Recalculate center before rotating to avoid drift
        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=old_center) # Apply rotation around the calculated center

        # Kill if far off screen
        off_screen_buffer = 150 # Increased buffer due to potentially larger screen/sprites
        if not pygame.Rect(-off_screen_buffer, -off_screen_buffer,
                           SCREEN_WIDTH + 2 * off_screen_buffer, SCREEN_HEIGHT + 2 * off_screen_buffer).colliderect(self.rect):
            self.kill()

# --- CrazyDuckSprite remains the same ---
class CrazyDuckSprite(DistractorSprite):
    def __init__(self, play_sound_func=None): # Added play_sound_func
        super().__init__() # Calls the updated DistractorSprite init first
        self.play_sound_func = play_sound_func
        # --- Duck Specific Drawing (Overwrites generic shape) ---
        self.size = random.randint(45, 70) # Duck size range
        self.original_image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
        self.original_image.fill((0,0,0,0)) # Ensure clear background

        body_color = COLOR_DUCK; beak_color = ORANGE; eye_color = BLACK
        # Body Ellipse
        body_rect = pygame.Rect(self.size*0.1, self.size*0.35, self.size*0.8, self.size*0.55)
        pygame.draw.ellipse(self.original_image, body_color, body_rect)
        # Head Circle
        head_center = (int(self.size*0.75), int(self.size*0.3))
        pygame.draw.circle(self.original_image, body_color, head_center, int(self.size*0.22))
        # Beak Polygon
        beak_tip_x = head_center[0] + int(self.size*0.25)
        beak_points = [(head_center[0] + int(self.size*0.15), head_center[1] - int(self.size*0.08)),
                       (beak_tip_x, head_center[1]),
                       (head_center[0] + int(self.size*0.15), head_center[1] + int(self.size*0.08))]
        pygame.draw.polygon(self.original_image, beak_color, beak_points)
        # Eye Circle
        pygame.draw.circle(self.original_image, eye_color, (head_center[0] + int(self.size*0.05), head_center[1] - int(self.size*0.05)), int(self.size*0.05))

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect() # Reset rect based on duck image

        # --- Duck Specific Movement ---
        self.velocity = [0, random.uniform(CRAZY_DUCK_VERTICAL_SPEED_RANGE[0], CRAZY_DUCK_VERTICAL_SPEED_RANGE[1])]
        if random.choice([True, False]): self.velocity[1] *= -1

        self.rect.centerx = random.randint(self.size // 2, SCREEN_WIDTH - self.size // 2)
        if self.velocity[1] > 0: self.rect.bottom = 0
        else: self.rect.top = SCREEN_HEIGHT

        self.rotation_speed = random.uniform(-3, 3) # Ducks rotate less wildly than generic shapes
        self.angle = random.uniform(0, 360)

        # --- Duck Quack Logic ---
        self.quack_timer = random.randint(60,150)
        self.is_quacking = False
        self.quack_display_timer = 0
        self.played_quack_sound_this_sequence = False
        try: self.quack_font = pygame.font.SysFont("Arial", 18, True) # Slightly larger quack font
        except pygame.error: self.quack_font = pygame.font.Font(None, 22)
        self.hit_cooldown = 0

    def update(self, current_time_tick): # Renamed from time_tick for clarity
        # Use duck's vertical movement
        self.rect.y += self.velocity[1]
        # Apply duck's rotation
        self.angle = (self.angle + self.rotation_speed) % 360
        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=old_center)

        # Kill duck if off screen
        if self.velocity[1] > 0 and self.rect.top > SCREEN_HEIGHT + self.size: self.kill()
        elif self.velocity[1] < 0 and self.rect.bottom < -self.size: self.kill()

        # Quack timer logic
        self.quack_timer -= 1
        if self.quack_timer <= 0:
            self.is_quacking = True
            self.quack_display_timer = random.randint(25, 45)
            self.quack_timer = random.randint(80, 220)
            if not self.played_quack_sound_this_sequence and self.play_sound_func:
                self.play_sound_func("duck_quack")
                self.played_quack_sound_this_sequence = True

        if self.is_quacking:
            self.quack_display_timer -=1
            if self.quack_display_timer <= 0:
                self.is_quacking = False
                self.played_quack_sound_this_sequence = False # Reset for next quack

        if self.hit_cooldown > 0: self.hit_cooldown -= 1

    def hit_ball(self, ball):
        if self.hit_cooldown <= 0:
            if self.play_sound_func:
                 self.play_sound_func("duck_hit_ball")
            # Modify ball velocity and spin based on duck constants
            ball.velocity[0] *= random.uniform(0.7, -1.2) # Random horizontal effect
            ball.velocity[1] += random.uniform(-CRAZY_DUCK_HIT_STRENGTH_Y * 0.7, CRAZY_DUCK_HIT_STRENGTH_Y * 0.7)
            ball.spin_y += random.uniform(-CRAZY_DUCK_HIT_SPIN * 0.8, CRAZY_DUCK_HIT_SPIN * 0.8)
            ball.spin_y = max(-BALL_MAX_SPIN, min(BALL_MAX_SPIN, ball.spin_y))
            ball.last_hit_paddle_instance = None # Duck hit resets last paddle hit
            self.hit_cooldown = 20 # Cooldown before duck can hit again
            self.velocity[1] *= -1 # Duck reverses direction on hit
            return True
        return False

    def hit_paddle(self, paddle): # Ducks still don't interact with paddles
        return False

    def draw_quack(self, surface):
        if self.is_quacking:
            quack_text = self.quack_font.render("QUACK!", True, BLACK)
            x = self.rect.centerx - quack_text.get_width() / 2
            y = self.rect.top - quack_text.get_height() - 3 # Position above the duck
            surface.blit(quack_text, (x, y))

# --- PowerUp class remains the same ---
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y): # play_sound_func will be passed to collected method
        super().__init__()
        self.image = pygame.Surface([POWERUP_SIZE, POWERUP_SIZE], pygame.SRCALPHA)
        self.color = get_random_crazy_color(200)
        pygame.draw.rect(self.image, self.color, (0, 0, POWERUP_SIZE, POWERUP_SIZE), border_radius=5)
        try: font = pygame.font.SysFont("Impact", int(POWERUP_SIZE * 0.7))
        except pygame.error: font = pygame.font.Font(None, int(POWERUP_SIZE * 0.8))
        text_surf = font.render("?", True, WHITE)
        self.image.blit(text_surf, text_surf.get_rect(center=(POWERUP_SIZE/2, POWERUP_SIZE/2)))
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha_pulse_dir = -5
        self.current_alpha = 255

    def update(self, main_ball_rect=None, time_tick=0):
        self.current_alpha += self.alpha_pulse_dir
        if self.current_alpha <= 150 or self.current_alpha >= 255:
            self.alpha_pulse_dir *= -1
            self.current_alpha = max(150, min(255, self.current_alpha))
        self.image.set_alpha(self.current_alpha)
        # Magnet effect adjusted for new config constants
        if main_ball_rect:
            dx = main_ball_rect.centerx - self.rect.centerx
            dy = main_ball_rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if 0 < distance < POWERUP_MAGNET_RANGE:
                # Move towards the ball if within range
                move_speed = POWERUP_MAGNET_SPEED * (1 - distance / POWERUP_MAGNET_RANGE) # Faster when closer
                self.rect.x += (dx / distance) * move_speed
                self.rect.y += (dy / distance) * move_speed


    def collected(self, collecting_paddle, other_paddle, balls_sprite_group, main_ball_ref,
                  impact_particles_group, current_tick, play_sound_func): # Added play_sound_func
        actual_type = random.choice(ALL_POWERUP_TYPES)
        self.kill()
        indicator = POWERUP_DISPLAY_NAMES.get(actual_type, actual_type.upper().replace("_"," ") + "!")

        general_collect_sound_name = "powerup_collect" # Default
        good_for_self_types = ["paddle_big_self", "shield_self", "sticky_paddle_self",
                               "curve_ball_self", "laser_shot_self", "point_shield_self",
                               "ball_ghost_self", "paddle_teleport_self", "repel_field_self",
                               "ball_split_self"]
        bad_for_opponent_types = ["opp_freeze", "slow_opponent", "confuse_opponent_controls",
                                  "opponent_paddle_shrink"]
        bad_for_self_types = ["paddle_small_self"]

        if actual_type in good_for_self_types or actual_type in bad_for_opponent_types:
            general_collect_sound_name = "powerup_collect_good"
        elif actual_type in bad_for_self_types:
            general_collect_sound_name = "powerup_collect_bad"

        # Apply effects and play specific activation sounds for immediate/global effects
        if actual_type == "paddle_big_self":
            collecting_paddle.add_effect(actual_type, POWERUP_GENERAL_DURATION, intensity=POWERUP_PADDLE_HEIGHT_BIG, display_text=indicator, start_tick=current_tick)
        elif actual_type == "paddle_small_self":
            collecting_paddle.add_effect(actual_type, POWERUP_GENERAL_DURATION, intensity=POWERUP_PADDLE_HEIGHT_SMALL, display_text=indicator, start_tick=current_tick)
        elif actual_type == "multi_ball":
            if play_sound_func: play_sound_func("multi_ball") # Specific sound for this action
            collecting_paddle.add_effect(actual_type, POWERUP_SHORT_DURATION, display_text=indicator, start_tick=current_tick) # Indicator
            for _ in range(POWERUP_MULTIBALL_COUNT):
                new_ball = Ball(BALL_RADIUS_NORMAL, play_sound_func=play_sound_func, # Pass sound func to new balls
                                laser_channel=collecting_paddle.laser_channel, # Pass relevant sound params
                                laser_sound=collecting_paddle.laser_sound)
                new_ball.is_main_ball = False
                new_ball.rect.centerx = collecting_paddle.rect.centerx + random.randint(-20,20)
                new_ball.rect.centery = collecting_paddle.rect.centery + random.randint(-PADDLE_HEIGHT_NORMAL//2, PADDLE_HEIGHT_NORMAL//2)
                dir_x = 1 if collecting_paddle.player_num == 0 else -1
                new_ball.velocity = [dir_x * (BALL_INITIAL_SPEED_X * random.uniform(0.8,1.2)), random.uniform(-BALL_INITIAL_SPEED_X,BALL_INITIAL_SPEED_X)]
                new_ball.current_speed_x_magnitude = abs(new_ball.velocity[0])
                balls_sprite_group.add(new_ball)
                if hasattr(collecting_paddle, 'all_sprites_ref'): # If game's all_sprites is accessible
                    collecting_paddle.all_sprites_ref.add(new_ball)

        elif actual_type == "ball_fast_all":
            if play_sound_func: play_sound_func("ball_fast")
            for ball_obj in balls_sprite_group: ball_obj.activate_speed_boost(POWERUP_SHORT_DURATION)
            collecting_paddle.add_effect(actual_type, POWERUP_SHORT_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "opp_freeze":
            other_paddle.add_effect("freeze", PADDLE_FREEZE_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("freeze"), start_tick=current_tick)
            collecting_paddle.add_effect(actual_type, POWERUP_SHORT_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "ball_invis_all":
            if play_sound_func: play_sound_func("ball_invis")
            for ball_obj in balls_sprite_group: ball_obj.activate_invisibility(POWERUP_GENERAL_DURATION)
            collecting_paddle.add_effect(actual_type, POWERUP_GENERAL_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "shield_self":
            collecting_paddle.add_effect("shield", POWERUP_GENERAL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("shield"), start_tick=current_tick)
        elif actual_type == "slow_opponent":
            other_paddle.add_effect("slow", POWERUP_GENERAL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("slow"), start_tick=current_tick)
            collecting_paddle.add_effect(actual_type, POWERUP_GENERAL_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "sticky_paddle_self":
            collecting_paddle.add_effect("sticky", STICKY_BALL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("sticky"), start_tick=current_tick)
        elif actual_type == "curve_ball_self":
            collecting_paddle.add_effect("curve_shot_ready", POWERUP_GENERAL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("curve_shot_ready"), start_tick=current_tick)
        elif actual_type == "laser_shot_self": # This makes the PADDLE ready for a laser shot
            collecting_paddle.add_effect("laser_shot", POWERUP_GENERAL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("laser_shot"), start_tick=current_tick)
        elif actual_type == "confuse_opponent_controls":
            other_paddle.add_effect("confused_controls", PADDLE_CONFUSE_CONTROLS_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("confused_controls"), start_tick=current_tick)
            collecting_paddle.add_effect(actual_type, PADDLE_CONFUSE_CONTROLS_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "point_shield_self":
            collecting_paddle.add_effect("point_shield", -1, display_text=POWERUP_DISPLAY_NAMES.get("point_shield"), start_tick=current_tick) # -1 for indefinite until used
        elif actual_type == "ball_size_toggle_all":
            if play_sound_func: play_sound_func("ball_size_toggle")
            new_size = random.choice([BALL_RADIUS_BIG, BALL_RADIUS_SMALL])
            for ball_obj in balls_sprite_group: ball_obj.activate_size_change(POWERUP_GENERAL_DURATION, new_size)
            collecting_paddle.add_effect(actual_type, POWERUP_GENERAL_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "rainbow_ball_all":
            if play_sound_func: play_sound_func("rainbow_ball")
            for ball_obj in balls_sprite_group: ball_obj.activate_rainbow_effect(POWERUP_GENERAL_DURATION)
            collecting_paddle.add_effect(actual_type, POWERUP_GENERAL_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "opponent_paddle_shrink":
            other_paddle.add_effect("shrunken_by_opponent", OPPONENT_PADDLE_SHRINK_DURATION, intensity=OPPONENT_PADDLE_SHRINK_HEIGHT, display_text=POWERUP_DISPLAY_NAMES.get("shrunken_by_opponent"), start_tick=current_tick)
            collecting_paddle.add_effect(actual_type, POWERUP_SHORT_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "ball_ghost_self": # Paddle ready for ghost shot
            collecting_paddle.add_effect("ghost_shot_ready", POWERUP_GENERAL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("ghost_shot_ready"), start_tick=current_tick)
        elif actual_type == "paddle_teleport_self": # Immediate effect
            collecting_paddle.teleport_self(balls_sprite_group) # teleport_self will play its sound
            collecting_paddle.add_effect(actual_type, 20, display_text=indicator, start_tick=current_tick) # Short indicator
        elif actual_type == "repel_field_self":
            collecting_paddle.add_effect("repel_field", REPEL_FIELD_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("repel_field"), start_tick=current_tick)
        elif actual_type == "ball_split_self": # Paddle ready for split
            collecting_paddle.add_effect("ball_split_ready", POWERUP_GENERAL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("ball_split_ready"), start_tick=current_tick)
        elif actual_type == "ball_teleport_all":
            if play_sound_func: play_sound_func("ball_teleport")
            for ball_obj in balls_sprite_group: ball_obj.teleport_random(impact_particles_group)
            collecting_paddle.add_effect(actual_type, POWERUP_SHORT_DURATION, display_text=indicator, start_tick=current_tick)

        return actual_type, general_collect_sound_name # Return for game.py to play general sound


# --- Paddle class remains the same ---
class Paddle(pygame.sprite.Sprite):
    def __init__(self, width, height, player_num, game_tick_ref_func, play_sound_func=None): # Added play_sound_func
        super().__init__()
        self.player_num = player_num
        self.base_width = width
        self.base_height = height # Now uses value from config
        self.current_height = self.base_height
        # Adjust initial x based on potentially wider screen/paddle
        self.initial_x_pos = 40 if player_num == 0 else SCREEN_WIDTH - 40 - width
        self.rect = pygame.Rect(self.initial_x_pos, (SCREEN_HEIGHT - self.current_height) // 2, self.base_width, self.current_height)
        self.initial_y = self.rect.y
        self.speed_y_for_spin = 0
        self.last_y = self.rect.y

        self.active_effects = []
        self.get_current_tick = game_tick_ref_func
        self.play_sound_func = play_sound_func # Store the sound playing function

        self.laser_channel = None
        self.laser_sound = None
        self.all_sprites_ref = None

        self.shield_sprite = None
        self.stuck_ball = None
        self.powerup_indicator_text = ""
        self._update_visuals()

    def _get_effect(self, effect_name):
        for effect in self.active_effects:
            if effect.name == effect_name: return effect
        return None

    def has_effect(self, effect_name):
        return self._get_effect(effect_name) is not None

    def add_effect(self, name, duration_frames, intensity=None, display_text="", start_tick=None, allow_stacking=False):
        if start_tick is None: start_tick = self.get_current_tick()
        if not allow_stacking:
            existing_effect = self._get_effect(name)
            if existing_effect: self.active_effects.remove(existing_effect)

        effect = Effect(name, duration_frames, intensity, start_tick, display_text or POWERUP_DISPLAY_NAMES.get(name, name.upper().replace("_"," ") + "!"))
        self.active_effects.append(effect)

        # Play sound associated with this effect starting
        if self.play_sound_func:
            sound_map = {
                "paddle_big_self": "paddle_big", "paddle_small_self": "paddle_small",
                "shrunken_by_opponent": "paddle_small", "freeze": "opp_freeze",
                "shield": "shield_activate", "slow": "slow_opponent",
                "sticky": "sticky_paddle", "curve_shot_ready": "curve_ball_ready",
                "laser_shot": "curve_ball_ready", # Placeholder sound
                "confused_controls": "confuse_controls", "point_shield": "point_shield_activate",
                "repel_field": "repel_field",
            }
            if name in sound_map:
                self.play_sound_func(sound_map[name])

        self._update_effects_state()
        self._update_visuals()

    def remove_effect(self, effect_name):
        initial_len = len(self.active_effects)
        self.active_effects = [eff for eff in self.active_effects if eff.name != effect_name]
        if len(self.active_effects) < initial_len:
            self._update_effects_state()
            self._update_visuals()

    def _update_effects_state(self):
        self.current_height = self.base_height # Start with base height from config
        shrunken_effect = self._get_effect("shrunken_by_opponent")
        big_effect = self._get_effect("paddle_big_self")
        small_effect = self._get_effect("paddle_small_self")

        # Apply size effects based on constants from config
        if shrunken_effect: self.current_height = OPPONENT_PADDLE_SHRINK_HEIGHT
        elif big_effect: self.current_height = POWERUP_PADDLE_HEIGHT_BIG
        elif small_effect: self.current_height = POWERUP_PADDLE_HEIGHT_SMALL

        if not self.has_effect("sticky") and self.stuck_ball:
            self.stuck_ball.is_stuck = False
            self.stuck_ball = None

        if self.has_effect("shield") and not self.shield_sprite: self._create_shield_sprite()
        elif not self.has_effect("shield") and self.shield_sprite:
            self.shield_sprite.kill()
            self.shield_sprite = None

        self._update_powerup_indicator()

    def _update_powerup_indicator(self):
        negative_effects_priority = ["freeze", "stunned_by_duck", "confused_controls", "shrunken_by_opponent", "slow"]
        for neg_eff_name in negative_effects_priority:
            if self.has_effect(neg_eff_name):
                self.powerup_indicator_text = POWERUP_DISPLAY_NAMES.get(neg_eff_name, neg_eff_name.upper() + "!")
                return

        most_recent_beneficial_effect = None
        latest_start_tick = -1
        for effect in reversed(self.active_effects): # Most recently added is last
            is_negative_handled_above = effect.name in negative_effects_priority
            if effect.display_text and not is_negative_handled_above:
                if effect.start_tick >= latest_start_tick:
                    latest_start_tick = effect.start_tick
                    most_recent_beneficial_effect = effect

        if most_recent_beneficial_effect:
            self.powerup_indicator_text = most_recent_beneficial_effect.display_text
        else:
            self.powerup_indicator_text = ""

    def _create_shield_sprite(self):
        if self.shield_sprite: self.shield_sprite.kill()
        self.shield_sprite = pygame.sprite.Sprite()
        # Use SHIELD_SIZE from config
        self.shield_sprite.image = pygame.Surface(SHIELD_SIZE, pygame.SRCALPHA)
        shield_base_color = COLOR_SHIELD if COLOR_SHIELD else BLUE
        self.shield_sprite.image.fill(shield_base_color + (150,)) # Alpha for shield color
        pygame.draw.rect(self.shield_sprite.image, WHITE + (200,), self.shield_sprite.image.get_rect(), 2, border_radius=3)
        self.shield_sprite.rect = self.shield_sprite.image.get_rect()
        self._position_shield_sprite()
        if hasattr(self, 'all_sprites_ref') and self.all_sprites_ref is not None:
             self.all_sprites_ref.add(self.shield_sprite)

    def _position_shield_sprite(self):
        if self.shield_sprite:
            # Use SHIELD_OFFSET and SHIELD_SIZE from config
            shield_x = self.rect.right + SHIELD_OFFSET if self.player_num == 0 else self.rect.left - SHIELD_OFFSET - SHIELD_SIZE[0]
            self.shield_sprite.rect.topleft = (shield_x, self.rect.centery - SHIELD_SIZE[1]//2)

    def reset_all_effects(self, keep_effects_named=None):
        if keep_effects_named is None: keep_effects_named = []
        effects_to_keep_instances = []
        for name_to_keep in keep_effects_named:
            effect_instance = self._get_effect(name_to_keep)
            if effect_instance: effects_to_keep_instances.append(effect_instance)

        self.active_effects = effects_to_keep_instances
        if self.stuck_ball and not self.has_effect("sticky"):
            self.stuck_ball.is_stuck = False
            self.stuck_ball = None
        self._update_effects_state()
        self._update_visuals()

    def _update_visuals(self):
        old_center = self.rect.center
        self.current_height = int(self.current_height) # Ensure int
        self.image = pygame.Surface([self.base_width, self.current_height], pygame.SRCALPHA)
        color_rgb = list(COLOR_PADDLE_BASE if COLOR_PADDLE_BASE else BLUE)
        alpha = 255; border_color = WHITE

        if self.has_effect("paddle_small_self") or self.has_effect("shrunken_by_opponent"): color_rgb = [max(0, c-30) for c in color_rgb[:3]]
        if self.has_effect("shrunken_by_opponent"): border_color = RED; color_rgb = [max(0, c-60) for c in color_rgb[:3]]
        if self.has_effect("freeze") or self.has_effect("stunned_by_duck"): alpha = 100; border_color = (100, 100, 200)
        elif self.has_effect("slow"): alpha = 180; border_color = (200, 200, 100)
        elif self.has_effect("repel_field"): border_color = CYAN

        final_color = tuple(max(0, min(255, int(c))) for c in color_rgb) + (alpha,)
        self.image.fill(final_color)
        pygame.draw.rect(self.image, border_color, (0, 0, self.base_width, self.current_height), PADDLE_BORDER_WIDTH, border_radius=3)

        self.rect = self.image.get_rect(center=old_center)
        self.rect.x = self.initial_x_pos
        # Ensure paddle stays within new screen bounds
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.current_height))
        if self.shield_sprite: self._position_shield_sprite()

    def update_timers_and_effects(self):
        current_tick = self.get_current_tick()
        active_effects_before_update = len(self.active_effects)
        self.active_effects = [eff for eff in self.active_effects if eff.is_active(current_tick)]
        if len(self.active_effects) < active_effects_before_update:
            self._update_effects_state()
            self._update_visuals()
        self._update_powerup_indicator()

    def update_movement_state(self):
        self.speed_y_for_spin = self.rect.y - self.last_y
        self.last_y = self.rect.y

    def can_move(self):
        return not (self.has_effect("freeze") or self.has_effect("stunned_by_duck"))

    def move(self, direction, speed):
        if not self.can_move(): return
        # Use speed from config (PLAYER_PADDLE_SPEED or PLAYER_2_PADDLE_SPEED)
        base_speed = speed # Passed in speed should be from config
        current_speed = base_speed * (PADDLE_SLOW_FACTOR if self.has_effect("slow") else 1.0)
        move_direction = direction * (-1 if self.has_effect("confused_controls") else 1)
        self.rect.y += move_direction * current_speed
        # Clamp position based on new SCREEN_HEIGHT and current_height
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.current_height))
        if self.shield_sprite: self._position_shield_sprite()

    def ai_move(self, balls_group, difficulty):
        if not self.can_move(): return
        target_ball = None; closest_distance = float('inf')
        # AI logic to find target ball (remains largely the same concept)
        for ball in balls_group:
            moving_towards_ai = (self.player_num == 1 and ball.velocity[0] > 0) or \
                                (self.player_num == 0 and ball.velocity[0] < 0)
            on_ais_side_or_approaching = (self.player_num == 1 and ball.rect.centerx > SCREEN_WIDTH / 3) or \
                                         (self.player_num == 0 and ball.rect.centerx < SCREEN_WIDTH * 2 / 3)

            if moving_towards_ai or on_ais_side_or_approaching:
                effective_distance = abs(ball.rect.centerx - self.rect.centerx) + abs(ball.rect.centery - self.rect.centery) * 0.75
                if effective_distance < closest_distance:
                    closest_distance = effective_distance
                    target_ball = ball

        if not target_ball and balls_group:
            for ball in balls_group:
                dist = math.hypot(ball.rect.centerx - self.rect.centerx, ball.rect.centery - self.rect.centery)
                if dist < closest_distance:
                    closest_distance = dist
                    target_ball = ball

        if target_ball:
            target_y = target_ball.rect.centery
            # Use AI speeds from config
            ai_speed_map = {DIFFICULTY_EASY: AI_PADDLE_SPEED_EASY,
                            DIFFICULTY_MEDIUM: AI_PADDLE_SPEED_MEDIUM,
                            DIFFICULTY_HARD: AI_PADDLE_SPEED_HARD}
            ai_base_speed = ai_speed_map.get(difficulty, AI_PADDLE_SPEED_MEDIUM)

            # Adjust target based on difficulty
            if difficulty == DIFFICULTY_EASY: target_y += random.uniform(-self.current_height * 0.45, self.current_height * 0.45)
            elif difficulty == DIFFICULTY_MEDIUM: target_y += random.uniform(-self.current_height * 0.25, self.current_height * 0.25)

            # Hard difficulty prediction (adjust for screen size if needed, though logic is relative)
            if difficulty == DIFFICULTY_HARD and abs(target_ball.velocity[0]) > 0.1:
                 try:
                     time_to_reach_paddle_x = abs(self.rect.centerx - target_ball.rect.centerx) / abs(target_ball.velocity[0])
                     predicted_y = target_ball.rect.centery + target_ball.velocity[1] * time_to_reach_paddle_x
                     if abs(target_ball.spin_y) > 0.5:
                         predicted_y += target_ball.spin_y * BALL_SPIN_EFFECT_ON_CURVE * time_to_reach_paddle_x * 0.5
                     target_y = max(self.current_height / 2, min(SCREEN_HEIGHT - self.current_height / 2, predicted_y))
                     target_y += random.uniform(-self.current_height * 0.1, self.current_height * 0.1)
                 except ZeroDivisionError:
                      pass # Keep target_y as ball's current y if velocity[0] is zero

            actual_ai_speed = ai_base_speed * (PADDLE_SLOW_FACTOR if self.has_effect("slow") else 1.0)
            # Move towards target_y
            if abs(self.rect.centery - target_y) > actual_ai_speed:
                move_dir = 1 if self.rect.centery < target_y else -1
                self.move(move_dir, actual_ai_speed) # Use the move method
        else: # No ball, center paddle
             actual_ai_speed = AI_PADDLE_SPEED_EASY * (PADDLE_SLOW_FACTOR if self.has_effect("slow") else 1.0)
             if abs(self.rect.centery - SCREEN_HEIGHT // 2) > actual_ai_speed:
                 move_dir = 1 if self.rect.centery < SCREEN_HEIGHT // 2 else -1
                 self.move(move_dir, actual_ai_speed)


    def teleport_self(self, balls_group):
        if self.play_sound_func:
            self.play_sound_func("paddle_teleport")
        ball_to_follow = None
        if balls_group:
            my_side_balls = [b for b in balls_group if (self.player_num == 0 and b.rect.centerx < SCREEN_WIDTH / 2) or \
                                                    (self.player_num == 1 and b.rect.centerx > SCREEN_WIDTH / 2)]
            if my_side_balls: ball_to_follow = random.choice(my_side_balls)
            elif balls_group: ball_to_follow = random.choice(list(balls_group))

        if ball_to_follow: self.rect.centery = ball_to_follow.rect.centery
        else: self.rect.centery = random.randint(self.current_height // 2, SCREEN_HEIGHT - self.current_height // 2)

        # Clamp position after teleport
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.current_height))
        self._update_visuals() # Ensure shield moves with paddle


# --- Ball class remains the same ---
class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, play_sound_func=None, laser_channel=None, laser_sound=None): # Added sound params
        super().__init__()
        self.base_radius = radius # Use radius from config
        self.current_radius = radius
        self.image = pygame.Surface([self.current_radius * 2, self.current_radius * 2], pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self.base_speed_x = BALL_INITIAL_SPEED_X # Use speed from config
        self.current_speed_x_magnitude = self.base_speed_x
        self.velocity = [0, 0]
        self.spin_y = 0

        self.trail_positions = []
        self.last_hit_by_timer = 0
        self.last_hit_paddle_instance = None
        self.is_main_ball = False
        self.last_scored_on_player = None # Track for serve direction

        self.speed_boost_timer = 0; self.speed_boost_active = False
        self.invisibility_timer = 0; self.is_invisible_flicker = False; self.flicker_countdown = 0
        self.size_change_timer = 0
        self.is_stuck = False
        self.rainbow_effect_timer = 0

        self.is_laser_shot = False
        self.laser_sound_playing = False # To track laser loop state

        self.is_ghost_ball = False
        self.ghost_ball_timer = 0
        self.ghost_can_pass_paddle = True # For one-time pass through

        self.play_sound_func = play_sound_func
        self.laser_channel = laser_channel
        self.laser_sound = laser_sound # This is the loaded Sound object for laser_shot_loop

        self._update_visuals()
        self.reset(initial_spawn=False)

    def _update_visuals(self, current_time_tick=0):
        draw_radius = max(int(self.current_radius), 1)
        # Ensure surface size matches radius
        new_surface_size = (draw_radius * 2, draw_radius * 2)
        if self.image.get_size() != new_surface_size:
            self.image = pygame.Surface(new_surface_size, pygame.SRCALPHA)
            # Keep current center when resizing surface
            current_center = self.rect.center
            self.rect = self.image.get_rect(center=current_center)
        else:
            self.image.fill((0,0,0,0)) # Clear existing surface

        ball_color_rgb = COLOR_BALL_BASE
        if self.is_laser_shot: ball_color_rgb = LASER_SHOT_COLOR

        if self.rainbow_effect_timer > 0:
            hue = (current_time_tick * 7 + random.randint(0,10)) % 360
            c = pygame.Color(0)
            c.hsva = (hue, 100, 100, 100)
            ball_color_rgb = (c.r, c.g, c.b)

        r, g, b = ball_color_rgb
        if not self.is_laser_shot: # Spin coloration
            factor = min(1, abs(self.spin_y) / BALL_MAX_SPIN)
            if self.spin_y > 0.5:
                r = min(255, int(r + 80*factor)); g = int(g*(1-0.5*factor)); b = int(b*(1-0.7*factor))
            elif self.spin_y < -0.5:
                r = int(r*(1-0.7*factor)); g = int(g*(1-0.3*factor)); b = min(255, int(b+80*factor))

        final_color_rgb = (max(0,min(255,int(r))), max(0,min(255,int(g))), max(0,min(255,int(b))))
        alpha = 255
        if self.invisibility_timer > 0: alpha = BALL_INVISIBILITY_ALPHA if self.is_invisible_flicker else 180
        elif self.is_ghost_ball: alpha = GHOST_BALL_ALPHA

        pygame.draw.circle(self.image, final_color_rgb + (alpha,), (draw_radius, draw_radius), draw_radius)
        pygame.draw.circle(self.image, WHITE + (alpha,), (draw_radius, draw_radius), draw_radius, 1) # Outline

        # Update rect size if radius changed, keeping center
        current_center = self.rect.center
        self.rect = self.image.get_rect(center=current_center)


    def update(self, rally_active_for_speedup, current_time_tick):
        if self.is_stuck:
            self._update_visuals(current_time_tick)
            return

        # Timers
        if self.last_hit_by_timer > 0: self.last_hit_by_timer -= 1
        if self.last_hit_by_timer == 0: self.last_hit_paddle_instance = None

        if self.speed_boost_timer > 0: self.speed_boost_timer -= 1
        if self.speed_boost_timer == 0 and self.speed_boost_active: self.deactivate_speed_boost()

        if self.invisibility_timer > 0:
            self.invisibility_timer -= 1
            self.flicker_countdown -= 1
            if self.flicker_countdown <= 0:
                self.is_invisible_flicker = not self.is_invisible_flicker
                self.flicker_countdown = BALL_INVISIBILITY_FLICKER_RATE
            if self.invisibility_timer == 0: self.is_invisible_flicker = False

        if self.size_change_timer > 0: self.size_change_timer -= 1
        if self.size_change_timer == 0 and self.current_radius != self.base_radius:
            self.current_radius = self.base_radius # Revert to base size from config

        if self.rainbow_effect_timer > 0: self.rainbow_effect_timer -= 1

        if self.ghost_ball_timer > 0: self.ghost_ball_timer -= 1
        if self.ghost_ball_timer == 0 and self.is_ghost_ball:
            self.is_ghost_ball = False
            self.ghost_can_pass_paddle = True

        # Laser sound loop
        if self.is_laser_shot and not self.laser_sound_playing and self.laser_sound and self.laser_channel:
            self.laser_channel.play(self.laser_sound, loops=-1)
            self.laser_sound_playing = True
        elif not self.is_laser_shot and self.laser_sound_playing and self.laser_channel:
            self.laser_channel.stop()
            self.laser_sound_playing = False

        # Trail
        trail_len_mod = 0.5 if self.is_laser_shot else 1.0
        max_trail_len = int(BALL_TRAIL_LENGTH_GHOST * trail_len_mod) # Use constant from config
        self.trail_positions.append((self.rect.center, abs(self.spin_y), self.rainbow_effect_timer > 0, self.is_laser_shot))
        if len(self.trail_positions) > max_trail_len: self.trail_positions.pop(0)

        # Movement Physics
        if not self.is_laser_shot: # Apply spin curve
            self.velocity[1] += self.spin_y * BALL_SPIN_EFFECT_ON_CURVE # Use constant from config
            self.spin_y *= BALL_SPIN_DECAY # Use constant from config
            if abs(self.spin_y) < 0.1: self.spin_y = 0
        else:
            self.spin_y = 0 # Laser shots ignore spin

        self._update_visuals(current_time_tick) # Update visuals after physics changes

        # Apply velocity
        mult = (BALL_SPEED_BOOST_MULTIPLIER if self.speed_boost_active else 1.0) * \
               (LASER_SHOT_SPEED_MULTIPLIER if self.is_laser_shot else 1.0)
        self.rect.x += self.velocity[0] * mult
        self.rect.y += self.velocity[1] * mult

        # Rally speed increase
        if rally_active_for_speedup and abs(self.velocity[0]) < BALL_MAX_SPEED_X and \
           not self.speed_boost_active and not self.is_laser_shot:
            self.current_speed_x_magnitude = min(BALL_MAX_SPEED_X, self.current_speed_x_magnitude + BALL_SPEED_INCREMENT_RALLY)
            self.velocity[0] = math.copysign(self.current_speed_x_magnitude, self.velocity[0])

    def activate_speed_boost(self, duration):
        self.speed_boost_timer = duration
        self.speed_boost_active = True
        if self.play_sound_func: self.play_sound_func("ball_fast")

    def deactivate_speed_boost(self):
        self.speed_boost_active = False

    def activate_invisibility(self, duration):
        self.invisibility_timer = duration
        self.is_invisible_flicker = True
        self.flicker_countdown = BALL_INVISIBILITY_FLICKER_RATE
        if self.play_sound_func: self.play_sound_func("ball_invis")

    def activate_size_change(self, duration, new_radius):
        self.size_change_timer = duration
        self.current_radius = new_radius
        if self.play_sound_func: self.play_sound_func("ball_size_toggle")
        self._update_visuals() # Update visuals immediately after size change

    def activate_rainbow_effect(self, duration):
        self.rainbow_effect_timer = duration
        if self.play_sound_func: self.play_sound_func("rainbow_ball")

    def activate_laser_shot(self):
        self.is_laser_shot = True
        # Loop sound started in update()

    def activate_ghost_mode(self, duration):
        self.is_ghost_ball = True
        self.ghost_ball_timer = duration
        self.ghost_can_pass_paddle = True
        if self.play_sound_func: self.play_sound_func("ball_ghost")
        self._update_visuals()

    def teleport_random(self, particle_group):
        if self.play_sound_func: self.play_sound_func("ball_teleport")
        old_center = self.rect.center
        margin = self.current_radius + 30 # Increased margin for larger screen
        self.rect.centerx = random.randint(margin, SCREEN_WIDTH - margin)
        self.rect.centery = random.randint(margin, SCREEN_HEIGHT - margin)
        create_impact_particles(old_center[0], old_center[1], particle_group, "teleport_vanish")
        create_impact_particles(self.rect.centerx, self.rect.centery, particle_group, "teleport_appear")

    def reset(self, initial_spawn=False, scored_on_player=None, start_static=False):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + random.randint(-60, 60)) # Wider random Y range
        self.current_speed_x_magnitude = self.base_speed_x # Use base speed from config

        # Reset effects
        self.deactivate_speed_boost()
        self.invisibility_timer = 0; self.is_invisible_flicker = False
        self.size_change_timer = 0; self.current_radius = self.base_radius # Use base radius from config
        self.is_stuck = False
        self.rainbow_effect_timer = 0

        if self.is_laser_shot and self.laser_channel and self.laser_sound_playing:
            self.laser_channel.stop()
        self.is_laser_shot = False; self.laser_sound_playing = False

        self.is_ghost_ball = False; self.ghost_ball_timer = 0; self.ghost_can_pass_paddle = True

        # Set velocity
        if start_static:
            self.velocity = [0, 0]
        else:
            direction_x = 1 if scored_on_player == 1 else -1 # Serve towards player who was scored on
            self.velocity = [direction_x * self.current_speed_x_magnitude,
                             random.uniform(-self.current_speed_x_magnitude * 0.6, self.current_speed_x_magnitude * 0.6)]

        self.spin_y = 0
        self.trail_positions = []
        self.last_hit_paddle_instance = None
        self.last_hit_by_timer = 0
        if initial_spawn: self.is_main_ball = True
        self.last_scored_on_player = scored_on_player # Store for reference if needed

        self._update_visuals() # Update visuals after reset

    # Helper methods added dynamically in game.py
    # def stick_to_paddle(self, paddle): ...
    # def launch_from_paddle(self, paddle): ...

