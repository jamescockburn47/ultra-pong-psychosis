# sprites.py — Updated with Duck & Paddle Indicator Fixes, Spin Dynamics

import pygame
import random
import math
from config import *
from utils import create_impact_particles, get_random_crazy_color

class Effect:
    def __init__(self, name, duration_frames, intensity=None, start_tick=0, display_text=""):
        self.name = name
        self.duration_frames = duration_frames
        self.intensity = intensity
        self.start_tick = start_tick
        self.display_text = display_text
    def is_active(self, current_tick):
        if self.duration_frames <= 0: return True
        return current_tick < self.start_tick + self.duration_frames
    def __repr__(self):
        return f"Effect(name='{self.name}', duration={self.duration_frames}, intensity={self.intensity}, start_tick={self.start_tick})"

class Particle(pygame.sprite.Sprite):
    # ... (Particle class remains the same) ...
    def __init__(self, x, y, color_func, size_range=(2,6), speed_range=(1,PARTICLE_SPEED_IMPACT), lifespan_mod=0):
        super().__init__()
        size = random.randint(*size_range)
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        self.color_val = color_func() if callable(color_func) else color_func
        initial_color_fill = self.color_val if len(self.color_val) == 4 else self.color_val + (255,)
        self.image.fill(initial_color_fill)
        self.rect = self.image.get_rect(center=(x, y))
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        self.velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
        self.lifespan = PARTICLE_LIFESPAN_IMPACT + random.randint(-5,5) + lifespan_mod
        self.initial_lifespan = max(self.lifespan, 1)
    def update(self):
        self.rect.x += self.velocity[0]; self.rect.y += self.velocity[1]; self.lifespan -= 1
        alpha = max(0, int(255 * (self.lifespan / self.initial_lifespan)))
        draw_size = self.image.get_width(); self.image = pygame.Surface([draw_size, draw_size], pygame.SRCALPHA)
        base_color = self.color_val[:3] if len(self.color_val) >= 3 else (self.color_val[0],) * 3
        current_color_tuple = base_color + (alpha,); self.image.fill(current_color_tuple)
        if self.lifespan <= 0: self.kill()

class DistractorSprite(pygame.sprite.Sprite):
    # ... (DistractorSprite class remains largely the same, used as base for Duck) ...
    def __init__(self):
        super().__init__()
        size = random.randint(20, 60); self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        hue = random.randint(0,360); color = pygame.Color(0,0,0,0); hsva_alpha = int((180 / 255.0) * 100)
        color.hsva = (hue % 361, 100, 100, hsva_alpha)
        shape_type = random.choice(["rect", "circle", "poly"])
        if shape_type == "rect": pygame.draw.rect(self.image, color, (0,0,size,size), border_radius=size//4)
        elif shape_type == "circle": pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        else: points = [(random.randint(0,size), random.randint(0,size)) for _ in range(random.randint(3,5))]; pygame.draw.polygon(self.image, color, points)
        self.rect = self.image.get_rect()
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top": self.rect.bottom = 0; self.rect.centerx = random.randint(0,SCREEN_WIDTH)
        elif edge == "bottom": self.rect.top = SCREEN_HEIGHT; self.rect.centerx = random.randint(0,SCREEN_WIDTH)
        elif edge == "left": self.rect.right = 0; self.rect.centery = random.randint(0,SCREEN_HEIGHT)
        else: self.rect.left = SCREEN_WIDTH; self.rect.centery = random.randint(0,SCREEN_HEIGHT)
        angle_to_centerish = math.atan2(SCREEN_HEIGHT/2 - self.rect.centery, SCREEN_WIDTH/2 - self.rect.centerx)
        actual_angle = angle_to_centerish + random.uniform(-math.pi/3, math.pi/3)
        speed = random.uniform(*DISTRACTOR_SPEED_RANGE)
        self.velocity = [math.cos(actual_angle) * speed, math.sin(actual_angle) * speed]
        self.rotation_speed = random.uniform(-5, 5); self.angle = 0; self.original_image = self.image.copy()
    def update(self, time_tick=0):
        self.rect.x += self.velocity[0]; self.rect.y += self.velocity[1]
        self.angle = (self.angle + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if not pygame.Rect(-100, -100, SCREEN_WIDTH+200, SCREEN_HEIGHT+200).colliderect(self.rect): self.kill()

class CrazyDuckSprite(DistractorSprite):
    """A special distractor sprite (duck) that now moves vertically and doesn't hit paddles."""
    def __init__(self):
        super().__init__() # Calls DistractorSprite init for basic setup
        self.size = random.randint(40, 65) # Slightly smaller ducks
        self.original_image = pygame.Surface([self.size, self.size], pygame.SRCALPHA)
        # --- Duck Drawing (simplified from previous, ensure it's complete in your actual code) ---
        body_color = COLOR_DUCK; beak_color = ORANGE; eye_color = BLACK
        body_rect = pygame.Rect(self.size*0.1, self.size*0.35, self.size*0.8, self.size*0.55)
        pygame.draw.ellipse(self.original_image, body_color, body_rect)
        head_center = (int(self.size*0.75), int(self.size*0.3))
        pygame.draw.circle(self.original_image, body_color, head_center, int(self.size*0.22))
        beak_tip_x = head_center[0] + int(self.size*0.25)
        beak_points = [(head_center[0] + int(self.size*0.15), head_center[1] - int(self.size*0.08)), (beak_tip_x, head_center[1]), (head_center[0] + int(self.size*0.15), head_center[1] + int(self.size*0.08))]
        pygame.draw.polygon(self.original_image, beak_color, beak_points)
        pygame.draw.circle(self.original_image, eye_color, (head_center[0] + int(self.size*0.05), head_center[1] - int(self.size*0.05)), int(self.size*0.05))
        # --- End Duck Drawing ---
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect() # Get initial rect from size

        # --- New Vertical Movement Logic ---
        self.velocity = [0, random.uniform(CRAZY_DUCK_VERTICAL_SPEED_RANGE[0], CRAZY_DUCK_VERTICAL_SPEED_RANGE[1])]
        if random.choice([True, False]): # 50% chance to start moving upwards
            self.velocity[1] *= -1
        
        # Spawn at random horizontal position, either top or bottom
        self.rect.centerx = random.randint(self.size // 2, SCREEN_WIDTH - self.size // 2)
        if self.velocity[1] > 0: # Moving downwards, spawn at top
            self.rect.bottom = 0
        else: # Moving upwards, spawn at bottom
            self.rect.top = SCREEN_HEIGHT
        
        self.rotation_speed = random.uniform(-3, 3) # Slower rotation
        self.angle = random.uniform(0, 360) # Random initial angle

        self.quack_timer = random.randint(60,150); self.is_quacking = False; self.quack_display_timer = 0
        try: self.quack_font = pygame.font.SysFont("Arial", 16, True)
        except pygame.error: self.quack_font = pygame.font.Font(None, 20)
        self.hit_cooldown = 0

    def update(self, current_time_tick):
        self.rect.y += self.velocity[1] # Vertical movement
        self.angle = (self.angle + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Kill if it moves far off-screen vertically
        if self.velocity[1] > 0 and self.rect.top > SCREEN_HEIGHT + self.size: self.kill()
        elif self.velocity[1] < 0 and self.rect.bottom < -self.size: self.kill()

        self.quack_timer -= 1
        if self.quack_timer <= 0:
            self.is_quacking = True; self.quack_display_timer = random.randint(25, 45)
            self.quack_timer = random.randint(80, 220)
        if self.is_quacking:
            self.quack_display_timer -=1
            if self.quack_display_timer <= 0: self.is_quacking = False
        if self.hit_cooldown > 0: self.hit_cooldown -= 1

    def hit_ball(self, ball):
        if self.hit_cooldown <= 0:
            # Ducks still affect ball, but maybe less dramatically or differently
            ball.velocity[0] *= random.uniform(0.7, -1.2) # Can reverse or dampen X
            ball.velocity[1] += random.uniform(-CRAZY_DUCK_HIT_STRENGTH_Y * 0.7, CRAZY_DUCK_HIT_STRENGTH_Y * 0.7)
            ball.spin_y += random.uniform(-CRAZY_DUCK_HIT_SPIN * 0.8, CRAZY_DUCK_HIT_SPIN * 0.8)
            ball.spin_y = max(-BALL_MAX_SPIN, min(BALL_MAX_SPIN, ball.spin_y))
            ball.last_hit_paddle_instance = None 
            self.hit_cooldown = 20 # Shorter cooldown as they don't stun paddles
            # Flip duck's vertical direction on hit
            self.velocity[1] *= -1 
            return True
        return False

    def hit_paddle(self, paddle):
        """Ducks no longer interact with paddles."""
        return False # Does nothing

    def draw_quack(self, surface):
        if self.is_quacking:
            quack_text = self.quack_font.render("QUACK!", True, BLACK)
            x = self.rect.centerx - quack_text.get_width() / 2
            y = self.rect.top - quack_text.get_height() - 3 # Closer to duck
            surface.blit(quack_text, (x, y))

class PowerUp(pygame.sprite.Sprite):
    # ... (PowerUp class remains the same as in sprites_refactor_effects) ...
    def __init__(self, x, y):
        super().__init__(); self.image = pygame.Surface([POWERUP_SIZE, POWERUP_SIZE], pygame.SRCALPHA)
        self.color = get_random_crazy_color(200); pygame.draw.rect(self.image, self.color, (0, 0, POWERUP_SIZE, POWERUP_SIZE), border_radius=5)
        try: font = pygame.font.SysFont("Impact", int(POWERUP_SIZE * 0.7))
        except pygame.error: font = pygame.font.Font(None, int(POWERUP_SIZE * 0.8))
        text_surf = font.render("?", True, WHITE); self.image.blit(text_surf, text_surf.get_rect(center=(POWERUP_SIZE/2, POWERUP_SIZE/2)))
        self.rect = self.image.get_rect(center=(x, y)); self.alpha_pulse_dir = -5; self.current_alpha = 255
    def update(self, main_ball_rect=None, time_tick=0):
        self.current_alpha += self.alpha_pulse_dir
        if self.current_alpha <= 150 or self.current_alpha >= 255: self.alpha_pulse_dir *= -1; self.current_alpha = max(150, min(255, self.current_alpha))
        self.image.set_alpha(self.current_alpha)
        if main_ball_rect:
            dx = main_ball_rect.centerx - self.rect.centerx; dy = main_ball_rect.centery - self.rect.centery; distance = math.hypot(dx, dy)
            if 0 < distance < POWERUP_MAGNET_RANGE: self.rect.x += (dx / distance) * POWERUP_MAGNET_SPEED; self.rect.y += (dy / distance) * POWERUP_MAGNET_SPEED
    def collected(self, collecting_paddle, other_paddle, balls_sprite_group, main_ball_ref, impact_particles_group, current_tick):
        actual_type = random.choice(ALL_POWERUP_TYPES); self.kill()
        indicator = POWERUP_DISPLAY_NAMES.get(actual_type, actual_type.upper().replace("_"," ") + "!") # Default indicator if not in map
        # --- Power-up effects application using add_effect ---
        # (This logic is extensive and assumed to be mostly correct from previous version, ensure all actual_type map to an effect name or direct ball manipulation)
        if actual_type == "paddle_big_self": collecting_paddle.add_effect(actual_type, POWERUP_GENERAL_DURATION, intensity=POWERUP_PADDLE_HEIGHT_BIG, display_text=indicator, start_tick=current_tick)
        elif actual_type == "paddle_small_self": collecting_paddle.add_effect(actual_type, POWERUP_GENERAL_DURATION, intensity=POWERUP_PADDLE_HEIGHT_SMALL, display_text=indicator, start_tick=current_tick)
        elif actual_type == "multi_ball":
            collecting_paddle.add_effect(actual_type, POWERUP_SHORT_DURATION, display_text=indicator, start_tick=current_tick)
            for _ in range(POWERUP_MULTIBALL_COUNT): # Create new balls
                new_ball = Ball(BALL_RADIUS_NORMAL); new_ball.is_main_ball = False
                new_ball.rect.centerx = collecting_paddle.rect.centerx + random.randint(-20,20); new_ball.rect.centery = collecting_paddle.rect.centery + random.randint(-PADDLE_HEIGHT_NORMAL//2, PADDLE_HEIGHT_NORMAL//2)
                dir_x = 1 if collecting_paddle.player_num == 0 else -1
                new_ball.velocity = [dir_x * (BALL_INITIAL_SPEED_X * random.uniform(0.8,1.2)), random.uniform(-BALL_INITIAL_SPEED_X,BALL_INITIAL_SPEED_X)]
                new_ball.current_speed_x_magnitude = abs(new_ball.velocity[0]); balls_sprite_group.add(new_ball) # Game.py needs to add to all_sprites
        elif actual_type == "ball_fast_all":
            for ball_obj in balls_sprite_group: ball_obj.activate_speed_boost(POWERUP_SHORT_DURATION)
            collecting_paddle.add_effect(actual_type, POWERUP_SHORT_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "opp_freeze":
            other_paddle.add_effect("freeze", PADDLE_FREEZE_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("freeze"), start_tick=current_tick)
            collecting_paddle.add_effect(actual_type, POWERUP_SHORT_DURATION, display_text=indicator, start_tick=current_tick) # Indicator for collector
        elif actual_type == "ball_invis_all":
            for ball_obj in balls_sprite_group: ball_obj.activate_invisibility(POWERUP_GENERAL_DURATION)
            collecting_paddle.add_effect(actual_type, POWERUP_GENERAL_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "shield_self": collecting_paddle.add_effect("shield", POWERUP_GENERAL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("shield"), start_tick=current_tick)
        elif actual_type == "slow_opponent":
            other_paddle.add_effect("slow", POWERUP_GENERAL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("slow"), start_tick=current_tick)
            collecting_paddle.add_effect(actual_type, POWERUP_GENERAL_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "sticky_paddle_self": collecting_paddle.add_effect("sticky", STICKY_BALL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("sticky"), start_tick=current_tick)
        elif actual_type == "curve_ball_self": collecting_paddle.add_effect("curve_shot_ready", POWERUP_GENERAL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("curve_shot_ready"), start_tick=current_tick)
        elif actual_type == "laser_shot_self": collecting_paddle.add_effect("laser_shot", POWERUP_GENERAL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("laser_shot"), start_tick=current_tick)
        elif actual_type == "confuse_opponent_controls":
            other_paddle.add_effect("confused_controls", PADDLE_CONFUSE_CONTROLS_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("confused_controls"), start_tick=current_tick)
            collecting_paddle.add_effect(actual_type, PADDLE_CONFUSE_CONTROLS_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "point_shield_self": collecting_paddle.add_effect("point_shield", -1, display_text=POWERUP_DISPLAY_NAMES.get("point_shield"), start_tick=current_tick)
        elif actual_type == "ball_size_toggle_all":
            new_size = random.choice([BALL_RADIUS_BIG, BALL_RADIUS_SMALL])
            for ball_obj in balls_sprite_group: ball_obj.activate_size_change(POWERUP_GENERAL_DURATION, new_size)
            collecting_paddle.add_effect(actual_type, POWERUP_GENERAL_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "rainbow_ball_all":
            for ball_obj in balls_sprite_group: ball_obj.activate_rainbow_effect(POWERUP_GENERAL_DURATION)
            collecting_paddle.add_effect(actual_type, POWERUP_GENERAL_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "opponent_paddle_shrink":
            other_paddle.add_effect("shrunken_by_opponent", OPPONENT_PADDLE_SHRINK_DURATION, intensity=OPPONENT_PADDLE_SHRINK_HEIGHT, display_text=POWERUP_DISPLAY_NAMES.get("shrunken_by_opponent"), start_tick=current_tick)
            collecting_paddle.add_effect(actual_type, POWERUP_SHORT_DURATION, display_text=indicator, start_tick=current_tick)
        elif actual_type == "ball_ghost_self": collecting_paddle.add_effect("ghost_shot_ready", POWERUP_GENERAL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("ghost_shot_ready"), start_tick=current_tick)
        elif actual_type == "paddle_teleport_self":
            collecting_paddle.add_effect(actual_type, 20, display_text=indicator, start_tick=current_tick) # Short indicator
            collecting_paddle.teleport_self(balls_sprite_group)
        elif actual_type == "repel_field_self": collecting_paddle.add_effect("repel_field", REPEL_FIELD_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("repel_field"), start_tick=current_tick)
        elif actual_type == "ball_split_self": collecting_paddle.add_effect("ball_split_ready", POWERUP_GENERAL_DURATION, display_text=POWERUP_DISPLAY_NAMES.get("ball_split_ready"), start_tick=current_tick)
        elif actual_type == "ball_teleport_all":
            collecting_paddle.add_effect(actual_type, POWERUP_SHORT_DURATION, display_text=indicator, start_tick=current_tick)
            for ball_obj in balls_sprite_group: ball_obj.teleport_random(impact_particles_group)
        return actual_type

class Paddle(pygame.sprite.Sprite):
    def __init__(self, width, height, player_num, game_tick_ref_func):
        # ... (Paddle __init__ remains the same) ...
        super().__init__(); self.player_num = player_num; self.base_width = width; self.base_height = height
        self.current_height = height; self.initial_x_pos = 30 if player_num == 0 else SCREEN_WIDTH - 30 - width
        self.rect = pygame.Rect(self.initial_x_pos, (SCREEN_HEIGHT - self.current_height) // 2, self.base_width, self.current_height)
        self.initial_y = self.rect.y; self.speed_y_for_spin = 0; self.last_y = self.rect.y
        self.active_effects = []; self.get_current_tick = game_tick_ref_func
        self.shield_sprite = None; self.stuck_ball = None; self.powerup_indicator_text = ""
        self._update_visuals()
    def _get_effect(self, effect_name):
        for effect in self.active_effects:
            if effect.name == effect_name: return effect
        return None
    def has_effect(self, effect_name): return self._get_effect(effect_name) is not None
    def add_effect(self, name, duration_frames, intensity=None, display_text="", start_tick=None, allow_stacking=False):
        # ... (add_effect remains the same) ...
        if start_tick is None: start_tick = self.get_current_tick()
        if not allow_stacking:
            existing_effect = self._get_effect(name)
            if existing_effect: self.active_effects.remove(existing_effect)
        effect = Effect(name, duration_frames, intensity, start_tick, display_text or POWERUP_DISPLAY_NAMES.get(name, name.upper().replace("_"," ") + "!"))
        self.active_effects.append(effect); self._update_effects_state(); self._update_visuals()
    def remove_effect(self, effect_name):
        # ... (remove_effect remains the same) ...
        initial_len = len(self.active_effects)
        self.active_effects = [eff for eff in self.active_effects if eff.name != effect_name]
        if len(self.active_effects) < initial_len: self._update_effects_state(); self._update_visuals()
    
    def _update_effects_state(self):
        # ... (Paddle _update_effects_state remains the same) ...
        self.current_height = self.base_height
        shrunken_effect = self._get_effect("shrunken_by_opponent"); big_effect = self._get_effect("paddle_big_self"); small_effect = self._get_effect("paddle_small_self")
        if shrunken_effect and shrunken_effect.intensity is not None: self.current_height = shrunken_effect.intensity
        elif big_effect and big_effect.intensity is not None: self.current_height = big_effect.intensity
        elif small_effect and small_effect.intensity is not None: self.current_height = small_effect.intensity
        if not self.has_effect("sticky") and self.stuck_ball: self.stuck_ball.is_stuck = False; self.stuck_ball = None
        if self.has_effect("shield") and not self.shield_sprite: self._create_shield_sprite()
        elif not self.has_effect("shield") and self.shield_sprite: self.shield_sprite.kill(); self.shield_sprite = None
        self._update_powerup_indicator()

    def _update_powerup_indicator(self):
        """Updates the powerup_indicator_text based on active effects.
           Prioritizes negative status effects, then the most recent beneficial one.
        """
        # Highest priority: Negative status effects that have specific display names in POWERUP_DISPLAY_NAMES
        if self.has_effect("freeze"): self.powerup_indicator_text = POWERUP_DISPLAY_NAMES.get("freeze", "FROZEN!"); return
        if self.has_effect("stunned_by_duck"): self.powerup_indicator_text = POWERUP_DISPLAY_NAMES.get("stunned_by_duck", "STUNNED!"); return
        if self.has_effect("confused_controls"): self.powerup_indicator_text = POWERUP_DISPLAY_NAMES.get("confused_controls", "CONFUSED!"); return
        if self.has_effect("shrunken_by_opponent"): self.powerup_indicator_text = POWERUP_DISPLAY_NAMES.get("shrunken_by_opponent", "SHRUNKEN!"); return
        if self.has_effect("slow"): self.powerup_indicator_text = POWERUP_DISPLAY_NAMES.get("slow", "SLOWED!"); return

        most_recent_beneficial_effect = None
        latest_start_tick = -1
        # Iterate in reverse to find the most recently added effect first
        for effect in reversed(self.active_effects):
            is_negative_handled_above = effect.name in ["freeze", "stunned_by_duck", "confused_controls", "shrunken_by_opponent", "slow"]
            if effect.display_text and not is_negative_handled_above:
                # Check if this effect is more recent or equally recent (preferring the one found first in reversed list)
                if effect.start_tick >= latest_start_tick: # Use >= to catch effects added on same tick
                    latest_start_tick = effect.start_tick
                    most_recent_beneficial_effect = effect
                    # If we want strictly the newest, we can break after finding the first one in reversed iteration.
                    # For now, this ensures the one with highest start_tick, or last added on same tick, is chosen.
        
        if most_recent_beneficial_effect:
            self.powerup_indicator_text = most_recent_beneficial_effect.display_text
        else:
            self.powerup_indicator_text = ""
            
    def _create_shield_sprite(self):
        # ... (Paddle _create_shield_sprite remains the same) ...
        if self.shield_sprite: self.shield_sprite.kill()
        self.shield_sprite = pygame.sprite.Sprite(); self.shield_sprite.image = pygame.Surface(SHIELD_SIZE, pygame.SRCALPHA)
        self.shield_sprite.image.fill((COLOR_SHIELD if COLOR_SHIELD else BLUE) + (150,))
        pygame.draw.rect(self.shield_sprite.image, WHITE + (200,), self.shield_sprite.image.get_rect(), 2, border_radius=3)
        self.shield_sprite.rect = self.shield_sprite.image.get_rect(); self._position_shield_sprite()
    def _position_shield_sprite(self):
        # ... (Paddle _position_shield_sprite remains the same) ...
        if self.shield_sprite:
            shield_x = self.rect.right + SHIELD_OFFSET if self.player_num == 0 else self.rect.left - SHIELD_OFFSET - SHIELD_SIZE[0]
            self.shield_sprite.rect.topleft = (shield_x, self.rect.centery - SHIELD_SIZE[1]//2)
    def reset_all_effects(self, keep_effects_named=None):
        # ... (Paddle reset_all_effects remains the same) ...
        if keep_effects_named is None: keep_effects_named = []
        effects_to_keep_instances = []
        for name_to_keep in keep_effects_named:
            effect_instance = self._get_effect(name_to_keep)
            if effect_instance: effects_to_keep_instances.append(effect_instance)
        self.active_effects = effects_to_keep_instances
        if self.stuck_ball and not self.has_effect("sticky"): self.stuck_ball.is_stuck = False; self.stuck_ball = None
        self._update_effects_state(); self._update_visuals()
    def _update_visuals(self):
        # ... (Paddle _update_visuals remains the same, ensure current_height is int) ...
        old_center = self.rect.center; self.current_height = int(self.current_height) # Ensure int for Surface
        self.image = pygame.Surface([self.base_width, self.current_height], pygame.SRCALPHA)
        color_rgb = list(COLOR_PADDLE_BASE if COLOR_PADDLE_BASE else BLUE); alpha = 255; border_color = WHITE
        if self.has_effect("paddle_small_self") or self.has_effect("shrunken_by_opponent"): color_rgb = [max(0, c-30) for c in color_rgb[:3]]
        if self.has_effect("shrunken_by_opponent"): border_color = RED; color_rgb = [max(0, c-60) for c in color_rgb[:3]]
        if self.has_effect("freeze") or self.has_effect("stunned_by_duck"): alpha = 100; border_color = (100, 100, 200)
        elif self.has_effect("slow"): alpha = 180; border_color = (200, 200, 100)
        elif self.has_effect("repel_field"): border_color = CYAN
        final_color = tuple(max(0, min(255, int(c))) for c in color_rgb) + (alpha,)
        self.image.fill(final_color)
        pygame.draw.rect(self.image, border_color, (0, 0, self.base_width, self.current_height), PADDLE_BORDER_WIDTH, border_radius=3)
        self.rect = self.image.get_rect(center=old_center); self.rect.x = self.initial_x_pos
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.current_height))
        if self.shield_sprite: self._position_shield_sprite()
    def update_timers_and_effects(self):
        # ... (Paddle update_timers_and_effects remains the same) ...
        current_tick = self.get_current_tick(); active_effects_before_update = len(self.active_effects)
        self.active_effects = [eff for eff in self.active_effects if eff.is_active(current_tick)]
        if len(self.active_effects) < active_effects_before_update: self._update_effects_state(); self._update_visuals()
        self._update_powerup_indicator()
    def update_movement_state(self):
        # ... (Paddle update_movement_state remains the same) ...
        self.speed_y_for_spin = self.rect.y - self.last_y; self.last_y = self.rect.y
    def can_move(self): return not (self.has_effect("freeze") or self.has_effect("stunned_by_duck"))
    def move(self, direction, speed):
        # ... (Paddle move remains the same) ...
        if not self.can_move(): return
        current_speed = speed * (PADDLE_SLOW_FACTOR if self.has_effect("slow") else 1.0)
        move_direction = direction * (-1 if self.has_effect("confused_controls") else 1)
        self.rect.y += move_direction * current_speed
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.current_height))
        if self.shield_sprite: self._position_shield_sprite()
    def ai_move(self, balls_group, difficulty):
        # ... (Paddle ai_move remains the same) ...
        if not self.can_move(): return
        target_ball = None; closest_distance = float('inf')
        for ball in balls_group:
            moving_towards_ai = (self.player_num == 1 and ball.velocity[0] > 0) or (self.player_num == 0 and ball.velocity[0] < 0)
            in_central_zone = (SCREEN_WIDTH / 3 < ball.rect.centerx < SCREEN_WIDTH * 2 / 3)
            if moving_towards_ai or in_central_zone:
                effective_distance = abs(ball.rect.centerx - self.rect.centerx) + abs(ball.rect.centery - self.rect.centery) * 0.5
                if effective_distance < closest_distance: closest_distance = effective_distance; target_ball = ball
        if target_ball:
            target_y = target_ball.rect.centery
            ai_speed_map = {DIFFICULTY_EASY: AI_PADDLE_SPEED_EASY, DIFFICULTY_MEDIUM: AI_PADDLE_SPEED_MEDIUM, DIFFICULTY_HARD: AI_PADDLE_SPEED_HARD}
            ai_base_speed = ai_speed_map.get(difficulty, AI_PADDLE_SPEED_MEDIUM)
            if difficulty == DIFFICULTY_EASY: target_y += random.uniform(-self.current_height * 0.45, self.current_height * 0.45)
            elif difficulty == DIFFICULTY_MEDIUM: target_y += random.uniform(-self.current_height * 0.25, self.current_height * 0.25)
            if difficulty == DIFFICULTY_HARD and abs(target_ball.velocity[0]) > 0.1:
                time_to_reach_paddle_x = abs(self.rect.centerx - target_ball.rect.centerx) / abs(target_ball.velocity[0])
                predicted_y = target_ball.rect.centery + target_ball.velocity[1] * time_to_reach_paddle_x
                target_y = max(self.current_height / 2, min(SCREEN_HEIGHT - self.current_height / 2, predicted_y))
                target_y += random.uniform(-self.current_height * 0.1, self.current_height * 0.1)
            actual_ai_speed = ai_base_speed * (PADDLE_SLOW_FACTOR if self.has_effect("slow") else 1.0)
            if abs(self.rect.centery - target_y) > actual_ai_speed:
                if self.rect.centery < target_y: self.move(1, actual_ai_speed)
                elif self.rect.centery > target_y: self.move(-1, actual_ai_speed)
        else:
             actual_ai_speed = AI_PADDLE_SPEED_EASY * (PADDLE_SLOW_FACTOR if self.has_effect("slow") else 1.0)
             if abs(self.rect.centery - SCREEN_HEIGHT // 2) > actual_ai_speed:
                 if self.rect.centery < SCREEN_HEIGHT // 2: self.move(1, actual_ai_speed)
                 else: self.move(-1, actual_ai_speed)
    def teleport_self(self, balls_group):
        # ... (Paddle teleport_self remains the same) ...
        ball_to_follow = None
        if balls_group:
            my_side_balls = [b for b in balls_group if (self.player_num == 0 and b.rect.centerx < SCREEN_WIDTH / 2) or (self.player_num == 1 and b.rect.centerx > SCREEN_WIDTH / 2)]
            if my_side_balls: ball_to_follow = random.choice(my_side_balls)
            elif balls_group: ball_to_follow = random.choice(list(balls_group))
        if ball_to_follow: self.rect.centery = ball_to_follow.rect.centery
        else: self.rect.centery = random.randint(self.current_height // 2, SCREEN_HEIGHT - self.current_height // 2)
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.current_height)); self._update_visuals()

class Ball(pygame.sprite.Sprite):
    # ... (Ball class remains largely the same as in sprites_refactor_effects, with minor visual/reset tweaks) ...
    def __init__(self, radius):
        super().__init__(); self.base_radius = radius; self.current_radius = radius
        self.image = pygame.Surface([self.current_radius * 2, self.current_radius * 2], pygame.SRCALPHA); self.rect = self.image.get_rect()
        self.base_speed_x = BALL_INITIAL_SPEED_X; self.current_speed_x_magnitude = self.base_speed_x; self.velocity = [0, 0]; self.spin_y = 0
        self.trail_positions = []; self.last_hit_by_timer = 0; self.last_hit_paddle_instance = None; self.is_main_ball = False
        self.speed_boost_timer = 0; self.speed_boost_active = False; self.invisibility_timer = 0; self.is_invisible_flicker = False; self.flicker_countdown = 0
        self.size_change_timer = 0; self.is_stuck = False; self.rainbow_effect_timer = 0; self.is_laser_shot = False
        self.is_ghost_ball = False; self.ghost_ball_timer = 0; self.ghost_can_pass_paddle = True
        self._update_visuals(); self.reset(initial_spawn=False)
    def _update_visuals(self, current_time_tick=0): # Visuals update based on state
        draw_radius = max(int(self.current_radius), 1); self.image = pygame.Surface([draw_radius * 2, draw_radius * 2], pygame.SRCALPHA); self.image.fill((0,0,0,0))
        ball_color_rgb = COLOR_BALL_BASE;
        if self.is_laser_shot: ball_color_rgb = LASER_SHOT_COLOR
        if self.rainbow_effect_timer > 0: hue = (current_time_tick * 7 + random.randint(0,10)) % 360; c = pygame.Color(0); c.hsva = (hue, 100, 100, 255); ball_color_rgb = (c.r, c.g, c.b)
        r, g, b = ball_color_rgb
        if not self.is_laser_shot:
            factor = min(1, abs(self.spin_y) / BALL_MAX_SPIN)
            if self.spin_y > 0.5: r = min(255, int(r + 80*factor)); g = int(g*(1-0.5*factor)); b = int(b*(1-0.7*factor))
            elif self.spin_y < -0.5: r = int(r*(1-0.7*factor)); g = int(g*(1-0.3*factor)); b = min(255, int(b+80*factor))
        final_color_rgb = (max(0,min(255,int(r))), max(0,min(255,int(g))), max(0,min(255,int(b))))
        alpha = 255
        if self.invisibility_timer > 0: alpha = BALL_INVISIBILITY_ALPHA if self.is_invisible_flicker else 180
        elif self.is_ghost_ball: alpha = GHOST_BALL_ALPHA
        pygame.draw.circle(self.image, final_color_rgb + (alpha,), (draw_radius, draw_radius), draw_radius)
        pygame.draw.circle(self.image, WHITE + (alpha,), (draw_radius, draw_radius), draw_radius, 1)
        current_center = self.rect.center if hasattr(self, 'rect') and self.rect else (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        self.rect = self.image.get_rect(center=current_center)
    def update(self, rally_active_for_speedup, current_time_tick): # Ball update logic
        if self.is_stuck: self._update_visuals(current_time_tick); return
        if self.last_hit_by_timer > 0: self.last_hit_by_timer -= 1
        if self.last_hit_by_timer == 0: self.last_hit_paddle_instance = None
        if self.speed_boost_timer > 0: self.speed_boost_timer -= 1
        if self.speed_boost_timer == 0 and self.speed_boost_active: self.deactivate_speed_boost()
        if self.invisibility_timer > 0:
            self.invisibility_timer -= 1; self.flicker_countdown -= 1
            if self.flicker_countdown <= 0: self.is_invisible_flicker = not self.is_invisible_flicker; self.flicker_countdown = BALL_INVISIBILITY_FLICKER_RATE
            if self.invisibility_timer == 0: self.is_invisible_flicker = False
        if self.size_change_timer > 0: self.size_change_timer -= 1
        if self.size_change_timer == 0 and self.current_radius != self.base_radius: self.current_radius = self.base_radius
        if self.rainbow_effect_timer > 0: self.rainbow_effect_timer -= 1
        if self.ghost_ball_timer > 0: self.ghost_ball_timer -= 1
        if self.ghost_ball_timer == 0 and self.is_ghost_ball: self.is_ghost_ball = False; self.ghost_can_pass_paddle = True
        trail_len_mod = 0.5 if self.is_laser_shot else 1.0; max_trail_len = int(BALL_TRAIL_LENGTH_GHOST * trail_len_mod)
        self.trail_positions.append((self.rect.center, abs(self.spin_y), self.rainbow_effect_timer > 0, self.is_laser_shot))
        if len(self.trail_positions) > max_trail_len: self.trail_positions.pop(0)
        if not self.is_laser_shot:
            self.velocity[1] += self.spin_y * BALL_SPIN_EFFECT_ON_CURVE; self.spin_y *= BALL_SPIN_DECAY
            if abs(self.spin_y) < 0.1: self.spin_y = 0
        else: self.spin_y = 0
        self._update_visuals(current_time_tick)
        mult = (BALL_SPEED_BOOST_MULTIPLIER if self.speed_boost_active else 1.0) * (LASER_SHOT_SPEED_MULTIPLIER if self.is_laser_shot else 1.0)
        self.rect.x += self.velocity[0] * mult; self.rect.y += self.velocity[1] * mult
        if rally_active_for_speedup and abs(self.velocity[0]) < BALL_MAX_SPEED_X and not self.speed_boost_active and not self.is_laser_shot:
            self.current_speed_x_magnitude = min(BALL_MAX_SPEED_X, self.current_speed_x_magnitude + BALL_SPEED_INCREMENT_RALLY)
            self.velocity[0] = math.copysign(self.current_speed_x_magnitude, self.velocity[0])
    def activate_speed_boost(self, duration): self.speed_boost_timer = duration; self.speed_boost_active = True
    def deactivate_speed_boost(self): self.speed_boost_active = False
    def activate_invisibility(self, duration): self.invisibility_timer = duration; self.is_invisible_flicker = True; self.flicker_countdown = BALL_INVISIBILITY_FLICKER_RATE
    def activate_size_change(self, duration, new_radius): self.size_change_timer = duration; self.current_radius = new_radius
    def activate_rainbow_effect(self, duration): self.rainbow_effect_timer = duration
    def activate_ghost_mode(self, duration): self.is_ghost_ball = True; self.ghost_ball_timer = duration; self.ghost_can_pass_paddle = True; self._update_visuals()
    def teleport_random(self, particle_group):
        old_center = self.rect.center; margin = self.current_radius + 20
        self.rect.centerx = random.randint(margin, SCREEN_WIDTH - margin); self.rect.centery = random.randint(margin, SCREEN_HEIGHT - margin)
        create_impact_particles(old_center[0], old_center[1], particle_group, "teleport_vanish")
        create_impact_particles(self.rect.centerx, self.rect.centery, particle_group, "teleport_appear")
    def reset(self, initial_spawn=False, scored_on_player=None, start_static=False): # Ball reset logic
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + random.randint(-50, 50)); self.current_speed_x_magnitude = self.base_speed_x
        self.deactivate_speed_boost(); self.invisibility_timer = 0; self.is_invisible_flicker = False; self.size_change_timer = 0
        self.current_radius = self.base_radius; self.is_stuck = False; self.rainbow_effect_timer = 0; self.is_laser_shot = False
        self.is_ghost_ball = False; self.ghost_ball_timer = 0; self.ghost_can_pass_paddle = True
        if start_static: self.velocity = [0, 0]
        else:
            direction_x = random.choice([-1, 1])
            if scored_on_player == 0: direction_x = -1
            elif scored_on_player == 1: direction_x = 1
            self.velocity = [direction_x * self.current_speed_x_magnitude, random.uniform(-self.current_speed_x_magnitude * 0.6, self.current_speed_x_magnitude * 0.6)]
        self.spin_y = 0; self.trail_positions = []; self.last_hit_paddle_instance = None; self.last_hit_by_timer = 0
        if initial_spawn: self.is_main_ball = True
        self._update_visuals()
