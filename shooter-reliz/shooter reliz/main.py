import pygame
import sys
import random
import os

# Налаштування
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 150, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 40)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Гра-Стрілялка")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 40)

def load_image(name, size=None):
    if not os.path.exists(name):
        print(f"❌ Файл не знайдено: {name}")
        pygame.quit()
        sys.exit()
    img = pygame.image.load(name).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

# Зображення
background_img = load_image("shooter reliz/assets/fon.jpg", (WIDTH, HEIGHT))
player_img = load_image("shooter reliz/assets/tank.png", (60, 60))
enemy_img = load_image("shooter reliz/assets/enemy.jpg", (40, 40))
enemy_tank_img = load_image("shooter reliz/assets/enemy_tank.jpg", (50, 50))
bullet_img = load_image("shooter reliz/assets/kvitka.png", (10, 20))
bonus_heart_img = load_image("shooter reliz/assets/hart.jpg", (30, 30))
bonus_fire_img = load_image("shooter reliz/assets/fire.jpg", (30, 30))

# Прямокутники кнопок меню
button_easy_rect = pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2, 180, 60)
button_hard_rect = pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2, 180, 60)
button_settings_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 90, 160, 50)
button_quit_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 160, 160, 50)

menu_button_rect = pygame.Rect(WIDTH - 130, 10, 120, 40)

# Налаштування звуку (поки без звуку, для прикладу)
volume = 0.5

# Керування
control_scheme = "AD"  # варіанти: "AD", "ARROWS"

# Складність
difficulty = None  # "easy" або "hard"

# Ігрові змінні і константи
WIN_WAVE = 5
shoot_cooldown = 500

# --- Ігрові об'єкти ---
player = pygame.Rect(WIDTH // 2, HEIGHT - 70, 60, 60)
enemy_types = [
    {"img": enemy_img, "hp": 1},
    {"img": enemy_tank_img, "hp": 2}
]

def reset_game():
    global bullets, enemies, bonus_list
    global score, lives, wave, kills, spawn_timer, fire_mode, fire_mode_end_time, last_shot
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
    fire_mode_end_time = 0
    last_shot = 0

reset_game()

game_state = "menu"
paused = False
high_score = 0

# --- Допоміжні функції ---

def draw_text_center(text, y, font_, color=WHITE):
    surf = font_.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))

def draw_button(rect, text, color_bg, color_text=BLACK):
    pygame.draw.rect(screen, color_bg, rect)
    text_surf = font.render(text, True, color_text)
    screen.blit(text_surf, (rect.x + (rect.width - text_surf.get_width()) // 2,
                            rect.y + (rect.height - text_surf.get_height()) // 2))

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
    pygame.draw.rect(screen, (0, 255, 0), (x, y, width * min(lives, max_lives) / max_lives, 10))

def draw_ui():
    screen.blit(font.render(f"Рахунок: {score}", True, WHITE), (10, 10))
    draw_health_bar(10, 40, lives)
    screen.blit(font.render(f"Хвиля: {wave}", True, (100, 255, 255)), (10, 60))
    screen.blit(font.render(f"Рекорд: {high_score}", True, WHITE), (10, 90))
    pygame.draw.rect(screen, RED, menu_button_rect)
    screen.blit(font.render("Меню", True, WHITE), (menu_button_rect.x + 25, menu_button_rect.y + 10))

def bullet_hit(enemy):
    global score, kills
    enemy["hp"] -= 1
    if enemy["hp"] <= 0:
        enemies.remove(enemy)
        score += 10
        kills += 1
        spawn_bonus(enemy["rect"].x, enemy["rect"].y)

# --- Головний цикл ---

while True:
    dt = clock.tick(FPS)
    screen.blit(background_img, (0, 0))
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "menu":
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
                elif button_settings_rect.collidepoint(event.pos):
                    game_state = "settings"
                elif button_quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            elif game_state == "settings":
                mx, my = event.pos
                if control_ad_rect.collidepoint(mx, my):
                    control_scheme = "AD"
                if control_arrows_rect.collidepoint(mx, my):
                    control_scheme = "ARROWS"
                if vol_up_rect.collidepoint(mx, my):
                    volume = min(volume + 0.1, 1.0)
                if vol_down_rect.collidepoint(mx, my):
                    volume = max(volume - 0.1, 0.0)
                if settings_back_rect.collidepoint(mx, my):
                    game_state = "menu"

            elif game_state == "play":
                if menu_button_rect.collidepoint(event.pos):
                    game_state = "menu"
                    paused = False

        if event.type == pygame.KEYDOWN:
            if game_state == "play":
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                    paused = False
            elif game_state == "settings":
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"

    if game_state == "menu":
        draw_text_center("Вітання у грі!", HEIGHT // 2 - 150, big_font, BLUE)
        draw_button(button_easy_rect, "Легкий режим", GREEN)
        draw_button(button_hard_rect, "Важкий режим", RED)
        draw_button(button_settings_rect, "Налаштування", GRAY)
        draw_button(button_quit_rect, "Вийти", DARK_GRAY)
        hs_surf = font.render(f"Рекорд: {high_score}", True, WHITE)
        screen.blit(hs_surf, (10, HEIGHT - 40))

    elif game_state == "settings":
        draw_text_center("Налаштування", HEIGHT // 2 - 140, big_font, BLUE)

        # Прямокутники кнопок для налаштувань
        control_ad_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 60, 120, 40)
        control_arrows_rect = pygame.Rect(WIDTH // 2 + 30, HEIGHT // 2 - 60, 120, 40)
        vol_down_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 10, 40, 40)
        vol_up_rect = pygame.Rect(WIDTH // 2 + 30, HEIGHT // 2 + 10, 40, 40)
        settings_back_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 90, 160, 50)

        # Керування
        draw_text_center("Керування:", HEIGHT // 2 - 100, font, BLACK)
        draw_button(control_ad_rect, "Клавіші A/D", GREEN if control_scheme == "AD" else GRAY)
        draw_button(control_arrows_rect, "Стрілки", GREEN if control_scheme == "ARROWS" else GRAY)

        # Гучність
        draw_text_center("Гучність:", HEIGHT // 2 - 20, font, BLACK)
    
        pygame.draw.rect(screen, GRAY, vol_down_rect)
        pygame.draw.rect(screen, GRAY, vol_up_rect)
        minus_surf = font.render("-", True, BLACK)
        plus_surf = font.render("+", True, BLACK)
        screen.blit(minus_surf, (vol_down_rect.x + 12, vol_down_rect.y + 5))
        screen.blit(plus_surf, (vol_up_rect.x + 10, vol_up_rect.y + 5))
        vol_text = font.render(f"{int(volume * 100)}%", True, BLACK)
        screen.blit(vol_text, (WIDTH // 2 - vol_text.get_width() // 2, HEIGHT // 2 + 15))

        # Кнопка назад
        draw_button(settings_back_rect, "Назад", DARK_GRAY, WHITE)

    elif game_state == "play":
        if paused:
            draw_text_center("Пауза - натисніть P щоб продовжити", HEIGHT // 2, big_font, WHITE)
        else:
            # Рух гравця
            speed = 5
            if control_scheme == "AD":
                if keys[pygame.K_a] and player.left > 0:
                    player.x -= speed
                if keys[pygame.K_d] and player.right < WIDTH:
                    player.x += speed
            else:  # ARROWS
                if keys[pygame.K_LEFT] and player.left > 0:
                    player.x -= speed
                if keys[pygame.K_RIGHT] and player.right < WIDTH:
                    player.x += speed

            # Стрільба
            now = pygame.time.get_ticks()
            if keys[pygame.K_SPACE] and now - last_shot > shoot_cooldown:
                last_shot = now
                if fire_mode:
                    # подвійний постріл
                    bullets.append(pygame.Rect(player.centerx - 20, player.top, 10, 20))
                    bullets.append(pygame.Rect(player.centerx + 10, player.top, 10, 20))
                else:
                    bullets.append(pygame.Rect(player.centerx - 5, player.top, 10, 20))

            # Оновлення пострілів
            for bullet in bullets[:]:
                bullet.y -= 10
                if bullet.bottom < 0:
                    bullets.remove(bullet)

            # Спавн ворогів
            spawn_timer += dt
            spawn_interval = 1500 if difficulty == "easy" else 1000
            if spawn_timer > spawn_interval:
                spawn_enemy()
                spawn_timer = 0

            # Оновлення ворогів
            for enemy in enemies[:]:
                enemy["rect"].y += 2 if difficulty == "easy" else 3
                if enemy["rect"].top > HEIGHT:
                    enemies.remove(enemy)
                    lives -= 1
                    if lives <= 0:
                        game_state = "menu"
                        if score > high_score:
                            high_score = score
                # Перевірка попадання в гравця
                if enemy["rect"].colliderect(player):
                    enemies.remove(enemy)
                    lives -= 1
                    if lives <= 0:
                        game_state = "menu"
                        if score > high_score:
                            high_score = score

            # Перевірка попадання пострілів у ворогів
            for bullet in bullets[:]:
                for enemy in enemies[:]:
                    if bullet.colliderect(enemy["rect"]):
                        bullets.remove(bullet)
                        bullet_hit(enemy)
                        break

            # Оновлення бонусів
            for bonus in bonus_list[:]:
                bonus["rect"].y += 2
                if bonus["rect"].top > HEIGHT:
                    bonus_list.remove(bonus)
                    continue
                if bonus["rect"].colliderect(player):
                    if bonus["type"] == "heart":
                        lives = min(lives + 1, 5)
                    elif bonus["type"] == "fire":
                        fire_mode = True
                        fire_mode_end_time = pygame.time.get_ticks() + 5000
                    bonus_list.remove(bonus)

            # Відключення подвійного вогню
            if fire_mode and pygame.time.get_ticks() > fire_mode_end_time:
                fire_mode = False

            # Малюємо гравця
            screen.blit(player_img, player.topleft)

            # Малюємо ворогів
            for enemy in enemies:
                screen.blit(enemy["img"], enemy["rect"].topleft)

            # Малюємо постріли
            for bullet in bullets:
                screen.blit(bullet_img, bullet.topleft)

            # Малюємо бонуси
            for bonus in bonus_list:
                screen.blit(bonus["img"], bonus["rect"].topleft)

            # Малюємо UI
            draw_ui()

    pygame.display.flip()
