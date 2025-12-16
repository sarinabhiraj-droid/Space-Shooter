import pygame
import random
import math

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

shoot_sound = pygame.mixer.Sound("sounds/shoot.wav")
explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
powerup_sound = pygame.mixer.Sound("sounds/powerup.wav")
game_over_sound = pygame.mixer.Sound("sounds/game_over.wav")

shoot_sound.set_volume(0.4)
explosion_sound.set_volume(0.6)
powerup_sound.set_volume(0.5)
game_over_sound.set_volume(0.7)

pygame.mixer.music.load("sounds/bg_music.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

played_game_over_sound = False


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(20, 0), (0, 30), (40, 30)])
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.weapon_type = "basic"
        self.fire_rate = 250
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.fire_rate:
            self.last_shot = now
            if self.weapon_type == "basic":
                create_bullet(self.rect.centerx, self.rect.top, 0)
            elif self.weapon_type == "spread":
                for angle in (-20, 0, 20):
                    create_bullet(self.rect.centerx, self.rect.top, angle)
            elif self.weapon_type == "laser":
                create_bullet(self.rect.centerx, self.rect.top, 0, 15, BLUE)
            shoot_sound.play()

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def draw_health_bar(self, surface):
        fill = int((self.health / self.max_health) * 50)
        x = self.rect.centerx - 25
        y = self.rect.top - 10
        pygame.draw.rect(surface, RED, (x, y, fill, 5))
        pygame.draw.rect(surface, WHITE, (x, y, 50, 5), 1)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, color):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        rad = math.radians(angle)
        self.vel_x = math.sin(rad) * speed
        self.vel_y = -math.cos(rad) * speed
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.rect.bottom < 0:
            self.kill()


def create_bullet(x, y, angle, speed=10, color=YELLOW):
    bullet = Bullet(x, y, angle, speed, color)
    all_sprites.add(bullet)
    bullets.add(bullet)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        if enemy_type == "basic":
            self.image = pygame.Surface((30, 30))
            self.image.fill(RED)
            self.health = 20
            self.speed = 2
            self.points = 10
        elif enemy_type == "fast":
            self.image = pygame.Surface((20, 20))
            self.image.fill(ORANGE)
            self.health = 10
            self.speed = 4
            self.points = 15
        else:
            self.image = pygame.Surface((50, 40))
            self.image.fill((150, 0, 0))
            self.health = 50
            self.speed = 1
            self.points = 30
        self.max_health = self.health
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.kind = kind
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN if kind == "health" else ORANGE if kind == "spread" else BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        size = random.randint(2, 5)
        self.image = pygame.Surface((size, size))
        self.image.fill(random.choice([RED, ORANGE, YELLOW]))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = random.randint(-4, 4)
        self.vel_y = random.randint(-4, 4)
        self.life = 30

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.life -= 1
        if self.life <= 0:
            self.kill()


def explode(x, y):
    explosion_sound.play()
    for _ in range(15):
        all_sprites.add(Particle(x, y))


def spawn_enemy():
    enemy_type = random.choices(["basic", "fast", "tank"], [60, 30, 10])[0]
    e = Enemy(random.randint(20, SCREEN_WIDTH - 20), -40, enemy_type)
    all_sprites.add(e)
    enemies.add(e)


score = 0
wave = 1
enemy_spawn_rate = 1500
last_enemy_spawn = pygame.time.get_ticks()

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

running = True
game_over = False

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
            game_over = False
            played_game_over_sound = False
            score = 0
            wave = 1
            enemy_spawn_rate = 1500
            last_enemy_spawn = pygame.time.get_ticks()
            all_sprites.empty()
            bullets.empty()
            enemies.empty()
            powerups.empty()
            player = Player()
            all_sprites.add(player)
            pygame.mixer.music.play(-1)

    if not game_over:
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            player.shoot()

        if pygame.time.get_ticks() - last_enemy_spawn >= enemy_spawn_rate:
            last_enemy_spawn = pygame.time.get_ticks()
            spawn_enemy()

        all_sprites.update()

        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, enemies, False)
            if hits:
                bullet.kill()
                for enemy in hits:
                    damage = 10 if player.weapon_type == "basic" else 7 if player.weapon_type == "spread" else 20
                    enemy.health -= damage
                    if enemy.health <= 0:
                        score += enemy.points
                        explode(enemy.rect.centerx, enemy.rect.centery)
                        if random.random() < 0.3:
                            p = PowerUp(enemy.rect.centerx, enemy.rect.centery,
                                        random.choice(["health", "spread", "laser"]))
                            all_sprites.add(p)
                            powerups.add(p)
                        enemy.kill()

        for p in pygame.sprite.spritecollide(player, powerups, True):
            powerup_sound.play()
            if p.kind == "health":
                player.health = min(player.max_health, player.health + 30)
            else:
                player.weapon_type = p.kind

        if pygame.sprite.spritecollide(player, enemies, True):
            player.take_damage(20)

        if player.health <= 0:
            game_over = True
            pygame.mixer.music.stop()
            if not played_game_over_sound:
                game_over_sound.play()
                played_game_over_sound = True

        if score >= wave * 100:
            wave += 1
            enemy_spawn_rate = max(500, enemy_spawn_rate - 100)

    screen.fill(BLACK)
    all_sprites.draw(screen)
    player.draw_health_bar(screen)

    screen.blit(small_font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(small_font.render(f"Wave: {wave}", True, WHITE), (10, 40))
    screen.blit(small_font.render(f"Weapon: {player.weapon_type}", True, WHITE), (10, 70))

    if game_over:
        screen.blit(font.render("GAME OVER", True, RED), (300, 250))
        screen.blit(small_font.render("Press R to Restart", True, WHITE), (300, 300))

    pygame.display.flip()

pygame.quit()
