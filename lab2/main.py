import pygame
import random
from pygame import mixer
import time

pygame.init()
mixer.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
SPEED_INCREASE_INTERVAL = 3
SPEED_INCREASE_AMOUNT = 0.5
INITIAL_ASTEROID_SPEED = 1

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
CLOCK = pygame.time.Clock()
pygame.display.set_caption("Space Scavenger")

SHIP_IMG = pygame.image.load("spaceship.png").convert_alpha()
ASTEROID_IMG = pygame.image.load("asteroid.png").convert_alpha()
CRYSTAL_IMG = pygame.image.load("energy_crystal.png").convert_alpha()
BACKGROUND_MUSIC = mixer.Sound("background_music.wav")
CLASH_SOUND = mixer.Sound("clash_sound.wav")
BACKGROUND_MUSIC.play(-1)

top_scores = [0, 0, 0]


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.is_hovered = False

    def draw(self, surface):
        color = GRAY if self.is_hovered else WHITE
        pygame.draw.rect(surface, color, self.rect, 2)
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            return True
        return False


class GameObject:
    def __init__(self, x, y, width, height, speed=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed


class Menu:
    def __init__(self):
        self.play_button = Button(300, 400, 200, 50, "Play")
        self.title_font = pygame.font.Font(None, 64)
        self.font = pygame.font.Font(None, 24)

    def draw(self):
        SCREEN.fill(BLACK)
        title = self.title_font.render("Space Scavenger", True, WHITE)
        SCREEN.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        ship_scaled = pygame.transform.scale(SHIP_IMG, (100, 100))
        SCREEN.blit(ship_scaled, (350, 200))

        controls = [
            "Controls:",
            "Arrow Keys - Move the ship",
            "Space - Shoot",
            "",
            "Objective:",
            "Collect crystals",
            "Avoid asteroids"
        ]

        for i, text in enumerate(controls):
            control_text = self.font.render(text, True, WHITE)
            SCREEN.blit(control_text, (50, 300 + i * 25))

        score_text = self.font.render("Top Scores:", True, WHITE)
        SCREEN.blit(score_text, (600, 50))
        for i, score in enumerate(sorted(top_scores, reverse=True)[:3]):
            score_display = self.font.render(f"{score}", True, WHITE)
            SCREEN.blit(score_display, (600, 80 + i * 25))

        self.play_button.draw(SCREEN)
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if self.play_button.handle_event(event):
                    return True
            self.draw()
            CLOCK.tick(60)


class Game:
    def __init__(self):
        self.ship = GameObject(400, 500, 50, 50)
        self.asteroids = []
        self.crystals = []
        self.bullets = []
        self.score = 0
        self.game_over = False
        self.asteroid_speed = INITIAL_ASTEROID_SPEED
        self.start_time = time.time()
        self.last_speed_increase = self.start_time

    def update(self):
        if self.game_over:
            return

        current_time = time.time()
        if current_time - self.last_speed_increase >= SPEED_INCREASE_INTERVAL:
            self.asteroid_speed += SPEED_INCREASE_AMOUNT
            self.last_speed_increase = current_time

        keys = pygame.key.get_pressed()
        self.ship.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 5
        self.ship.rect.clamp_ip(SCREEN.get_rect())

        for bullet in self.bullets[:]:
            bullet.rect.y -= 7
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)
            for asteroid in self.asteroids[:]:
                if bullet.rect.colliderect(asteroid.rect):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    break

        for asteroid in self.asteroids[:]:
            asteroid.rect.y += self.asteroid_speed
            if asteroid.rect.top > SCREEN_HEIGHT:
                self.asteroids.remove(asteroid)
            elif asteroid.rect.colliderect(self.ship.rect):
                self.game_over = True
                CLASH_SOUND.play()

        for crystal in self.crystals[:]:
            crystal.rect.y += 2
            if crystal.rect.top > SCREEN_HEIGHT:
                self.crystals.remove(crystal)
            elif crystal.rect.colliderect(self.ship.rect):
                self.crystals.remove(crystal)
                self.score += 1

        if random.random() < 0.05:
            self.asteroids.append(GameObject(random.randint(0, 770), -50, 30 + self.score // 10, 30 + self.score // 10))
        if random.random() < 0.01:
            self.crystals.append(GameObject(random.randint(0, 780), -30, 20, 20))

    def draw(self):
        SCREEN.fill(BLACK)
        SCREEN.blit(pygame.transform.scale(SHIP_IMG, (50, 50)), self.ship.rect)
        for bullet in self.bullets:
            pygame.draw.rect(SCREEN, RED, bullet.rect)
        for asteroid in self.asteroids:
            SCREEN.blit(pygame.transform.scale(ASTEROID_IMG, (asteroid.rect.width, asteroid.rect.height)),
                        asteroid.rect)
        for crystal in self.crystals:
            SCREEN.blit(pygame.transform.scale(CRYSTAL_IMG, (20, 20)), crystal.rect)

        font = pygame.font.Font(None, 36)
        SCREEN.blit(font.render(f"Score: {self.score}", True, WHITE), (10, 10))

        speed_text = f"Speed: {self.asteroid_speed:.1f}"
        speed_surface = font.render(speed_text, True, WHITE)
        SCREEN.blit(speed_surface, (10, 50))

        if self.game_over:
            text = font.render("Game Over!", True, WHITE)
            SCREEN.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        return False
                    elif event.key == pygame.K_SPACE:
                        self.bullets.append(GameObject(self.ship.rect.centerx - 2, self.ship.rect.top, 4, 10))

            self.update()
            self.draw()
            CLOCK.tick(60)

    def game_over_cleanup(self):
        if self.score > min(top_scores):
            top_scores.append(self.score)
            top_scores.sort(reverse=True)
            if len(top_scores) > 3:
                top_scores.pop()


def main():
    while True:
        menu = Menu()
        if not menu.run():
            break

        game = Game()
        game.run()
        game.game_over_cleanup()


if __name__ == "__main__":
    main()
