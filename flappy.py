import pygame
import random
import os
import math
import wave
import struct

# ---------------------------
# Config / Constants
# ---------------------------
pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2)
except Exception:
    # mixer may fail on some systems; continue without sound
    pass

WIDTH, HEIGHT = 540, 760
FPS = 60
# create screen with new resolution
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Improved")
CLOCK = pygame.time.Clock()

# Safer asset dir (works if __file__ is missing in some environments)
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSET_DIR, exist_ok=True)

# Font handling: prefer bundled TTF (PressStart2P-Regular.ttf). Use pygame.font.Font for
# scaling so font rendering is consistent. If the TTF is missing, fall back to the
# default pygame font via pygame.font.Font(None, size).
FONT_PATH = os.path.join(ASSET_DIR, "PressStart2P-Regular.ttf")

def load_font(size):
    """Return a pygame Font object at the requested size using the bundled TTF
    when available, otherwise use the default pygame font (Font(None, size)).
    """
    try:
        if os.path.exists(FONT_PATH):
            return pygame.font.Font(FONT_PATH, size)
    except Exception:
        pass
    # Fallback to default font (still using pygame.font.Font API)
    return pygame.font.Font(None, size)

# Pre-create a few common sizes
FONT_BIG = load_font(64)
FONT_MED = load_font(40)
FONT_SMALL = load_font(24)


def render_text_fit(text, font, color, max_width):
    """Render text to a surface and scale it down if it exceeds max_width.

    This keeps the font visually consistent but avoids text being clipped by the
    window. Returns a pygame.Surface.
    """
    surf = font.render(text, True, color)
    if surf.get_width() <= max_width:
        return surf
    # scale surface down proportionally
    scale = max_width / surf.get_width()
    new_w = max(1, int(surf.get_width() * scale))
    new_h = max(1, int(surf.get_height() * scale))
    return pygame.transform.smoothscale(surf, (new_w, new_h))

WHITE = (255, 255, 255)
SKY = (24, 154, 255)
GROUND_COLOR = (222, 184, 135)
PIPE_COLOR = (0, 180, 0)
PIPE_SHADOW = (0, 140, 0)
PIPE_HIGHLIGHT = (80, 220, 80)

# Sound filenames (generated if missing)
FLAP_WAV = os.path.join(ASSET_DIR, "flap.wav")
POINT_WAV = os.path.join(ASSET_DIR, "point.wav")
HIT_WAV = os.path.join(ASSET_DIR, "hit.wav")


def make_tone(path, freq=440.0, duration=0.12, volume=0.5):
    """Generate a simple sine wave WAV file at path if it doesn't exist."""
    if os.path.exists(path):
        return
    framerate = 44100
    amplitude = int(32767 * volume)
    nframes = int(duration * framerate)
    comptype = "NONE"
    compname = "not compressed"
    nchannels = 1
    sampwidth = 2

    with wave.open(path, 'w') as wav:
        wav.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
        for i in range(nframes):
            t = float(i) / framerate
            val = int(amplitude * math.sin(2.0 * math.pi * freq * t))
            wav.writeframes(struct.pack('<h', val))


# create short fx if missing
try:
    make_tone(FLAP_WAV, freq=650.0, duration=0.08, volume=0.6)
    make_tone(POINT_WAV, freq=900.0, duration=0.16, volume=0.35)
    make_tone(HIT_WAV, freq=120.0, duration=0.35, volume=0.6)
except Exception:
    pass

# load sounds (safe)
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

SND_FLAP = load_sound(FLAP_WAV)
SND_POINT = load_sound(POINT_WAV)
SND_HIT = load_sound(HIT_WAV)


# ---------------------------
# Load assets (sprites)
# ---------------------------
def load_image(name, scale=None):
    path = os.path.join(ASSET_DIR, name)
    img = pygame.image.load(path).convert_alpha()
    if scale:
        img = pygame.transform.smoothscale(img, scale)
    return img


try:
    # scale bird sprite to match the larger window
    BIRD_IMG = load_image("Flappy-Bird-PNG-Images.png", scale=(72, 72))
except Exception:
    # fallback: simple circle if image missing
    BIRD_IMG = pygame.Surface((72, 72), pygame.SRCALPHA)
    pygame.draw.circle(BIRD_IMG, (255, 255, 0), (36, 36), 30)

try:
    LOGO_IMG = load_image("Flappy-Bird-PNG-HD-Image.png")
except Exception:
    LOGO_IMG = None


# ---------------------------
# Game variables
# ---------------------------
GRAVITY = 0.45
JUMP_VELOCITY = -9

PIPE_WIDTH = 90
PIPE_GAP = 180
# Dynamic gap settings: start with a bigger gap and shrink as score increases
START_PIPE_GAP = 300
MIN_PIPE_GAP = 140
GAP_SHRINK_PER_POINT = 3  # how many pixels smaller per point
PIPE_SPEED_BASE = 4.0

GROUND_HEIGHT = 110


class Pipe:
    def __init__(self, x, gap=None):
        self.x = x
        # if a gap is provided use it, otherwise default to constant
        self.gap = gap if gap is not None else PIPE_GAP
        # ensure top is within reasonable bounds given the gap and ground
        max_top = HEIGHT - GROUND_HEIGHT - 80 - self.gap
        self.top = random.randint(80, max(80, max_top))
        self.bottom = self.top + self.gap
        self.passed = False

    def rects(self):
        top = pygame.Rect(self.x, 0, PIPE_WIDTH, self.top)
        bot = pygame.Rect(self.x, self.bottom, PIPE_WIDTH, HEIGHT - self.bottom - GROUND_HEIGHT)
        return top, bot

    def update(self, speed):
        self.x -= speed

    def draw(self, surf):
        top_rect, bot_rect = self.rects()
        # main pipe
        pygame.draw.rect(surf, PIPE_COLOR, top_rect)
        pygame.draw.rect(surf, PIPE_COLOR, bot_rect)
        # shadow stripe
        shadow_w = max(4, PIPE_WIDTH // 6)
        pygame.draw.rect(surf, PIPE_SHADOW, (top_rect.x + PIPE_WIDTH - shadow_w, top_rect.y, shadow_w, top_rect.height))
        pygame.draw.rect(surf, PIPE_SHADOW, (bot_rect.x + PIPE_WIDTH - shadow_w, bot_rect.y, shadow_w, bot_rect.height))
        # rounded caps
        cap_radius = PIPE_WIDTH // 2
        pygame.draw.circle(surf, PIPE_COLOR, (top_rect.x + PIPE_WIDTH // 2, top_rect.bottom), cap_radius)
        pygame.draw.circle(surf, PIPE_SHADOW, (top_rect.x + PIPE_WIDTH - shadow_w // 2, top_rect.bottom), cap_radius // 2)
        pygame.draw.circle(surf, PIPE_COLOR, (bot_rect.x + PIPE_WIDTH // 2, bot_rect.y), cap_radius)


class Bird:
    def __init__(self):
        self.x = 120
        self.y = HEIGHT // 2
        self.vel = 0
        self.img = BIRD_IMG

    def flap(self):
        self.vel = JUMP_VELOCITY

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel

    def get_rect(self):
        w, h = self.img.get_size()
        return pygame.Rect(int(self.x - w // 2), int(self.y - h // 2), w, h)

    def draw(self, surf):
        # rotate bird slightly based on velocity
        angle = max(-25, min(45, -self.vel * 3))
        rotated = pygame.transform.rotozoom(self.img, angle, 1)
        r = rotated.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(rotated, r.topleft)


# ---------------------------
# Helpers: highscore
# ---------------------------
HIGHSCORE_FILE = os.path.join(ASSET_DIR, "highscore.txt")

def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0

def save_highscore(value):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(int(value)))
    except Exception:
        pass


# ---------------------------
# Game states + main loop
# ---------------------------
def title_screen(screen):
    # nicer gradient background
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(24 + (135 - 24) * t)
        g = int(154 + (206 - 154) * t)
        b = int(255 - (60 * t))
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # logo box
    if LOGO_IMG:
        logo = pygame.transform.smoothscale(LOGO_IMG, (320, 90))
        box = pygame.Surface((logo.get_width() + 24, logo.get_height() + 24), pygame.SRCALPHA)
        box.fill((0, 0, 0, 90))
        screen.blit(box, (WIDTH // 2 - box.get_width() // 2, 40))
        screen.blit(logo, (WIDTH // 2 - logo.get_width() // 2, 52))

    # position UI proportional to screen height
    maxw = WIDTH - 40
    title = render_text_fit("Flappy Bird", FONT_BIG, (255, 250, 200), maxw)
    title_y = int(HEIGHT * 0.22)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, title_y))

    instr = render_text_fit("Press SPACE to start", FONT_MED, (255, 255, 255), maxw)
    instr_y = int(HEIGHT * 0.34)
    screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, instr_y))

    small = render_text_fit("Use SPACE to flap. Press Q to quit.", FONT_SMALL, (240, 240, 240), maxw)
    small_y = int(HEIGHT * 0.42)
    screen.blit(small, (WIDTH // 2 - small.get_width() // 2, small_y))

    # credit
    credit = FONT_SMALL.render("Created by Sahid", True, (230, 230, 230))
    screen.blit(credit, (WIDTH - credit.get_width() - 8, HEIGHT - 36))

    pygame.display.flip()


def game_over_screen(screen, score, highscore):
    screen.fill(SKY)
    maxw = WIDTH - 40
    over = render_text_fit("Game Over", FONT_BIG, WHITE, maxw)
    over_y = int(HEIGHT * 0.16)
    screen.blit(over, (WIDTH // 2 - over.get_width() // 2, over_y))

    sc = render_text_fit(f"Score: {score}", FONT_MED, WHITE, maxw)
    hs = render_text_fit(f"High Score: {highscore}", FONT_MED, WHITE, maxw)
    screen.blit(sc, (WIDTH // 2 - sc.get_width() // 2, int(HEIGHT * 0.28)))
    screen.blit(hs, (WIDTH // 2 - hs.get_width() // 2, int(HEIGHT * 0.34)))

    again = render_text_fit("Press SPACE to play again or Q to quit.", FONT_SMALL, WHITE, maxw)
    screen.blit(again, (WIDTH // 2 - again.get_width() // 2, int(HEIGHT * 0.44)))

    pygame.display.flip()


def main():
    highscore = load_highscore()

    state = "menu"  # menu, play, gameover

    bird = Bird()
    pipes = []
    frame = 0
    score = 0

    pipe_speed = PIPE_SPEED_BASE

    running = True
    while running:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                if state == "menu":
                    if event.key == pygame.K_SPACE:
                        # start game
                        state = "play"
                        bird = Bird()
                        pipes = []
                        score = 0
                        frame = 0
                        pipe_speed = PIPE_SPEED_BASE
                elif state == "play":
                    if event.key == pygame.K_SPACE:
                        bird.flap()
                        if SND_FLAP:
                            try:
                                SND_FLAP.play()
                            except Exception:
                                pass
                elif state == "gameover":
                    if event.key == pygame.K_SPACE:
                        state = "play"
                        bird = Bird()
                        pipes = []
                        score = 0
                        frame = 0
                        pipe_speed = PIPE_SPEED_BASE

        if state == "menu":
            title_screen(SCREEN)
            continue

        if state == "play":
            # update
            bird.update()

            frame += 1
            if frame % 90 == 0:
                # gap starts larger and shrinks as score increases, but never below MIN_PIPE_GAP
                dynamic_gap = max(MIN_PIPE_GAP, START_PIPE_GAP - int(score * GAP_SHRINK_PER_POINT))
                pipes.append(Pipe(WIDTH + 40, gap=dynamic_gap))

            # gradually increase speed
            pipe_speed = PIPE_SPEED_BASE + min(2.5, score * 0.05)

            for p in pipes:
                p.update(pipe_speed)

            # remove off-screen
            pipes = [p for p in pipes if p.x + PIPE_WIDTH > -50]

            # scoring
            for p in pipes:
                if not p.passed and p.x + PIPE_WIDTH < bird.x:
                    p.passed = True
                    score += 1
                    if SND_POINT:
                        try:
                            SND_POINT.play()
                        except Exception:
                            pass

            # collision
            bird_rect = bird.get_rect()
            # ground/ceiling
            if bird.y - bird_rect.height/2 <= 0 or bird.y + bird_rect.height/2 >= HEIGHT - GROUND_HEIGHT:
                state = "gameover"
                if score > highscore:
                    highscore = score
                    save_highscore(highscore)
                if SND_HIT:
                    try:
                        SND_HIT.play()
                    except Exception:
                        pass

            for p in pipes:
                top_rect, bot_rect = p.rects()
                if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bot_rect):
                    state = "gameover"
                    if score > highscore:
                        highscore = score
                        save_highscore(highscore)
                    if SND_HIT:
                        try:
                            SND_HIT.play()
                        except Exception:
                            pass
                    break

            # draw with gradient background
            for y in range(HEIGHT - GROUND_HEIGHT):
                t = y / (HEIGHT - GROUND_HEIGHT)
                r = int(24 + (135 - 24) * t)
                g = int(154 + (206 - 154) * t)
                b = int(255 - (60 * t))
                pygame.draw.line(SCREEN, (r, g, b), (0, y), (WIDTH, y))
            # draw pipes
            for p in pipes:
                p.draw(SCREEN)

            # draw ground
            pygame.draw.rect(SCREEN, GROUND_COLOR, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))

            # draw bird
            bird.draw(SCREEN)

            # draw score (slightly lower to fit large font)
            score_surf = render_text_fit(str(score), FONT_BIG, WHITE, WIDTH - 40)
            SCREEN.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, int(HEIGHT * 0.04)))

            # draw highscore in corner
            hs_surf = render_text_fit(f"High: {highscore}", FONT_SMALL, (255, 240, 180), WIDTH - 40)
            SCREEN.blit(hs_surf, (12, 12))

            pygame.display.flip()
            continue

        if state == "gameover":
            game_over_screen(SCREEN, score, highscore)

    pygame.quit()


if __name__ == "__main__":
    main()
