
from flappy_bird import FlappyBird
from src.AI_Types.AI_evolution import train_neat
import pickle


def test():
    train_neat('../../AI_Types/flappy_bird_neat_configs.txt', FlappyBird,
              100, 'ai')
    """""with open('ai.pickle', 'rb') as f:
        ai = pickle.load(f)

    fp = FlappyBird()
    fp.reset_game(name='test', ai=ai)
    fp.game_loop()
    fp.kill()
    """""


if __name__ == '__main__':
    test()
