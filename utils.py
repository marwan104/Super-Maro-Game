import pygame, os

def load_image_safe(path, fallback_size=(100, 100), color=(150,150,150)):
    try:
        surf = pygame.image.load(path)
        return surf.convert_alpha() if surf.get_alpha() else surf.convert()
    except:
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        surf.fill(color)
        return surf

def scale_to_height(surf, new_h, allow_upscale=False):
    w, h = surf.get_size()
    if h == 0:
        return surf
    scale = new_h / h
    new_w = int(w * scale)
    if not allow_upscale and new_w > w:
        return surf
    return pygame.transform.smoothscale(surf, (new_w, new_h))

def load_sound(folder, filename):
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    return None
