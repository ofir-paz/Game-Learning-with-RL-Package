"""
This is my attempt at re-creating the iconic flappy bird game which took
the internet by storm in early 2013.
"""

import pygame
from setup.constants import *
import random


class FlappyBird:
    def __init__(self):
        # Pygame Initialisation
        pygame.init()
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        self.bird_names = []
        self.agent_names = self.bird_names
        self.scores = {}
        self.fitnesses = {}
        self.high_score = 0
        self.cans_score = {}
        self.games_active = {}
        self.ai_agents = {}

        pygame.display.set_caption("Flappy Bird")
        gameicon = pygame.image.load('assets/scene/gameicon.png').convert_alpha()
        pygame.display.set_icon(gameicon)
        self.clock = pygame.time.Clock()

        # Rendering game scene
        background_scene = pygame.image.load('assets/scene/background.png').convert()
        self.background_scene = pygame.transform.scale(background_scene, (WIDTH, HEIGHT))
        floor_scene = pygame.image.load('assets/scene/floor.png').convert()
        self.floor_scene = pygame.transform.scale2x(floor_scene)

        # Loading fonts
        self.game_font = pygame.font.Font('assets/fonts/flappy.ttf', 40)

        # Loading bird sprites
        bird_downflap = pygame.transform.scale2x(
            pygame.image.load('assets/sprites/bird_down.png').convert_alpha())
        bird_midflap = pygame.transform.scale2x(
            pygame.image.load('assets/sprites/bird_mid.png').convert_alpha())
        bird_upflap = pygame.transform.scale2x(
            pygame.image.load('assets/sprites/bird_up.png').convert_alpha())
        self.bird_frames = [bird_downflap, bird_midflap, bird_upflap]
        self.bird_indexes = {}
        self.bird_sprites = {}
        self.rotated_bird_sprites = {}
        self.bird_hitboxes = {}
        self.bird_velocities = {}

        # Loading game sounds
        self.flap_sound = pygame.mixer.Sound('assets/sounds/flap.ogg')
        self.clash_sound = pygame.mixer.Sound('assets/sounds/clash.ogg')
        self.score_sound = pygame.mixer.Sound('assets/sounds/score.ogg')

        # Game-over scene
        gameover_scene = pygame.image.load('assets/scene/onset.png').convert_alpha()
        self.gameover_scene = pygame.transform.scale2x(gameover_scene)
        self.gameover_rect = self.gameover_scene.get_rect(center=(262, 400))

        # Drawing pipe obstacles
        pipe_sprite = pygame.image.load('assets/sprites/pipe.png').convert()
        self.pipe_sprite = pygame.transform.scale2x(pipe_sprite)
        self.pipe_list = []
        self.SPAWNPIPE = pygame.USEREVENT
        pygame.time.set_timer(self.SPAWNPIPE, 1500)

        # Bird flap event
        self.BIRD_FLAP = pygame.USEREVENT + 1
        pygame.time.set_timer(self.BIRD_FLAP, 200)

    def reset_game(self, name: int | str = "FlappyBird", ai=None):

        if name not in self.bird_names:
            self.bird_names.append(name)
        self.ai_agents[name] = ai
        self.scores[name] = 0
        self.fitnesses[name] = 0
        self.cans_score[name] = True
        self.games_active[name] = True
        self.bird_indexes[name] = 0
        self.bird_sprites[name] = self.bird_frames[self.bird_indexes[name]]
        self.rotated_bird_sprites[name] = self.bird_frames[self.bird_indexes[name]]
        self.bird_hitboxes[name] = self.bird_sprites[name].get_rect(
            center=(100, random.gauss(400, 100)))
        self.bird_velocities[name] = 0

    def get_state(self, bird_name):
        state = [self.bird_hitboxes[bird_name].centery / HEIGHT,
                 self.bird_velocities[bird_name] / 6]

        pipe_state = (self.pipe_list[0].bottom + self.pipe_list[1].top)/(2 * HEIGHT) \
            if len(self.pipe_list) >= 2 else 0.5

        state.append(pipe_state)
        return state

    # Drawing dynamic floor
    def draw_floor(self):
        self.win.blit(self.floor_scene, (DYNAMIC_FLOOR, 700))
        self.win.blit(self.floor_scene, (DYNAMIC_FLOOR + 500, 700))

    # Drawing new pipe
    def create_pipe(self):
        random_pipe = random.choice(PIPE_HEIGHT)
        bottom_pipe = self.pipe_sprite.get_rect(midtop=(700, random_pipe))
        top_pipe = self.pipe_sprite.get_rect(midbottom=(700, random_pipe - 250))
        return bottom_pipe, top_pipe

    # Dynamic obstacles
    def move_pipe(self):
        for pipe in self.pipe_list:
            pipe.centerx -= 5
        self.pipe_list = [pipe for pipe in self.pipe_list if pipe.right > -50]

    # Rendering pipes
    def draw_pipe(self):
        for pipe in self.pipe_list:
            if pipe.bottom >= 800:
                self.win.blit(self.pipe_sprite, pipe)
            else:
                flip_pipe = pygame.transform.flip(self.pipe_sprite, False, True)
                self.win.blit(flip_pipe, pipe)

    # Collision detection
    def check_collision(self, bird_name):
        for pipe in self.pipe_list:
            if self.bird_hitboxes[bird_name].colliderect(pipe):
                self.clash_sound.play()
                #pygame.time.delay(300)
                self.cans_score[bird_name] = True
                return False
        if self.bird_hitboxes[bird_name].top <= -150 or self.bird_hitboxes[bird_name].bottom >= 700:
            self.clash_sound.play()
            #pygame.time.delay(300)
            self.cans_score[bird_name] = True
            return False
        return True

    # Animating bird
    def rotate_bird(self, bird_name):
        self.rotated_bird_sprites[bird_name] = pygame.transform.rotozoom(
            self.bird_sprites[bird_name], -self.bird_velocities[bird_name] * 3, 1)

    # Bird flap animation
    def bird_animation(self, bird_name):
        self.bird_sprites[bird_name] = self.bird_frames[self.bird_indexes[bird_name]]
        self.bird_hitboxes[bird_name] = self.bird_sprites[bird_name].get_rect(
            center=(100, self.bird_hitboxes[bird_name].centery))

    # Current game score
    def score_display(self):
        global WHITE
        if any(self.games_active.values()):
            score_surface = self.game_font.render(str(int(max(self.scores.values()))), True, WHITE)
            score_rect = score_surface.get_rect(center=(262, 100))
            self.win.blit(score_surface, score_rect)

        else:
            score_surface = self.game_font.render(f'Score: {int(max(self.scores.values()))}',
                                                  True, WHITE)
            score_rect = score_surface.get_rect(center=(262, 100))
            self.win.blit(score_surface, score_rect)

            HIGHSCORE_surface = self.game_font.render(
                f'High Score: {int(self.high_score)}', True, WHITE)
            HIGHSCORE_rect = score_surface.get_rect(center=(200, 685))
            self.win.blit(HIGHSCORE_surface, HIGHSCORE_rect)

    # High Score
    def update_score(self):
        self.high_score = max(self.scores.values()) if max(self.scores.values()) > self.high_score \
            else self.high_score

    # Enhanced Scoring System
    def pipe_score_check(self):
        # This function can have improved time performance.
        if self.pipe_list:
            for bottom_pipe, top_pipe in zip(self.pipe_list[::2], self.pipe_list[1::2]):
                for bird in self.bird_names:
                    if 95 < bottom_pipe.centerx < 105:
                        if self.cans_score[bird]:
                            self.scores[bird] += 1
                            self.fitnesses[bird] += 1000
                            self.score_sound.play()
                            self.cans_score[bird] = False
                    if (abs(self.bird_hitboxes[bird].centery -
                            (bottom_pipe.top + top_pipe.bottom)/2) < 150):
                        self.fitnesses[bird] += 1
                    else:
                        self.fitnesses[bird] -= 1

                if bottom_pipe.centerx < 0:
                    self.cans_score = {bird_name: True for bird_name in self.bird_names}

    def game_loop(self):
        global DYNAMIC_FLOOR, FPS
        # Game loop
        while True:
            # setting up game events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if any(self.games_active.values()):
                    for bird in self.bird_names:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            if self.games_active[bird] is True:
                                self.bird_velocities[bird] = 0
                                self.bird_velocities[bird] -= 6
                                self.flap_sound.play()

                        # Ai mechanism
                        elif self.ai_agents[bird] and self.games_active[bird] is True:
                            action = self.ai_agents[bird].predict(self.get_state(bird))
                            if action == 0:
                                self.bird_velocities[bird] = 0
                                self.bird_velocities[bird] -= 6
                                self.flap_sound.play()

                        # bird flap event
                        if event.type == self.BIRD_FLAP:
                            if self.bird_indexes[bird] < 2:
                                self.bird_indexes[bird] += 1
                            else:
                                self.bird_indexes[bird] = 0
                                self.bird_animation(bird)

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    for bird in self.bird_names:
                        self.reset_game(bird, self.ai_agents[bird])
                    self.pipe_list.clear()

                # spawning obstacles
                if event.type == self.SPAWNPIPE:
                    self.pipe_list.extend(self.create_pipe())

            self.win.blit(self.background_scene, (0, 0))

            if any(self.games_active.values()):
                for bird in self.bird_names:
                    if self.games_active[bird]:
                        # implementing bird physics
                        self.bird_velocities[bird] += GRAVITY
                        self.bird_hitboxes[bird].centery += self.bird_velocities[bird]
                        self.rotate_bird(bird)
                        self.win.blit(self.rotated_bird_sprites[bird], self.bird_hitboxes[bird])
                        self.games_active[bird] = self.check_collision(bird)

                # rendering obstacles
                self.move_pipe()
                self.draw_pipe()

                # updating score
                self.pipe_score_check()
                self.score_display()

            else:
                # game over scene with scores
                self.win.blit(self.gameover_scene, self.gameover_rect)
                self.update_score()
                self.score_display()
                if any(self.ai_agents.values()):
                    self.pipe_list.clear()
                    return

            # dynamic floor
            DYNAMIC_FLOOR -= 1
            self.draw_floor()
            if DYNAMIC_FLOOR <= -500:
                DYNAMIC_FLOOR = 0

            pygame.display.update()
            self.clock.tick(FPS)

    @staticmethod
    def kill():
        pygame.quit()
