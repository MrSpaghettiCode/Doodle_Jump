import pygame as pg
from pygame.locals import *
import os
import random

pg.mixer.pre_init(44100, -16, 2, 4096)
pg.init()

os.environ['SDL_VIDEODRIVER'] = 'directx'   
WIDTH = 400
HEIGHT = 850

FLAGS = DOUBLEBUF #helps with fps

WIN = pg.display.set_mode((WIDTH, HEIGHT), FLAGS, 8)

audio_player = pg.mixer
audio_player.music.set_volume(0.2)
sound_files = ["\\Assets\\Sounds\\break_jump.mp3", "\\Assets\\Sounds\\regular_jump.mp3", "\\Assets\\Sounds\\boost_jump.wav"]
                        
def load_audio(asset_path):
    audio_player.music.load(os.path.realpath(os.path.dirname(__file__)) + asset_path)

def play_audio(index:int):
    load_audio(sound_files[index])
    audio_player.music.play()

def get_and_scale_Image(path, rotate = 90, scale = (WIDTH, HEIGHT)):
    return pg.transform.scale(pg.transform.rotate(pg.image.load(os.path.realpath(os.path.dirname(__file__)) + path), rotate), scale)

BACK1 = get_and_scale_Image("\\Assets\\Background\\back_side_1.png").convert()
BACK2 = get_and_scale_Image("\\Assets\\Background\\back_side_2.png").convert_alpha()
BACK3 = get_and_scale_Image("\\Assets\\Background\\back_side_3.png").convert_alpha()

WIN_SIZE = WIN.get_size()

UI_COLOR = (255,255,255)
UI_FONT = pg.font.SysFont("monospace", 16)
UI_POS_Y = int(WIN_SIZE[1] * 0.025)

SCORE_POS_X = int(WIN_SIZE[0] * 0.05)
SCORE_POSITION = (SCORE_POS_X, UI_POS_Y)

FPS_COUNTER_POS_X = int(WIN_SIZE[0] * 0.80)
FPS_COUNTER_POSITION = (FPS_COUNTER_POS_X, UI_POS_Y)

GAME_SCALE = 0.5
FPS = 60

CAMERA_BOOST_HIGHT = WIN_SIZE[1]*0.05
CAMERA_BOOSTING_FORCE = 0.5

OBSTACLE_MIN_WIDTH = 20
OBSTACLE_WIDTH_AT_START = int(120 * GAME_SCALE)
OBSTACLE_HEIGHT = int(80 * GAME_SCALE)
OBSTACLE_HORIZONTAL_SPEED_ODD = 0
OBSTACLE_HORIZONTAL_SPEED = -1
OBSTACLE_PRELOAD_AMOUNT = 2000
OBSTACLE_SPAWN_OFFSET = -100
OBSTACLE_SPAWN_AMOUNT = 1
OBSTACLE_SPAWN_EVENT_TIME = 300
OBSTACLE_SPAWN_EVENT_ID = pg.USEREVENT+1
OBSTACLE_SCALING_OVER_TIME = 0.80

ENTITY_SIZE = int(75 * GAME_SCALE)

PLAYER_LANDING_FRAME = 22
PLAYER_INITIAL_FRAME = 15

PLAYER_JUMPING_FORCE = 22
PLAYER_JUMPING_BOOST = 20
PLAYER_MOVEMENT_SPEED = 6
PLAYER_MAX_FALLING_SPEED = int(OBSTACLE_HEIGHT * 0.5)
PLAYER_MAX_HIGHT = HEIGHT * 0.05
PLAYER_SPAWN_POINT = (int(WIDTH*0.5), PLAYER_MAX_HIGHT)#-ENTITY_SIZE)
PLAYER_ANIMATION_STATES_LEFT = []
PLAYER_ANIMATION_STATES_RIGHT = []
PLAYER_ANIMATION_STATES_DEFAULT = []

for i in range(0, 23): #this transforms all the player animation frames at start, so it doesnt need to be done every time a button is pressed
    PLAYER_ANIMATION_STATES_DEFAULT.append(get_and_scale_Image("\\Assets\\PlayerAnimationStates\\" + str(i+1) + ".png", 0, (ENTITY_SIZE, ENTITY_SIZE)).convert_alpha())
    if i == PLAYER_LANDING_FRAME:
        PLAYER_ANIMATION_STATES_LEFT.append(get_and_scale_Image("\\Assets\\PlayerAnimationStates\\" + str(i+1) + ".png", 0, (ENTITY_SIZE, ENTITY_SIZE)).convert_alpha())
        PLAYER_ANIMATION_STATES_RIGHT.append(get_and_scale_Image("\\Assets\\PlayerAnimationStates\\" + str(i+1) + ".png", 0, (ENTITY_SIZE, ENTITY_SIZE)).convert_alpha())
    elif i not in [13, 14, 15, 16] and i != PLAYER_LANDING_FRAME:
        PLAYER_ANIMATION_STATES_LEFT.append(get_and_scale_Image("\\Assets\\PlayerAnimationStates\\" + str(i+1) + ".png", -30, (ENTITY_SIZE*1.3, ENTITY_SIZE*1.3)).convert_alpha())
        PLAYER_ANIMATION_STATES_RIGHT.append(get_and_scale_Image("\\Assets\\PlayerAnimationStates\\" + str(i+1) + ".png", 30, (ENTITY_SIZE*1.3, ENTITY_SIZE*1.3)).convert_alpha())
    else:
        PLAYER_ANIMATION_STATES_LEFT.append(get_and_scale_Image("\\Assets\\PlayerAnimationStates\\" + str(i+1) + ".png", 30, (ENTITY_SIZE*1.3, ENTITY_SIZE*1.3)).convert_alpha())
        PLAYER_ANIMATION_STATES_RIGHT.append(get_and_scale_Image("\\Assets\\PlayerAnimationStates\\" + str(i+1) + ".png", -30, (ENTITY_SIZE*1.3, ENTITY_SIZE*1.3)).convert_alpha())

REGULAR_PAD_IMPAGE = get_and_scale_Image("\\Assets\\Pads\\Pad_1_3.png", 0, (OBSTACLE_WIDTH_AT_START, OBSTACLE_HEIGHT))
BREAKING_PAD_IMPAGE = get_and_scale_Image("\\Assets\\Pads\\Pad_4_3.png", 0, (OBSTACLE_WIDTH_AT_START, OBSTACLE_HEIGHT))

GROUND_PAD_IMPAGE = get_and_scale_Image("\\Assets\\Pads\\Pad_1_3.png", 0, (WIDTH*2, HEIGHT))
#helps with fps
pg.event.set_allowed([OBSTACLE_SPAWN_EVENT_ID, QUIT, KEYDOWN, KEYUP])

obstacle_pregen = []
active_obstacles = []
#region TODO
    #generell:
        #gegner einbauen
        #am end Items einbauen

    #bei zu viel Zeit:
        #player class entwurschteln
        
#endregion
#region classes
class player_animation_handler():
    def __init__(self, initial_state:int) -> None:
        self.animation_states_right = PLAYER_ANIMATION_STATES_LEFT
        self.animation_states_left = PLAYER_ANIMATION_STATES_RIGHT
        self.animation_states_default = PLAYER_ANIMATION_STATES_DEFAULT
        self.current_state = initial_state
        self.current_frame_time = 0

    def get_current_animation_piece(self, user_left, user_right):
        if user_left:
            return self.animation_states_left[self.current_state]
        elif user_right:
            return self.animation_states_right[self.current_state]
        else:
            return self.animation_states_default[self.current_state]

    def set_animation_state(self, state:int, frame_time = 0):
        if self.current_frame_time <= 0:
            self.current_state = state
            self.current_frame_time = frame_time
        else:
            self.current_frame_time -= 1

class background_image():
    def __init__(self, background):
        self.size = background.get_size()[1]
        self.image = pg.surface.Surface((WIDTH, HEIGHT*3))
        self.canvas = background
     
        self.image.blit(self.canvas, (0, 0))
        self.image.blit(self.canvas, (0, self.size))
        self.image.blit(self.canvas, (0, self.size*2))
        self.image.set_colorkey(pg.Color(0,0,0))

        self.image.convert()

class background_handler():
    def __init__(self) -> None:
        self.height = HEIGHT
        
        self.b1 = background_image(BACK1)
        self.b2 = background_image(BACK2)
        self.b3 = background_image(BACK3)
        
        self.animation_states = [0, 0, 0]

    def update_animation_state(self, index, value):
        if self.animation_states[index] < self.b1.size:
            self.animation_states[index] += value
        else:
            self.animation_states[index] = 0

    def update_animation_states(self, value):
        self.update_animation_state(0, value)
        self.update_animation_state(1, value * 0.5)
        self.update_animation_state(2, value * 0.25)

    def draw(self, value):
        WIN.blit(self.b1.image, (0, -self.height + self.animation_states[2]))
        WIN.blit(self.b2.image, (0, -self.height + self.animation_states[1]))
        WIN.blit(self.b3.image, (0, -self.height + self.animation_states[0]))

        self.update_animation_states(value)

background = background_handler()
class hitbox():
    def __init__(self, x, y, size:tuple) -> None:
        self.coordinates = (x, y)
        self.size = size
        self.canvas = WIN

    def is_colliding(self, hitbox):
        self_x2 = self.coordinates[0] + self.size[0]
        self_y2 = self.coordinates[1] + self.size[1]

        other_x2 = hitbox.coordinates[0] + hitbox.size[0]
        other_y2 = hitbox.coordinates[1] + hitbox.size[1]

        return self.coordinates[0] < other_x2 and self_x2 > hitbox.coordinates[0] and self.coordinates[1] < other_y2 and self_y2 > hitbox.coordinates[1]

    def draw(self):
        pg.draw.rect(self.canvas, (255,0, 0), (self.coordinates[0], self.coordinates[1], self.size[0], self.size[1]))

    def update_position(self, x, y):
        self.coordinates = (x, y)

class obstacle():
    def __init__(self, coordinates, is_static = False, size =(OBSTACLE_WIDTH_AT_START, OBSTACLE_HEIGHT), image = None, offset=0):
        self.offset = offset
        self.size = size
        self.coordinates = coordinates
        self.starting_coordinates = coordinates
        self.hitbox = hitbox(coordinates[0], coordinates[1]+offset, self.size)

        self.was_seen = False

        self.is_static = is_static
        self.is_left_centered = True

        self.is_destructable = False
        if not is_static:
            self.is_destructable = random.randint(0, 10) > 6

        self.image = pg.transform.scale(REGULAR_PAD_IMPAGE, size)
        if self.is_destructable:
            self.image = pg.transform.scale(BREAKING_PAD_IMPAGE, size)

        if image != None:
            self.image = image

    def draw(self):
        WIN.blit(self.image, (self.coordinates[0], self.coordinates[1], self.size[0], self.size[1]))

    def update_hitbox(self, x, y):
        self.hitbox.update_position(x, y+self.offset)
        self.coordinates = (x, y)

    def update_horizontal_position(self):
        x = self.coordinates[0] + OBSTACLE_HORIZONTAL_SPEED
        self.update_hitbox(x, self.coordinates[1])

    def update_vertical_position(self, score, amount = 0):
        y = self.coordinates[1] + amount

        if not self.was_seen and self.is_in_playarea():
            y += random.randint(1, 3)

        if amount == 0:
            y -= user.ver_move_speed * 2
            score -= int(user.ver_move_speed * 0.1)

        if user.coordinates[1] < CAMERA_BOOST_HIGHT:
            y += CAMERA_BOOSTING_FORCE

        self.update_hitbox(self.coordinates[0], y)
        return score

    def is_in_playarea(self):
        return self.coordinates[1] <= WIN_SIZE[1] * 2

class collider():
    def __init__(self, coordinates: tuple, size) -> None:
        self.coordinates = coordinates
        self.size = size
        self.bottom = hitbox(self.coordinates[0], self.coordinates[1], (self.size[0], 2))
        #andere Richtungen waren nich nötig, aber besser haben und nicht brauchen...

    def update_position(self, new_x, new_y):
        x = new_x 
        y = new_y 

        self.bottom.update_position(x, y+ENTITY_SIZE)

        self.coordinates = (x, y)
    
    def check_for_collision(self, hitbox: hitbox) -> tuple:
        ob:obstacle
        if not user.is_jumping:
            index = 0
            for ob in active_obstacles:
                if hitbox.is_colliding(ob.hitbox):
                        if ob.is_destructable:
                            play_audio(0)
                        else:
                            play_audio(1)
                        return (True, index)
                index += 1
        
        return (False, -1)

    def is_top_colliding(self) -> tuple:
        return self.check_for_collision(self.top)

    def is_left_colliding(self) -> tuple:
        return self.check_for_collision(self.left)

    def is_bottom_colliding(self) -> tuple:
       return self.check_for_collision(self.bottom)

    def is_right_colliding(self) -> tuple:
       return self.check_for_collision(self.right)

class entity():
    def __init__(self, coordinates: tuple) -> None:
        self.size = (ENTITY_SIZE, ENTITY_SIZE)
        self.coordinates = coordinates
        self.hitbox = hitbox(self.coordinates[0], self.coordinates[1], self.size)
        self.collider = collider(coordinates, self.size)

    def is_dead(self):
        return self.coordinates[1] > HEIGHT + ENTITY_SIZE

    def update_position(self, x_plus, y_plus):
        x = self.coordinates[0] + x_plus 
        y = self.coordinates[1] + y_plus
        
        if self.coordinates[0] > WIN_SIZE[0]+ENTITY_SIZE:
            x = -ENTITY_SIZE
        elif self.coordinates[0] < -ENTITY_SIZE:
            x = WIN_SIZE[0] 

        self.hitbox.update_position(x, y)
        self.collider.update_position(x, y)
        self.coordinates = (x, y)

    def is_top_colliding(self) -> tuple:
        return self.collider.is_top_colliding()

    def is_bottom_colliding(self) -> tuple:
        return self.collider.is_bottom_colliding()
    
    def is_left_colliding(self) -> tuple:
        return self.collider.is_left_colliding()
    
    def is_right_colliding(self) -> tuple:
        return self.collider.is_right_colliding()

class player(entity):
    def __init__(self) -> None:
        super().__init__(PLAYER_SPAWN_POINT)
        self.animation_handler = player_animation_handler(11)
        self.is_moving_left = False
        self.is_moving_right = False
        self.is_jumping = False
        self.remaining_jump_height = PLAYER_JUMPING_FORCE
        self.frames_since_falling = 0
        self.ver_move_speed = 0

    def draw(self):
        WIN.blit(self.animation_handler.get_current_animation_piece(self.is_moving_left, self.is_moving_right), (self.coordinates[0], self.coordinates[1]))

    def update_position(self): # sorry :C
        gravforce = 5
        ver_move_val = 0
        hor_move_val = 0
        animation_state = 0
        frame_time = 0

        collision = self.is_bottom_colliding()
        
        if self.is_jumping:
            animation_state = 2
            if self.remaining_jump_height > 0:
                ver_move_val -= PLAYER_JUMPING_BOOST*(self.remaining_jump_height * 0.05)#/ PLAYER_JUMPING_FORCE)
            else:
                self.is_jumping = False
            self.remaining_jump_height -= 1
        elif not collision[0]:
            gravity = gravforce + self.frames_since_falling * 0.25
            animation_state = 13
            if gravity < PLAYER_MAX_FALLING_SPEED:
                ver_move_val += gravity
            else:
                ver_move_val += PLAYER_MAX_FALLING_SPEED
            self.frames_since_falling += 1
        elif collision[0]:
            animation_state = PLAYER_LANDING_FRAME
            frame_time = 8
            self.is_jumping = True
            self.remaining_jump_height = PLAYER_JUMPING_FORCE + self.frames_since_falling*0.1
            self.frames_since_falling = 0
            ver_move_val -= PLAYER_MOVEMENT_SPEED 
            
            if active_obstacles[collision[1]].is_destructable:
                active_obstacles.pop(collision[1])

        if self.is_moving_left:
            hor_move_val -= PLAYER_MOVEMENT_SPEED
        elif self.is_moving_right:
            hor_move_val += PLAYER_MOVEMENT_SPEED

        self.ver_move_speed = ver_move_val

        self.animation_handler.set_animation_state(animation_state, frame_time)
        if self.coordinates[1] <= PLAYER_MAX_HIGHT:
            self.ver_move_speed = self.ver_move_speed * 1.5 
            return super().update_position(hor_move_val, 1) 
        else:
            return super().update_position(hor_move_val, ver_move_val)
#endregion

user = player()

#region methods
obstacle_pregen_index = 0
def spawn_obstacles(amount):
    global obstacle_pregen_index
    for i in range(amount):
        active_obstacles.append(obstacle_pregen[obstacle_pregen_index])
        obstacle_pregen_index += 1

def handle_user_input(event:pg.event.Event):
    if event.key == pg.K_a:
        user.is_moving_left = True
        user.is_moving_right = False
    elif event.key == pg.K_d:
        user.is_moving_right = True
        user.is_moving_left = False

def handle_obstacles(score):
    ob:obstacle 
    ob_index = 0
    for ob in active_obstacles:
        if not ob.is_static:
            ob.update_horizontal_position()
        if user.is_jumping:
            score = ob.update_vertical_position(score)
        else:
            score = ob.update_vertical_position(score, -user.ver_move_speed)
        if ob.is_in_playarea():
            ob.was_seen = True
            ob.draw()
        else:
            active_obstacles.pop(ob_index)
            ob_index-=1
        ob_index += 1    
    return score 

def draw_game(background, score):
    if user.coordinates[1] < CAMERA_BOOST_HIGHT:
        background.draw(-(user.ver_move_speed - CAMERA_BOOSTING_FORCE))
    else:
        background.draw(-user.ver_move_speed)

    score = handle_obstacles(score)
    user.update_position()
    scoretext = UI_FONT.render("Score: "+str(score), 1, UI_COLOR)
    WIN.blit(scoretext, SCORE_POSITION)
    user.draw()
    pg.display.update()
    return score

def pregen_obstacles(size):
    width = OBSTACLE_WIDTH_AT_START
    for i in range(size):
        if width > OBSTACLE_MIN_WIDTH and i % 50 == 0:
            width = int(width*OBSTACLE_SCALING_OVER_TIME)
        obstacle_pregen.append(obstacle((random.randint(0, int(WIDTH*0.75)), random.randint(OBSTACLE_SPAWN_OFFSET, -OBSTACLE_HEIGHT)), random.randint(0, 10) > 2, (width, OBSTACLE_HEIGHT)))
#endregion

def main(background):
    pg.display.set_caption("SOME JUMPING GAME")
    pregen_obstacles(OBSTACLE_PRELOAD_AMOUNT)
    audio_player.init()
    
    score = 0
    clock = pg.time.Clock()
    pg.time.set_timer(OBSTACLE_SPAWN_EVENT_ID, OBSTACLE_SPAWN_EVENT_TIME)
    active_obstacles.append(obstacle((-OBSTACLE_WIDTH_AT_START, int(HEIGHT*0.20)), True, (WIDTH*2, HEIGHT), GROUND_PAD_IMPAGE, 350))
    
    while (1):
        score = draw_game(background, score)
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                handle_user_input(event)
            elif event.type == OBSTACLE_SPAWN_EVENT_ID:
                spawn_obstacles(OBSTACLE_SPAWN_AMOUNT)
            elif event.type == pg.QUIT:
                pg.quit()
        if user.is_dead():
            break
        clock.tick_busy_loop(FPS)
    print("Score: " + str(score))
    pg.quit()

main(background)