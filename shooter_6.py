from pygame import *
from random import randint

font.init()
font1 = font.Font(None, 80)
win = font1.render("YOU WIN!", True, (255, 255, 255))
lose = font1.render("YOU LOSE!", True, (180, 0, 0))
font2 = font.Font(None, 36)

img_back = "galaxy.jpg"
img_bullet = "bullet.png"
img_hero = "rocket.png"
img_enemy = "ufo.png"
img_button = "play_again.png"
img_energy = "energy.png"

score = 0
goal = 10
lost = 0
max_lost = 3
level = 1
max_level = 5
health = 100
max_health = 100
game_state = "start"


class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5: self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80: self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)


class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.shoot_timer = randint(60, 180)

    def update(self):
        self.rect.y += self.speed
        global lost
        if level >= 2:
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.fire()
                self.shoot_timer = randint(60, 180)
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost += 1

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.bottom, 15, 20, 7)
        enemy_bullets.add(bullet)


class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.speed < 0 and self.rect.y < 0: self.kill()
        if self.speed > 0 and self.rect.y > win_height: self.kill()


class Energy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = randint(-300, -50)


class Button(GameSprite):
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))

ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)
monsters = sprite.Group()
bullets = sprite.Group()
enemy_bullets = sprite.Group()
energies = sprite.Group()

for i in range(2):
    energy = Energy(img_energy, randint(80, win_width - 80), randint(-400, -50), 40, 40, 3)
    energies.add(energy)

play_button = Button(img_button, 300, 300, 100, 10, 0)


def create_enemies():
    monsters.empty()
    for i in range(1, 6):
        monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
        monsters.add(monster)


def start_level():
    global score, lost, health
    score = 0
    lost = 0
    health = max_health
    ship.rect.x = 5
    ship.rect.y = win_height - 100
    bullets.empty()
    enemy_bullets.empty()
    create_enemies()


run = True

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE and game_state == "level" + str(level):
                ship.fire()
        elif e.type == MOUSEBUTTONDOWN:
            if play_button.is_clicked(e.pos):
                if game_state == "start":
                    level = 1
                    start_level()
                    game_state = "level1"
                elif game_state == "level" + str(level) + "_completed":
                    level += 1
                    start_level()
                    game_state = "level" + str(level)
                elif game_state == "lose":
                    start_level()
                    game_state = "level" + str(level)
                elif game_state == "win":
                    level = 1
                    start_level()
                    game_state = "level1"

    if game_state == "start":
        window.blit(background, (0, 0))
        name_text = font1.render("SPACE SHOOTER", True, (255, 255, 255))
        window.blit(name_text, (100, 100))
        level_text = font2.render("LEVEL 1", True, (255, 255, 255))
        window.blit(level_text, (270, 200))
        play_button.reset()

    elif game_state == "level" + str(level):
        window.blit(background, (0, 0))
        ship.update()
        monsters.update()
        bullets.update()
        energies.update()
        ship.reset()
        monsters.draw(window)
        bullets.draw(window)
        energies.draw(window)

        if level >= 2:
            enemy_bullets.update()
            enemy_bullets.draw(window)

        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        if sprite.spritecollide(ship, monsters, True):
            health -= 20
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        if level >= 2:
            if sprite.spritecollide(ship, enemy_bullets, True):
                health -= 10

        collected_energy = sprite.spritecollide(ship, energies, True)
        for energy in collected_energy:
            health += 20
            if health > max_health:
                health = max_health

        if health <= 0 or lost >= max_lost:
            game_state = "lose"

        if score >= goal:
            if level < max_level:
                game_state = "level" + str(level) + "_completed"
            else:
                game_state = "win"

        text = font2.render("Score: " + str(score), True, (255, 255, 255))
        window.blit(text, (10, 20))
        text_lose = font2.render("Missed: " + str(lost), True, (255, 255, 255))
        window.blit(text_lose, (10, 50))
        text_health = font2.render("Health: " + str(health), True, (255, 255, 255))
        window.blit(text_health, (10, 80))
        text_level = font2.render("Level: " + str(level), True, (255, 255, 255))
        window.blit(text_level, (10, 110))

    elif game_state == "level" + str(level) + "_completed":
        window.blit(background, (0, 0))
        level_complete = font1.render("YOU WIN!", True, (255, 255, 255))
        window.blit(level_complete, (200, 120))
        next_level = font2.render("LEVEL " + str(level + 1), True, (255, 255, 255))
        window.blit(next_level, (280, 220))
        play_button.reset()

    elif game_state == "lose":
        window.blit(background, (0, 0))
        window.blit(lose, (200, 150))
        retry_text = font2.render("PLAY LEVEL " + str(level) + " AGAIN", True, (255, 255, 255))
        window.blit(retry_text, (210, 220))
        play_button.reset()

    elif game_state == "win":
        window.blit(background, (0, 0))
        window.blit(win, (200, 150))
        play_button.reset()

    display.update()
    time.delay(50)