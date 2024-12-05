import pygame
import sys
import random
import math

# Inicializa o pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo 2D - Movimento do Personagem")

# Configurações do som
pygame.mixer.init()
pygame.mixer.music.load(r"C:\GitHub\game_py\mapa\som.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Carrega e configura o mapa
background = pygame.image.load(r"C:\GitHub\game_py\mapa\mapa.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Carrega e configura o personagem
player = pygame.image.load(r"C:\GitHub\game_py\personagem\spr_player_idle.png")
player = pygame.transform.scale(player, (50, 50))
character_x, character_y = WIDTH // 2, HEIGHT // 2
character_speed = 2

# Configura a barra de vida
max_health = 5
current_health = max_health
health_bar_width = 50
health_bar_height = 10
health_bar_offset = 10

# Configura a barra de XP
xp = 0
xp_needed = 20
level = 1
xp_bar_height = 20

# Carrega e configura o inimigo
enemy_img = pygame.image.load(r"C:\GitHub\game_py\inimigo\spr_enemy_orc.png")
enemy_img = pygame.transform.scale(enemy_img, (50, 50))
enemies = []
enemy_spawn_time = random.randint(1000, 3000)
last_spawn_time = pygame.time.get_ticks()
enemy_speed = 2

# Carrega e configura o item de drop
item_img = pygame.image.load(r"C:\GitHub\game_py\personagem\spr_spell_1.png")
item_img = pygame.transform.scale(item_img, (30, 30))
dropped_items = []

# Configurações de ataque
attack_active = False
attack_duration = 300  # Duração do ataque em milissegundos
attack_start_time = 0
attack_range = 60  # Alcance do ataque

# Clock para controlar a taxa de quadros
clock = pygame.time.Clock()

# Função para criar um inimigo
def create_enemy():
    enemy_x = random.randint(0, WIDTH - 50)
    enemy_y = random.randint(0, HEIGHT - 50)
    return {"x": enemy_x, "y": enemy_y, "rect": pygame.Rect(enemy_x, enemy_y, 50, 50)}

# Loop principal do jogo
while True:
    # Lida com eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Obtém as teclas pressionadas
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        character_y -= character_speed
    if keys[pygame.K_DOWN]:
        character_y += character_speed
    if keys[pygame.K_LEFT]:
        character_x -= character_speed
    if keys[pygame.K_RIGHT]:
        character_x += character_speed
    if keys[pygame.K_f]:  # Ativar ataque
        if not attack_active:
            attack_active = True
            attack_start_time = pygame.time.get_ticks()

    # Previne que o personagem saia da tela
    character_x = max(0, min(WIDTH - player.get_width(), character_x))
    character_y = max(0, min(HEIGHT - player.get_height(), character_y))

    # Controle de tempo para spawn de inimigos
    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time > enemy_spawn_time:
        enemies.append(create_enemy())
        last_spawn_time = current_time
        enemy_spawn_time = random.randint(1000, 3000)

    # Atualiza a tela
    screen.blit(background, (0, 0))  # Desenha o mapa
    screen.blit(player, (character_x, character_y))  # Desenha o personagem

    # Desenha a barra de vida
    health_ratio = current_health / max_health
    pygame.draw.rect(screen, (255, 0, 0), 
                     (character_x, character_y + player.get_height() + health_bar_offset, 
                      health_bar_width, health_bar_height))
    pygame.draw.rect(screen, (0, 255, 0), 
                     (character_x, character_y + player.get_height() + health_bar_offset, 
                      health_bar_width * health_ratio, health_bar_height))

    # Desenha a barra de XP no topo da tela
    xp_ratio = xp / xp_needed
    pygame.draw.rect(screen, (128, 128, 128), (0, 0, WIDTH, xp_bar_height))
    pygame.draw.rect(screen, (0, 0, 255), (0, 0, WIDTH * xp_ratio, xp_bar_height))

    # Verifica colisão com inimigos e atualiza movimento dos inimigos
    player_rect = pygame.Rect(character_x, character_y, 50, 50)
    enemies_to_remove = []
    for enemy in enemies:
        # Movimenta o inimigo em direção ao personagem
        dx = character_x - enemy["x"]
        dy = character_y - enemy["y"]
        distance = math.sqrt(dx**2 + dy**2)
        if distance != 0:
            dx /= distance
            dy /= distance

        enemy["x"] += dx * enemy_speed
        enemy["y"] += dy * enemy_speed
        enemy["rect"].topleft = (enemy["x"], enemy["y"])

        # Desenha o inimigo
        screen.blit(enemy_img, (enemy["x"], enemy["y"]))

        # Verifica colisão com o jogador
        if player_rect.colliderect(enemy["rect"]):
            current_health -= 1
            enemies_to_remove.append(enemy)
            if current_health <= 0:
                print("Game Over!")
                pygame.quit()
                sys.exit()

    # Ataque do personagem
    if attack_active:
        pygame.draw.circle(screen, (255, 0, 0), (character_x + 25, character_y + 25), attack_range, 2)
        if current_time - attack_start_time > attack_duration:
            attack_active = False

        # Verifica se o ataque atinge algum inimigo
        for enemy in enemies:
            enemy_center = (enemy["x"] + 25, enemy["y"] + 25)
            distance_to_enemy = math.sqrt((enemy_center[0] - (character_x + 25))**2 + (enemy_center[1] - (character_y + 25))**2)
            if distance_to_enemy <= attack_range:
                enemies_to_remove.append(enemy)

    # Remove inimigos atingidos e gera drops
    for enemy in enemies_to_remove:
        if enemy in enemies:
            enemies.remove(enemy)
            dropped_items.append({"x": enemy["x"], "y": enemy["y"], "rect": pygame.Rect(enemy["x"], enemy["y"], 30, 30)})

    # Atualiza e desenha itens no chão
    items_to_remove = []
    for item in dropped_items:
        screen.blit(item_img, (item["x"], item["y"]))
        if player_rect.colliderect(item["rect"]):
            xp += 5
            items_to_remove.append(item)

    for item in items_to_remove:
        if item in dropped_items:
            dropped_items.remove(item)

    # Verifica se o XP atingiu o necessário para o próximo nível
    if xp >= xp_needed:
        xp = 0
        level += 1
        xp_needed += 20  # Aumenta o XP necessário para o próximo nível
        character_speed += 1  # Aumenta a velocidade do personagem
        print(character_speed)
        print(f"Level Up! Nível: {level}")

    # Atualiza a tela
    pygame.display.flip()

    # Controla a taxa de quadros
    clock.tick(60)
