
import random
import pygame


class GameResultType:
    WIN = 'win'
    LOSE = 'lose'
    CONTINUE = 'continue'


class Player(pygame.sprite.Sprite):
    """
    Represents the Player in the game.

    Attributes
    ----------
    s_width : int
        Screen width
    s_height : int
        Screen height
    width : int
        Player's width
    height : int
        Player's height
    color : tuple of int
        Player's color in RGB
    speed : float
        Player's movement speed
    rect : pygame.Rect
        Rectangular area representing Player's position and dimensions
    """

    def __init__(self, screen_size, color: tuple[int, int, int], speed: float = 0.5):
        """
        Initialize the Player with given screen size, color and speed.

        Parameters
        ----------
        screen_size : tuple of int
            Screen size in (width, height)
        color : tuple of int
            Player's color in RGB
        speed : float (optional)
            Player's movement speed, default is 0.5
        """
        super().__init__()
        self.s_width, self.s_height = screen_size
        self.width, self.height = self.s_width // 10, self.s_height // 30
        self.color = color
        self.speed = speed
        self.rect = self._calculate_initial_rect()
        self.floatx = float(self.rect.x)

    def _calculate_initial_rect(self):
        """
        Calculate initial position and dimensions of the Player.

        Returns
        -------
        pygame.Rect
            Rectangular area representing Player's initial position and dimensions
        """
        x = self.s_width // 2 - self.width // 2
        y = self.s_height - self.height
        return pygame.Rect(x, y, self.width, self.height)

    def reset(self):
        """
        Reset the Player's position to initial position.
        """
        self.rect.topleft = self._calculate_initial_rect().topleft
        self.floatx = float(self.rect.x)

    def get_pos(self):
        """
        Calculate Player's central position with respect to x-axis.

        Returns
        -------
        int
            Player's central position
        """
        return self.rect.centerx

    def draw(self, surface: pygame.Surface):
        """
        Draw the Player on given surface.

        Parameters
        -----------
        surface : pygame.Surface
            Surface to draw the Player on
        """
        pygame.draw.rect(surface, self.color, self.rect)

    def move(self, direction=None):
        """
        Moves the Player based on provided direction or keyboard keys.

        Parameters
        ----------
        direction : str, optional
            Direction to move the Player in, default is None (keyboard input)

        Returns
        -------
        str
            Actual direction Player is moved in
        """
        direction = direction or self._get_direction_based_on_key()
        self._move_based_on_direction(direction)
        return direction

    @staticmethod
    def _get_direction_based_on_key():
        """
        Get direction of movement based on keyboard keys.

        Returns
        -------
        str
            Direction of movement: 'right', 'left' or 'still'
        """
        key = pygame.key.get_pressed()
        if key[pygame.K_RIGHT] and not key[pygame.K_LEFT]:
            return 'right'
        elif key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
            return 'left'
        else:
            return 'still'

    def _move_based_on_direction(self, direction):
        """
        Move the Player based on provided direction.

        Parameters
        ----------
        direction : str
            Direction of movement: 'right', 'left' or 'still'
        """
        if direction == 'right' and self.rect.right < self.s_width:
            self.floatx += self.speed
        elif direction == 'left' and self.rect.x > 0:
            self.floatx -= self.speed

        self.rect.x = int(self.floatx)


class Ball(pygame.sprite.Sprite):
    def __init__(self, screen_size: tuple[int, int], color: tuple[int, int, int],
                 speed: float = 0.25):
        super().__init__()
        self.color = color
        self.speed = speed
        self.s_width, self.s_height = screen_size
        self.radius = self.s_width // 40
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        self.floaty = 0
        self.reset()

    def reset(self):
        self.rect.centery = self.radius
        self.rect.centerx = random.choice(range(self.radius, self.s_width - self.radius, 1))
        self.floaty = float(self.rect.y)

    def get_pos(self):
        return self.rect.centerx

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def move(self):
        self.floaty += self.speed
        self.rect.y = int(self.floaty)

    def check_win_or_loss(self, player: Player):
        if self.rect.colliderect(player.rect):  # Win
            return GameResultType.WIN
        elif self.rect.bottom >= self.s_height:  # Lose
            return GameResultType.LOSE

        return GameResultType.CONTINUE
