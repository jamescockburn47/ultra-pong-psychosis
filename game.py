# game.py - Fixed wobble frequency & removed countdown after points

import pygame
import random
import sys
import math
import os # For path joining

# Import config first to get SCREEN_WIDTH/HEIGHT before other imports might use them implicitly
from config import *
from sprites import Paddle, Ball, PowerUp, Particle, DistractorSprite, CrazyDuckSprite # Ensure PowerUp is imported
# --- IMPORT 'resource_path' from utils ---
from utils import get_random_crazy_color, draw_psychedelic_background, draw_text_adv, create_impact_particles, resource_path

# Global sounds dictionary and laser channel (accessed by helper and sprites)
sounds = {}
laser_channel = None # Will be initialized after mixer

# Helper function to play sounds safely
def play_sound(sound_name, loops=0, specific_channel=None):
    """Plays a sound from the global 'sounds' dictionary."""
    global sounds # Ensure we are using the global dict
    # Only attempt to play if mixer is initialized and sound exists
    if pygame.mixer.get_init() and sound_name in sounds and sounds[sound_name]:
        sound_to_play = sounds[sound_name]
        try:
            if specific_channel:
                # Check if channel is valid before playing
                if isinstance(specific_channel, pygame.mixer.Channel):
                    specific_channel.play(sound_to_play, loops)
                # else: print(f"Debug: Invalid specific channel for {sound_name}") # Optional debug
            else:
                channel = pygame.mixer.find_channel(True) # Force find an unused channel
                if channel:
                    channel.play(sound_to_play, loops)
                # else: print(f"Debug: No available channel for {sound_name}") # Optional debug
        except pygame.error as e:
            print(f"Error playing sound '{sound_name}': {e}")
    # elif not pygame.mixer.get_init():
        # print(f"Debug: Mixer not initialized, cannot play {sound_name}") # Optional debug
    # elif sound_name not in sounds or not sounds[sound_name]:
        # print(f"Debug: Sound '{sound_name}' not found or not loaded.") # Optional debug


# Dictionary for comical power-up descriptions
COMICAL_POWERUP_DESCRIPTIONS = {
    "paddle_big_self": "BIG PADDLE: Suddenly, hitting the ball seems... easier?",
    "paddle_small_self": "SMALL PADDLE: Hope you like a challenge (and squinting).",
    "multi_ball": "MULTIBALL: Because one ball is never enough chaos!",
    "ball_fast_all": "SPEED BOOST: Good luck tracking this hyperactive sphere.",
    "opp_freeze": "OPPONENT FREEZE: Chill out! Your opponent literally has to.",
    "ball_invis_all": "INVISIBLE BALL: Now you see it, now you... wait, where'd it go?",
    "shield_self": "SHIELD: Activate your personal 'nope' field.",
    "slow_opponent": "SLOW OPPONENT: Like moving through cosmic molasses.",
    "sticky_paddle_self": "STICKY PADDLE: Catch and release (when you feel like it).",
    "curve_ball_self": "CURVE READY: Prepare to bend it like... well, someone.",
    "laser_shot_self": "LASER READY: Pew pew! Turns the ball into a light speed menace.",
    "confuse_opponent_controls": "CONFUSE OPPONENT: Left is right, up is down, panic is certain.",
    "point_shield_self": "POINT SHIELD: A one-time 'get out of jail free' card for scoring.",
    "ball_size_toggle_all": "BALL SIZE TOGGLE: Tiny terror or giant annoyance? Spin the wheel!",
    "rainbow_ball_all": "RAINBOW BALL: Taste the rainbow... of visual distraction!",
    "opponent_paddle_shrink": "SHRINK OPPONENT: It's like they're playing with a toothpick.",
    "ball_ghost_self": "GHOST READY: Make the ball phase through reality (and paddles).",
    "paddle_teleport_self": "PADDLE TELEPORT: Bamf! Instant relocation, hopefully useful.",
    "repel_field_self": "REPEL FIELD: Personal space bubble, enforced by physics.",
    "ball_split_self": "SPLIT READY: Double the balls, double the fun (or panic).",
    "ball_teleport_all": "BALL TELEPORT: Randomly relocates the ball(s). Surprise!",
}


def main_game():
    """Main function to run the Ultra Pong Psychosis game."""
    global time_tick, sounds, laser_channel

    pygame.init()
    pygame.font.init()
    # --- Mixer Initialization ---
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        pygame.mixer.set_num_channels(32)
        print(f"Mixer initialized with {pygame.mixer.get_num_channels()} channels and buffer size 4096.")
    except pygame.error as e:
        print(f"Error initializing mixer: {e}. Sound effects will be disabled.")
        pygame.mixer.quit()

    # Use screen dimensions from config
    screen_actual = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ULTRA PONG PSYCHOSIS - CHAOS MODE")
    clock = pygame.time.Clock()

    time_tick = 0
    is_sudden_death_mode = False
    sudden_death_sound_played_this_activation = False

    # --- Use resource_path to find the base 'assets' directory ---
    try:
        assets_base_path = resource_path("assets")
        if not os.path.isdir(assets_base_path):
             raise FileNotFoundError(f"Base assets directory not found at resolved path: {assets_base_path}")
        print(f"Assets base path resolved to: {assets_base_path}") # Optional debug print
    except Exception as e:
        print(f"FATAL ERROR: Could not resolve base assets path: {e}")
        pygame.quit()
        sys.exit()

    # --- Sound Effect Loading (Using resource_path) ---
    sounds.clear()
    sound_files = {
        "ball_fast": "ball_fast.wav", "ball_ghost": "ball_ghost.wav",
        "ball_invis": "ball_invis.wav", "ball_size_toggle": "ball_size_toggle.wav",
        "ball_teleport": "ball_teleport.wav", "confuse_controls": "confuse_controls.wav",
        "countdown_tick": "countdown.wav",
        "curve_ball_ready": "curve_ball_ready.wav", "duck_hit_ball": "duck_hit_ball.wav",
        "duck_quack": "duck_quack.wav", "duck_spawn": "duck_spawn.wav",
        "game_over_lose": "game_over_lose.wav", "game_over_win": "game_over_win.wav",
        "goal_scored": "goal_scored.wav", "laser_shot_hit": "laser_shot_hit.wav",
        "laser_shot_loop": "laser_shot_loop.wav", "menu_click": "menu_click.wav",
        "multi_ball": "multi_ball.wav", "opp_freeze": "opp_freeze.wav",
        "paddle_big": "paddle_big.wav", "paddle_hit": "paddle_hit.wav",
        "paddle_hit_spin": "paddle_hit_spin.wav", "paddle_small": "paddle_small.wav",
        "paddle_teleport": "paddle_teleport.wav", "point_shield_activate": "point_shield_activate.wav",
        "point_shield_denied": "point_shield_denied.wav", "powerup_collect": "powerup_collect.wav",
        "powerup_collect_bad": "powerup_collect_bad.wav", "powerup_collect_good": "powerup_collect_good.wav",
        "powerup_spawn": "powerup_spawn.wav", "rainbow_ball": "rainbow_ball.wav",
        "repel_field": "repel_field.wav", "shield_activate": "shield_activate.wav",
        "shield_hit": "shield_hit.wav", "shield_mock_laugh": "shield_mock_laugh.wav",
        "slow_opponent": "slow_opponent.wav", "sticky_ball_launch": "sticky_ball_launch.wav",
        "sticky_paddle": "sticky_paddle.wav", "sudden_death": "sudden_death.wav",
        "wall_hit": "wall_hit.wav"
    }
    sound_folder = os.path.join(assets_base_path, "sounds")

    for name, filename in sound_files.items():
        path = os.path.join(sound_folder, filename)
        if os.path.exists(path):
            if pygame.mixer.get_init():
                try:
                    sounds[name] = pygame.mixer.Sound(path)
                except pygame.error as e:
                     print(f"Warning: Could not load sound '{name}' from '{path}': {e}")
                     sounds[name] = None
            else:
                sounds[name] = None
        else:
             print(f"ERROR: Sound file not found for '{name}': '{path}' (Resolved from base: {assets_base_path})")
             sounds[name] = None

    # --- Laser Channel Setup ---
    if pygame.mixer.get_init():
        try:
            laser_channel = pygame.mixer.Channel(0)
            print("Reserved channel 0 for laser sound.")
        except pygame.error as e:
            print(f"Warning: Could not get Channel(0) for laser sound: {e}")
            laser_channel = None
    else:
        laser_channel = None

    # --- Background Music (Using resource_path via sound_folder) ---
    if pygame.mixer.get_init():
        try:
            music_base_filename = "psychosis_loop_dark"
            music_base_path = os.path.join(sound_folder, music_base_filename)
            music_path = None
            potential_paths = [music_base_path + ext for ext in [".ogg", ".wav", ".mp3"]]
            for potential_path in potential_paths:
                if os.path.exists(potential_path):
                    if potential_path.endswith(".mp3"):
                        print("Warning: Found .mp3 music file, attempting to load...")
                    music_path = potential_path
                    break

            if music_path:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                print(f"Loaded music: {music_path}")
            else:
                raise pygame.error(f"Background music file not found ({music_base_filename}.ogg/wav/mp3) in '{sound_folder}'")
        except pygame.error as e:
            print(f"Warning: Could not load or play background music: {e}")

    # --- Sprite Group Initializations ---
    all_sprites = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    active_powerups = pygame.sprite.Group()
    impact_particles = pygame.sprite.Group()
    distractor_sprites_group = pygame.sprite.Group()
    all_paddle_related_sprites = pygame.sprite.Group()

    # --- Game Objects ---
    # Pass the new PADDLE_HEIGHT_NORMAL from config
    player_paddle_left = Paddle(PADDLE_WIDTH, PADDLE_HEIGHT_NORMAL, 0, lambda: time_tick, play_sound_func=play_sound)
    player_paddle_left.laser_channel = laser_channel
    player_paddle_left.laser_sound = sounds.get("laser_shot_loop")
    player_paddle_left.all_sprites_ref = all_sprites

    player_paddle_right = Paddle(PADDLE_WIDTH, PADDLE_HEIGHT_NORMAL, 1, lambda: time_tick, play_sound_func=play_sound)
    player_paddle_right.laser_channel = laser_channel
    player_paddle_right.laser_sound = sounds.get("laser_shot_loop")
    player_paddle_right.all_sprites_ref = all_sprites

    all_paddle_related_sprites.add(player_paddle_left, player_paddle_right)
    all_sprites.add(player_paddle_left, player_paddle_right)

    # Create the initial main ball (will be reset before play starts)
    # Pass the new BALL_RADIUS_NORMAL from config
    main_ball = Ball(BALL_RADIUS_NORMAL, play_sound_func=play_sound,
                     laser_channel=laser_channel, laser_sound=sounds.get("laser_shot_loop"))
    balls.add(main_ball)
    all_sprites.add(main_ball)

    # --- Game State Variables ---
    current_state = STATE_START_MENU
    current_game_mode = GAME_MODE_AI
    game_difficulty = DIFFICULTY_MEDIUM
    score_a = 0
    score_b = 0
    winner_text = ""
    rally_ongoing = False
    countdown_timer = 0
    countdown_value = COUNTDOWN_INITIAL_VALUE
    last_player_scored_on = random.choice([0, 1])

    # --- Game Reset Functions ---
    def reset_internal_game_state_for_new_round(serve_to_player_idx=None, start_immediately=False):
        """Resets ball, powerups, effects for a new point."""
        nonlocal main_ball, rally_ongoing, last_player_scored_on
        rally_ongoing = False
        for p in [player_paddle_left, player_paddle_right]:
            effects_to_keep = ["shrunken_by_opponent"] # Keep shrink effect between points
            p.reset_all_effects(keep_effects_named=effects_to_keep)

        # Clear transient sprites
        for ball_obj in balls:
            if ball_obj.is_laser_shot and laser_channel and ball_obj.laser_sound_playing:
                laser_channel.stop()
                ball_obj.laser_sound_playing = False
            ball_obj.kill() # Remove from all groups
        balls.empty()
        active_powerups.empty()
        distractor_sprites_group.empty()
        impact_particles.empty()

        # Create a new main ball instance using new BALL_RADIUS_NORMAL
        main_ball = Ball(BALL_RADIUS_NORMAL, play_sound_func=play_sound,
                         laser_channel=laser_channel, laser_sound=sounds.get("laser_shot_loop"))

        # Determine serve direction
        player_to_serve_towards = serve_to_player_idx if serve_to_player_idx is not None else last_player_scored_on
        if player_to_serve_towards is None: player_to_serve_towards = random.choice([0,1])

        # Reset the new ball's state
        main_ball.reset(initial_spawn=True, scored_on_player=player_to_serve_towards, start_static=(not start_immediately))
        balls.add(main_ball)
        all_sprites.add(main_ball) # Add the new ball to the main sprite group

    def reset_game_full(new_game_state_after_reset=STATE_PLAYING):
        """Resets the entire game state for a new match."""
        nonlocal score_a, score_b, winner_text, current_state, countdown_timer, countdown_value
        nonlocal is_sudden_death_mode, sudden_death_sound_played_this_activation, last_player_scored_on
        score_a, score_b = 0, 0
        winner_text = ""
        is_sudden_death_mode = False
        sudden_death_sound_played_this_activation = False
        # Reset paddle positions using new PADDLE_HEIGHT_NORMAL
        player_paddle_left.rect.y = (SCREEN_HEIGHT - player_paddle_left.base_height) // 2
        player_paddle_right.rect.y = (SCREEN_HEIGHT - player_paddle_right.base_height) // 2
        player_paddle_left.reset_all_effects() # Clear all effects on full reset
        player_paddle_right.reset_all_effects()

        if laser_channel: laser_channel.stop() # Stop laser sound if playing

        last_player_scored_on = random.choice([0, 1]) # Randomize first serve
        # Reset ball, powerups etc. Ball will start static because start_immediately=False
        reset_internal_game_state_for_new_round(serve_to_player_idx=last_player_scored_on, start_immediately=False)

        # Set the state after reset
        if new_game_state_after_reset == STATE_PLAYING:
            # Start the countdown for the very first serve of the game
            current_state = STATE_COUNTDOWN
            countdown_value = COUNTDOWN_INITIAL_VALUE
            countdown_timer = COUNTDOWN_FRAMES_PER_NUMBER
        else:
            # Go directly to the specified menu state
            current_state = new_game_state_after_reset

    # --- Main Game Loop ---
    button_rects_map = {}
    running = True
    while running:
        time_tick += 1
        dt = clock.tick(60) / 1000.0 # Delta time in seconds
        mouse_pos = pygame.mouse.get_pos()
        keys_pressed_this_frame = pygame.key.get_pressed()

        # Update paddle shield sprites group
        all_paddle_related_sprites.empty()
        all_paddle_related_sprites.add(player_paddle_left, player_paddle_right)
        if player_paddle_left.shield_sprite and player_paddle_left.shield_sprite.alive():
             all_paddle_related_sprites.add(player_paddle_left.shield_sprite)
        if player_paddle_right.shield_sprite and player_paddle_right.shield_sprite.alive():
             all_paddle_related_sprites.add(player_paddle_right.shield_sprite)


        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state in [STATE_PLAYING]: current_state = STATE_PAUSED
                    elif current_state == STATE_PAUSED: current_state = STATE_PLAYING
                    elif current_state in [STATE_GAME_OVER, STATE_INSTRUCTIONS, STATE_MODE_SELECT, STATE_AI_DIFFICULTY_SELECT]:
                        play_sound("menu_click")
                        reset_game_full(STATE_START_MENU)
                    elif current_state == STATE_START_MENU: running = False
                if current_state == STATE_PLAYING and event.key == pygame.K_p: current_state = STATE_PAUSED
                elif current_state == STATE_PAUSED and event.key == pygame.K_p: current_state = STATE_PLAYING

                # Handle sticky ball launch
                if current_state == STATE_PLAYING:
                    if player_paddle_left.stuck_ball and event.key == pygame.K_SPACE:
                        play_sound("sticky_ball_launch")
                        stuck_ball_ref = player_paddle_left.stuck_ball
                        player_paddle_left.remove_effect("sticky")
                        if stuck_ball_ref:
                           stuck_ball_ref.launch_from_paddle(player_paddle_left)
                        player_paddle_left.stuck_ball = None

                    if current_game_mode == GAME_MODE_2P and player_paddle_right.stuck_ball and event.key == pygame.K_RSHIFT:
                        play_sound("sticky_ball_launch")
                        stuck_ball_ref = player_paddle_right.stuck_ball
                        player_paddle_right.remove_effect("sticky")
                        if stuck_ball_ref:
                            stuck_ball_ref.launch_from_paddle(player_paddle_right)
                        player_paddle_right.stuck_ball = None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_button_key = None
                for key, rect in button_rects_map.items():
                    if rect and rect.collidepoint(mouse_pos): clicked_button_key = key; break

                if clicked_button_key:
                    play_sound("menu_click")

                # Handle button clicks based on current state
                if current_state == STATE_START_MENU:
                    if clicked_button_key == "start": current_state = STATE_MODE_SELECT
                    elif clicked_button_key == "instr": current_state = STATE_INSTRUCTIONS
                    elif clicked_button_key == "quit": running = False
                elif current_state == STATE_MODE_SELECT:
                    if clicked_button_key == "1p": current_game_mode = GAME_MODE_AI; current_state = STATE_AI_DIFFICULTY_SELECT
                    elif clicked_button_key == "2p": current_game_mode = GAME_MODE_2P; reset_game_full(STATE_PLAYING) # Starts countdown
                elif current_state == STATE_AI_DIFFICULTY_SELECT:
                    if clicked_button_key == "easy": game_difficulty = DIFFICULTY_EASY
                    elif clicked_button_key == "medium": game_difficulty = DIFFICULTY_MEDIUM
                    elif clicked_button_key == "hard": game_difficulty = DIFFICULTY_HARD
                    if clicked_button_key in ["easy", "medium", "hard"]: reset_game_full(STATE_PLAYING) # Starts countdown
                elif current_state == STATE_GAME_OVER:
                    if clicked_button_key == "play_again": reset_game_full(STATE_PLAYING) # Starts countdown
                    elif clicked_button_key == "main_menu": reset_game_full(STATE_START_MENU)
                elif current_state == STATE_PAUSED:
                    if clicked_button_key == "resume": current_state = STATE_PLAYING
                    elif clicked_button_key == "restart_pause": reset_game_full(STATE_PLAYING) # Starts countdown
                    elif clicked_button_key == "menu_pause": reset_game_full(STATE_START_MENU)
                elif current_state == STATE_INSTRUCTIONS:
                     if clicked_button_key == "return_from_instructions": reset_game_full(STATE_START_MENU)


        # --- State Updates ---
        if current_state == STATE_COUNTDOWN:
            # Keep ball centered and static during countdown
            if main_ball.alive():
                 main_ball.velocity = [0, 0]
                 main_ball.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                 main_ball.spin_y = 0

            countdown_timer -= 1
            if countdown_timer <= 0:
                countdown_value -= 1
                if countdown_value <= 0: # Countdown finished
                    current_state = STATE_PLAYING # Switch to playing state
                    play_sound("countdown_tick") # Final tick sound
                    if main_ball.alive(): # Reset ball with movement
                        main_ball.reset(scored_on_player=last_player_scored_on, start_static=False)
                else: # Still counting down
                    play_sound("countdown_tick")
                    countdown_timer = COUNTDOWN_FRAMES_PER_NUMBER # Reset timer for next number

        elif current_state == STATE_PLAYING:
            # Update paddle states
            player_paddle_left.update_movement_state()
            player_paddle_right.update_movement_state()
            player_paddle_left.update_timers_and_effects()
            player_paddle_right.update_timers_and_effects()

            # --- Player Movement ---
            if player_paddle_left.can_move():
                move_dir_left = 0
                if keys_pressed_this_frame[pygame.K_w]: move_dir_left = -1
                if keys_pressed_this_frame[pygame.K_s]: move_dir_left = 1
                if move_dir_left != 0: player_paddle_left.move(move_dir_left, PADDLE_SPEED) # Use new PADDLE_SPEED

            if player_paddle_right.can_move():
                if current_game_mode == GAME_MODE_2P:
                    move_dir_right = 0
                    if keys_pressed_this_frame[pygame.K_o]: move_dir_right = -1
                    if keys_pressed_this_frame[pygame.K_l]: move_dir_right = 1
                    if move_dir_right != 0: player_paddle_right.move(move_dir_right, PLAYER_2_PADDLE_SPEED) # Use new PLAYER_2_PADDLE_SPEED
                elif current_game_mode == GAME_MODE_AI:
                    player_paddle_right.ai_move(balls, game_difficulty) # AI uses speeds from config

            rally_ongoing = len(balls) > 0 and any(b.velocity != [0,0] for b in balls if b.alive())

            # --- Ball Updates and Collisions ---
            for ball_obj in list(balls):
                if not ball_obj.alive(): continue

                # --- Handle Stuck Ball ---
                if ball_obj.is_stuck and ball_obj.last_hit_paddle_instance:
                    stuck_paddle = ball_obj.last_hit_paddle_instance
                    if stuck_paddle.alive() and stuck_paddle.has_effect("sticky"):
                        offset_x = (stuck_paddle.base_width // 2 + ball_obj.current_radius + 2) * (1 if stuck_paddle.player_num == 0 else -1)
                        ball_obj.rect.centerx = stuck_paddle.rect.centerx + offset_x
                        ball_obj.rect.centery = stuck_paddle.rect.centery
                        ball_obj.velocity = [0,0]; ball_obj.spin_y = 0
                        ball_obj.update(rally_ongoing, time_tick)
                        continue
                    else:
                         ball_obj.is_stuck = False
                         ball_obj.last_hit_paddle_instance = None
                         direction = 1 if stuck_paddle.player_num == 0 else -1
                         # Use new BALL_INITIAL_SPEED_X
                         ball_obj.velocity = [BALL_INITIAL_SPEED_X * 0.5 * direction, random.uniform(-1,1)]
                         ball_obj.current_speed_x_magnitude = abs(ball_obj.velocity[0])

                # --- Regular Ball Update ---
                ball_obj.update(rally_ongoing, time_tick)

                # --- Boundary Collisions (Top/Bottom Walls) ---
                if ball_obj.rect.top <= 0:
                    ball_obj.rect.top = 0; ball_obj.velocity[1] *= -1
                    play_sound("wall_hit")
                    create_impact_particles(ball_obj.rect.centerx, ball_obj.rect.top, impact_particles, "wall")
                if ball_obj.rect.bottom >= SCREEN_HEIGHT:
                    ball_obj.rect.bottom = SCREEN_HEIGHT; ball_obj.velocity[1] *= -1
                    play_sound("wall_hit")
                    create_impact_particles(ball_obj.rect.centerx, ball_obj.rect.bottom, impact_particles, "wall")

                # --- Goal Scoring ---
                scored_this_frame = False
                player_scored_on = -1

                # Left Goal
                if ball_obj.rect.left <= 0:
                    if player_paddle_left.has_effect("point_shield"):
                        player_paddle_left.remove_effect("point_shield")
                        play_sound("point_shield_denied")
                        ball_obj.rect.left = 1; ball_obj.velocity[0] *= -1
                        create_impact_particles(ball_obj.rect.left, ball_obj.rect.centery, impact_particles, "wall")
                    else:
                        score_b += 1; scored_this_frame = True; player_scored_on = 0
                        play_sound("goal_scored")
                        create_impact_particles(0, ball_obj.rect.centery, impact_particles, "goal")

                # Right Goal
                elif ball_obj.rect.right >= SCREEN_WIDTH:
                    if player_paddle_right.has_effect("point_shield"):
                        player_paddle_right.remove_effect("point_shield")
                        play_sound("point_shield_denied")
                        ball_obj.rect.right = SCREEN_WIDTH - 1; ball_obj.velocity[0] *= -1
                        create_impact_particles(ball_obj.rect.right, ball_obj.rect.centery, impact_particles, "wall")
                    else:
                        score_a += 1; scored_this_frame = True; player_scored_on = 1
                        play_sound("goal_scored")
                        create_impact_particles(SCREEN_WIDTH, ball_obj.rect.centery, impact_particles, "goal")

                # --- Handle Post-Score Logic ---
                if scored_this_frame:
                    last_player_scored_on = player_scored_on

                    # Check for Sudden Death Activation
                    if not is_sudden_death_mode and \
                       (score_a >= SUDDEN_DEATH_SCORE_THRESHOLD or score_b >= SUDDEN_DEATH_SCORE_THRESHOLD) and \
                       abs(score_a - score_b) < 2:
                        if not sudden_death_sound_played_this_activation :
                             play_sound("sudden_death")
                             sudden_death_sound_played_this_activation = True
                        is_sudden_death_mode = True

                    # Check for Game Over Condition
                    game_is_over = False
                    if is_sudden_death_mode:
                        if abs(score_a - score_b) >= 2: game_is_over = True
                    elif score_a >= WINNING_SCORE or score_b >= WINNING_SCORE:
                         game_is_over = True

                    if game_is_over:
                        current_state = STATE_GAME_OVER
                        winner_text = f"Player {'Left' if score_a > score_b else 'Right'} Wins!"
                        player_is_left_human = True
                        if current_game_mode == GAME_MODE_2P: play_sound("game_over_win")
                        elif player_is_left_human and score_a > score_b: play_sound("game_over_win")
                        else: play_sound("game_over_lose")
                        if laser_channel: laser_channel.stop()
                        balls.empty(); active_powerups.empty(); distractor_sprites_group.empty(); impact_particles.empty()
                        if ball_obj.alive(): ball_obj.kill()
                        break # Exit ball loop
                    else:
                        # *** Point scored, but game not over: Reset and continue playing ***
                        if ball_obj.alive():
                            if ball_obj.is_laser_shot and laser_channel and ball_obj.laser_sound_playing:
                                 laser_channel.stop()
                                 ball_obj.laser_sound_playing = False
                            ball_obj.kill()
                        # Reset ball state, starting immediately (no countdown)
                        reset_internal_game_state_for_new_round(serve_to_player_idx=player_scored_on, start_immediately=True)
                        # *** Stay in STATE_PLAYING ***
                        current_state = STATE_PLAYING
                        # Continue processing other balls (if any) this frame
                        continue

                # --- Paddle Collisions ---
                collision_list = pygame.sprite.spritecollide(ball_obj, all_paddle_related_sprites, False)
                collided_paddle = None
                collided_shield = None
                for item in collision_list:
                    if isinstance(item, Paddle): collided_paddle = item
                    elif item.alive(): # Shield check
                         if player_paddle_left.shield_sprite == item: collided_shield = player_paddle_left
                         elif player_paddle_right.shield_sprite == item: collided_shield = player_paddle_right
                    if collided_paddle: break

                # --- Handle Paddle Hit ---
                if collided_paddle:
                    paddle = collided_paddle
                    is_ghost_pass = ball_obj.is_ghost_ball and ball_obj.ghost_can_pass_paddle
                    if is_ghost_pass:
                        ball_obj.ghost_can_pass_paddle = False
                        continue

                    is_moving_towards_paddle = (paddle.player_num == 0 and ball_obj.velocity[0] < 0) or \
                                                (paddle.player_num == 1 and ball_obj.velocity[0] > 0)

                    if is_moving_towards_paddle:
                        if paddle.player_num == 0: ball_obj.rect.left = paddle.rect.right
                        else: ball_obj.rect.right = paddle.rect.left
                        original_velocity_x_direction = math.copysign(1, ball_obj.velocity[0])
                        ball_obj.velocity[0] *= -1
                        relative_hit_pos = max(-1.0, min(1.0, (ball_obj.rect.centery - paddle.rect.centery) / (paddle.current_height / 2)))
                        spin_from_hit = relative_hit_pos * PADDLE_SPIN_FACTOR
                        spin_from_motion = paddle.speed_y_for_spin * PADDLE_EDGE_SPIN_FACTOR
                        ball_obj.spin_y += spin_from_hit + spin_from_motion
                        # Use new BALL_MAX_SPIN
                        ball_obj.spin_y = max(-BALL_MAX_SPIN, min(BALL_MAX_SPIN, ball_obj.spin_y))

                        if ball_obj.is_laser_shot:
                            play_sound("laser_shot_hit")
                        else:
                            # Use new BALL_MAX_SPEED_X and BALL_SPEED_INCREMENT_HIT
                            ball_obj.current_speed_x_magnitude = min(BALL_MAX_SPEED_X, ball_obj.current_speed_x_magnitude + BALL_SPEED_INCREMENT_HIT)
                            ball_obj.velocity[0] = math.copysign(ball_obj.current_speed_x_magnitude, ball_obj.velocity[0])
                            if abs(ball_obj.spin_y) > PADDLE_SPIN_FACTOR * 0.6 or abs(paddle.speed_y_for_spin) > PADDLE_SPEED * 0.4:
                                play_sound("paddle_hit_spin")
                            else:
                                play_sound("paddle_hit")

                        ball_obj.last_hit_paddle_instance = paddle
                        ball_obj.last_hit_by_timer = BALL_LAST_HIT_TIMER_DURATION
                        create_impact_particles(ball_obj.rect.centerx, ball_obj.rect.centery, impact_particles, "paddle")

                        # Handle Paddle Effects on Hit
                        if paddle.has_effect("sticky") and not ball_obj.is_stuck:
                            ball_obj.stick_to_paddle(paddle)
                            continue # Skip other effects if stuck

                        if paddle.has_effect("laser_shot") and not ball_obj.is_laser_shot:
                            ball_obj.activate_laser_shot(); paddle.remove_effect("laser_shot")
                        if paddle.has_effect("curve_shot_ready"):
                            curve_spin = random.uniform(2.5, 4.5) * (-1 if original_velocity_x_direction > 0 else 1)
                            ball_obj.spin_y += curve_spin
                            # Use new BALL_MAX_SPIN
                            ball_obj.spin_y = max(-BALL_MAX_SPIN, min(BALL_MAX_SPIN, ball_obj.spin_y))
                            paddle.remove_effect("curve_shot_ready")
                        if paddle.has_effect("ghost_shot_ready"):
                            ball_obj.activate_ghost_mode(GHOST_BALL_DURATION); paddle.remove_effect("ghost_shot_ready")
                        if paddle.has_effect("ball_split_ready"):
                            paddle.remove_effect("ball_split_ready"); play_sound("multi_ball")
                            for i in range(POWERUP_MULTIBALL_COUNT):
                                # Use new BALL_RADIUS_NORMAL
                                new_ball = Ball(BALL_RADIUS_NORMAL, play_sound_func=play_sound, laser_channel=laser_channel, laser_sound=sounds.get("laser_shot_loop"))
                                new_ball.rect.center = ball_obj.rect.center
                                angle_offset = random.uniform(-math.pi/7, math.pi/7) * (1 if i == 0 else -1)
                                original_angle = math.atan2(ball_obj.velocity[1], ball_obj.velocity[0])
                                new_angle = original_angle + angle_offset
                                new_ball_speed = ball_obj.current_speed_x_magnitude * 0.85
                                new_ball.velocity = [math.cos(new_angle) * new_ball_speed, math.sin(new_angle) * new_ball_speed]
                                new_ball.current_speed_x_magnitude = new_ball_speed
                                new_ball.spin_y = ball_obj.spin_y * 0.5 + random.uniform(-1.5,1.5)
                                new_ball.is_main_ball = False
                                balls.add(new_ball); all_sprites.add(new_ball)
                        collided_shield = None # Paddle hit overrides shield

                # --- Handle Shield Hit ---
                elif collided_shield:
                    paddle = collided_shield
                    moving_towards_shield = (paddle.player_num == 0 and ball_obj.velocity[0] < 0) or \
                                            (paddle.player_num == 1 and ball_obj.velocity[0] > 0)
                    if moving_towards_shield:
                        shield_rect = paddle.shield_sprite.rect
                        if paddle.player_num == 0: ball_obj.rect.left = shield_rect.right
                        else: ball_obj.rect.right = shield_rect.left
                        if ball_obj.is_laser_shot: play_sound("laser_shot_hit")
                        play_sound("shield_hit")
                        if random.random() < 0.1: play_sound("shield_mock_laugh")
                        ball_obj.velocity[0] *= -1.05
                        # Use new BALL_MAX_SPEED_X
                        ball_obj.current_speed_x_magnitude = min(BALL_MAX_SPEED_X, abs(ball_obj.velocity[0]))
                        ball_obj.velocity[0] = math.copysign(ball_obj.current_speed_x_magnitude, ball_obj.velocity[0])
                        ball_obj.velocity[1] *= 0.9; ball_obj.spin_y *= 0.5
                        create_impact_particles(ball_obj.rect.centerx, ball_obj.rect.centery, impact_particles, "wall")

                # --- Power-up Collisions ---
                powerup_hit_list = pygame.sprite.spritecollide(ball_obj, active_powerups, True)
                for powerup in powerup_hit_list:
                    collecting_paddle = None
                    if ball_obj.last_hit_paddle_instance and ball_obj.last_hit_by_timer > 0:
                        collecting_paddle = ball_obj.last_hit_paddle_instance
                    else:
                         dist_left = abs(powerup.rect.centerx - player_paddle_left.rect.centerx)
                         dist_right = abs(powerup.rect.centerx - player_paddle_right.rect.centerx)
                         collecting_paddle = player_paddle_left if dist_left < dist_right else player_paddle_right

                    if collecting_paddle:
                        other_paddle = player_paddle_right if collecting_paddle == player_paddle_left else player_paddle_left
                        _, general_collect_sound_name = powerup.collected(
                            collecting_paddle, other_paddle, balls, main_ball,
                            impact_particles, time_tick, play_sound
                        )
                        play_sound(general_collect_sound_name)

                # --- Distractor Collisions ---
                distractor_hit_list = pygame.sprite.spritecollide(ball_obj, distractor_sprites_group, False)
                for distractor in distractor_hit_list:
                    if isinstance(distractor, CrazyDuckSprite):
                        if distractor.hit_ball(ball_obj):
                            create_impact_particles(ball_obj.rect.centerx, ball_obj.rect.centery, impact_particles, "generic")

                # --- Repel Field Interaction ---
                for paddle in [player_paddle_left, player_paddle_right]:
                    if paddle.has_effect("repel_field"):
                        repel_radius = paddle.current_height * REPEL_FIELD_RADIUS_FACTOR
                        repel_radius_sq = repel_radius * repel_radius
                        dx = ball_obj.rect.centerx - paddle.rect.centerx
                        dy = ball_obj.rect.centery - paddle.rect.centery
                        distance_sq = dx*dx + dy*dy
                        if 0 < distance_sq < repel_radius_sq:
                            distance = math.sqrt(distance_sq)
                            force_magnitude = REPEL_FIELD_STRENGTH * (1 - distance / repel_radius)
                            if distance > 0:
                                force_x = (dx / distance) * force_magnitude
                                force_y = (dy / distance) * force_magnitude
                                ball_obj.velocity[0] += force_x
                                ball_obj.velocity[1] += force_y
                                speed_mag_sq = ball_obj.velocity[0]**2 + ball_obj.velocity[1]**2
                                # Use new BALL_MAX_SPEED_X
                                max_speed_sq = (BALL_MAX_SPEED_X * 1.3)**2
                                if speed_mag_sq > max_speed_sq:
                                    scale = math.sqrt(max_speed_sq / speed_mag_sq)
                                    ball_obj.velocity[0] *= scale
                                    ball_obj.velocity[1] *= scale
                                ball_obj.current_speed_x_magnitude = abs(ball_obj.velocity[0])


            # --- Spawning Power-ups ---
            # Use new POWERUP_SIZE
            if random.random() < POWERUP_SPAWN_CHANCE and len(active_powerups) < MAX_POWERUPS_ONSCREEN :
                spawn_x = random.randint(int(SCREEN_WIDTH * 0.15), int(SCREEN_WIDTH * 0.85))
                if SCREEN_WIDTH * 0.4 < spawn_x < SCREEN_WIDTH * 0.6 :
                     spawn_x += SCREEN_WIDTH * 0.15 * random.choice([-1,1])
                spawn_y = random.randint(POWERUP_SIZE, SCREEN_HEIGHT - POWERUP_SIZE)
                spawn_rect = pygame.Rect(0,0, POWERUP_SIZE, POWERUP_SIZE); spawn_rect.center = (spawn_x, spawn_y)
                if not any(p.rect.colliderect(spawn_rect) for p in active_powerups):
                    new_powerup = PowerUp(spawn_x, spawn_y)
                    active_powerups.add(new_powerup); all_sprites.add(new_powerup)
                    play_sound("powerup_spawn")

            # --- Spawning Distractors ---
            if random.random() < DISTRACTOR_SPAWN_CHANCE_TOTAL and len(distractor_sprites_group) < DISTRACTOR_MAX_ONSCREEN_TOTAL:
                num_ducks = len([s for s in distractor_sprites_group if isinstance(s, CrazyDuckSprite)])
                num_generic = len(distractor_sprites_group) - num_ducks
                spawn_duck = (random.random() < CRAZY_DUCK_SPAWN_CHANCE_RATIO and num_ducks < MAX_DUCKS_ONSCREEN)
                spawn_generic = (not spawn_duck and num_generic < (DISTRACTOR_MAX_ONSCREEN_TOTAL - MAX_DUCKS_ONSCREEN))
                new_distractor = None
                if spawn_duck: new_distractor = CrazyDuckSprite(play_sound_func=play_sound);
                elif spawn_generic: new_distractor = DistractorSprite()
                if new_distractor:
                    distractor_sprites_group.add(new_distractor); all_sprites.add(new_distractor)
                    if spawn_duck: play_sound("duck_spawn")

            # --- Update Groups ---
            main_ball_rect_for_magnet = main_ball.rect if main_ball.alive() else None
            active_powerups.update(main_ball_rect_for_magnet, time_tick)
            distractor_sprites_group.update(time_tick)
            impact_particles.update()

        # --- Drawing ---
        # Background
        draw_psychedelic_background(game_surface, time_tick * PSYCHEDELIC_BACKGROUND_SPEED)

        # Sudden Death Tint Overlay
        if is_sudden_death_mode and current_state in [STATE_PLAYING, STATE_COUNTDOWN]:
            flash_alpha = (math.sin(time_tick * SUDDEN_DEATH_FLASH_SPEED) * 0.5 + 0.5) * SUDDEN_DEATH_FLASH_ALPHA_MAX # Adjusted frequency
            sudden_death_tint_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            sudden_death_tint_surface.fill(RED + (int(flash_alpha),))
            game_surface.blit(sudden_death_tint_surface, (0, 0))

        # Center Line and Border
        pygame.draw.line(game_surface, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 3)
        pygame.draw.rect(game_surface, WHITE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 5)

        # --- Draw Sprites ---
        all_paddle_related_sprites.draw(game_surface)
        balls.draw(game_surface)
        active_powerups.draw(game_surface)
        impact_particles.draw(game_surface)
        distractor_sprites_group.draw(game_surface)

        # --- Draw Ball Trails ---
        for ball_obj in balls:
             if ball_obj.alive() and ball_obj.trail_positions:
                try:
                     trail_color_base = ball_obj.image.get_at((ball_obj.image.get_width()//2, ball_obj.image.get_height()//2))[:3]
                     if ball_obj.is_laser_shot: trail_color_base = LASER_SHOT_COLOR
                except IndexError:
                     trail_color_base = COLOR_BALL_BASE

                num_points = len(ball_obj.trail_positions)
                if ball_obj.rainbow_effect_timer > 0:
                    for i in range(num_points - 1):
                        pos1, _, _, _ = ball_obj.trail_positions[i]
                        pos2, _, _, _ = ball_obj.trail_positions[i+1]
                        hue = (time_tick * 7 + i * (360 / max(1, num_points))) % 360
                        c = pygame.Color(0); c.hsva = (hue, 100, 100, 100)
                        trail_width = max(1, int(ball_obj.current_radius * (1 - (i / num_points)) * 1.5))
                        pygame.draw.line(game_surface, (c.r, c.g, c.b), pos1, pos2, trail_width)
                else:
                    for i in range(num_points - 1):
                        pos1, _, _, _ = ball_obj.trail_positions[i]
                        pos2, _, _, _ = ball_obj.trail_positions[i+1]
                        alpha = max(0, int(200 * (i / num_points)))
                        final_trail_color = trail_color_base[:3] + (alpha,)
                        trail_width = max(1, int(ball_obj.current_radius * (1 - (i / num_points))))
                        try:
                            pygame.draw.line(game_surface, final_trail_color, pos1, pos2, trail_width)
                        except ValueError:
                            pygame.draw.line(game_surface, trail_color_base[:3], pos1, pos2, trail_width)

        # --- UI Indicators ---
        if player_paddle_left.powerup_indicator_text:
            draw_text_adv(game_surface, player_paddle_left.powerup_indicator_text, 22, SCREEN_WIDTH // 4, SCREEN_HEIGHT - 35, YELLOW, center_aligned=True, font_type="Arial Black", shadow_color=BLACK, shadow_offset=(1,1))
        if player_paddle_right.powerup_indicator_text:
            draw_text_adv(game_surface, player_paddle_right.powerup_indicator_text, 22, SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT - 35, YELLOW, center_aligned=True, font_type="Arial Black", shadow_color=BLACK, shadow_offset=(1,1))
        for sprite in distractor_sprites_group:
             if isinstance(sprite, CrazyDuckSprite):
                 sprite.draw_quack(game_surface)

        # --- Screen Wobble & Final Blit ---
        # Use new SCREEN_WOBBLE_AMPLITUDE and SCREEN_WOBBLE_SPEED
        wobble_x = math.sin(time_tick * SCREEN_WOBBLE_SPEED) * SCREEN_WOBBLE_AMPLITUDE if current_state == STATE_PLAYING else 0
        wobble_y = math.cos(time_tick * SCREEN_WOBBLE_SPEED * 0.7) * SCREEN_WOBBLE_AMPLITUDE if current_state == STATE_PLAYING else 0
        screen_actual.blit(game_surface, (wobble_x, wobble_y)) # Blit the potentially wobbled game surface

        # --- UI Overlays (Scores, Menus - Drawn directly onto screen_actual) ---
        button_rects_map.clear(); hover_color_button = (255,255,0)
        score_font_size = 50 # Slightly smaller font for smaller screen
        score_y_pos = 40 # *** INCREASED Y-POSITION FOR SCORE ***
        draw_text_adv(screen_actual, str(score_a), score_font_size, SCREEN_WIDTH // 4, score_y_pos, WHITE, center_aligned=True, font_type="Impact", shadow_color=BLACK, shadow_offset=(2,2))
        draw_text_adv(screen_actual, str(score_b), score_font_size, SCREEN_WIDTH * 3 // 4, score_y_pos, WHITE, center_aligned=True, font_type="Impact", shadow_color=BLACK, shadow_offset=(2,2))

        # --- State-Specific UI ---
        if current_state == STATE_COUNTDOWN:
            display_text = str(countdown_value) if countdown_value > 0 else "GO!"
            color = COUNTDOWN_TEXT_COLOR if countdown_value > 0 else COUNTDOWN_GO_TEXT_COLOR
            draw_text_adv(screen_actual, display_text, 100, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, color, center_aligned=True, font_type="Impact", shadow_color=BLACK, shadow_offset=(3,3))

        elif current_state == STATE_START_MENU:
            title_color = (255, int(150 + 100 * math.sin(time_tick * 0.1)), 0)
            draw_text_adv(screen_actual, "ULTRA PONG PSYCHOSIS", 65, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, title_color, center_aligned=True, font_type="Impact", shadow_offset=(3,3))
            button_y_start = SCREEN_HEIGHT/2 + 10; button_spacing = 70 # Adjusted spacing
            button_width = 220; button_height = 45; font_size = 40 # Adjusted sizes
            start_rect = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start-button_height/2,button_width,button_height)
            instr_rect = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start+button_spacing-button_height/2,button_width,button_height)
            quit_rect = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start+2*button_spacing-button_height/2,button_width,button_height)
            button_rects_map["start"] = draw_text_adv(screen_actual, "START", font_size, SCREEN_WIDTH/2, button_y_start, (200,200,255), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=start_rect)
            button_rects_map["instr"] = draw_text_adv(screen_actual, "Instructions", font_size-5, SCREEN_WIDTH/2, button_y_start + button_spacing, (180,180,220), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=instr_rect)
            button_rects_map["quit"] = draw_text_adv(screen_actual, "QUIT", font_size-5, SCREEN_WIDTH/2, button_y_start + 2*button_spacing, (150,150,180), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=quit_rect)

        elif current_state == STATE_MODE_SELECT:
             dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim_surface.fill((0,0,0,180)); screen_actual.blit(dim_surface, (0,0))
             draw_text_adv(screen_actual, "SELECT MODE", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, YELLOW, center_aligned=True, font_type="Impact", shadow_offset=(3,3))
             button_y_start = SCREEN_HEIGHT/2 + 15; button_spacing = 80; button_width=300; button_height=50; font_size=45 # Adjusted sizes
             rect_1p = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start-button_height/2,button_width,button_height)
             rect_2p = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start+button_spacing-button_height/2,button_width,button_height)
             button_rects_map["1p"] = draw_text_adv(screen_actual, "1 PLAYER (AI)", font_size, SCREEN_WIDTH/2, button_y_start, (150,255,150), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=rect_1p)
             button_rects_map["2p"] = draw_text_adv(screen_actual, "2 PLAYER", font_size, SCREEN_WIDTH/2, button_y_start + button_spacing, (150,200,255), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=rect_2p)

        elif current_state == STATE_AI_DIFFICULTY_SELECT:
             dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim_surface.fill((0,0,0,180)); screen_actual.blit(dim_surface, (0,0))
             draw_text_adv(screen_actual, "SELECT DIFFICULTY", 60, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, ORANGE, center_aligned=True, font_type="Impact", shadow_offset=(3,3))
             button_y_start = SCREEN_HEIGHT/2 ; button_spacing = 70; button_width=250; button_height=45; font_size=45 # Adjusted sizes
             rect_easy = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start-button_spacing-button_height/2,button_width,button_height)
             rect_medium = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start-button_height/2,button_width,button_height)
             rect_hard = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start+button_spacing-button_height/2,button_width,button_height)
             button_rects_map["easy"] = draw_text_adv(screen_actual, "EASY", font_size, SCREEN_WIDTH/2, button_y_start - button_spacing, (100,255,100), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=rect_easy)
             button_rects_map["medium"] = draw_text_adv(screen_actual, "MEDIUM", font_size, SCREEN_WIDTH/2, button_y_start, (255,255,100), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=rect_medium)
             button_rects_map["hard"] = draw_text_adv(screen_actual, "HARD", font_size, SCREEN_WIDTH/2, button_y_start + button_spacing, (255,100,100), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=rect_hard)

        elif current_state == STATE_GAME_OVER:
            dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim_surface.fill((0,0,0,180)); screen_actual.blit(dim_surface, (0,0))
            draw_text_adv(screen_actual, "GAME OVER", 70, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, RED, center_aligned=True, font_type="Impact")
            draw_text_adv(screen_actual, winner_text, 50, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50, YELLOW, center_aligned=True, font_type="Impact")
            button_y_start = SCREEN_HEIGHT/2 + 40; button_spacing = 60; button_width=280; button_height=40; font_size=35 # Adjusted sizes
            rect_play_again = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start-button_height/2,button_width,button_height)
            rect_main_menu = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start+button_spacing-button_height/2,button_width,button_height)
            button_rects_map["play_again"] = draw_text_adv(screen_actual, "Play Again", font_size, SCREEN_WIDTH/2, button_y_start, (150,255,150), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=rect_play_again)
            button_rects_map["main_menu"] = draw_text_adv(screen_actual, "Main Menu", font_size, SCREEN_WIDTH/2, button_y_start + button_spacing, (150,200,255), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=rect_main_menu)

        elif current_state == STATE_PAUSED:
            dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim_surface.fill((0,0,0,180)); screen_actual.blit(dim_surface, (0,0))
            draw_text_adv(screen_actual, "PAUSED", 70, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, ORANGE, center_aligned=True, font_type="Impact")
            button_y_start = SCREEN_HEIGHT/2 ; button_spacing = 60; button_width=280; button_height=45; font_size=40 # Adjusted sizes
            rect_resume = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start-button_spacing/2-button_height/2,button_width,button_height)
            rect_restart = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start+button_spacing/2-button_height/2+5,button_width,button_height)
            rect_menu = pygame.Rect(SCREEN_WIDTH/2-button_width/2, button_y_start+button_spacing*1.5-button_height/2+5,button_width,button_height)
            button_rects_map["resume"] = draw_text_adv(screen_actual, "Resume", font_size, SCREEN_WIDTH/2, button_y_start - button_spacing/2, (150,255,150), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=rect_resume)
            button_rects_map["restart_pause"] = draw_text_adv(screen_actual, "Restart", font_size-5, SCREEN_WIDTH/2, button_y_start + button_spacing/2, (200,200,100), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=rect_restart)
            button_rects_map["menu_pause"] = draw_text_adv(screen_actual, "Main Menu", font_size-5, SCREEN_WIDTH/2, button_y_start + button_spacing*1.5, (150,200,255), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=rect_menu)

        elif current_state == STATE_INSTRUCTIONS:
            dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim_surf.fill((0,0,0,200)); screen_actual.blit(dim_surf, (0,0))
            instr_y_start = SCREEN_HEIGHT * 0.04
            draw_text_adv(screen_actual, "HOW TO PLAY", 40, SCREEN_WIDTH/2, instr_y_start, CYAN, center_aligned=True, font_type="Impact")
            instr_y_start += 50 # Adjusted spacing
            basic_instructions = [
                "Player 1 (Left): W/S keys", "Player 2 (Right): O/L keys (2P)",
                "AI (Right): Computer (1P)", "Move paddle into ball to add SPIN!",
                "Faster paddle movement = more spin.",
                f"First to {WINNING_SCORE} wins (Sudden Death at {SUDDEN_DEATH_SCORE_THRESHOLD}+, win by 2).",
                "Sticky Ball: Space (P1) / RShift (P2) to launch.",
                "ESC to Pause / Return to Menu."
            ]
            line_height_basic = 24; basic_font_size = 18 # Adjusted sizes
            for line in basic_instructions:
                draw_text_adv(screen_actual, line, basic_font_size, SCREEN_WIDTH/2, instr_y_start, (200,200,220), center_aligned=True, font_type="Arial")
                instr_y_start += line_height_basic
            instr_y_start += line_height_basic

            draw_text_adv(screen_actual, "POWER-UPS (?)", 30, SCREEN_WIDTH/2, instr_y_start, YELLOW, center_aligned=True, font_type="Impact")
            instr_y_start += 40 # Adjusted spacing
            line_height_powerup = 19; powerup_font_size = 15 # Adjusted sizes
            col_margin = SCREEN_WIDTH * 0.05; col_width = (SCREEN_WIDTH - 3 * col_margin) / 2
            col1_x = col_margin; col2_x = col_margin * 2 + col_width
            col1_y = instr_y_start; col2_y = instr_y_start
            max_y_pos = SCREEN_HEIGHT - 80 # Adjusted max Y
            powerup_items = list(COMICAL_POWERUP_DESCRIPTIONS.items())
            num_powerups = len(powerup_items); mid_point = (num_powerups + 1) // 2
            for i, (p_name, p_desc) in enumerate(powerup_items):
                 is_col1 = i < mid_point
                 current_x = col1_x if is_col1 else col2_x
                 current_y = col1_y if is_col1 else col2_y
                 if current_y + line_height_powerup > max_y_pos:
                      if is_col1 and col2_y == instr_y_start and col2_y + line_height_powerup <= max_y_pos:
                           current_x = col2_x; current_y = col2_y; is_col1 = False
                      else: break
                 draw_text_adv(screen_actual, p_desc, powerup_font_size, current_x, current_y, (210, 210, 210), center_aligned=False, font_type="Arial")
                 if is_col1: col1_y += line_height_powerup
                 else: col2_y += line_height_powerup

            button_width = 280; button_height=40; font_size=30 # Adjusted sizes
            rect_return = pygame.Rect(SCREEN_WIDTH/2-button_width/2, SCREEN_HEIGHT - 55 - button_height/2,button_width,button_height) # Adjusted Y
            button_rects_map["return_from_instructions"] = draw_text_adv(screen_actual, "Return to Menu", font_size, SCREEN_WIDTH/2, SCREEN_HEIGHT - 55, (180,180,220), center_aligned=True, font_type="Arial Black", hover_color=hover_color_button, mouse_pos=mouse_pos, click_rect_ref=rect_return)


        # Update the full display surface
        pygame.display.flip()

    # --- Cleanup ---
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    pygame.quit()
    sys.exit()

# --- Ball Helper Methods ---
def stick_to_paddle(self, paddle):
    self.is_stuck = True
    self.last_hit_paddle_instance = paddle
    paddle.stuck_ball = self
    self.velocity = [0, 0]
    self.spin_y = 0
Ball.stick_to_paddle = stick_to_paddle

def launch_from_paddle(self, paddle):
    self.is_stuck = False
    if paddle.stuck_ball == self:
        paddle.stuck_ball = None
    direction = 1 if paddle.player_num == 0 else -1
    # Use new BALL_INITIAL_SPEED_X
    launch_speed_x = BALL_INITIAL_SPEED_X * 1.2
    self.velocity[0] = launch_speed_x * direction
    self.velocity[1] = random.uniform(-BALL_INITIAL_SPEED_X * 0.5, BALL_INITIAL_SPEED_X * 0.5)
    self.current_speed_x_magnitude = abs(self.velocity[0])
    self.last_hit_paddle_instance = None
Ball.launch_from_paddle = launch_from_paddle


if __name__ == "__main__":
    main_game()
