import pygame
import random
import numpy
import math
import shelve

# Global constants
speed_apple_y = 5
speed_player_x = 15
game_over = False

# Colors
BLACK = (60, 60, 60)
WHITE = (255, 255, 255)
BROWN = (160, 82, 45)
BROWN_LIGHTER = (205,133,63)
BLUE = (135, 206, 250)
RED = (240, 20, 60)
RED_DARKER = (200, 20, 60)
GREEN = (60, 199, 113)
GREEN_DARKER = (60, 159, 113)

# Basic screen values
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
WIDTH_LEFT = SCREEN_WIDTH/3
WIDTH_RIGHT = SCREEN_WIDTH/(3/2)
HEIGHT_LOWER = SCREEN_HEIGHT/(3/2)

cloud = pygame.image.load('cloud.png')
cloud = pygame.transform.scale(cloud, (300, 150))

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()


""" Player Class.
Handles the main components
of the player and determines
how he moves. """
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        global speed_player_x

        width = 155
        height = 35

        self.image = pygame.Surface([width, height])
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()

        self.change_x = 0

    def update(self):
        self.rect.x += self.change_x

    def go_left(self):
        self.change_x = -speed_player_x

    def go_right(self):
        self.change_x = speed_player_x

    def stop(self):
        self.change_x = 0


""" Apples Class.
Handles the main components
of the apples and determines
how there type and some of their motion. """
class Apples(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        global speed_apple_y

        width = 50
        height = 50

        # Pick apple type with weighted randomness.
        choices = ['r', 'g', 's']
        weights = [0.70, 0.25, 0.05]
        appletype = numpy.random.choice(choices, p=weights)
        self.appletype = appletype

        if appletype == 'r':
            color = (220, 20, 60)

        elif appletype == 'g':
            color = (60, 179, 113)

        elif appletype == 's':
            color = (148, 0, 211)

        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

        self.change_x = 0
        self.change_y = speed_apple_y

    def update(self):
        self.rect.y += self.change_y
        self.rect.x += self.change_x

""" Handles the text boxes. """
def text(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

""" Handles buttons. """
def button(msg,x,y,w,h,init_color,hover_color,action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(screen, hover_color,(x,y,w,h))
        if click[0] == 1 and action != None:
            action()

    else:
        pygame.draw.rect(screen, init_color,(x,y,w,h))

    smallText = pygame.font.SysFont("comicsansms", 52)
    textSurf, textRect = text(msg, smallText, WHITE)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    screen.blit(textSurf, textRect)

""" Intro Screen with text and buttons. """
def intro():
    intro = True

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

        screen.fill(BLUE)
        largeText = pygame.font.Font('freesansbold.ttf', 115)
        color = WHITE
        TextSurf, TextRect = text("Apple Catcher", largeText, color)
        TextRect.center = ((SCREEN_WIDTH/2), (SCREEN_HEIGHT/3))
        screen.blit(TextSurf, TextRect)

        button("Start", WIDTH_LEFT - 100, HEIGHT_LOWER - 50, 200, 100, GREEN_DARKER, GREEN, main)
        button("Quit", WIDTH_RIGHT - 100, HEIGHT_LOWER - 50, 200, 100, RED_DARKER, RED, quit)

        pygame.display.update()
        clock.tick(15)

""" Handles the quit button. """
def quit():
    pygame.quit()

""" Main Method.
Handles almost all
logic and gameplay."""
def main():
    global speed_apple_y, speed_player_x, game_over

    # Some variables
    game_over = False
    done = False
    speed_apple_y = 5
    speed_player_x = 15

    pygame.display.set_caption("Apple Catcher")

    # Sprite groups
    active_sprite_list = pygame.sprite.Group()
    apple_list = pygame.sprite.Group()

    # Timers and frame rate counts
    frame_count_special = 0
    frame_rate = 60
    timer = 0
    timer_spawn = 0

    # Variables that handle fairness and spawning logic
    special = False
    score = 0
    lives = 5
    chance = 1.5
    rate = 0.75
    rndx_lower = 0
    rndx_upper = 1870

    player = Player()

    player.rect.x = 960
    player.rect.y = 1080 - player.rect.height
    active_sprite_list.add(player)

    # -------- Main Program Loop -----------
    while not done:

        # Handle key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    done = True

        # Game over sceen
        if game_over:
            screen.fill(BLACK)

            largeText = pygame.font.Font('freesansbold.ttf', 115)
            TextSurf, TextRect = text("GAME OVER!", largeText, WHITE)
            TextRect.center = ((SCREEN_WIDTH/2), (SCREEN_HEIGHT/3))
            screen.blit(TextSurf, TextRect)

            score_text = pygame.font.SysFont("comicsansms", 58)
            TextSurf, TextRect = text("Your Score: "+str(score), score_text, WHITE)
            TextRect.center = ((SCREEN_WIDTH/2), (SCREEN_HEIGHT/2))
            screen.blit(TextSurf, TextRect)

            button("Play Again?", WIDTH_LEFT - 100, HEIGHT_LOWER - 50, 200, 100, GREEN_DARKER, GREEN, main)
            button("Quit", WIDTH_RIGHT - 100, HEIGHT_LOWER - 50, 200, 100, RED_DARKER, RED, quit)
        else:
            total_seconds_special = frame_count_special // frame_rate

            # Handles the spawning rates of apples.
            # The chance that an apple can spawn each frame.
            if random.randrange(0, 100) < chance:

                # Addition check used for fairness. Even if apple is told to spawn on frame, it wont unless minimum time, rate, has passed.
                if (timer_spawn / frame_rate) >= rate:
                    rndx = random.randint(rndx_lower, rndx_upper)
                    rndy = random.randint(-1130, -1080)

                    new_apple = Apples()

                    # Adds fairness. New apple can only spawn up to half the screen away.
                    rndx_upper = rndx + 960
                    rndx_lower = rndx - 960

                    # Make sure apple is not off the screen
                    if rndx_upper >= 1870:
                        rndx_upper = 1870

                    if rndx_lower <= 0:
                        rndx_lower = 0

                    new_apple.rect.x = rndx
                    new_apple.rect.y = rndy

                    apple_list.add(new_apple)
                    active_sprite_list.add(new_apple)

                    # Reset timer for min spawn time
                    timer_spawn = 0

            apple_hit_list = pygame.sprite.spritecollide(player, apple_list, False)

            # Which apple was caught?
            for apple in apple_hit_list:
                apple_list.remove(apple)
                active_sprite_list.remove(apple)
                if apple.appletype == 'r':
                    score += 1
                elif apple.appletype == 'g':
                    lives -= 1
                elif apple.appletype == 's':
                    special = True

            # Remove apples that go off the screen
            for apple in apple_list:
                if apple.rect.y >= 1055:
                    apple_list.remove(apple)
                    active_sprite_list.remove(apple)
                    if apple.appletype == 'r':
                        lives -= 1

            # Handles special apples
            if special is True:
                for apple in apple_list:
                    # Make every apple fly to the player for free points after special apple is caught!
                    dx = (player.rect.x - apple.rect.x)/math.sqrt((player.rect.x - apple.rect.x) ** 2 + (player.rect.y - apple.rect.y) ** 2)
                    dy = (player.rect.y - apple.rect.y)/math.sqrt((player.rect.x - apple.rect.x) ** 2 + (player.rect.y - apple.rect.y) ** 2)
                    apple.rect.y += dy * 50
                    apple.rect.x += dx * 75

                    # Make every apple look red and be of type 'r' so that the special apple is better.
                    apple.appletype = 'r'
                    color = (220, 20, 60)
                    apple.image.fill(color)

                    # Special apple lasts for 10 seconds. Reset.
                    if total_seconds_special >= 10:
                        frame_count_special = 0
                        special = False

                frame_count_special += 1

            # Handles difficulty increase over time every 10 seconds.
            if (timer / frame_rate) % 10 == 0:
                # Increase apple fall rate up to a max.
                if speed_apple_y >= 25:
                    speed_apple_y = 25
                else:
                    speed_apple_y += 2

                # Increase player speed up to a max.
                if speed_player_x >= 35:
                    speed_player_x = 35
                else:
                    speed_player_x += 2

                # Increase chance of apple spawning each from up to a max. Also only start this once apple fall rate is at max.
                if speed_apple_y == 25:
                    if chance >= 5:
                        chance = 5
                    else:
                        chance += 0.5

                # Decrease min time between spawns allowed up to a max. Also only start once apple fall rate is 10.
                if speed_apple_y >= 10:
                    if rate <= 0.45:
                        rate = 0.45
                    else:
                        rate -= 0.1

            # Update all the sprites
            active_sprite_list.update()

            # If out of lives game over
            if lives == 0:
                for apple in apple_list:
                    apple_list.remove(apple)
                    active_sprite_list.remove(apple)
                active_sprite_list.remove(player)
                game_over = True

            screen.fill(BLUE)
            pygame.draw.rect(screen, GREEN_DARKER, (0, SCREEN_HEIGHT - 15, SCREEN_WIDTH, 15))

            # Make sure player cant move off the screen.
            if player.rect.right >= 1920:
                player.rect.right = 1920

            if player.rect.left <= 0:
                player.rect.left = 0

            # Draw all the sprites
            active_sprite_list.draw(screen)

            pygame.draw.rect(screen, BROWN_LIGHTER, (0, 0, SCREEN_WIDTH, 100))

            # Randomize cloud placement (Kinda)
            for i in range(3):
                screen.blit(cloud, (i * 800 + 10, 120 + i*20))
            for i in range(3):
                screen.blit(cloud, (i * 400 + 300, 180 - i*20))

            bonus_text = pygame.font.SysFont("comicsansms", 56)
            if total_seconds_special == 0:
                TextSurf, TextRect = text("Bonus: None", bonus_text, WHITE)
            else:
                TextSurf, TextRect = text("Bonus: "+str(10 - total_seconds_special), lives_text, WHITE)
            TextRect.center = ((WIDTH_RIGHT + 200), (50))
            screen.blit(TextSurf, TextRect)

            lives_text = pygame.font.SysFont("comicsansms", 56)
            TextSurf, TextRect = text("Lives: "+str(lives), lives_text, WHITE)
            TextRect.center = ((SCREEN_WIDTH / 2), (50))
            screen.blit(TextSurf, TextRect)

            score_text = pygame.font.SysFont("comicsansms", 56)
            TextSurf, TextRect = text("Score: "+str(score), score_text, WHITE)
            TextRect.center = ((WIDTH_LEFT - 200), (50))
            screen.blit(TextSurf, TextRect)

            # Timers
            timer += 1
            timer_spawn += 1

        clock.tick(60)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    intro()
    main()
