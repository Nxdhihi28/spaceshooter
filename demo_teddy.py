
from pygame import *
from random import randint
#loading font functions separately
font.init()
font1 = font.Font(None, 80)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))

font2 = font.Font(None, 36)



#we need the following images:
img_back = "galaxy.jpg" #game background
img_bullet = "bullet.png" #bullet
img_hero = "rocket.png" #hero
img_enemy = "ufo.png" #enemy
img_button = "play_again.png"
img_energy = "energy.png"

score = 0 #ships destroyed
goal = 10 #how many ships need to be shot down to win
lost = 0 #ships missed
max_lost = 3 #lose if you miss that many
health = 100
max_health = 100
level = 1
game_state = "start"
max_level = 5
#parent class for other sprites
class GameSprite(sprite.Sprite):
    #class constructor
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        #call for the class (Sprite) constructor:
        sprite.Sprite.__init__(self)


        #every sprite must store the image property
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed


        #every sprite must have the rect property that represents the rectangle it is fitted in
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    #method drawing the character on the window
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


#main player class
class Player(GameSprite):
    #method to control the sprite with arrow keys
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
    #method to "shoot" (use the player position to create a bullet there)
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, 15)
        bullets.add(bullet)


#enemy sprite class  
class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.shoot_timer = randint(60, 180)
    #enemy movement
    def update(self):
        self.rect.y += self.speed
        global lost
        if level == 2:
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.fire()
                self.shoot_timer = randint(60, 180)
        #disappears upon reaching the screen edge
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost = lost + 1
            
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

#bullet sprite class  
class Bullet(GameSprite):
# enemy movement
    def update(self):
        self.rect.y -= self.speed
        # disappears upon reaching the screen edge
        if self.rect.y < 0:
            self.kill()
        if self.rect.y > win_height:
            self.kill()
            
class Energy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0

class Button (GameSprite):
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
#create a small window
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))
#create sprites
ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)
play_button = Button(img_button, 250, 300, 100, 100, 0)

#creating a group of enemy sprites
monsters = sprite.Group()
def create_enemies():
    monsters.empty()
    for i in range(1, 6):
        monster = Enemy(img_enemy, randint(80, win_width - 80), 0, 80, 50, randint(1, 5))
        monsters.add(monster)

bullets = sprite.Group()
enemy_bullets = sprite.Group()

energies = sprite.Group()
for i in range(1, 3):
    energy = Energy(img_enemy, randint(80, win_width - 80), 0, 80, 50, randint(1, 5))
    energies.add(energy)

def start_level():
    global score, lost, health
    score = 0
    lost = 0
    health = 100
    ship.rect.x = 5
    ship.rect.y = win_height - 100
    bullets.empty()
    enemy_bullets.empty()
    create_enemies()
    #create_asteroid()

start_level()

#main game loop:
run = True #the flag is reset by the window close button
while run:
#"Close" button press event
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                ship.fire()
        elif e.type == MOUSEBUTTONDOWN:
            if play_button.is_clicked(e.pos):
                if game_state == "start":
                    level = 1
                    start_level()
                    game_state = "level1"

                elif game_state == "level" + str(level) +"_completed":
                    level += 1
                    start_level()
                    game_state = "level" + str(level)

                elif game_state == "win":
                    level = 1
                    start_level()
                    game_state = "level1"
                
                elif game_state == "lose":
                    start_level()
                    game_state = "level" + str(level)

    if game_state == "start":
        window.blit(background, (0, 0))
        name_text = font1.render("SPACE SHOOTER", True, (255, 255, 255))
        window.blit(name_text, (100, 100))
        level_text = font2.render("LEVEL 1", True, (255, 255, 255))
        window.blit(level_text, (270, 200))
        play_button.reset()

    elif game_state == "level" + str(level):
        window.blit(background,(0,0))
        ship.reset()
        monsters.draw(window)
        bullets.draw(window)
        ship.update()
        monsters.update()
        bullets.update()
        if level >= 3:
            enemy_bullets.draw(window)
            enemy_bullets.update()
            if sprite.spritecollide(ship, enemy_bullets, True):
                health -= 10


        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        if sprite.spritecollide(ship, monsters, True):
            health -= 20
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        if sprite.spritecollide(ship, energies, True):
            health += 10
            energy = Energy(img_enemy, randint(80, win_width - 80), 0, 80, 50, randint(1, 5))
            energies.add(energy)
            if health > max_health:
                healt = max_health

        text_score = font2.render("Score: " + str(score), 1, (255, 255, 255))
        window.blit(text_score, (10, 20))

        text_health = font2.render("Health: " + str(health), 1, (255, 255, 255))
        window.blit(text_health, (10, 50))

        text_lost = font2.render("Missed: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lost, (10, 80))

        text_level = font2.render("Level: " + str(level), 1, (255, 255, 255))
        window.blit(text_level, (10, 110))


        if score >= goal:
            if level < max_level:
                game_state = "level" + str(level) +"_completed"
            else:
                game_state = "win"

        if lost >= max_lost or health <= 0:
            game_state = "lose"
        
    display.update()



