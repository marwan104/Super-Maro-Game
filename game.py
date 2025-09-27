# game.py
import pygame, os, random
from utils import load_image_safe, scale_to_height, load_sound
from particles import create_dust_particles, create_score_particles
from player import Player

class Game:
    def __init__(self, screen, width=800, height=400):
        self.screen = screen
        self.WIDTH, self.HEIGHT = width, height
        self.GROUND_Y = 325

        # Player
        self.PLAYER_HEIGHT = int(self.HEIGHT * 0.25)
        self.player = Player(os.path.join("assets", "player"), self.PLAYER_HEIGHT)
        self.player_rect = self.player.get_current_sprite("running", False).get_rect(midbottom=(100, self.GROUND_Y))

        # Game/menu state
        self.state = "menu"      # "menu" or "playing"
        self.player_state = "running"
        self.is_jumping = False
        self.player_y_change = 0
        self.slide_timer = 0
        self.wall_slide_timer = 0
        self.wall_jump_available = False

        # Difficulty & obstacles
        self.game_level = 1
        self.obstacle_speed = 5
        self.spawn_rate = 60
        self.obstacle_timer = 0

        # obstacle sizes and lists (natural scaling)
        # ground obstacles ~ same height as player, flying ~ half player height
        self.obstacle_images_ground = self.load_obstacles(os.path.join("assets", "ground_obstacles"), scale=0.48)
        self.obstacle_images_flying = self.load_obstacles(os.path.join("assets", "flying_obstacles"), scale=0.5)
        self.obstacles = []
        self.FLYING_PROB = 0.4
        self.FLYING_HEIGHT = int(self.PLAYER_HEIGHT * 0.5)

        # scoring
        self.score = 0
        self.last_score = 0
        self.last_player_name = ""
        self.player_name = "Player"  # Current player name
        self.score_timer = 0
        self.last_score_milestone = 0

        # particles container
        self.particles = []

        # sounds (utils.load_sound(folder, filename))
        self.jump_sound = load_sound("gameplay_sounds", "jump.mp3")
        self.landing_sound = load_sound("gameplay_sounds", "landing.wav")
        self.score_sound = load_sound("gameplay_sounds", "score.wav")
        self.game_over_sound = load_sound("gameplay_sounds", "game_over.mp3")

        # fonts
        self.font = pygame.font.SysFont(None, 40)
        self.small_font = pygame.font.SysFont(None, 28)

        # background image
        self.background = self.load_background(os.path.join("assets", "background.png"))

        # try load background music (robust)
        self._try_play_music()

    # ---------- assets helpers ----------
    def load_obstacles(self, folder, scale=0.5):
        items = []
        if not os.path.isdir(folder):
            return items
        for fn in sorted(os.listdir(folder)):
            if fn.lower().endswith((".png", ".jpg", ".jpeg")):
                p = os.path.join(folder, fn)
                surf = load_image_safe(p)
                if surf is None:
                    continue
                new_h = max(4, int(self.PLAYER_HEIGHT * scale))
                surf = scale_to_height(surf, new_h, allow_upscale=True)
                mask = pygame.mask.from_surface(surf)
                items.append({"surf": surf, "mask": mask})
        return items

    def load_background(self, path):
        if os.path.exists(path):
            try:
                bg = pygame.image.load(path).convert()
                return pygame.transform.scale(bg, (self.WIDTH, self.HEIGHT))
            except Exception:
                return None
        return None

    def _try_play_music(self):
        # Search common music filenames in gameplay_sounds folder and play looped if found
        music_folder = "gameplay_sounds"
        for name in ("background_music.ogg", "background_music.mp3", "background_music.wav"):
            p = os.path.join(music_folder, name)
            if os.path.exists(p):
                try:
                    pygame.mixer.music.load(p)
                    pygame.mixer.music.set_volume(0.25)
                    pygame.mixer.music.play(-1)
                    return True
                except Exception as e:
                    print("Music load/play error:", e)
        return False

    # ---------- game lifecycle ----------
    def reset(self, player_name="Player"):
        self.player_name = player_name
        self.player_rect = self.player.get_current_sprite("running", False).get_rect(midbottom=(100, self.GROUND_Y))
        self.player_state = "running"
        self.is_jumping = False
        self.player_y_change = 0
        self.slide_timer = 0
        self.wall_slide_timer = 0
        self.wall_jump_available = False

        self.score = 0
        self.score_timer = 0
        self.last_score_milestone = 0

        self.obstacles = []
        self.obstacle_timer = 0

        self.game_level = 1
        self.obstacle_speed = 5
        self.spawn_rate = 60

        self.particles = []

    def calculate_difficulty(self):
        new_level = (self.score // 100) + 1
        if new_level > self.game_level:
            self.game_level = new_level
            # tune these to taste
            self.obstacle_speed = min(5 + (self.game_level - 1) * 1.5, 12)
            self.spawn_rate = max(60 - (self.game_level - 1) * 5, 25)

    # ---------- input handling ----------
    def handle_event(self, event):
        if self.state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    # start game
                    self.reset()
                    self.state = "playing"

        elif self.state == "playing":
            if event.type == pygame.KEYDOWN:
                # jump (single)
                if event.key in (pygame.K_SPACE, pygame.K_UP) and self.player_state != "sliding":
                    if not self.is_jumping:
                        self.player_y_change = -16
                        self.is_jumping = True
                        self.player_state = "jumping"
                        if self.jump_sound: self.jump_sound.play()
                    elif self.wall_jump_available and self.player_state == "wall_sliding":
                        self.player_y_change = -14
                        self.wall_jump_available = False
                        self.player_state = "jumping"
                        if self.jump_sound: self.jump_sound.play()

                # slide (down / s)
                elif event.key in (pygame.K_DOWN, pygame.K_s) and not self.is_jumping:
                    if self.player_state != "sliding":
                        self.player_state = "sliding"
                        self.slide_timer = 30
                        old_bottom = self.player_rect.bottom
                        self.player_rect = self.player.slide.get_rect()
                        self.player_rect.bottom = old_bottom
                        self.player_rect.x = 100

    # ---------- update logic ----------
    def update(self):
        if self.state != "playing":
            return

        self.calculate_difficulty()

        # slide timer end
        if self.player_state == "sliding":
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.player_state = "running" if not self.is_jumping else "jumping"
                old_bottom = self.player_rect.bottom
                self.player_rect = self.player.get_current_sprite(self.player_state, self.is_jumping).get_rect()
                self.player_rect.bottom = old_bottom
                self.player_rect.x = 100

        # gravity / wall slide
        if self.player_state == "wall_sliding":
            self.player_y_change += 0.3
            self.wall_slide_timer -= 1
            if self.wall_slide_timer <= 0:
                self.player_state = "jumping" if self.is_jumping else "running"
        else:
            self.player_y_change += 1.0

        self.player_rect.y += self.player_y_change

        # ground collision
        if self.player_rect.bottom >= self.GROUND_Y:
            if self.is_jumping:
                create_dust_particles(self.particles, self.player_rect.centerx, self.GROUND_Y, 6)
                if self.landing_sound: self.landing_sound.play()
            self.player_rect.bottom = self.GROUND_Y
            self.is_jumping = False
            if self.player_state == "jumping":
                self.player_state = "running"

        # wall detection (optional)
        if self.is_jumping and self.player_rect.right >= self.WIDTH - 10 and self.player_y_change > 0:
            if self.player_state != "wall_sliding":
                self.player_state = "wall_sliding"
                self.wall_slide_timer = 60
                self.wall_jump_available = True
                self.player_y_change = min(self.player_y_change, 2)

        # spawn obstacles
        self.obstacle_timer += 1
        if self.obstacle_timer > self.spawn_rate:
            obs_x = self.WIDTH
            if random.random() < self.FLYING_PROB and self.obstacle_images_flying:
                choice = random.choice(self.obstacle_images_flying)
                surf = choice["surf"]; mask = choice["mask"]
                rect = surf.get_rect(bottomleft=(obs_x, self.GROUND_Y - self.FLYING_HEIGHT))
                self.obstacles.append({"surf": surf, "rect": rect, "mask": mask, "type": "flying"})
            elif self.obstacle_images_ground:
                choice = random.choice(self.obstacle_images_ground)
                surf = choice["surf"]; mask = choice["mask"]
                rect = surf.get_rect(bottomleft=(obs_x, self.GROUND_Y))
                self.obstacles.append({"surf": surf, "rect": rect, "mask": mask, "type": "ground"})
            self.obstacle_timer = 0

        # move obstacles & check collisions (with hitbox logic)
        for obs in self.obstacles:
            obs["rect"].x -= int(self.obstacle_speed)

        # hitbox calculation
        if self.player_state == "sliding":
            hitbox_height = max(4, int(self.PLAYER_HEIGHT * 0.15))
            hitbox_width = max(10, int(self.player_rect.width * 0.7))
        else:
            hitbox_height = max(6, int(self.PLAYER_HEIGHT * 0.25))
            hitbox_width = max(10, int(self.player_rect.width * 0.5))

        hitbox = pygame.Rect(
            self.player_rect.centerx - hitbox_width // 2,
            self.player_rect.bottom - hitbox_height,
            hitbox_width,
            hitbox_height
        )

        collided = False
        for obs in self.obstacles:
            obs_type = obs.get("type", "ground")

            # for flying obstacles, if player not sliding use tall_hitbox to force collision on jumps
            if obs_type == "flying" and self.player_state != "sliding":
                tall_hitbox = pygame.Rect(
                    self.player_rect.centerx - hitbox_width // 2,
                    self.player_rect.top - 50,
                    hitbox_width,
                    self.player_rect.height + 100
                )
                collision_box = tall_hitbox
            else:
                collision_box = hitbox

            # if obstacle has mask, check mask overlap with rectangular hitbox
            if obs.get("mask") is not None:
                if obs["rect"].colliderect(collision_box):
                    hb_mask = pygame.mask.Mask((collision_box.width, collision_box.height), fill=True)
                    offset_x = collision_box.x - obs["rect"].x
                    offset_y = collision_box.y - obs["rect"].y
                    if obs["mask"].overlap(hb_mask, (offset_x, offset_y)):
                        collided = True
                        break
            else:
                if obs["rect"].colliderect(collision_box):
                    collided = True
                    break

        if collided:
            # game over - save score to database
            if self.game_over_sound: 
                self.game_over_sound.play()
            
            # Save score to database (with better error handling)
            try:
                from database import save_score
                success = save_score(self.player_name, self.score)
                if success:
                    print(f"Score saved successfully: {self.player_name} - {self.score}")
                else:
                    print(f"Failed to save score: {self.player_name} - {self.score}")
            except ImportError:
                print("Database module not available - score not saved")
            except Exception as e:
                print(f"Error saving score: {e}")
            
            self.last_score = self.score
            self.last_player_name = self.player_name
            self.state = "menu"

        # purge off-screen
        self.obstacles = [o for o in self.obstacles if o["rect"].x > -50]

        # scoring
        self.score_timer += 1
        if self.score_timer >= 5:
            self.score += 1
            self.score_timer = 0
            if self.score % 10 == 0 and self.score > self.last_score_milestone:
                create_score_particles(self.particles, self.player_rect.centerx, self.player_rect.top, 10)
                if self.score_sound: self.score_sound.play()
                self.last_score_milestone = self.score

        # update particles (remove dead)
        self.particles = [p for p in self.particles if p.update()]

    # ---------- drawing ----------
    def draw(self):
        # background
        if self.background:
            self.screen.blit(self.background, (0,0))
        else:
            self.screen.fill((135,206,235))
            pygame.draw.rect(self.screen, (80,180,60), pygame.Rect(0, self.GROUND_Y, self.WIDTH, self.HEIGHT - self.GROUND_Y))

        if self.state == "menu":
            title = self.font.render("Super Maro", True, (0,0,0))
            prompt = self.font.render("Press SPACE to Start", True, (0,0,0))
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, self.HEIGHT//3))
            self.screen.blit(prompt, (self.WIDTH//2 - prompt.get_width()//2, self.HEIGHT//2))
            if self.last_score > 0:
                last_text = self.font.render(f"{self.last_player_name} - {self.last_score}", True, (255,215,0))
                self.screen.blit(last_text, (self.WIDTH//2 - last_text.get_width()//2, self.HEIGHT//2 + 40))

        elif self.state == "playing":
            # player sprite
            sprite = self.player.get_current_sprite(self.player_state, self.is_jumping)
            self.screen.blit(sprite, self.player_rect)

            # obstacles
            for obs in self.obstacles:
                self.screen.blit(obs["surf"], obs["rect"])

            # particles
            for p in self.particles:
                p.draw(self.screen)

            # HUD
            score_text = self.font.render(f"Score: {self.score}", True, (255,215,0))
            self.screen.blit(score_text, (10,10))
            level_text = self.small_font.render(f"Level: {self.game_level}", True, (255,215,0))
            self.screen.blit(level_text, (10,45))
            
            # Show player name
            name_text = self.small_font.render(f"Player: {self.player_name}", True, (255,255,255))
            self.screen.blit(name_text, (10,70))