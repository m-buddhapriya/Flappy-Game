import pygame
import random
import os
import json

pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 288, 512
GRAVITY = 0.25
FLAP_POWER = -4.5
PIPE_GAP = 100
FPS = 60

# Paths
ASSETS = "."
SPRITES = os.path.join(ASSETS, "sprites")
SOUNDS = os.path.join(ASSETS, "audio")
SCORE_FILE = "highscore.json"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Flappy Bird")

# Bird skins
BIRD_SKINS = {
    'yellow': ['yellowbird-upflap.png', 'yellowbird-midflap.png', 'yellowbird-downflap.png'],
    'blue': ['bluebird-upflap.png', 'bluebird-midflap.png', 'bluebird-downflap.png'],
    'red': ['redbird-upflap.png', 'redbird-midflap.png', 'redbird-downflap.png']
}

# Load images
IMAGES = {
    'background_day': pygame.image.load(os.path.join(SPRITES, 'background-day.png')),
    'background_night': pygame.image.load(os.path.join(SPRITES, 'background-night.png')),
    'base': pygame.image.load(os.path.join(SPRITES, 'base.png')),
    'pipe': pygame.image.load(os.path.join(SPRITES, 'pipe-green.png')),
    'pipe_flipped': pygame.transform.flip(pygame.image.load(os.path.join(SPRITES, 'pipe-green.png')), False, True),
    'message': pygame.image.load(os.path.join(SPRITES, 'message.png')),
    'gameover': pygame.image.load(os.path.join(SPRITES, 'gameover.png')),
    'numbers': [pygame.image.load(os.path.join(SPRITES, f'{i}.png')) for i in range(10)],
}

# Load sounds
SOUND = {
    'die': pygame.mixer.Sound(os.path.join(SOUNDS, 'die.wav')),
    'hit': pygame.mixer.Sound(os.path.join(SOUNDS, 'hit.wav')),
    'point': pygame.mixer.Sound(os.path.join(SOUNDS, 'point.wav')),
    'wing': pygame.mixer.Sound(os.path.join(SOUNDS, 'wing.wav')),
    'swoosh': pygame.mixer.Sound(os.path.join(SOUNDS, 'swoosh.wav'))
}

# Score handling
def load_highscore():
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, 'r') as f:
                return int(json.load(f).get('highscore', 0))
        except:
            return 0
    return 0

def save_highscore(score):
    with open(SCORE_FILE, 'w') as f:
        json.dump({'highscore': score}, f)

# Bird class
class Bird:
    def __init__(self, skin='yellow'):
        self.frames = [pygame.image.load(os.path.join(SPRITES, img)) for img in BIRD_SKINS[skin]]
        self.x = 50
        self.y = 200
        self.vel = 0
        self.tick = 0
        self.index = 0

    def flap(self):
        self.vel = FLAP_POWER
        SOUND['wing'].play()

    def update(self):
        self.tick += 1
        self.vel += GRAVITY
        self.y += self.vel
        if self.tick % 5 == 0:
            self.index = (self.index + 1) % 3

    def draw(self):
        screen.blit(self.frames[self.index], (self.x, self.y))

    def rect(self):
        return self.frames[0].get_rect(topleft=(self.x, self.y))

# Pipe class
class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH + 30
        self.height = random.randint(100, 300)
        self.passed = False

    def update(self):
        self.x -= 2

    def draw(self):
        screen.blit(IMAGES['pipe_flipped'], (self.x, self.height - PIPE_GAP - IMAGES['pipe'].get_height()))
        screen.blit(IMAGES['pipe'], (self.x, self.height))

    def rects(self):
        top_rect = IMAGES['pipe'].get_rect(topleft=(self.x, self.height))
        bottom_rect = IMAGES['pipe'].get_rect(topleft=(self.x, self.height - PIPE_GAP - IMAGES['pipe'].get_height()))
        return bottom_rect, top_rect

# Drawing functions
def draw_text_centered(text, font, color, y):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(render, rect)

def draw_score(score):
    digits = list(str(score))
    width = sum(IMAGES['numbers'][int(d)].get_width() for d in digits)
    x = (SCREEN_WIDTH - width) // 2
    for d in digits:
        screen.blit(IMAGES['numbers'][int(d)], (x, 20))
        x += IMAGES['numbers'][int(d)].get_width()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# Fonts
FONT_SMALL = pygame.font.SysFont(None, 24)
FONT_MEDIUM = pygame.font.SysFont(None, 32)

def main():
    bird = Bird('yellow')
    pipes = []
    base_x = 0
    score = 0
    highscore = load_highscore()
    background = random.choice(['background_day', 'background_night'])
    paused = False
    game_active = False
    game_started = False
    running = True

    # Pause button rectangle
    pause_btn_rect = pygame.Rect(SCREEN_WIDTH - 70, 10, 60, 30)
    # Restart button rectangle (will show only when game over)
    restart_btn_rect = pygame.Rect((SCREEN_WIDTH // 2) - 50, 350, 100, 40)

    while running:
        screen.blit(IMAGES[background], (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False  # Reset once per frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_started:
                        game_started = True
                        game_active = True
                        bird = Bird('yellow')
                        pipes.clear()
                        score = 0
                    elif not game_active:
                        bird = Bird('yellow')
                        pipes.clear()
                        score = 0
                        game_active = True
                    if not paused:
                        bird.flap()

        # Pause button click handling
        if game_active and mouse_clicked and pause_btn_rect.collidepoint(mouse_pos):
            paused = not paused
            if paused:
                SOUND['swoosh'].play()

        # Restart button click handling
        if not game_active and game_started and mouse_clicked and restart_btn_rect.collidepoint(mouse_pos):
            bird = Bird('yellow')
            pipes.clear()
            score = 0
            game_active = True
            paused = False

        if game_active and not paused:
            bird.update()
            if len(pipes) == 0 or pipes[-1].x < SCREEN_WIDTH - 150:
                pipes.append(Pipe())

            for pipe in pipes:
                pipe.update()
                bottom, top = pipe.rects()
                if bird.rect().colliderect(bottom) or bird.rect().colliderect(top):
                    SOUND['hit'].play()
                    game_active = False

            if bird.y + bird.frames[0].get_height() >= SCREEN_HEIGHT - 112:
                SOUND['die'].play()
                game_active = False

            # Remove off-screen pipes
            pipes = [p for p in pipes if p.x > -50]

            # Update score
            for pipe in pipes:
                if not pipe.passed and pipe.x + IMAGES['pipe'].get_width() < bird.x:
                    pipe.passed = True
                    score += 1
                    SOUND['point'].play()

        bird.draw()
        for pipe in pipes:
            pipe.draw()

        # Draw base
        base_x = (base_x - 2) % -48
        screen.blit(IMAGES['base'], (base_x, SCREEN_HEIGHT - 112))

        draw_score(score)

        # Draw pause button if game active
        if game_active:
            pygame.draw.rect(screen, GRAY, pause_btn_rect)
            pause_text = FONT_SMALL.render("Pause" if not paused else "Resume", True, WHITE)
            pause_text_rect = pause_text.get_rect(center=pause_btn_rect.center)
            screen.blit(pause_text, pause_text_rect)

        # Start screen
        if not game_started:
            screen.blit(IMAGES['message'], (SCREEN_WIDTH // 2 - IMAGES['message'].get_width() // 2, 100))
        # Game over screen
        elif not game_active:
            screen.blit(IMAGES['gameover'], (SCREEN_WIDTH // 2 - IMAGES['gameover'].get_width() // 2, 200))
            if score > highscore:
                highscore = score
                save_highscore(highscore)
            draw_text_centered(f"Highscore: {highscore}", FONT_MEDIUM, WHITE, 300)

            # Draw restart button
            pygame.draw.rect(screen, GREEN, restart_btn_rect)
            restart_text = FONT_SMALL.render("Restart", True, WHITE)
            restart_text_rect = restart_text.get_rect(center=restart_btn_rect.center)
            screen.blit(restart_text, restart_text_rect)

        # Pause overlay text
        if paused:
            draw_text_centered("Paused", FONT_MEDIUM, RED, SCREEN_HEIGHT // 2)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()
