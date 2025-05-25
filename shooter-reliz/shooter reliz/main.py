import pygame
import sys
import random
import os

# Налаштування
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Ініціалізація
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Гра-Стрілялка")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Завантаження зображень
def load_image(name, size=None):
    if not os.path.exists(name):
        print(f"❌ Файл не знайдено: {name}")
        pygame.quit()
        sys.exit()
    img = pygame.image.load(name).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

background_img = load_image("shooter reliz/assets/fon.jpg", (WIDTH, HEIGHT))
player_img = load_image("shooter reliz/assets/tank.png", (60, 60))
enemy_img = load_image("shooter reliz/assets/enemy.jpg", (40, 40))
enemy_tank_img = load_image("shooter reliz/assets/enemy_tank.jpg", (50, 50))
bullet_img = load_image("shooter reliz/assets/kvitka.png", (10, 20))
bonus_heart_img = load_image("shooter reliz/assets/hart.jpg", (30, 30))
bonus_fire_img = load_image("shooter reliz/assets/fire.jpg", (30, 30))

menu_button_rect = pygame.Rect(WIDTH - 130, 10, 120, 40)
button_easy_rect = pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 50, 180, 60)
button_hard_rect = pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2 + 50, 180, 60)

# --- Функції ---
def spawn_enemy():
    etype = random.choice(enemy_types)
    width = etype["img"].get_width()
    height = etype["img"].get_height()
    rect = pygame.Rect(random.randint(0, WIDTH - width), -height - 10, width, height)
    enemies.append({"rect": rect, "img": etype["img"], "hp": etype["hp"]})

def spawn_bonus(x, y):
    if random.random() < 0.3:
        kind = random.choice(["heart", "fire"])
        img = bonus_heart_img if kind == "heart" else bonus_fire_img
        bonus = {"rect": pygame.Rect(x, y, 30, 30), "type": kind, "img": img}
        bonus_list.append(bonus)

def draw_health_bar(x, y, lives):
    max_lives = 5
    width = 100
    pygame.draw.rect(screen, (255, 0, 0), (x, y, width, 10))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, width * lives / max_lives, 10))

def draw_ui():
    screen.blit(font.render(f"Рахунок: {score}", True, WHITE), (10, 10))
    draw_health_bar(10, 40, lives)
    screen.blit(font.render(f"Хвиля: {wave}", True, (100, 255, 255)), (10, 60))
    screen.blit(font.render(f"Рекорд: {high_score}", True, WHITE), (10, 90))
    screen.blit(font.render("Меню", True, WHITE), (menu_button_rect.x + 25, menu_button_rect.y + 10))

def bullet_hit(enemy):
    global score, kills
    enemy["hp"] -= 1
    if enemy["hp"] <= 0:
        enemies.remove(enemy)
        score += 10
        kills += 1
        spawn_bonus(enemy["rect"].x, enemy["rect"].y)

def reset_game():
    global bullets, enemies, bonus_list
    global score, lives, wave, kills, spawn_timer, shoot_cooldown, fire_mode
    player.x = WIDTH // 2
    player.y = HEIGHT - 70
    bullets = []
    enemies = []
    bonus_list = []
    score = 0
    lives = 5
    wave = 1
    kills = 0
    spawn_timer = 0
    fire_mode = False

player = pygame.Rect(WIDTH // 2, HEIGHT - 70, 60, 60)
enemy_types = [
    {"img": enemy_img, "hp": 1},
    {"img": enemy_tank_img, "hp": 2}
]

fire_mode = False
reset_game()
game_state = "menu"
high_score = 0
WIN_WAVE = 5
shoot_cooldown = 500
last_shot = pygame.time.get_ticks()
difficulty = None

running = True
while running:
    dt = clock.tick(FPS)
    screen.blit(background_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "menu" or game_state in ["win", "lose"]:
                if button_easy_rect.collidepoint(event.pos):
                    difficulty = "easy"
                    shoot_cooldown = 500
                    WIN_WAVE = 4
                    reset_game()
                    game_state = "play"
                elif button_hard_rect.collidepoint(event.pos):
                    difficulty = "hard"
                    shoot_cooldown = 300
                    WIN_WAVE = 6
                    reset_game()
                    game_state = "play"
            elif game_state == "play" and menu_button_rect.collidepoint(event.pos):
                game_state = "menu"

        if event.type == pygame.USEREVENT + 1:
            fire_mode = False
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)

    keys = pygame.key.get_pressed()
    if game_state == "menu" or game_state in ["win", "lose"]:
        pygame.draw.rect(screen, (200, 255, 200), button_easy_rect)
        pygame.draw.rect(screen, (255, 200, 200), button_hard_rect)
        screen.blit(font.render("Легкий режим", True, BLACK), (button_easy_rect.x + 10, button_easy_rect.y + 15))
        screen.blit(font.render("Важкий режим", True, BLACK), (button_hard_rect.x + 10, button_hard_rect.y + 15))
        if game_state in ["win", "lose"]:
            message = "ТИ ВИГРАВ!" if game_state == "win" else "ТИ ПРОГРАВ!"
            msg_surface = font.render(message, True, WHITE)
            screen.blit(msg_surface, (WIDTH // 2 - msg_surface.get_width() // 2, HEIGHT // 2 - 80))
            hs_surface = font.render(f"Рекорд: {high_score}", True, WHITE)
            screen.blit(hs_surface, (WIDTH // 2 - hs_surface.get_width() // 2, HEIGHT // 2 - 40))
    elif game_state == "play":
        if keys[pygame.K_a] and player.left > 0:
            player.x -= 5
        if keys[pygame.K_d] and player.right < WIDTH:
            player.x += 5
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - last_shot > shoot_cooldown:
                if fire_mode:
                    bullets.append(pygame.Rect(player.centerx - 20, player.top - 20, 10, 20))
                    bullets.append(pygame.Rect(player.centerx + 10, player.top - 20, 10, 20))
                else:
                    bullets.append(pygame.Rect(player.centerx - 5, player.top - 20, 10, 20))
                last_shot = now

        for bullet in bullets[:]:
            bullet.y -= 10
            if bullet.bottom < 0:
                bullets.remove(bullet)

        spawn_timer += 1
        if spawn_timer > 60:
            spawn_enemy()
            spawn_timer = 0

        for enemy in enemies[:]:
            speed = 1.5 + 0.1 * wave
            enemy["rect"].y += speed
            if player.colliderect(enemy["rect"]):
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    game_state = "lose"
                    high_score = max(high_score, score)
            elif enemy["rect"].top > HEIGHT:
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    game_state = "lose"
                    high_score = max(high_score, score)

        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet.colliderect(enemy["rect"]):
                    bullet_hit(enemy)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

        for bonus in bonus_list[:]:
            bonus["rect"].y += 2
            if bonus["rect"].top > HEIGHT:
                bonus_list.remove(bonus)
            elif player.colliderect(bonus["rect"]):
                if bonus["type"] == "heart":
                    lives += 1
                elif bonus["type"] == "fire":
                    fire_mode = True
                    pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
                bonus_list.remove(bonus)

        if kills >= wave * 20:
            wave += 1
            if wave == WIN_WAVE:
                enemies.append({"rect": pygame.Rect(WIDTH // 2 - 50, -100, 100, 100), "img": enemy_tank_img, "hp": 10})
            elif wave > WIN_WAVE:
                game_state = "win"
                high_score = max(high_score, score)

        screen.blit(player_img, player)
        for bullet in bullets:
            screen.blit(bullet_img, bullet)
        for enemy in enemies:
            screen.blit(enemy["img"], enemy["rect"])
        for bonus in bonus_list:
            screen.blit(bonus["img"], bonus["rect"])
        draw_ui()

    pygame.display.flip()

pygame.quit()
sys.exit()
