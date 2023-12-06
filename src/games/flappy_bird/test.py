import pygame
import sys
import random

WIDTH = 400
HEIGHT = 600
FPS = 90

PLAYER_JUMP = -9
GRAVITY = 0.25
BIRD_VELOCITY = 0
RUN = True
GAME_ACTIVE = True
SCORE = 0
HIGH_SCORE = 0
DYNAMIC_FLOOR = 0
CAN_SCORE = True

WHITE = (255, 255, 255)


class FlappyBird:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.player = pygame.image.load('assets/scene/background.png').convert()
        self.player = pygame.transform.scale(self.player, (60, 60))
        self.player_rect = self.player.get_rect(center=(80, HEIGHT / 2))
        self.pipe_surface = pygame.image.load('assets/scene/floor.png').convert()
        self.pipe_surface = pygame.transform.scale(self.pipe_surface, (100, 500))
        self.pipe_height = [200, 300, 400]
        self.pipe_list = []
        self.spawnpipe = pygame.USEREVENT
        pygame.time.set_timer(self.spawnpipe, 1200)
        self.create_pipe()

    def create_pipe(self):
        random_pipe_pos = random.choice(self.pipe_height)
        self.bottom_pipe = self.pipe_surface.get_rect(midtop=(500, random_pipe_pos))
        self.top_pipe = self.pipe_surface.get_rect(midbottom=(500, random_pipe_pos - 300))
        self.pipe_list = [self.bottom_pipe, self.top_pipe]

    def move_pipes(self):
        for pipe in self.pipe_list:
            pipe.centerx -= 5

    def draw_pipes(self):
        for pipe in self.pipe_list:
            if pipe.bottom >= HEIGHT:
                self.screen.blit(self.pipe_surface, pipe)
            else:
                flip_pipe = pygame.transform.flip(self.pipe_surface, False, True)
                self.screen.blit(flip_pipe, pipe)

    def check_collision(self):
        for pipe in self.pipe_list:
            if self.player_rect.colliderect(pipe):
                return False
        return True

    def rotate_player(self):
        return pygame.transform.rotozoom(self.player, -BIRD_VELOCITY * 3, 1)

    def make_action(self, action):
        if action == 1:
            BIRD_VELOCITY = 0
            BIRD_VELOCITY -= 9

    def game_loop(self, state, action):
        clock = pygame.time.Clock()
        global GAME_ACTIVE, BIRD_VELOCITY, SCORE, HIGH_SCORE, CAN_SCORE
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == self.spawnpipe:
                self.create_pipe()
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.player, self.player_rect)

        if GAME_ACTIVE:
            BIRD_VELOCITY += GRAVITY
            rotated_player = self.rotate_player()
            self.player_rect.centery += BIRD_VELOCITY
            self.screen.blit(rotated_player, self.player_rect)
            GAME_ACTIVE = self.check_collision()

            self.pipe_list = self.move_pipes()
            self.draw_pipes()
        pygame.display.update()
        clock.tick(FPS)

    def get_state(self):
        next_pipe_pos = \
            [pipe.midtop for pipe in self.pipe_list if pipe.midtop[0] > self.player_rect.right][0]
        next_pipe_distance = next_pipe_pos[0] - self.player_rect.right
        state = [self.player_rect.centery, BIRD_VELOCITY, next_pipe_distance, next_pipe_pos[1]]

        return state
