import pygame
import random

SCREEN_SIZE = (800, 600)
PLAYER_SIZE = (50, 50)
PLATFORM_COLOR = (255, 0, 0)
POINTS_PER_PLATFORM = 10
STARTING_PLATFORMS = 20


class Player():
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2, *PLAYER_SIZE)
        self.y_velocity = 0
        self.on_ground = False

    def jump(self):
        if self.on_ground:
            self.y_velocity = -10
            self.on_ground = False

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.move_ip(-5, 0)
        if keys[pygame.K_RIGHT]:
            self.rect.move_ip(5, 0)

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_SIZE[0]: self.rect.right = SCREEN_SIZE[0]

        self.y_velocity += 0.5
        self.rect.move_ip(0, self.y_velocity)

        for plat in [p for p in platforms if p.rect.colliderect(self.rect)]:
            if self.rect.bottom < plat.rect.bottom:
                self.rect.bottom = plat.rect.top
                self.y_velocity = 0
                self.on_ground = True
                return True
        return False


class Platform():
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)


class Platformer():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.player = Player()
        self.platforms = []
        self.score = 0
        self.platform_width = 100
        self.platform_spacing = 150
        self.generate_platforms(STARTING_PLATFORMS)

    def generate_platforms(self, num_platforms):
        for i in range(num_platforms):
            self.platforms.append(Platform(random.randint(0, SCREEN_SIZE[0] - self.platform_width),
                                           i * self.platform_spacing, self.platform_width, 20))

    def reset_game(self):
        self.player = Player()
        self.score = 0
        self.platforms.clear()
        self.platform_width = 100
        self.platform_spacing = 150
        self.generate_platforms(STARTING_PLATFORMS)

    def game_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
            self.screen.fill((255, 255, 255))

            on_platform = self.player.update(self.platforms)
            while self.platforms and self.platforms[0].rect.top > SCREEN_SIZE[1]:
                self.platforms.pop(0)
            if self.player.rect.top < 200 and len(self.platforms) * self.platform_spacing < \
                    SCREEN_SIZE[1]:
                self.generate_platforms(1)

            if on_platform and self.score % (POINTS_PER_PLATFORM * 20) == 0 and self.score != 0:
                self.platform_width = max(20, self.platform_width - 10)
                self.platform_spacing += 50

            for platform in self.platforms:
                pygame.draw.rect(self.screen, PLATFORM_COLOR, platform.rect)
                platform.rect.move_ip(0, 1)
                if platform.rect.colliderect(self.player.rect):
                    self.score += POINTS_PER_PLATFORM

            pygame.draw.rect(self.screen, (0, 0, 255), self.player.rect)

            self.screen.blit(self.font.render("Score: " + str(self.score), True, (0, 0, 0)),
                             (10, 10))

            pygame.display.flip()
            self.clock.tick(60)

    @staticmethod
    def kill(self):
        pygame.quit()
