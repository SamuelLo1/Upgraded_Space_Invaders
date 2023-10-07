import pygame
import os
import time
import random
from pygame import mixer
#defines font for pygame


#-->Things I want to add: audio (DONE!!)
#-->ScoreBoard System (use txt file)  (DONE !!)
#-->explosions when enemy killed   (DONE !!)
#-->add a shop (DONE !!)


pygame.init() 
pygame.font.init() 
#The initial display 
WIDTH = 750 
HEIGHT = 750
WINDOW = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invaders")


#SCOREBOARD: 
#Loading in images
#enemy ships
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

#Player ship 
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#Lasers
RED_LASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png" ))
GREEN_LASER = pygame.image.load(os.path.join("assets","pixel_laser_green.png" ))
BLUE_LASER = pygame.image.load(os.path.join("assets","pixel_laser_blue.png" ))
YELLOW_LASER = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png" ))

#Music Button 
BUTTON = pygame.image.load(os.path.join("assets","audio.png"))
BUTTON2 = pygame.image.load(os.path.join("assets","no_audio.png"))

#Sounds 
DEATH_SOUND = mixer.Sound(os.path.join ("assets","Lose.wav"))
SHOOT_SOUND = mixer.Sound(os.path.join ("assets","shoot.wav"))
PLAYER_SHOOT = mixer.Sound(os.path.join ("assets","Player_shoot.mp3"))
EXPLOSION = mixer.Sound(os.path.join ("assets","Explosion.mp3"))
#background which is scaled with the window height and width
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")),(WIDTH,HEIGHT))


#Shop: 
UPGRADE = pygame.image.load(os.path.join("assets","Upgrade.png"))

#background music



#Creates an audio button which allows for audio or no audio 
class Button: 
    def __init__(self, img, x, y): 
        self.x = x
        self.y = y
        self.img = img 
        self.store_font = pygame.font.SysFont("roboto",30)
        


    def draw(self, window, outline = None, buy = None): 
        
        if outline: 
            pygame.draw.rect(window, outline, (self.x -2, self.y -2, self.img.get_width() + 4,self.img.get_height() + 4), 0) 

        if buy: 
            pygame.draw.rect(window, (124,252,0), pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height()))
        else: 
            pygame.draw.rect(window, (255,255,255), pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height()))
        window.blit(self.img, (self.x, self.y))

    #checks if mouse is over the position 
    def isOver(self, pos): 
        #pos is the mouse position ( x, y)
        if pos[0] > self.x and pos[0] < self.x + self.img.get_width():
            if pos[1] > self.y and pos[1] < self.y + self.img.get_height(): 
                return True
        
        return False 
    
    def add_label(self, msg, window): 
        store_label = self.store_font.render(f"{msg}", 1, (255, 255, 255))
        window.blit(store_label, (self.x - 20, self.y + self.img.get_height() + 20))

    #checks if the player can buy item
    def can_buy(self, bal, price): 
        if bal >= price: 
            return True 
        return False

        

class Laser: 
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window): 
        window.blit(self.img, (self.x, self.y))

    def move(self, vel): 
        self.y += vel
    
    #checks if the laser is off the screen
    def off_screen(self, height): 
        return not (self.y <= height and self.y >= 0)

    #chekcs for collision
    def collision(self, obj): 
        return collide(self, obj)



#Abstract Class which we plan to inherit from 
class Ship: 

    COOLDOWN_COUNTER = 30 

    def __init__(self, x, y, health = 100): 
        self.x = x
        self.y = y
        self.health = health
        #allows to draw images ( ships )
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    #Draws the ship within the given window 
    def draw(self, window): 
        #draws a rectangle on position 
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers: 
            laser.draw(window)
    #gets width of the ship 
    def get_width(self): 
        return self.ship_img.get_width() 
    #gets height of the ship 
    def get_height(self): 
        return self.ship_img.get_height()

    #moves lasers of enemies
    #check if each laser has hit the player
    #removes laser if hit player or off screen
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:  
            laser.move(vel)
            if laser.off_screen(HEIGHT): 
                self.lasers.remove(laser)
            elif laser.collision(obj): 
                obj.health -= 10 
                self.lasers.remove(laser)

    #provides the cooldown for shooting laser
    #only allows the player to shoot laser every half-second
    def cooldown(self): 
        if self.cool_down_counter >= self.COOLDOWN_COUNTER: 
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0: 
            self.cool_down_counter += 1 


    def shoot(self, upgraded = None):
        if upgraded and self.cool_down_counter == 0: 
            laser1 = Laser(self.x + 50, self.y, self.laser_img)
            self.lasers.append(laser1)
            laser2 = Laser(self.x , self.y, self.laser_img)
            self.lasers.append(laser2)
            laser3 = Laser(self.x - 50, self.y, self.laser_img)
            self.lasers.append(laser3)
            self.cool_down_counter = 1
        elif self.cool_down_counter == 0: 
            laser = Laser(self.x , self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1




class Player(Ship):
    def __init__(self, x, y, health = 100): 
        #super allows to take in methods from parent and parameters
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        # allows for pixel perfect collisions
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.bal = 0 
        self.score = 0
    
    #(move_lasers) already called in parent class
    #if restated in child class the method in child takes priority

    #moves player laser and checks if it colliding with any enemies
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:  
            laser.move(vel)
            if laser.off_screen(HEIGHT): 
                self.lasers.remove(laser)
            else: 
                for  obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
                        EXPLOSION.play()
                        self.bal += 10
                        self.score += 100 

    def draw(self, window): 
        #super(). can give a child any element of parent class even a method
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window): 
        #creates rectangular healthbar
        #green rectangle over red rectangle
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


        



class Enemy(Ship): 
    #allows to choose between which ship to use
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER), 
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health = 100): 
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    #allows to move enemy ship 
    def move(self, vel): 
        self.y += vel
    
    def off_screen(self, height): 
        return not (self.y <= height and self.y >= 0)

    def shoot(self):
        if self.cool_down_counter == 0: 
            laser = Laser(self.x - 15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

#checks for collisions 
def collide(obj1, obj2): 
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    # will return none if not overlapping
    return obj1.mask.overlap(obj2.mask, (offset_x,offset_y)) != None


#main playing loop 

def main(): 
    #Background Music
    pygame.mixer.unpause()
    mixer.music.load(os.path.join ("assets","Background.mp3"))
    mixer.music.set_volume(0.7)
    mixer.music.play(-1)
    

    #when starting game these all are initialized
    FPS = 60 
    clock = pygame.time.Clock() 
    running = True
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("roboto",50)
    lost_font = pygame.font.SysFont("roboto",60)

    lost_count = 0
    laser_vel = 5

    enemies = []
    wave_length = 5
    enemy_vel = 1

    

    lost = False

    #velocity of player
    player_vel = 5
    player = Player(300, 630)

    #Audio Button 
    sound_count = 0
    sound = True 
    audio = Button(BUTTON, WIDTH - BUTTON.get_width() - 40, HEIGHT - 50)
    # keeps track of button clicks
    click = 0 

    #makes sure that only one element is written into Space_Invaders.txt
    count = 0 

    #Shop: 
    Upgraded = False
    upgrades = Button(UPGRADE, WIDTH - UPGRADE.get_width()- 40, 150)

    #Making a function inside another function 
    #Can only be accessed when main is called
    #Can access all the declared variables inside main()
    def redraw_window(): 
        # Y coord at 0 is top to down
        # X Coord at 0 is at the left
        WINDOW.blit(BG, (0,0))

        #draws the button 
        audio.draw(WINDOW, (33,123,123))
        upgrades.draw(WINDOW, (33,123,123), upgrades.can_buy(player.bal, 200))

        #draws the shop: 
        upgrades.draw
        upgrades.add_label("$200 Upgrade", WINDOW)
        
        #drawing text 
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255)) 
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        score_label = main_font.render(f"Score: {player.score}", 1, (255,255,255))
        bal_label = main_font.render(f"Balance: ${player.bal}", 1, (255, 255, 255))

        WINDOW.blit(lives_label, (10, 10))
        WINDOW.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WINDOW.blit(score_label, (WIDTH - score_label.get_width() - 10, 50))
        WINDOW.blit(bal_label, (0 + 10, HEIGHT - bal_label.get_height() - 10))
        #draws enemies
        for enemy in enemies: 
            enemy.draw(WINDOW)

        #draws player
        player.draw(WINDOW)
        
        if lost: 
            lost_label = lost_font.render("You Lost!", 1, (255,255,255))
            #centers the lost label
            WINDOW.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
            
        
        pygame.display.update() 

    while running: 


        clock.tick(FPS)
        redraw_window()
        #Audio button 
        #gets position of where player clicked
        for event in pygame.event.get(): 
            pos = pygame.mouse.get_pos()

            #Manages the music in game
        
            if event.type == pygame.MOUSEBUTTONDOWN: 
                if audio.isOver(pos): 
                    click += 1 
                    if click % 2 == 0: 
                        audio = Button(BUTTON, WIDTH - BUTTON.get_width() - 40, HEIGHT - 50)
                        sound = True
                        pygame.mixer.music.unpause() 
                        
                    else: 
                        audio = Button(BUTTON2, WIDTH - BUTTON.get_width() - 40, HEIGHT - 50)
                        sound = False
                        pygame.mixer.music.pause() 
            
            #allows the tri - shot upgrade 
            if event.type == pygame.MOUSEBUTTONDOWN: 
                if upgrades.isOver(pos) and upgrades.can_buy(player.bal, 200): 
                    Upgraded = True
                    player.bal -= 200 
                    if player.health < 100: 
                        player.health += 10 
                

            

                       

        
        #checks if player has lost
        
                
        if lives <= 0 or player.health <= 0: 
            if count == 0: 
                f = open("Space_Invaders.txt", "a+")
                f.write(f"{player.score}\n")
                f.close() 
                count += 1
            if sound and sound_count == 0: 
                DEATH_SOUND.play()
                sound_count += 1 
            lost = True
            lost_count += 1
        
        
        if lost: 
            #The while loop runs 60 times in 1 second: 
            #This allows the lost message to display for 3 secs before ending game
            if lost_count > FPS * 3:
                running = False
            else: 
                #ends current iteration and moves onto next iteration
                continue

        if len(enemies) == 0: 
            level += 1
            wave_length += 5 
            #spawns enemies
            #each new enemy is declared with enemy class
            for i in range(wave_length): 
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1200, -100), random.choice(["red", "blue", "green" ]))
                enemies.append(enemy)
        #checks all events in pygame
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                running = False
                pygame.quit()
        # returns a library of all keys being pressed
        keys = pygame.key.get_pressed()
        #checks if key is in libarary ( being pressed )
        if keys[pygame.K_a] and player.x - player_vel > 0: #moving left ( does not allow player to travel out of bounds)
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #moving right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: #up
            player.y -= player_vel 
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: #down
            player.y += player_vel
        if keys[pygame.K_SPACE]: 
            if sound: 
                PLAYER_SHOOT.play()
            if Upgraded: 
                player.shoot(Upgraded)
            else: 
                player.shoot() 
        
        #The enemies will move down until they hit border and die
        for enemy in enemies: 
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * FPS) == 1: 
                if not enemy.off_screen(HEIGHT) and sound: 
                    SHOOT_SOUND.play() 
                enemy.shoot()
            #checks if enemy has collided with player
            if collide(enemy, player): 
                if sound: 
                    EXPLOSION.play()
                player.score += 100
                player.health -= 10 
                enemies.remove(enemy)
            #checks if enemies have reached bottom of screen
            elif enemy.y + enemy.get_height() > HEIGHT: 
                lives -= 1
                enemies.remove(enemy)

        
        player.move_lasers(-laser_vel,  enemies)
        
#Creates main menu
def main_menu(): 

    greatest_score = 0
    #gets the greatest score 
    def get_greatest(greatest): 
        #get the highest score from scoreboard
        file = open("Space_Invaders.txt", "r")
        scores = file.readlines() 
        for score in scores: 
            if int(score) > greatest: 
                greatest = int(score)
        return(greatest)

    #Creates the menu screen 
    title_font = pygame.font.SysFont("comicsans", 50)
    score_font = pygame.font.SysFont("Serif Sans", 40)
    
    run = True
    while run: 
        WINDOW.blit(BG, (0,0))
        get_greatest(greatest_score)
        title_label = title_font.render("Press the mouse to begin...",1,(255,255,255))
        scored_label = score_font.render(f"RECORD HOLDER: {get_greatest(greatest_score)} points!",1,(255,255,255))
        WINDOW.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        WINDOW.blit(scored_label, (WIDTH/2 - scored_label.get_width()/2,440))
        pygame.display.update()
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN: 
                main()
    
    pygame.quit()


main_menu()        