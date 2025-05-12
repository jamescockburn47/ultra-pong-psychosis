# game.py — Updated with Power-up Fixes, Duck Logic, Spin, and other refinements

import pygame
import random
import sys
import math

from config import *
from sprites import Paddle, Ball, PowerUp, Particle, DistractorSprite, CrazyDuckSprite
from utils import get_random_crazy_color, draw_psychedelic_background, draw_text_adv, create_impact_particles


def main_game():
    """Main function to run the Ultra Pong Psychosis game."""
    global time_tick 
    global is_sudden_death_mode

    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    screen_actual = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ULTRA PONG PSYCHOSIS - CHAOS MODE")
    clock = pygame.time.Clock()

    time_tick = 0 

    player_paddle_left = Paddle(PADDLE_WIDTH, PADDLE_HEIGHT_NORMAL, 0, lambda: time_tick)
    player_paddle_right = Paddle(PADDLE_WIDTH, PADDLE_HEIGHT_NORMAL, 1, lambda: time_tick)

    all_sprites = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    active_powerups = pygame.sprite.Group()
    impact_particles = pygame.sprite.Group()
    distractor_sprites_group = pygame.sprite.Group()
    all_paddle_related_sprites = pygame.sprite.Group()

    all_paddle_related_sprites.add(player_paddle_left, player_paddle_right)

    main_ball = Ball(BALL_RADIUS_NORMAL)
    balls.add(main_ball)
    all_sprites.add(player_paddle_left, player_paddle_right, main_ball)

    current_state = STATE_START_MENU
    current_game_mode = GAME_MODE_AI
    game_difficulty = DIFFICULTY_MEDIUM
    score_a = 0
    score_b = 0
    winner_text = ""
    rally_ongoing = False

    countdown_timer = 0
    countdown_value = COUNTDOWN_INITIAL_VALUE
    is_sudden_death_mode = False

    def reset_internal_game_state_for_new_round(serve_to_player_idx=None):
        nonlocal main_ball, rally_ongoing 
        rally_ongoing = False
        for p in [player_paddle_left, player_paddle_right]:
            effects_to_keep = []
            if p.has_effect("shrunken_by_opponent"): # Keep shrunken status between rounds
                effects_to_keep.append("shrunken_by_opponent")
            p.reset_all_effects(keep_effects_named=effects_to_keep)

        balls.empty()
        active_powerups.empty()

        main_ball = Ball(BALL_RADIUS_NORMAL)
        player_who_was_scored_on = 1 if serve_to_player_idx == 0 else (0 if serve_to_player_idx == 1 else random.choice([0, 1]))
        main_ball.reset(initial_spawn=True, scored_on_player=player_who_was_scored_on, start_static=True)
        balls.add(main_ball)
        all_sprites.add(main_ball) # Ensure new ball is added to all_sprites for drawing

    def reset_game_full(new_game_state_after_reset=STATE_PLAYING):
        nonlocal score_a, score_b, winner_text, current_state, countdown_timer, countdown_value
        global is_sudden_death_mode
        score_a, score_b = 0, 0
        winner_text = ""
        is_sudden_death_mode = False
        player_paddle_left.rect.y = player_paddle_left.initial_y
        player_paddle_right.rect.y = player_paddle_right.initial_y
        player_paddle_left.reset_all_effects() # Full reset, no keeping effects
        player_paddle_right.reset_all_effects()
        distractor_sprites_group.empty()
        impact_particles.empty()
        active_powerups.empty()
        reset_internal_game_state_for_new_round(serve_to_player_idx=random.choice([0,1]))
        current_state = new_game_state_after_reset
        if new_game_state_after_reset == STATE_PLAYING:
            current_state = STATE_COUNTDOWN
            countdown_value = COUNTDOWN_INITIAL_VALUE
            countdown_timer = COUNTDOWN_FRAMES_PER_NUMBER

    button_rects_map = {}
    running = True
    while running:
        time_tick += 1
        mouse_pos = pygame.mouse.get_pos()
        keys_pressed_this_frame = pygame.key.get_pressed()

        all_paddle_related_sprites.empty()
        all_paddle_related_sprites.add(player_paddle_left, player_paddle_right)
        if player_paddle_left.shield_sprite: all_paddle_related_sprites.add(player_paddle_left.shield_sprite)
        if player_paddle_right.shield_sprite: all_paddle_related_sprites.add(player_paddle_right.shield_sprite)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ... (Escape key logic remains the same) ...
                    if current_state in [STATE_PLAYING, STATE_COUNTDOWN]: current_state = STATE_PAUSED
                    elif current_state == STATE_PAUSED: current_state = STATE_PLAYING if countdown_value <= 0 else STATE_COUNTDOWN
                    elif current_state in [STATE_GAME_OVER, STATE_INSTRUCTIONS, STATE_MODE_SELECT, STATE_AI_DIFFICULTY_SELECT]: reset_game_full(STATE_START_MENU)
                    elif current_state == STATE_START_MENU: running = False
                if current_state == STATE_PLAYING and event.key == pygame.K_p: current_state = STATE_PAUSED
                elif current_state == STATE_PAUSED and event.key == pygame.K_p: current_state = STATE_PLAYING if countdown_value <= 0 else STATE_COUNTDOWN
                
                if current_state == STATE_PLAYING:
                    if player_paddle_left.stuck_ball and event.key == pygame.K_SPACE:
                        player_paddle_left.stuck_ball.is_stuck = False
                        player_paddle_left.stuck_ball.velocity[0] = BALL_INITIAL_SPEED_X * 1.2 * (1 if player_paddle_left.player_num == 0 else -1)
                        player_paddle_left.stuck_ball.velocity[1] = random.uniform(-BALL_INITIAL_SPEED_X * 0.5, BALL_INITIAL_SPEED_X * 0.5)
                        player_paddle_left.stuck_ball.current_speed_x_magnitude = abs(player_paddle_left.stuck_ball.velocity[0])
                        player_paddle_left.stuck_ball = None
                        player_paddle_left.remove_effect("sticky")
                    if current_game_mode == GAME_MODE_2P and player_paddle_right.stuck_ball and event.key == pygame.K_RSHIFT:
                        player_paddle_right.stuck_ball.is_stuck = False
                        player_paddle_right.stuck_ball.velocity[0] = BALL_INITIAL_SPEED_X * 1.2 * (1 if player_paddle_right.player_num == 0 else -1)
                        player_paddle_right.stuck_ball.velocity[1] = random.uniform(-BALL_INITIAL_SPEED_X * 0.5, BALL_INITIAL_SPEED_X * 0.5)
                        player_paddle_right.stuck_ball.current_speed_x_magnitude = abs(player_paddle_right.stuck_ball.velocity[0])
                        player_paddle_right.stuck_ball = None
                        player_paddle_right.remove_effect("sticky")

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # ... (Mouse click logic for menus remains the same) ...
                clicked_button_key = None
                for key, rect in button_rects_map.items():
                    if rect and rect.collidepoint(mouse_pos): clicked_button_key = key; break
                if current_state == STATE_START_MENU:
                    if clicked_button_key == "start": current_state = STATE_MODE_SELECT
                    elif clicked_button_key == "instr": current_state = STATE_INSTRUCTIONS
                    elif clicked_button_key == "quit": running = False
                elif current_state == STATE_MODE_SELECT:
                    if clicked_button_key == "1p": current_game_mode = GAME_MODE_AI; current_state = STATE_AI_DIFFICULTY_SELECT
                    elif clicked_button_key == "2p": current_game_mode = GAME_MODE_2P; reset_game_full(STATE_PLAYING)
                elif current_state == STATE_AI_DIFFICULTY_SELECT:
                    if clicked_button_key == "easy": game_difficulty = DIFFICULTY_EASY
                    elif clicked_button_key == "medium": game_difficulty = DIFFICULTY_MEDIUM
                    elif clicked_button_key == "hard": game_difficulty = DIFFICULTY_HARD
                    if clicked_button_key in ["easy", "medium", "hard"]: reset_game_full(STATE_PLAYING)
                elif current_state == STATE_GAME_OVER:
                    if clicked_button_key == "play_again": reset_game_full(STATE_PLAYING)
                    elif clicked_button_key == "main_menu": reset_game_full(STATE_START_MENU)
                elif current_state == STATE_PAUSED:
                    if clicked_button_key == "resume": current_state = STATE_PLAYING if countdown_value <= 0 else STATE_COUNTDOWN
                    elif clicked_button_key == "restart_pause": reset_game_full(STATE_PLAYING)
                    elif clicked_button_key == "menu_pause": reset_game_full(STATE_START_MENU)
                elif current_state == STATE_INSTRUCTIONS:
                     if clicked_button_key == "return_from_instructions": reset_game_full(STATE_START_MENU)


        if current_state == STATE_COUNTDOWN:
            # ... (Countdown logic remains the same) ...
            if main_ball.alive(): main_ball.velocity = [0, 0]; main_ball.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            countdown_timer -= 1
            if countdown_timer <= 0:
                countdown_value -= 1
                if countdown_value <= 0:
                    current_state = STATE_PLAYING
                    if main_ball.alive(): main_ball.reset(scored_on_player=(main_ball.velocity[0] > 0 if main_ball.velocity[0] != 0 else random.choice([0, 1])), start_static=False)
                else: countdown_timer = COUNTDOWN_FRAMES_PER_NUMBER
        
        elif current_state == STATE_PLAYING:
            player_paddle_left.update_movement_state()
            player_paddle_right.update_movement_state()
            player_paddle_left.update_timers_and_effects()
            player_paddle_right.update_timers_and_effects()

            if player_paddle_left.can_move():
                # ... (P1 move logic)
                move_dir_left = 0
                if keys_pressed_this_frame[pygame.K_w]: move_dir_left = -1
                if keys_pressed_this_frame[pygame.K_s]: move_dir_left = 1
                if move_dir_left != 0: player_paddle_left.move(move_dir_left, PADDLE_SPEED)
            if player_paddle_right.can_move():
                if current_game_mode == GAME_MODE_2P:
                    # ... (P2 move logic)
                    move_dir_right = 0
                    if keys_pressed_this_frame[pygame.K_o]: move_dir_right = -1
                    if keys_pressed_this_frame[pygame.K_l]: move_dir_right = 1
                    if move_dir_right != 0: player_paddle_right.move(move_dir_right, PLAYER_2_PADDLE_SPEED)
                elif current_game_mode == GAME_MODE_AI:
                    player_paddle_right.ai_move(balls, game_difficulty)

            rally_ongoing = len(balls) > 0
            for ball_obj in list(balls):
                if not ball_obj.alive(): continue
                if ball_obj.is_stuck and ball_obj.last_hit_paddle_instance:
                    # ... (Sticky ball logic remains similar) ...
                    stuck_paddle = ball_obj.last_hit_paddle_instance
                    ball_obj.rect.centerx = stuck_paddle.rect.centerx + (stuck_paddle.base_width // 2 + ball_obj.current_radius + 2) * (1 if stuck_paddle.player_num == 0 else -1)
                    ball_obj.rect.centery = stuck_paddle.rect.centery
                    ball_obj.velocity = [0,0]; ball_obj.spin_y = 0
                    ball_obj.update(rally_ongoing, time_tick)
                    continue
                ball_obj.update(rally_ongoing, time_tick)

                # Ball - Wall Collision
                # ... (Wall collision logic remains the same) ...
                if ball_obj.rect.top <= 0: ball_obj.rect.top = 0; ball_obj.velocity[1] *= -1; create_impact_particles(ball_obj.rect.centerx, ball_obj.rect.top, impact_particles, "wall")
                if ball_obj.rect.bottom >= SCREEN_HEIGHT: ball_obj.rect.bottom = SCREEN_HEIGHT; ball_obj.velocity[1] *= -1; create_impact_particles(ball_obj.rect.centerx, ball_obj.rect.bottom, impact_particles, "wall")

                # Ball - Goal Collision
                scored_this_frame = False
                player_scored_on = -1 # -1 for no score, 0 for left, 1 for right

                if ball_obj.rect.left <= 0: # Player B (right) scores
                    if player_paddle_left.has_effect("point_shield"):
                        player_paddle_left.remove_effect("point_shield")
                        ball_obj.rect.left = 0; ball_obj.velocity[0] *= -1 # Bounce back
                        create_impact_particles(ball_obj.rect.left, ball_obj.rect.centery, impact_particles, "wall")
                    else:
                        score_b += 1; scored_this_frame = True; player_scored_on = 0
                        create_impact_particles(ball_obj.rect.left, ball_obj.rect.centery, impact_particles, "goal")
                elif ball_obj.rect.right >= SCREEN_WIDTH: # Player A (left) scores
                    if player_paddle_right.has_effect("point_shield"):
                        player_paddle_right.remove_effect("point_shield")
                        ball_obj.rect.right = SCREEN_WIDTH; ball_obj.velocity[0] *= -1 # Bounce back
                        create_impact_particles(ball_obj.rect.right, ball_obj.rect.centery, impact_particles, "wall")
                    else:
                        score_a += 1; scored_this_frame = True; player_scored_on = 1
                        create_impact_particles(ball_obj.rect.right, ball_obj.rect.centery, impact_particles, "goal")
                
                if scored_this_frame:
                    # ... (Scoring and game over logic remains similar) ...
                    if score_a >= WINNING_SCORE or score_b >= WINNING_SCORE:
                        if abs(score_a - score_b) < 2 and (score_a >= SUDDEN_DEATH_SCORE_THRESHOLD or score_b >= SUDDEN_DEATH_SCORE_THRESHOLD):
                            is_sudden_death_mode = True
                            if abs(score_a - score_b) >= 2: 
                                current_state = STATE_GAME_OVER; winner_text = f"Player {'Left' if score_a > score_b else 'Right'} Wins!"
                            else: 
                                reset_internal_game_state_for_new_round(serve_to_player_idx=player_scored_on); current_state = STATE_COUNTDOWN
                        else: 
                            current_state = STATE_GAME_OVER; winner_text = f"Player {'Left' if score_a > score_b else 'Right'} Wins!"
                    else: 
                        reset_internal_game_state_for_new_round(serve_to_player_idx=player_scored_on); current_state = STATE_COUNTDOWN
                    if current_state == STATE_GAME_OVER: balls.empty(); active_powerups.empty(); distractor_sprites_group.empty()
                    else: ball_obj.kill() # Kill the specific ball that scored

                # Ball - Paddle Collision
                for paddle in [player_paddle_left, player_paddle_right]:
                    if ball_obj.rect.colliderect(paddle.rect):
                        is_ghost_pass = ball_obj.is_ghost_ball and ball_obj.ghost_can_pass_paddle
                        if is_ghost_pass: ball_obj.ghost_can_pass_paddle = False
                        elif (paddle.player_num == 0 and ball_obj.velocity[0] < 0 and ball_obj.rect.right > paddle.rect.right - 5) or \
                             (paddle.player_num == 1 and ball_obj.velocity[0] > 0 and ball_obj.rect.left < paddle.rect.left + 5): # Added tolerance
                            if paddle.player_num == 0: ball_obj.rect.left = paddle.rect.right
                            else: ball_obj.rect.right = paddle.rect.left
                            ball_obj.velocity[0] *= -1
                            relative_hit_pos = (ball_obj.rect.centery - paddle.rect.centery) / (paddle.current_height / 2)
                            ball_obj.spin_y += relative_hit_pos * PADDLE_SPIN_FACTOR 
                            ball_obj.spin_y += paddle.speed_y_for_spin * PADDLE_EDGE_SPIN_FACTOR # Enhanced spin from paddle speed
                            ball_obj.spin_y = max(-BALL_MAX_SPIN, min(BALL_MAX_SPIN, ball_obj.spin_y))
                            ball_obj.current_speed_x_magnitude = min(BALL_MAX_SPEED_X, ball_obj.current_speed_x_magnitude + BALL_SPEED_INCREMENT_HIT)
                            ball_obj.velocity[0] = math.copysign(ball_obj.current_speed_x_magnitude, ball_obj.velocity[0])
                            ball_obj.last_hit_paddle_instance = paddle
                            ball_obj.last_hit_by_timer = BALL_LAST_HIT_TIMER_DURATION # Increased timer
                            create_impact_particles(ball_obj.rect.centerx, ball_obj.rect.centery, impact_particles, "paddle")
                            
                            # Handle paddle effects on ball hit
                            if paddle.has_effect("sticky") and not ball_obj.is_stuck:
                                ball_obj.is_stuck = True; paddle.stuck_ball = ball_obj
                            if paddle.has_effect("laser_shot"): ball_obj.is_laser_shot = True # Ball becomes laser
                            if paddle.has_effect("curve_shot_ready"): # Example for a "ready" effect
                                ball_obj.spin_y += random.uniform(-3,3) # Add extra random spin
                                paddle.remove_effect("curve_shot_ready") # Consume
                            if paddle.has_effect("ghost_shot_ready"):
                                ball_obj.activate_ghost_mode(GHOST_BALL_DURATION); paddle.remove_effect("ghost_shot_ready")
                            if paddle.has_effect("ball_split_ready"):
                                paddle.remove_effect("ball_split_ready")
                                # ... (Ball split logic remains similar) ...
                                for i in range(POWERUP_MULTIBALL_COUNT):
                                    new_ball = Ball(ball_obj.base_radius); new_ball.rect.center = ball_obj.rect.center
                                    angle_offset = random.uniform(-math.pi/7, math.pi/7) * (1 if i == 0 else -1)
                                    original_angle = math.atan2(ball_obj.velocity[1], ball_obj.velocity[0])
                                    new_angle = original_angle + angle_offset 
                                    new_ball_speed = ball_obj.current_speed_x_magnitude * 0.85
                                    new_ball.velocity = [math.cos(new_angle) * new_ball_speed, math.sin(new_angle) * new_ball_speed]
                                    new_ball.current_speed_x_magnitude = new_ball_speed
                                    new_ball.spin_y = ball_obj.spin_y * 0.5 + random.uniform(-1.5,1.5); new_ball.is_main_ball = False
                                    balls.add(new_ball); all_sprites.add(new_ball)
                            break 

                # Ball - Shield Collision
                # ... (Shield collision logic remains similar) ...
                for paddle in [player_paddle_left, player_paddle_right]:
                    if paddle.shield_sprite and ball_obj.rect.colliderect(paddle.shield_sprite.rect):
                        if (paddle.player_num == 0 and ball_obj.rect.right > paddle.shield_sprite.rect.right - 5) or \
                           (paddle.player_num == 1 and ball_obj.rect.left < paddle.shield_sprite.rect.left + 5):
                            if paddle.player_num == 0: ball_obj.rect.left = paddle.shield_sprite.rect.right
                            else: ball_obj.rect.right = paddle.shield_sprite.rect.left
                            ball_obj.velocity[0] *= -1.05 # Slightly faster bounce off shield
                            ball_obj.current_speed_x_magnitude = min(BALL_MAX_SPEED_X, ball_obj.current_speed_x_magnitude + BALL_SPEED_INCREMENT_HIT * 0.3)
                            ball_obj.velocity[0] = math.copysign(ball_obj.current_speed_x_magnitude, ball_obj.velocity[0])
                            create_impact_particles(ball_obj.rect.centerx, ball_obj.rect.centery, impact_particles, "wall")
                            break

                # Ball - Power-up Collision
                powerup_hit_list = pygame.sprite.spritecollide(ball_obj, active_powerups, True)
                for powerup in powerup_hit_list:
                    collecting_paddle = None; other_paddle = None
                    if ball_obj.last_hit_paddle_instance and ball_obj.last_hit_by_timer > 0:
                        collecting_paddle = ball_obj.last_hit_paddle_instance
                        other_paddle = player_paddle_right if collecting_paddle == player_paddle_left else player_paddle_left
                    elif len(balls) == 1 : # If only one ball, assign to closest paddle or last hitter if timer expired
                        dist_left = abs(powerup.rect.centerx - player_paddle_left.rect.centerx)
                        dist_right = abs(powerup.rect.centerx - player_paddle_right.rect.centerx)
                        if ball_obj.velocity[0] < 0 and dist_left < SCREEN_WIDTH * 0.6 : # Moving left, potentially for P1
                             collecting_paddle = player_paddle_left; other_paddle = player_paddle_right
                        elif ball_obj.velocity[0] > 0 and dist_right < SCREEN_WIDTH * 0.6: # Moving right
                             collecting_paddle = player_paddle_right; other_paddle = player_paddle_left
                        # else: powerup might not be collected if it's ambiguous

                    if collecting_paddle:
                        powerup.collected(collecting_paddle, other_paddle, balls, main_ball, impact_particles, time_tick)

                # Ball - Distractor (Duck) Collision
                duck_hit_list = pygame.sprite.spritecollide(ball_obj, distractor_sprites_group, False)
                for duck in duck_hit_list:
                    if isinstance(duck, CrazyDuckSprite) and duck.hit_ball(ball_obj):
                        create_impact_particles(ball_obj.rect.centerx, ball_obj.rect.centery, impact_particles, "generic")

                # Repel Field Effect
                # ... (Repel field logic remains similar) ...
                for paddle in [player_paddle_left, player_paddle_right]:
                    if paddle.has_effect("repel_field"):
                        repel_radius = paddle.current_height * REPEL_FIELD_RADIUS_FACTOR; dx = ball_obj.rect.centerx - paddle.rect.centerx
                        dy = ball_obj.rect.centery - paddle.rect.centery; distance = math.hypot(dx, dy)
                        if 0 < distance < repel_radius:
                            force_magnitude = REPEL_FIELD_STRENGTH * (1 - distance / repel_radius); angle = math.atan2(dy, dx)
                            ball_obj.velocity[0] += math.cos(angle) * force_magnitude; ball_obj.velocity[1] += math.sin(angle) * force_magnitude
                            speed_mag = math.hypot(ball_obj.velocity[0], ball_obj.velocity[1])
                            if speed_mag > BALL_MAX_SPEED_X * 1.5:
                                scale = (BALL_MAX_SPEED_X * 1.5) / speed_mag
                                ball_obj.velocity[0] *= scale; ball_obj.velocity[1] *= scale
                            ball_obj.current_speed_x_magnitude = abs(ball_obj.velocity[0])


            # Paddle - Distractor (Duck) Collision (Now ducks don't interact with paddles)
            # for paddle in [player_paddle_left, player_paddle_right]:
            #     duck_paddle_hits = pygame.sprite.spritecollide(paddle, distractor_sprites_group, False)
            #     for duck in duck_paddle_hits:
            #         if isinstance(duck, CrazyDuckSprite) and duck.hit_paddle(paddle):
            #             create_impact_particles(paddle.rect.centerx, paddle.rect.centery, impact_particles, "paddle")


            # Power-up Spawning
            if random.random() < POWERUP_SPAWN_CHANCE and len(active_powerups) < MAX_POWERUPS_ONSCREEN :
                spawn_x = random.randint(int(SCREEN_WIDTH * 0.25), int(SCREEN_WIDTH * 0.75))
                if SCREEN_WIDTH * 0.4 < spawn_x < SCREEN_WIDTH * 0.6 : 
                    spawn_x += SCREEN_WIDTH * 0.15 * random.choice([-1,1])
                spawn_y = random.randint(POWERUP_SIZE, SCREEN_HEIGHT - POWERUP_SIZE)
                new_powerup = PowerUp(spawn_x, spawn_y)
                active_powerups.add(new_powerup)
                all_sprites.add(new_powerup)

            # Distractor Spawning
            if random.random() < DISTRACTOR_SPAWN_CHANCE_TOTAL and len(distractor_sprites_group) < DISTRACTOR_MAX_ONSCREEN_TOTAL:
                if random.random() < CRAZY_DUCK_SPAWN_CHANCE_RATIO and \
                   len([s for s in distractor_sprites_group if isinstance(s, CrazyDuckSprite)]) < MAX_DUCKS_ONSCREEN:
                    new_distractor = CrazyDuckSprite() # Ducks now move vertically
                else:
                    new_distractor = DistractorSprite() # Generic distractors
                distractor_sprites_group.add(new_distractor)
                all_sprites.add(new_distractor)
            
            active_powerups.update(main_ball.rect if main_ball.alive() else None, time_tick)
            distractor_sprites_group.update(time_tick)
            impact_particles.update()

        # --- Drawing ---
        # ... (Drawing logic remains largely the same, ensure powerup text uses paddle.powerup_indicator_text) ...
        draw_psychedelic_background(game_surface, time_tick * PSYCHEDELIC_BACKGROUND_SPEED)
        if is_sudden_death_mode and current_state in [STATE_PLAYING, STATE_COUNTDOWN]:
            flash_alpha = (math.sin(time_tick * SUDDEN_DEATH_FLASH_SPEED * 2) * 0.5 + 0.5) * SUDDEN_DEATH_FLASH_ALPHA_MAX
            sudden_death_tint_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); sudden_death_tint_surface.fill(RED + (int(flash_alpha),)); game_surface.blit(sudden_death_tint_surface, (0, 0))
        pygame.draw.line(game_surface, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 3)
        pygame.draw.rect(game_surface, WHITE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 5)
        all_paddle_related_sprites.draw(game_surface)
        balls.draw(game_surface)
        active_powerups.draw(game_surface)
        impact_particles.draw(game_surface)
        distractor_sprites_group.draw(game_surface)
        for ball_obj in balls: # Ball Trails
             if ball_obj.trail_positions:
                 # ... (Trail drawing logic can remain similar)
                trail_color_base = ball_obj.image.get_at((int(ball_obj.current_radius), int(ball_obj.current_radius)))[:3]
                if ball_obj.is_laser_shot: trail_color_base = LASER_SHOT_COLOR
                if ball_obj.rainbow_effect_timer > 0:
                    for i in range(len(ball_obj.trail_positions) - 1):
                        pos1, _, _, _ = ball_obj.trail_positions[i]; pos2, _, _, _ = ball_obj.trail_positions[i+1]
                        hue = (time_tick * 7 + i * 12) % 360; c = pygame.Color(0); c.hsva = (hue, 100, 100, 100)
                        pygame.draw.line(game_surface, (c.r, c.g, c.b), pos1, pos2, max(1, int(ball_obj.current_radius * (1 - i / len(ball_obj.trail_positions)) * 1.5)))
                    continue
                for i in range(len(ball_obj.trail_positions) - 1):
                    pos1, _, _, _ = ball_obj.trail_positions[i]; pos2, _, _, _ = ball_obj.trail_positions[i+1]
                    alpha = max(0, int(200 * (i / len(ball_obj.trail_positions)))); final_trail_color = trail_color_base[:3] + (alpha,) if len(trail_color_base) >=3 else (200,200,200,alpha)
                    pygame.draw.line(game_surface, final_trail_color, pos1, pos2, max(1, int(ball_obj.current_radius * (1 - i / len(ball_obj.trail_positions)))))
        
        # Draw power-up indicator text
        if player_paddle_left.powerup_indicator_text:
            draw_text_adv(game_surface, player_paddle_left.powerup_indicator_text, 20, SCREEN_WIDTH // 4, SCREEN_HEIGHT - 30, YELLOW, center_aligned=True, font_type="Arial Black", shadow_color=BLACK, shadow_offset=(1,1))
        if player_paddle_right.powerup_indicator_text:
            draw_text_adv(game_surface, player_paddle_right.powerup_indicator_text, 20, SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT - 30, YELLOW, center_aligned=True, font_type="Arial Black", shadow_color=BLACK, shadow_offset=(1,1))

        for sprite in distractor_sprites_group:
             if isinstance(sprite, CrazyDuckSprite): sprite.draw_quack(game_surface)
        
        wobble_x = math.sin(time_tick * SCREEN_WOBBLE_SPEED) * SCREEN_WOBBLE_AMPLITUDE
        wobble_y = math.cos(time_tick * SCREEN_WOBBLE_SPEED * 0.7) * SCREEN_WOBBLE_AMPLITUDE
        screen_actual.blit(game_surface, (wobble_x, wobble_y))

        # UI Elements on screen_actual
        # ... (Menu drawing logic remains the same) ...
        button_rects_map.clear(); hover_color_button = (255,255,0)
        draw_text_adv(screen_actual, str(score_a), 50, SCREEN_WIDTH // 4, 20, WHITE, center_aligned=True, font_type="Impact", shadow_color=BLACK, shadow_offset=(2,2))
        draw_text_adv(screen_actual, str(score_b), 50, SCREEN_WIDTH * 3 // 4, 20, WHITE, center_aligned=True, font_type="Impact", shadow_color=BLACK, shadow_offset=(2,2))
        if current_state == STATE_COUNTDOWN:
            display_text = str(countdown_value) if countdown_value > 0 else "GO!"; color = COUNTDOWN_TEXT_COLOR if countdown_value > 0 else COUNTDOWN_GO_TEXT_COLOR
            draw_text_adv(screen_actual, display_text, 100, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, color, center_aligned=True, font_type="Impact", shadow_color=BLACK, shadow_offset=(3,3))
        elif current_state == STATE_START_MENU: # Start Menu
            title_color = (255, int(150 + 100 * math.sin(time_tick * 0.1)), 0)
            draw_text_adv(screen_actual, "ULTRA PONG PSYCHOSIS", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, title_color, center_aligned=True, font_type="Impact", shadow_offset=(3,3))
            button_rects_map["start"] = draw_text_adv(screen_actual, "START", 45, SCREEN_WIDTH/2, SCREEN_HEIGHT/2, (200,200,255), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-100, SCREEN_HEIGHT/2-22,200,45))
            button_rects_map["instr"] = draw_text_adv(screen_actual, "Instructions", 40, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 70, (180,180,220), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-120, SCREEN_HEIGHT/2+48,240,40))
            button_rects_map["quit"] = draw_text_adv(screen_actual, "QUIT", 40, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 130, (150,150,180), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-100, SCREEN_HEIGHT/2+108,200,40))
        # ... (Other menu states: MODE_SELECT, AI_DIFFICULTY_SELECT, GAME_OVER, PAUSED, INSTRUCTIONS - drawing logic assumed similar and correct)
        elif current_state == STATE_MODE_SELECT:
             dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim_surface.fill((0,0,0,180)); screen_actual.blit(dim_surface, (0,0))
             draw_text_adv(screen_actual, "SELECT MODE", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, YELLOW, center_aligned=True, font_type="Impact", shadow_offset=(3,3))
             button_rects_map["1p"] = draw_text_adv(screen_actual, "1 PLAYER (AI)", 45, SCREEN_WIDTH/2, SCREEN_HEIGHT/2, (150,255,150), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-150, SCREEN_HEIGHT/2-22,300,45))
             button_rects_map["2p"] = draw_text_adv(screen_actual, "2 PLAYER", 45, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 70, (150,200,255), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-150, SCREEN_HEIGHT/2+48,300,45))
        elif current_state == STATE_AI_DIFFICULTY_SELECT:
             dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim_surface.fill((0,0,0,180)); screen_actual.blit(dim_surface, (0,0))
             draw_text_adv(screen_actual, "SELECT DIFFICULTY", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, ORANGE, center_aligned=True, font_type="Impact", shadow_offset=(3,3))
             button_rects_map["easy"] = draw_text_adv(screen_actual, "EASY", 45, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40, (100,255,100), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-100, SCREEN_HEIGHT/2-62,200,45))
             button_rects_map["medium"] = draw_text_adv(screen_actual, "MEDIUM", 45, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20, (255,255,100), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-120, SCREEN_HEIGHT/2-2,240,45))
             button_rects_map["hard"] = draw_text_adv(screen_actual, "HARD", 45, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 80, (255,100,100), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-100, SCREEN_HEIGHT/2+58,200,45))
        elif current_state == STATE_GAME_OVER:
            dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim_surface.fill((0,0,0,180)); screen_actual.blit(dim_surface, (0,0))
            draw_text_adv(screen_actual, "GAME OVER", 70, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, RED, center_aligned=True, font_type="Impact")
            draw_text_adv(screen_actual, winner_text, 50, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50, YELLOW, center_aligned=True, font_type="Impact")
            button_rects_map["play_again"] = draw_text_adv(screen_actual, "Play Again", 35, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30, (150,255,150), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-150, SCREEN_HEIGHT/2+12,300,35))
            button_rects_map["main_menu"] = draw_text_adv(screen_actual, "Main Menu", 35, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 80, (150,200,255), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-150, SCREEN_HEIGHT/2+62,300,35))
        elif current_state == STATE_PAUSED:
            dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim_surface.fill((0,0,0,180)); screen_actual.blit(dim_surface, (0,0))
            draw_text_adv(screen_actual, "PAUSED", 70, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, ORANGE, center_aligned=True, font_type="Impact")
            button_rects_map["resume"] = draw_text_adv(screen_actual, "Resume", 40, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30, (150,255,150), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-180, SCREEN_HEIGHT/2-50,360,40))
            button_rects_map["restart_pause"] = draw_text_adv(screen_actual, "Restart", 35, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30, (200,200,100), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-150, SCREEN_HEIGHT/2+12,300,35))
            button_rects_map["menu_pause"] = draw_text_adv(screen_actual, "Main Menu", 35, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 80, (150,200,255), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-150, SCREEN_HEIGHT/2+62,300,35))
        elif current_state == STATE_INSTRUCTIONS:
            dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim_surf.fill((0,0,0,150)); screen_actual.blit(dim_surf, (0,0))
            draw_text_adv(screen_actual, "HOW TO PLAY", 45, SCREEN_WIDTH/2, SCREEN_HEIGHT/6 - 20, CYAN, center_aligned=True, font_type="Impact")
            instructions = [
                "Player 1 (Left): W/S keys", "Player 2 (Right): O/L keys (2P)",
                "AI (Right): Computer (1P)", "Move paddle into ball to add SPIN!",
                "Faster paddle movement = more spin.",
                "Power-ups (?) give special effects.", "Ducks are chaotic, hit the ball!", "",
                f"First to {WINNING_SCORE} wins.",
                f"Sudden Death if tied at {SUDDEN_DEATH_SCORE_THRESHOLD}+ (win by 2).",
                "Sticky Ball: Space (P1) / RShift (P2) to launch.",
                "", "ESC to Pause / Return to Menu."
            ]
            y_start = SCREEN_HEIGHT / 4 - 20
            for line in instructions:
                draw_text_adv(screen_actual, line, 21, SCREEN_WIDTH/2, y_start, (200,200,220), center_aligned=True, font_type="Arial")
                y_start += 27
            button_rects_map["return_from_instructions"] = draw_text_adv(screen_actual, "Return to Menu", 30, SCREEN_WIDTH/2, SCREEN_HEIGHT - 50, (180,180,220), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=pygame.Rect(SCREEN_WIDTH/2-150, SCREEN_HEIGHT - 70,300,40))


        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_game()
