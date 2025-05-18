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

background_img = load_image("assets/fon.jpg", (WIDTH, HEIGHT))
player_img = load_image("assets/tank.png", (60, 60))
enemy_img = load_image("assets/enemy.jpg", (40, 40))
enemy_tank_img = load_image("assets/enemy_tank.jpg", (50, 50))
bullet_img = load_image("assets/kvitka.png", (10, 20))
bonus_heart_img = load_image("assets/hart.jpg", (30, 30))
bonus_fire_img = load_image("assets/fire.jpg", (30, 30))

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

def draw_ui():
    screen.blit(font.render(f"Рахунок: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Життя: {lives}", True, (255, 100, 100)), (10, 40))
    screen.blit(font.render(f"Хвиля: {wave}", True, (100, 255, 255)), (10, 70))
    screen.blit(font.render(f"Рекорд: {high_score}", True, WHITE), (10, 100))

def bullet_hit(enemy):
    global score, kills
    enemy["hp"] -= 1
    if enemy["hp"] <= 0:
        enemies.remove(enemy)
        score += 10
        kills += 1
        spawn_bonus(enemy["rect"].x, enemy["rect"].y)

def reset_game():
    global player, bullets, enemies, bonus_list
    global score, lives, wave, kills, spawn_timer, shoot_cooldown

    player = pygame.Rect(WIDTH // 2, HEIGHT - 70, 60, 60)
    bullets = []
    enemies = []
    bonus_list = []
    score = 0
    lives = 5
    wave = 1
    kills = 0
    spawn_timer = 0
    shoot_cooldown = 500

# --- Початкові змінні ---
enemy_types = [
    {"img": enemy_img, "hp": 1},
    {"img": enemy_tank_img, "hp": 2}
]

reset_game()
game_state = "play"  # "play", "win", "lose"
high_score = 0
WIN_WAVE = 5
last_shot = pygame.time.get_ticks()
# --- Основний цикл ---
running = True
while running:
    dt = clock.tick(FPS)
    screen.blit(background_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Перезапуск гри після програшу або виграшу
        if event.type == pygame.KEYDOWN and game_state in ["win", "lose"]:
            if event.key == pygame.K_RETURN:
                reset_game()
                game_state = "play"

    keys = pygame.key.get_pressed()
    if game_state == "play":
        if keys[pygame.K_a] and player.left > 0:
            player.x -= 5
        if keys[pygame.K_d] and player.right < WIDTH:
            player.x += 5
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - last_shot > shoot_cooldown:
                bullet = pygame.Rect(player.centerx - 5, player.top - 20, 10, 20)
                bullets.append(bullet)
                last_shot = now

        # Оновлення куль
        for bullet in bullets[:]:
            bullet.y -= 10
            if bullet.bottom < 0:
                bullets.remove(bullet)

        # Спаун ворогів
        spawn_timer += 1
        if spawn_timer > 60:
            spawn_enemy()
            spawn_timer = 0

        # Рух ворогів
        for enemy in enemies[:]:
            enemy["rect"].y += 1.5

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

        # Перевірка попадань
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet.colliderect(enemy["rect"]):
                    bullet_hit(enemy)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

        # Бонуси
       # --- Бонуси ---
        for bonus in bonus_list[:]:
            bonus["rect"].y += 2
            if bonus["rect"].top > HEIGHT:
                bonus_list.remove(bonus)
            elif player.colliderect(bonus["rect"]):
                if bonus["type"] == "heart":
                    lives += 1
                elif bonus["type"] == "fire":
                    shoot_cooldown = max(100, shoot_cooldown - 50)  # 🔥 ЗМІНИ ЦЕ
                bonus_list.remove(bonus)


        # Хвилі
        if kills >= wave * 20:
            wave += 1
            if wave > WIN_WAVE:
                game_state = "win"
                high_score = max(high_score, score)

        # Малювання гри
        screen.blit(player_img, player)
        for bullet in bullets:
            screen.blit(bullet_img, bullet)
        for enemy in enemies:
            screen.blit(enemy["img"], enemy["rect"])
        for bonus in bonus_list:
            screen.blit(bonus["img"], bonus["rect"])
        draw_ui()

    else:
        # Екран кінця гри
        message = "ТИ ВИГРАВ!" if game_state == "win" else "ТИ ПРОГРАВ!"
        msg_surface = font.render(message, True, WHITE)
        restart_surface = font.render("Натисни Enter щоб почати спочатку", True, (200, 200, 200))
        screen.blit(msg_surface, (WIDTH // 2 - msg_surface.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(restart_surface, (WIDTH // 2 - restart_surface.get_width() // 2, HEIGHT // 2 + 10))
        hs_surface = font.render(f"Рекорд: {high_score}", True, WHITE)
        screen.blit(hs_surface, (WIDTH // 2 - hs_surface.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()

pygame.quit()
sys.exit()