import pygame, sys
from game import Game
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Maro")
clock = pygame.time.Clock()

game = Game(screen, WIDTH, HEIGHT)

# Menu states: "menu", "playing", "dashboard"
menu_state = "menu"
player_name_input = ""   # input buffer for name entry

# Fonts for UI
font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 28)
title_font = pygame.font.SysFont(None, 50)

def load_menu_background():
    """Try to load menu background image from assets folder"""
    background_paths = [
        os.path.join("assets", "menu_background.png"),
        os.path.join("assets", "menu_background.jpg"),
        os.path.join("assets", "backgrounds", "menu.png"),
        os.path.join("assets", "backgrounds", "menu.jpg"),
        "menu_background.png",
        "menu_background.jpg"
    ]
    
    for path in background_paths:
        if os.path.exists(path):
            try:
                bg = pygame.image.load(path).convert()
                return pygame.transform.scale(bg, (WIDTH, HEIGHT))
            except Exception as e:
                print(f"Error loading menu background {path}: {e}")
                continue
    
    return None

def draw_gradient_background():
    """Draw a beautiful gradient background as fallback"""
    # Create gradient from dark blue to light blue
    for y in range(HEIGHT):
        # Interpolate between colors
        ratio = y / HEIGHT
        
        # Dark blue to light blue gradient
        r = int(20 + (135 - 20) * ratio)
        g = int(30 + (206 - 30) * ratio)
        b = int(60 + (235 - 60) * ratio)
        
        color = (r, g, b)
        pygame.draw.line(game.screen, color, (0, y), (WIDTH, y))

def draw_menu():
    """Draw the main menu with name input and navigation options"""
    # Try to load and display menu background
    menu_background = load_menu_background()
    if menu_background:
        game.screen.blit(menu_background, (0, 0))
    else:
        # Fallback gradient background if no image found
        draw_gradient_background()
    
    # Title with gold color and shadow effect
    title_shadow = title_font.render("Super Maro", True, (0, 0, 0))  # Black shadow
    title = title_font.render("Super Maro", True, (255, 215, 0))  # Gold color
    # Draw title with shadow effect
    game.screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 3, 53))  # Shadow offset
    game.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    
    # Name input section
    name_label = font.render("Enter your name:", True, (50, 50, 50))
    game.screen.blit(name_label, (WIDTH//2 - name_label.get_width()//2, 150))
    
    # Name input box
    input_box = pygame.Rect(WIDTH//2 - 150, 180, 300, 40)
    pygame.draw.rect(game.screen, (255, 255, 255), input_box)
    pygame.draw.rect(game.screen, (0, 0, 0), input_box, 2)
    
    # Display current input
    name_text = font.render(player_name_input + "_", True, (0, 0, 0))
    game.screen.blit(name_text, (input_box.x + 5, input_box.y + 8))
    
    # Instructions
    start_text = small_font.render("Press ENTER to Start Game", True, (0, 100, 0))
    game.screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 250))
    
    dashboard_text = small_font.render("Press D for Dashboard/Leaderboard", True, (0, 0, 150))
    game.screen.blit(dashboard_text, (WIDTH//2 - dashboard_text.get_width()//2, 280))
    
    controls_text = small_font.render("Controls: SPACE=Jump, DOWN=Slide", True, (100, 100, 100))
    game.screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, 320))
    
    # Show last score if exists
    if game.last_score > 0:
        last_text = small_font.render(f"Last: {game.last_player_name} - {game.last_score}", True, (255, 215, 0))
        game.screen.blit(last_text, (WIDTH//2 - last_text.get_width()//2, 350))

def draw_dashboard():
    """Draw the dashboard/leaderboard screen"""
    game.screen.fill((20, 30, 60))  # Dark blue background
    
    # Title
    title = title_font.render("🏆 Leaderboard 🏆", True, (255, 215, 0))
    game.screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
    
    try:
        # Import here to avoid issues if database.py has problems
        from database import get_top_scores
        
        # Get top scores from database
        top_scores = get_top_scores(10)  # Top 10 scores
        
        if top_scores:
            y_pos = 100
            rank_text = small_font.render("Rank  Player          Score", True, (200, 200, 200))
            game.screen.blit(rank_text, (50, y_pos))
            y_pos += 30
            
            # Draw separator line
            pygame.draw.line(game.screen, (100, 100, 100), (50, y_pos), (WIDTH-50, y_pos), 2)
            y_pos += 20
            
            for i, record in enumerate(top_scores, 1):
                player = record.get('player', 'Unknown')
                score = record.get('score', 0)
                
                # Color coding for top 3
                if i == 1:
                    color = (255, 215, 0)  # Gold
                elif i == 2:
                    color = (192, 192, 192)  # Silver
                elif i == 3:
                    color = (205, 127, 50)  # Bronze
                else:
                    color = (255, 255, 255)  # White
                
                rank_str = f"{i:2d}."
                player_str = f"{player[:12]:<12}"  # Limit name length and pad
                score_str = f"{score:>6d}"
                
                line_text = small_font.render(f"{rank_str} {player_str} {score_str}", True, color)
                game.screen.blit(line_text, (60, y_pos))
                y_pos += 25
                
                if y_pos > 320:  # Don't overflow screen
                    break
        else:
            no_scores_text = font.render("No scores yet! Be the first to play!", True, (255, 255, 255))
            game.screen.blit(no_scores_text, (WIDTH//2 - no_scores_text.get_width()//2, 150))
            
    except ImportError:
        error_text = font.render("Database not available", True, (255, 100, 100))
        game.screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, 150))
    except Exception as e:
        error_text = small_font.render(f"Database error: {str(e)[:50]}", True, (255, 100, 100))
        game.screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, 150))
    
    # Instructions
    back_text = small_font.render("Press ESC or B to go Back to Menu", True, (150, 150, 255))
    game.screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT - 50))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if menu_state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    player_name_input = player_name_input[:-1]
                elif event.key == pygame.K_RETURN:
                    # Start game
                    final_name = player_name_input.strip() or "Player"
                    game.reset(final_name)
                    game.state = "playing"
                    menu_state = "playing"
                elif event.key == pygame.K_d:
                    # Go to dashboard
                    menu_state = "dashboard"
                else:
                    # Add character to name input
                    if len(player_name_input) < 12:
                        ch = event.unicode
                        if ch.isprintable() and ch not in ['/', '\\', '|', '<', '>', ':', '"', '?', '*']:
                            player_name_input += ch

        elif menu_state == "dashboard":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_b):
                    # Go back to menu
                    menu_state = "menu"

        elif menu_state == "playing":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Allow ESC to pause/return to menu during game
                menu_state = "menu"
                game.state = "menu"
            else:
                game.handle_event(event)

    # Update game logic
    if menu_state == "playing":
        game.update()
        
        # Check if game ended and return to menu
        if game.state == "menu":
            menu_state = "menu"

    # Drawing
    if menu_state == "menu":
        draw_menu()
    elif menu_state == "dashboard":
        draw_dashboard()
    elif menu_state == "playing":
        game.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()