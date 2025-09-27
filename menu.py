# menu.py
import pygame
from database import get_top_scores

class Menu:
    def __init__(self, screen, font, small_font):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.menu_name = ""
        self.max_length = 12
        self.state = "menu"  # "menu" or "tutorial"

    def handle_event(self, event):
        """
        Returns a name string when the player presses SPACE/ENTER to start.
        Otherwise returns None.
        """
        if event.type == pygame.KEYDOWN:
            if self.state == "menu":
                if event.key == pygame.K_BACKSPACE:
                    self.menu_name = self.menu_name[:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    return self.menu_name.strip() or "Player"
                elif event.key == pygame.K_t:
                    self.state = "tutorial"
                else:
                    ch = event.unicode
                    if ch and ch.isprintable() and len(self.menu_name) < self.max_length:
                        self.menu_name += ch
            elif self.state == "tutorial":
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    self.state = "menu"
        return None

    def draw(self, last_score=None):
        WIDTH, HEIGHT = self.screen.get_size()
        self.screen.fill((200, 230, 255))

        if self.state == "menu":
            title = self.font.render("Super Maro - Enhanced", True, (0,0,0))
            prompt = self.font.render("Type your name and press SPACE to start", True, (0,0,0))
            name_text = self.font.render(self.menu_name, True, (50,50,200))
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
            self.screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//4 + 60))
            self.screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, HEIGHT//4 + 120))

            # Last score
            if last_score:
                score_text = self.font.render(f"Last score: {last_score}", True, (255,215,0))
                self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//4 + 160))

            # Dashboard (top scores)
            top_scores = get_top_scores()
            y = HEIGHT//2 + 10
            title2 = self.small_font.render("Top Scores:", True, (0,0,0))
            self.screen.blit(title2, (WIDTH//2 - title2.get_width()//2, y))
            y += 30
            for i, (name, score) in enumerate(top_scores, 1):
                text = self.small_font.render(f"{i}. {name} - {score}", True, (0,0,0))
                self.screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
                y += 24

            tutorial_text = self.small_font.render("Press T for Tutorial", True, (100,0,0))
            self.screen.blit(tutorial_text, (WIDTH//2 - tutorial_text.get_width()//2, HEIGHT-50))

        else:  # tutorial
            lines = [
                "Tutorial - Controls:",
                "SPACE or UP: Jump (single jump)",
                "DOWN or S: Slide (use to pass low flying obstacles)",
                "Press ESC / SPACE to go back"
            ]
            y = 80
            for i, l in enumerate(lines):
                txt = self.small_font.render(l, True, (0,0,0))
                self.screen.blit(txt, (40, y))
                y += 40
