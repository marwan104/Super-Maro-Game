import pygame, random

class Particle:
    def __init__(self, x, y, vel_x, vel_y, color, life, size=2):
        self.x, self.y = x, y
        self.vel_x, self.vel_y = vel_x, vel_y
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.3
        self.life -= 1
        return self.life > 0
    
    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        if alpha > 0:
            surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (self.size, self.size), self.size)
            screen.blit(surf, (int(self.x-self.size), int(self.y-self.size)))

def create_dust_particles(particles, x, y, count=5):
    for _ in range(count):
        vel_x = random.uniform(-2, 2)
        vel_y = random.uniform(-4, -1)
        particles.append(Particle(x, y, vel_x, vel_y, (139,69,19), random.randint(20, 40), 2))

def create_score_particles(particles, x, y, count=8):
    for _ in range(count):
        vel_x = random.uniform(-3, 3)
        vel_y = random.uniform(-5, -2)
        particles.append(Particle(x, y, vel_x, vel_y, (255,215,0), random.randint(30, 60), random.randint(1, 3)))
