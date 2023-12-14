"""

"""

import pygame
from games.ball_game.ball_game_sprites import Player, Ball

# Define some colors.
GREY = (128, 128, 128)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

_ACTION_ENCODER = {'still': 0, 'right': 1, 'left': 2}
_ACTION_DECODER = {0: 'still', 1: 'right', 2: 'left'}


class GameResultType:
    WIN = 'win'
    LOSE = 'lose'
    CONTINUE = 'continue'


class BallGame:
    """
    Class representing a ball game.

    Attributes:
        STATE_FEATURES (int): Number of state features.
        NUM_ACTIONS (int): Number of possible actions.

    Args:
        screen_size (tuple[int, int]): Size of the game screen.

    Methods:
        __init__(self, screen_size: tuple[int, int], game_speed=0.1, ai: AI = None)
        reset(self, title: str = 'Ball Game', human_player: bool = True, collect_data: bool = False)
        kill(self)
        __game_loop(self)
        __game_frame(self, direction: str = None) -> tuple
        __collect_data(self, info: list[float, float], direction: str)
        make_action(self, action: int)
        get_state(self) -> list[float, float]
        get_reward(self, last_action) -> float
        is_lose(self) -> bool
        get_data(self) -> tuple
    """
    STATE_FEATURES = 2
    NUM_ACTIONS = 3

    def __init__(self, screen_size: tuple[int, int] = (800, 600),
                 collect_data: bool = False):
        """
        The `__init__` method initializes an instance of the `ball_game` class.

        """

        pygame.init()
        self.game_list = []
        self.screen_size = screen_size

        self.infos = []  # This is train_X.
        self.actions = []  # This is train_Y.
        self.save_fitnesses = {}  # Reset fitnesses flag dictionary
        self.fitnesses = {}  # Reset fitnesses values dictionary

        # Initialize agents and sprites dictionary
        self.agents = {}
        self.players = {}
        self.balls = {}

        self.win_or_loses = {}  # Win or lose state flag
        self.collect_data = collect_data  # Data collection flag.
        self.displayed_game = None  # None displayed game at the moment.

        # Initialize the screen variable.
        self.screen = None

    def reset_game(self, game_name: int | str = "Ball Game", game_title: str = "Ball Game",
                   game_speed: float = .5, show_game: bool = True, save_fitness: bool = True,
                   ai=None):
        """
        """

        if show_game:
            if self.screen is None:
                self.screen = pygame.display.set_mode(self.screen_size)
            self.displayed_game = game_name
            pygame.display.set_caption(game_title)
            self.screen.fill(GREY)

        if game_name not in self.game_list:
            self.__initialize_game(game_name, game_speed)

        # Save the agent and reset the sprites.
        self.agents[game_name] = ai
        self.players[game_name].reset()
        self.balls[game_name].reset()
        self.win_or_loses[game_name] = GameResultType.CONTINUE

        self.save_fitnesses[game_name] = save_fitness  # Save the flag
        self.fitnesses[game_name] = 0

        # Add game features.
        if show_game:
            pygame.display.flip()

    def __initialize_game(self, game_name: str, game_speed: float = 0.5):
        self.players[game_name] = Player(self.screen_size, BLUE, game_speed)
        self.balls[game_name] = Ball(self.screen_size, YELLOW, game_speed/2)
        self.game_list.append(game_name)

    @staticmethod
    def kill():
        """
        Terminate the game and close the pygame window.

        :return: None
        """

        pygame.quit()

    def game_loop(self):
        """
        Main loop for the ball game.

        :return: None
        """

        while True:
            all_lose = True
            for game, win_or_lose in self.win_or_loses.items():
                # Make a game frame if the game is not lost
                if win_or_lose is not GameResultType.LOSE:
                    all_lose = False
                    info, direction = self.__game_frame(game)
                    # Save the state if collect_data is True.
                    if self.collect_data is True:
                        self.__collect_data(info, direction)

                    if self.save_fitnesses[game] is True:
                        self.fitnesses[game] += self.get_reward(game, _ACTION_ENCODER[direction])
                        if self.fitnesses[game] > 50_000:
                            self.win_or_loses[game] = GameResultType.LOSE

            if all_lose:
                break

    def __get_direction(self, game: str, existing_direction: str | None = None) -> str | None:
        """
        Determine the direction for the player to move.
        If an existing direction is given, use that. If an AI is present, use the AI's prediction.
        Otherwise, no direction is returned.

        :param existing_direction: The current direction if exists
        :return: The direction for the player to move.
        """
        if existing_direction is not None:
            return existing_direction
        elif self.agents[game] is not None:
            info = self.get_state(game)
            return _ACTION_DECODER[self.agents[game].predict(info)]
        else:
            return None

    def __game_frame(self, game: str, direction: str | None = None):
        """
        Execute a single game frame. Check for QUIT event,  process player and ball movements,
        update the display, and check for win or loss.

        :param direction: A specific direction to move. If None, direction will be determined by AI
                or no movement.
        :return: The game state, the direction of movement, and the result of the game (win, lose,
                or continue).
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.kill()
                exit()

        # Single frame logic.
        info = self.get_state(game)
        if self.win_or_loses[game] == GameResultType.WIN:  # Handle win condition.
            self.balls[game].reset()
        direction = self.__get_direction(game, direction)
        # Save direction again here because Player.move() handles keyboard interaction.
        direction = self.players[game].move(direction)
        self.balls[game].move()
        self.win_or_loses[game] = self.balls[game].check_win_or_loss(self.players[game])

        # Single frame graphics
        if game is self.displayed_game:
            self.screen.fill(GREY)
            self.players[game].draw(self.screen)
            self.balls[game].draw(self.screen)
            pygame.display.flip()

        return info, direction

    def __collect_data(self, info: list[float, float], direction: str):
        self.infos.append((info[0] / self.screen_size[0], info[1] / self.screen_size[0]))
        self.actions.append(_ACTION_ENCODER[direction])

    def make_action(self, game_name: str, action: int):
        # Decode the action to a direction
        direction = _ACTION_DECODER[action]

        info, direction = self.__game_frame(game_name, direction)

        if self.collect_data is True:
            self.__collect_data(info, direction)

    def get_state(self, game: str):
        return [self.players[game].get_pos() / self.screen_size[0],
                self.balls[game].get_pos() / self.screen_size[0]]

    def get_reward(self, game: str, last_action: int):
        if self.win_or_loses[game] == GameResultType.WIN:
            reward = 100.

        elif self.win_or_loses[game] == GameResultType.LOSE:
            reward = -100.

        else:
            player_pos, ball_pos = self.get_state(game)
            # ADD: calc reward based on the last action.
            # last_direction = action_decoder[last_action]
            # good_direction =
            reward = 1/(0.25 + abs(player_pos - ball_pos))

        return reward

    def is_lose(self, game: str):
        return self.win_or_loses[game] == GameResultType.LOSE

    def get_data(self):
        return self.infos, self.actions
