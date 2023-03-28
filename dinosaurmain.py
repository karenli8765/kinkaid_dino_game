__author__ = 'Karen'  # put your name here!!!

# citations
# https://ya-webdesign.com/explore/chrome-dinosaur-png/
# https://www.tynker.com/community/projects/play/google-dino-dash-hacked/5c5c5010cebfbd68c70cf241

import pygame, sys, traceback, random
from pygame.locals import *

GAME_MODE_LEVEL_ONE = 0
GAME_MODE_TITLE_SCREEN = 1
GAME_MODE_GAME_OVER = 2
GAME_MODE_LEVEL_TWO = 3

from DinosaurFile import Dinosaur
from CactusFile import Cactus


# =====================  setup()
def setup():
    """
    This happens once in the program, at the very beginning.
    """
    pygame.mixer.init()
    global canvas, objects_on_screen, objects_to_add, bg_color, game_mode
    global the_dinosaur, time_since_last_jump, time_since_last_cactus, cactus_list, random_cactus
    global can_dino_jump, running_score, levelup_sound, dinosplat_sound, time_since_game_over, gameover_sound

    canvas = pygame.display.set_mode((1000, 600))
    objects_on_screen = []
    objects_to_add = []
    bg_color = pygame.Color("white")
    game_mode = GAME_MODE_LEVEL_ONE
    the_dinosaur = Dinosaur()
    time_since_last_jump = 0
    cactus_list = []
    objects_on_screen.append(the_dinosaur)
    time_since_last_cactus = 0
    can_dino_jump = 1
    running_score = 0
    levelup_sound = pygame.mixer.Sound("sounds/level_up.wav")
    dinosplat_sound = pygame.mixer.Sound("sounds/splat.wav")
    gameover_sound = pygame.mixer.Sound("sounds/game_over.wav")
    time_since_game_over = 0
    random_cactus = 0.5

# =====================  loop()
def loop(delta_T):
    """
     this is what determines what should happen over and over.
     delta_T is the time (in seconds) since the last loop() was called.
    """
    global random_cactus
    if game_mode == GAME_MODE_LEVEL_ONE or game_mode == GAME_MODE_LEVEL_TWO:
        if game_mode == GAME_MODE_LEVEL_ONE:
            bg_color = pygame.Color("white")
            ground_color = pygame.Color("black")
        if game_mode == GAME_MODE_LEVEL_TWO:
            bg_color = pygame.Color("black")
            ground_color = pygame.Color("white")
        canvas.fill(bg_color)
        pygame.draw.line(canvas, ground_color, (0, 400), (1000, 400), 2)
        animate_objects(delta_T)

        spawn_cactus(delta_T)
        dino_jump(delta_T)
        check_cactus_dino_collision()
        display_score()

        clear_dead_objects()
        add_new_objects()
        draw_objects()
        show_stats(delta_T)

    if game_mode == GAME_MODE_GAME_OVER:
        game_over_display(delta_T)

    pygame.display.flip()


# ===================== spawn_cactus
def spawn_cactus(delta_T):
    global time_since_last_cactus, random_cactus
    time_since_last_cactus += delta_T
    if time_since_last_cactus >= random_cactus:
        time_since_last_cactus = 0
        next_cactus = Cactus()
        next_cactus.x = 1010
        next_cactus.y = 375
        random_cactus = random.randrange(7, 15)/5
        cactus_list.append(next_cactus)
        objects_on_screen.append(next_cactus)
        if game_mode == GAME_MODE_LEVEL_TWO:
            next_cactus.vx = -350

# ===================== check_cactus_dino_collision
def check_cactus_dino_collision():
    global game_mode
    dinosaur = the_dinosaur
    for cactus in cactus_list:
        if abs(cactus.x - dinosaur.x) < (cactus.width + dinosaur.width)/2 and \
           abs(cactus.y - dinosaur.y) < (cactus.height + dinosaur.height)/2:
            gameover_sound.play()
            game_mode = GAME_MODE_GAME_OVER

# ===================== dino_jump()
def dino_jump(delta_T):
    global can_dino_jump, time_since_last_jump
    time_since_last_jump += delta_T
    dinosaur = the_dinosaur
    # can_dino_jump: 1 = regular running / 2 = up jump / 3 = start jump / 4 = down jump
    if game_mode == GAME_MODE_LEVEL_ONE:
        maxheight = 175
    if game_mode == GAME_MODE_LEVEL_TWO:
        maxheight = 210
    if can_dino_jump == 3:
        can_dino_jump = 2
    if can_dino_jump == 2:
        dinosaur.vy = -300
        if dinosaur.y <= maxheight:
            can_dino_jump = 4
    if can_dino_jump == 4:
        dinosaur.vy = 350
        if dinosaur.y >= 367:
            can_dino_jump = 1
            time_since_last_jump = 0
            dinosplat_sound.play()
    if can_dino_jump == 1:
        dinosaur.vy = 0
        dinosaur.y = 367

# ===================== display_score
def display_score():
    """
    display the score in the top right corner
    :return: None
    """
    global running_score, score_display_color, game_mode
    running_score += 0.1
    score = str(round(running_score))
    if game_mode == GAME_MODE_LEVEL_ONE:
        score_display_color = pygame.Color("black")
    if game_mode == GAME_MODE_LEVEL_TWO:
        score_display_color = pygame.Color("white")
    score_display_font = pygame.font.SysFont("Arial", 15)
    score_display_surface = score_display_font.render("Score: " + score, True, score_display_color)
    score_display_rect = score_display_surface.get_rect()
    canvas.blit(score_display_surface, (900 - score_display_rect.width/2, 50 - score_display_rect.height/2))
    if running_score >= 10:
        if running_score % 100 >= 0 and running_score % 100 < 5:
                levelup_sound.play()
    if game_mode == GAME_MODE_LEVEL_ONE or game_mode == GAME_MODE_LEVEL_TWO:
        if running_score >= 100:
            game_mode = GAME_MODE_LEVEL_TWO

# ===================== game_over_display()
def game_over_display(delta_T):
    global time_since_game_over
    time_since_game_over += delta_T
    dino = the_dinosaur
    if time_since_game_over <= 2:
        dino.vy = 0
        for i in range (0, len(cactus_list)):
            this_cactus = cactus_list[i]
            this_cactus.vx = 0
    if time_since_game_over > 2:
        canvas.fill(pygame.Color("grey"))
        gameover_font = pygame.font.SysFont("Arial", 45)
        gameover_color = pygame.Color("red")

        gameover_surface = gameover_font.render("Game Over", True, gameover_color)
        gameover_rectangle = gameover_surface.get_rect()

        canvas.blit(gameover_surface, (500 - gameover_rectangle.width / 2, 300 - gameover_rectangle.height / 2))

# =====================  animate_objects()
def animate_objects(delta_T):
    """
    tells each object to "step"...
    """
    global objects_on_screen
    for object in objects_on_screen:
        if object.is_dead():  # ...but don't bother "stepping" the dead ones.
            continue
        object.step(delta_T)


# =====================  clear_dead_objects()
def clear_dead_objects():
    """
    removes all objects that are dead from the "objectsOnScreen" list
    """
    global objects_on_screen
    i = 0
    for object in objects_on_screen[:]:
        if object.is_dead():
            objects_on_screen.pop(i)  # removes the ith object and pulls everything else inwards, so don't advance "i"
            #      ... they came back to you.
        else:
            i += 1
    i = 0
    for cactus in cactus_list:
        if cactus.is_dead():
            cactus_list.pop(i)
        else:
            i += 1


# =====================  add_new_objects()
def add_new_objects():
    """
    Adds all the objects in the list "objects to add" to the list of "objects on screen" and then clears the "to add" list.
    :return: None
    """
    global objects_to_add, objects_on_screen
    objects_on_screen.extend(objects_to_add)
    objects_to_add.clear()


# =====================  draw_objects()
def draw_objects():
    """
    Draws each object in the list of objects.
    """
    for object in objects_on_screen:
        object.draw_self(canvas)


# =====================  show_stats()
def show_stats(delta_T):
    """
    draws the frames-per-second in the lower-left corner and the number of objects on screen in the lower-right corner.
    Note: the number of objects on screen may be a bit misleading. They still count even if they are being drawn off the
    edges of the screen.
    :param delta_T: the time since the last time this loop happened, used to calculate fps.
    :return: None
    """
    white_color = pygame.Color(0, 255, 255)
    stats_font = pygame.font.SysFont('Arial', 10)

    fps_string = f"FPS: {(1.0 / delta_T):3.1f}"  # build a string with the calculation of FPS. (The 3.1f means a number with 1 decimal place after the decimal.)
    fps_text_surface = stats_font.render(fps_string, True, white_color)  # this makes a transparent box with text
    fps_text_rect = fps_text_surface.get_rect()  # gets a copy of the bounds of the transparent box
    fps_text_rect.left = 10  # now relocate the box to the lower left corner
    fps_text_rect.bottom = canvas.get_rect().bottom - 10
    canvas.blit(fps_text_surface, fps_text_rect)  # ... and copy it to the buffer at the location of the box

    objects_string = f"Objects: {(len(objects_on_screen)):5d}"  # build a string with the number of objects
    # (the 5d means an integer (d) with spaces so that it is always at least 5 characters wide.)
    objects_text_surface = stats_font.render(objects_string, True, white_color)
    objects_text_rect = objects_text_surface.get_rect()
    objects_text_rect.right = canvas.get_rect().right - 10  # move this box to the lower right corner
    objects_text_rect.bottom = canvas.get_rect().bottom - 10
    canvas.blit(objects_text_surface, objects_text_rect)


# =====================  read_events()
def read_events():
    """
    checks the list of events and determines whether to respond to one.
    """
    global can_dino_jump
    events = pygame.event.get()  # get the list of all events since the last time
    for evt in events:
        if evt.type == QUIT:
            pygame.quit()
            raise Exception("User quit the game")

        if evt.type == KEYDOWN:
            if can_dino_jump == 1:
                can_dino_jump = 3



# program start with game loop - this is what makes the loop() actually loop.
pygame.init()
try:
    setup()
    fpsClock = pygame.time.Clock()  # this will let us pass the deltaT to loop.
    while True:
        time_since_last_loop = fpsClock.tick(60) / 1000.0  # we set this to go up to as much as 60 fps, probably less.
        loop(time_since_last_loop)
        read_events()

except Exception as reason:  # If the user quit, exit gracefully. Otherwise, explain what happened.
    if len(reason.args) > 0 and reason.args[0] == "User quit the game":
        print("Game Over.")
    else:
        traceback.print_exc()
