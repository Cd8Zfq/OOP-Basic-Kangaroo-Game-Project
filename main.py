import pygame  
import tkinter as tk
import random
import sys
import os
import math 

# --- Constantes et configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Couleurs (RGB Pygame)
COLOR_BG = (135, 206, 250)
COLOR_KANGAROO = (200, 160, 120)  
COLOR_KANGAROO_DARK = (160, 120, 80)  
COLOR_GROUND = (139, 69, 19)
COLOR_TEXT = (46, 52, 64)
COLOR_CLOUD = (223, 220, 240)
COLOR_SCORE_HIGHLIGHT = (220, 20, 60)
COLOR_COIN = (255, 215, 0) 
COLOR_CACTUS = (34, 139, 34)

# Physique
GRAVITY = 0.4        
JUMP_STRENGTH = -10  
GAME_SPEED_START = 3 
MAX_SPEED = 10       
SPEED_INCREMENT = 0.005 

# Système de power-ups
POWERUP_CHANCE = 0.002
POWERUP_DURATION = 300

# Système de pièces
COIN_CHANCE = 0.005 
COIN_VALUE = 50

# Apparition des obstacles
MIN_CACTUS_GAP = 200 

# --- Aide : convertir RGB en Hex pour Tkinter ---
def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb

# Couleurs pour Tkinter
HEX_BTN_START = rgb_to_hex((144, 238, 144))
HEX_BTN_RESTART = rgb_to_hex((0, 200, 0))
HEX_BTN_QUIT = rgb_to_hex((255, 0, 0))
HEX_BTN_HIGHSCORE = rgb_to_hex((255, 215, 0))
HEX_BG_MENU = "#eceff4"

# --- Classes ---

class Kangaroo:
   def __init__(self):  
       assets_dir = os.path.dirname(__file__)
       try:
           # Charger les images brutes
           raw_image1 = pygame.image.load(os.path.join(assets_dir, 'Kangaroo_still.png')).convert_alpha()
           raw_image2 = pygame.image.load(os.path.join(assets_dir, 'Kangaroo_jump.png')).convert_alpha()

           # --- NETTOYAGE DU FOND BLANC ---
           def clean_white_background(img):
               width, height = img.get_size()
               for x in range(width):
                   for y in range(height):
                       r, g, b, a = img.get_at((x, y))
                       # Si le pixel est presque blanc (>200), on le rend transparent
                       if r > 200 and g > 200 and b > 200:
                           img.set_at((x, y), (255, 255, 255, 0))
               return img

           self.image1 = clean_white_background(raw_image1)
           self.image2 = clean_white_background(raw_image2)
           # -------------------------------

           target_height = 80
           scale_ratio = target_height / self.image1.get_height()
           new_width = int(self.image1.get_width() * scale_ratio)
           
           self.image1 = pygame.transform.scale(self.image1, (new_width, target_height))
           self.image2 = pygame.transform.scale(self.image2, (new_width, target_height))
           self.width = new_width
           self.height = target_height
       except:
           # Fallback si image manquante
           self.width = 50
           self.height = 80
           self.image1 = pygame.Surface((self.width, self.height))
           self.image1.fill(COLOR_KANGAROO)
           self.image2 = self.image1

       self.x = 50
       self.y = SCREEN_HEIGHT - 40 - self.height

       self.vel_y = 0
       self.is_jumping = False
       self.jump_count = 0
       self.invincible = False
       self.double_points = False
       self.powerup_timers = {'invincible': 0, 'double_points': 0}
       self.coins = 0 
       
       self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
       self.animation_frame = 0
       self.animation_speed = 0.3

   def jump(self, sounds):
       if self.jump_count < 2:
           self.vel_y = JUMP_STRENGTH
           self.is_jumping = True
           self.jump_count += 1
           if sounds and 'jump' in sounds: 
               sounds['jump'].play()
          
   def update(self):
       self.vel_y += GRAVITY
       self.y += self.vel_y
       
       self.animation_frame += self.animation_speed
       if self.animation_frame > 4:
           self.animation_frame = 0

       ground_y = SCREEN_HEIGHT - 40 - self.height
       if self.y >= ground_y:
           self.y = ground_y
           self.is_jumping = False
           self.vel_y = 0
           self.jump_count = 0

       self.rect.y = int(self.y)
       
       for powerup_type in list(self.powerup_timers.keys()):
           if self.powerup_timers[powerup_type] > 0:
               self.powerup_timers[powerup_type] -= 1
               if self.powerup_timers[powerup_type] == 0:
                   if powerup_type == 'invincible':
                       self.invincible = False
                   elif powerup_type == 'double_points':
                       self.double_points = False

   def activate_powerup(self, powerup_type, sounds): 
       self.powerup_timers[powerup_type] = POWERUP_DURATION
       if powerup_type == 'invincible':
           self.invincible = True
       elif powerup_type == 'double_points':
           self.double_points = True
           
       if sounds and 'powerup' in sounds: 
           sounds['powerup'].play()
       
   def draw(self, screen):
       current_image = self.image1 if int(self.animation_frame) % 2 == 0 else self.image2
       if self.invincible and pygame.time.get_ticks() % 200 < 100:
           temp = current_image.copy()
           temp.set_alpha(100)
           screen.blit(temp, (self.rect.x, self.rect.y))
       else:
           screen.blit(current_image, (self.rect.x, self.rect.y))

class Cactus:
    def __init__(self, speed):
        self.width = 30
        self.height = random.randint(60, 100)
        self.x = SCREEN_WIDTH + random.randint(0, 200)
        self.y = SCREEN_HEIGHT - 40 - self.height
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.variant = random.choice([1, 2, 3])

    def update(self, speed):
        self.x -= speed
        self.rect.x = int(self.x)

    def draw(self, screen):
        color = COLOR_CACTUS 
        base_x, base_y = self.rect.x, self.rect.y
        base_width = self.width
        base_height = self.height

        if self.variant == 1:
            pygame.draw.rect(screen, color, (base_x + 5, base_y, 20, base_height), border_radius=2)
            pygame.draw.rect(screen, color, (base_x - 10, base_y + base_height * 0.4, 25, 10), border_radius=2)
            pygame.draw.rect(screen, color, (base_x - 5, base_y + base_height * 0.4 - 20, 10, 20), border_radius=2)
            pygame.draw.rect(screen, color, (base_x + 20, base_y + base_height * 0.3, 25, 10), border_radius=2)
            pygame.draw.rect(screen, color, (base_x + 35, base_y + base_height * 0.3 - 15, 10, 15), border_radius=2)
        elif self.variant == 2:
            pygame.draw.rect(screen, color, (base_x - 5, base_y + base_height - 30, 40, 30), border_radius=5)
            pygame.draw.rect(screen, color, (base_x + 5, base_y + base_height - 50, 30, 20), border_radius=5)
            pygame.draw.rect(screen, color, (base_x, base_y + base_height - 75, 20, 25), border_radius=5)
        else:
            pygame.draw.rect(screen, color, (base_x + 10, base_y, 10, base_height), border_radius=2)
            branch_y = base_y + base_height * 0.6
            pygame.draw.rect(screen, color, (base_x - 5, branch_y, 15, 5))
            pygame.draw.rect(screen, color, (base_x - 5, branch_y - 20, 5, 20)) 
            branch_y2 = base_y + base_height * 0.3
            pygame.draw.rect(screen, color, (base_x + 15, branch_y2, 10, 5))
            pygame.draw.rect(screen, color, (base_x + 20, branch_y2 - 15, 5, 15)) 

class PowerUp:
    def __init__(self, speed):
        self.width = 30
        self.height = 30
        self.x = SCREEN_WIDTH
        self.y = random.randint(100, SCREEN_HEIGHT - 140)
        self.speed = speed
        self.type = random.choice(['invincible', 'double_points'])
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def update(self, speed):
        self.x -= speed
        self.rect.x = int(self.x)
        
    def draw(self, screen):
        colors = {'invincible': (255, 255, 0), 'double_points': (50, 205, 50)}
        color = colors.get(self.type, (255, 255, 255))
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        if self.type == 'invincible':
            pygame.draw.circle(screen, (0, 0, 0), (self.rect.centerx, self.rect.centery), 8, 2)
        else:
            font = pygame.font.Font(None, 24)
            text = font.render("2x", True, (0, 0, 0))
            screen.blit(text, (self.rect.centerx-10, self.rect.centery-10))

class Coin:
    def __init__(self, speed):
        self.width = 24 
        self.height = 24 
        self.x = SCREEN_WIDTH
        self.y = random.randint(100, SCREEN_HEIGHT - 120)
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.spin_frame = 0 
        
    def update(self, speed):
        self.x -= speed
        self.rect.x = int(self.x)
        self.spin_frame += 0.4 
        if self.spin_frame > 6:
            self.spin_frame = 0
            
    def draw(self, screen):
        center_x, center_y = self.rect.center
        radius_max = 12 
        radius_min = 5
        radius = radius_max - abs(radius_min - self.spin_frame % 6)
        pygame.draw.circle(screen, COLOR_COIN, (center_x, center_y), int(radius))
        inner_color = (200, 180, 0)
        pygame.draw.circle(screen, inner_color, (center_x, center_y), max(1, int(radius - 3))) 
        pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), int(radius), 1)

class Sun:
    def __init__(self):
        self.x = SCREEN_WIDTH - 100
        self.y = 80
        self.radius = 40
        self.color = (220, 200, 50)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(0, 100)
        self.y = random.randint(50, 150)
        self.width = random.randint(60, 100)
        self.speed = random.uniform(0.5, 1.5)
        self.color_variation = random.randint(220, 255)
        self.color = (self.color_variation, self.color_variation, 240)

    def update(self):
        self.x -= self.speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(50, 200)
            self.y = random.randint(50, 150)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 20)
        pygame.draw.circle(screen, self.color, (int(self.x + 25), int(self.y - 10)), 25)
        pygame.draw.circle(screen, self.color, (int(self.x + 50), int(self.y)), 20)

def init_sounds():
    sounds = {}
    assets_dir = os.path.dirname(__file__)
    try:
        sounds['jump'] = pygame.mixer.Sound(os.path.join(assets_dir, 'jump.mp3'))
        sounds['game_over'] = pygame.mixer.Sound(os.path.join(assets_dir, 'hit.mp3'))
        sounds['score'] = pygame.mixer.Sound(os.path.join(assets_dir, 'coin.mp3'))
        sounds['powerup'] = pygame.mixer.Sound(os.path.join(assets_dir, 'powerup.mp3'))
        for s in sounds.values():
            s.set_volume(0.4)
    except Exception as e:
        print(f"Erreur son : {e}")
    return sounds

def load_high_score():
    try:
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                return int(f.read().strip())
    except:
        pass
    return 0

def save_high_score(score):
    try:
        with open("highscore.txt", "w") as f:
            f.write(str(score))
    except:
        pass

# --- Fonction principale du jeu ---
def run_game():
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    assets_dir = os.path.dirname(__file__)
    try:
        icon = pygame.image.load(os.path.join(assets_dir, 'Kangaroo_jump.png')).convert()
        if icon:
            colorkey = icon.get_at((0,0))
            icon.set_colorkey(colorkey)
            pygame.display.set_icon(icon)
    except:
        pass

    pygame.display.set_caption("KANGAROO JUMPER") 
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    sounds = init_sounds()
    high_score = load_high_score()

    kangaroo = Kangaroo() 
    cacti = []
    powerups = []
    coins = []
    clouds = [Cloud() for _ in range(3)]
    sun = Sun()
    
    game_speed = GAME_SPEED_START
    score = 0
    running = True
    cactus_spawn_timer = 0
    
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    kangaroo.jump(sounds) 
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        actual_speed = game_speed
        
        kangaroo.update()
        for cloud in clouds:
            cloud.update()
        
        if random.random() < POWERUP_CHANCE and len(powerups) < 2:
            powerups.append(PowerUp(actual_speed))
        
        for powerup in powerups[:]:
            powerup.update(actual_speed)
            if powerup.x < -powerup.width:
                powerups.remove(powerup)
            elif kangaroo.rect.colliderect(powerup.rect):
                kangaroo.activate_powerup(powerup.type, sounds) 
                powerups.remove(powerup)
        
        if random.random() < COIN_CHANCE and len(coins) < 5:
            coins.append(Coin(actual_speed))
            
        for coin in coins[:]:
            coin.update(actual_speed)
            if coin.x < -coin.width:
                coins.remove(coin)
            elif kangaroo.rect.colliderect(coin.rect):
                kangaroo.coins += COIN_VALUE
                if sounds and 'coin' in sounds:
                    sounds['coin'].play()
                coins.remove(coin)
        
        cactus_spawn_timer += 1
        can_spawn = (cactus_spawn_timer > 60 or (len(cacti) == 0 and cactus_spawn_timer > 30))
        last_cactus_x = 0
        if cacti:
            last_cactus_x = max(c.x + c.width for c in cacti)
        is_far_enough = (SCREEN_WIDTH - last_cactus_x) >= MIN_CACTUS_GAP 
        
        if can_spawn and is_far_enough:
            cacti.append(Cactus(actual_speed))
            cactus_spawn_timer = 0 
        
        for cactus in cacti[:]:
            cactus.update(actual_speed)
            if cactus.x < -cactus.width:
                cacti.remove(cactus)
                score_increment = 2 if kangaroo.double_points else 1
                score += score_increment
                if 'score' in sounds:
                    sounds['score'].play()
            
            if not kangaroo.invincible and kangaroo.rect.inflate(-10, -10).colliderect(cactus.rect):
                if 'game_over' in sounds:
                    sounds['game_over'].play()
                running = False
        
        if game_speed < MAX_SPEED:
            game_speed += SPEED_INCREMENT
        
        screen.fill(COLOR_BG)
        pygame.draw.rect(screen, COLOR_GROUND, (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
        
        sun.draw(screen)
        for cloud in clouds:
            cloud.draw(screen)
        for cactus in cacti:
            cactus.draw(screen)
        for powerup in powerups:
            powerup.draw(screen)
        for coin in coins: 
            coin.draw(screen)
        kangaroo.draw(screen)
        
        score_color = COLOR_SCORE_HIGHLIGHT if score > high_score else COLOR_TEXT
        score_text = font.render(f"Score : {score}", True, score_color)
        screen.blit(score_text, (20, 20))
        high_score_text = small_font.render(f"Record : {high_score}", True, COLOR_TEXT)
        screen.blit(high_score_text, (20, 60))
        coin_text = font.render(f"Pièces : {kangaroo.coins}", True, COLOR_COIN)
        screen.blit(coin_text, (SCREEN_WIDTH - coin_text.get_width() - 20, 20))
        
        y_offset = 90
        for powerup_type, timer in kangaroo.powerup_timers.items():
            if timer > 0:
                seconds = timer // 60
                color = (255, 255, 0) if powerup_type == 'invincible' else (50, 205, 50)
                powerup_text = small_font.render(f"{powerup_type} : {seconds}s", True, color)
                screen.blit(powerup_text, (20, y_offset))
                y_offset += 25
        
        pygame.display.flip()
    
    if score > high_score:
        save_high_score(score)
    
    pygame.quit()
    return score

# --- Interfaces Tkinter ---
def start_screen():
    """Écran de démarrage (menu)"""
    root = tk.Tk()
    root.title("KANGAROO JUMPER - Menu") 
    
    # --- MODIF ICI : Fenêtre élargie à 600 ---
    window_width = 600
    window_height = 350
    
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws // 2) - (window_width // 2)
    y = (hs // 2) - (window_height // 2)
    
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    root.configure(bg=HEX_BG_MENU)
    root.resizable(False, False)

    lbl_title = tk.Label(root, text="KANGAROO JUMPER", 
                          font=("Helvetica", 32, "bold"),relief="flat", 
                          bg=HEX_BG_MENU, fg="#2e3440")
    lbl_title.pack(pady=20)
    
    high_score = load_high_score()
    lbl_highscore = tk.Label(root, text=f"Meilleur Score : {high_score}", relief='flat',
                             font=("Helvetica", 14,'bold'), 
                             bg=HEX_BG_MENU, fg="#bf616a")
    lbl_highscore.pack(pady=5)
    
    lbl_instr = tk.Label(root, 
                         text="Contrôles :\nESPACE ou HAUT : Sauter (Double saut)\nECHAP : Retour au Menu",
                         font=("Helvetica", 11,'bold'),relief='flat', 
                         bg=HEX_BG_MENU, justify="left")
    lbl_instr.pack(pady=10)
    
    lbl_powerups = tk.Label(root, 
                            text="Bonus :\nJaune : Invincible\nVert : Points x2",
                            font=("Helvetica", 11),relief='flat', 
                            bg=HEX_BG_MENU, justify="left")
    lbl_powerups.pack(pady=10)

    def launch():
        root.destroy()
        score = run_game()
        game_over_screen(score)

    btn_start = tk.Button(root, text="Jouer", 
                          font=("Helvetica", 14, "bold"),relief="flat", 
                          bg=HEX_BTN_START, fg="black", 
                          width=15, height=2,activebackground='#2980b9',bd=0,cursor="hand2",
                          command=launch)
    btn_start.pack(pady=10)
    
    btn_quit = tk.Button(root, text="Quitter", 
                          font=("Helvetica", 12,"bold"),relief="flat", 
                          bg=HEX_BTN_QUIT, fg="white",activebackground='#2980b9',bd=0,cursor="hand2", 
                          width=15, height=2,
                          command=root.destroy)
    btn_quit.pack(pady=10)

    root.mainloop()

def game_over_screen(final_score):
    """Écran de fin de partie"""
    root = tk.Tk()
    root.title("FIN DE PARTIE")
    
    # J'ai légèrement élargi cette fenêtre aussi (450) pour que les boutons larges rentrent bien
    window_width = 450
    window_height = 350
    
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws // 2) - (window_width // 2)
    y = (hs // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    root.configure(bg=HEX_BG_MENU)
    root.resizable(False, False)

    high_score = load_high_score()
    is_new_high_score = final_score > high_score
    
    lbl_go = tk.Label(root, text="PARTIE TERMINÉE", 
                      font=("Helvetica", 28, "bold"),relief="flat", 
                      bg=HEX_BG_MENU, fg="#bf616a")
    lbl_go.pack(pady=20)

    if is_new_high_score:
        lbl_new_high = tk.Label(root, text="NOUVEAU RECORD !", 
                                font=("Helvetica", 16, "bold"),relief="flat", 
                                bg=HEX_BG_MENU, fg="#FFD700")
        lbl_new_high.pack(pady=5)

    lbl_score = tk.Label(root, text=f"Score Final : {final_score}", 
                         font=("Helvetica", 18),relief="flat", 
                         bg=HEX_BG_MENU)
    lbl_score.pack(pady=5)

    def restart():
        root.destroy()
        score = run_game()
        game_over_screen(score)

    def back_to_menu():
        root.destroy()
        start_screen()

    def quit_game():
        root.destroy()
        sys.exit()

    # --- MODIF ICI : BOUTONS UNIFORMISÉS ---
    # Même largeur (20) et même police (Gras) pour tous
    COMMON_WIDTH = 20
    COMMON_FONT = ("Helvetica", 12, "bold") 
    
    btn_restart = tk.Button(root, text="Rejouer", 
                            font=COMMON_FONT, relief="flat", 
                            bg=HEX_BTN_RESTART, fg="white", 
                            width=COMMON_WIDTH, height=2,
                            activebackground='#2980b9', bd=0, cursor="hand2",
                            command=restart)
    btn_restart.pack(pady=5)
    
    btn_menu = tk.Button(root, text="Menu Principal", 
                          font=COMMON_FONT, relief="flat", 
                          bg=HEX_BTN_START, fg="black", 
                          width=COMMON_WIDTH, height=2,
                          activebackground='#2980b9', bd=0, cursor="hand2",
                          command=back_to_menu)
    btn_menu.pack(pady=5)
    
    btn_quit = tk.Button(root, text="Quitter", 
                          font=COMMON_FONT, relief="flat", 
                          bg=HEX_BTN_QUIT, fg="white", 
                          width=COMMON_WIDTH, height=2,
                          activebackground='orange', bd=0, cursor="hand2",
                          command=quit_game)  
    btn_quit.pack(pady=5)

    root.mainloop()

# --- Point d'entrée ---
if __name__ == "__main__":
    start_screen()