import os, pygame
from utils import load_image_safe, scale_to_height

class Player:
    def __init__(self, sprite_dir, height):
        self.sprite_dir = sprite_dir
        self.height = height
        self.run_frames = []
        self.jump = None
        self.slide = None
        self.idle = None
        self.run_index = 0
        self.run_timer = 0
        self.RUN_ANIMATION_SPEED = 8
        self.load_sprites()

    def load_sprites(self):
        # Run frames
        for i in range(1, 11):
            path = os.path.join(self.sprite_dir, f"run{i}.png")
            if os.path.exists(path):
                frame = load_image_safe(path)
                frame = scale_to_height(frame, self.height)
                self.run_frames.append(frame)
        if not self.run_frames:
            fallback = load_image_safe(os.path.join(self.sprite_dir, "run.png"))
            self.run_frames = [scale_to_height(fallback, self.height)]

        # Jump, Slide, Idle
        self.jump = scale_to_height(load_image_safe(os.path.join(self.sprite_dir, "jump.png")), self.height)
        self.slide = scale_to_height(load_image_safe(os.path.join(self.sprite_dir, "slide.png")), int(self.height*0.6))
        idle_path = os.path.join(self.sprite_dir, "idle.png")
        self.idle = scale_to_height(load_image_safe(idle_path if os.path.exists(idle_path) else os.path.join(self.sprite_dir,"run1.png")), self.height)

    def get_current_sprite(self, state, is_jumping):
        if state == "sliding":
            return self.slide
        elif is_jumping or state == "wall_sliding":
            return self.jump
        elif state == "running":
            self.run_timer += 1
            if self.run_timer >= self.RUN_ANIMATION_SPEED:
                self.run_timer = 0
                self.run_index = (self.run_index + 1) % len(self.run_frames)
            return self.run_frames[self.run_index]
        else:
            return self.idle
