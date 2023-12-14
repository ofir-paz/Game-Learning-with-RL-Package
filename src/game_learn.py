# This is a sample Python script.

import sys
import pickle
from games.ball_game.ball_game import BallGame
from AI_Types.AI_supervised import train_ai
from AI_Types.AI_DQL import train_qnet
from AI_Types.AI_evolution import train_neat

S_WIDTH = 800
S_HEIGHT = 600


def main():
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'save':
            game = BallGame((S_WIDTH, S_HEIGHT))
            game.reset(collect_data=True)
            infos, actions = game.get_data()
            save_infos_actions(infos, actions, sys.argv[2])

        elif sys.argv[1] == 'train':
            infos, actions = load_infos_actions(sys.argv[2])
            save_ai(infos, actions, sys.argv[3])

        elif sys.argv[1] == 'play':
            game = BallGame((S_WIDTH, S_HEIGHT))
            game.reset_game(save_fitness=False)
            game.game_loop()

        elif sys.argv[1] == 'ai':
            ai = load_ai(sys.argv[2])

            def predict_func(*args, **kwargs):
                outputs = ai.activate(*args, **kwargs)

                # Return index of the maximum.
                return outputs.index(max(outputs))

            # Assign the predict function (that is what the game is using)
            ai.predict = predict_func
            game = BallGame((S_WIDTH, S_HEIGHT))
            game.reset_game(game_title='Ai playing', game_speed=0.4, save_fitness=False, ai=ai)
            game.game_loop()

        elif sys.argv[1] == 'qlearn':
            train_qnet((S_WIDTH, S_HEIGHT), num_episodes=30, gamma=0.9,
                       eps_end=0, eps_decay=0.93)

        elif sys.argv[1] == 'NEAT':
            train_neat(sys.argv[3], num_generations=300, screen_size=(S_WIDTH, S_HEIGHT),
                       display_game=True, path_for_ai=sys.argv[2])

    else:
        print("Enter one of the options: save; train; play; ai; q-learn")


def save_infos_actions(infos, actions, filename):
    """
    Save the given infos and actions to a file using pickle.

    :param infos: The infos to save.
    :param actions: The actions to save.
    :param filename: The name of the file to save to.
    :return: None
    """
    with open(filename + ".pickle", 'wb') as f:
        # Put them in the file
        pickle.dump((infos, actions), f)


def load_infos_actions(filename):
    """
    Load Infos and Actions from Pickle File

    This method loads the information and action data from a pickle file.
    The pickle file should contain a tuple of two variables: infos and actions.

    :param filename: The name of the pickle file to load data from. Do not include the file extension.
    :return: A tuple containing the loaded infos and actions.

    :Example:

    load_infos_actions("data") -> (infos, actions)
    """
    with open(filename + ".pickle", 'rb') as f:
        # Load the variables
        infos, actions = pickle.load(f)

    return infos, actions


def save_ai(infos, actions, filename):
    ai = train_ai(infos, actions, S_WIDTH, lr=0.01, num_epochs=50, print_cost=True, print_stride=5)
    with open(filename + ".pickle", 'wb') as f:
        # Put AI in the file
        pickle.dump(ai, f)


def load_ai(filename):
    with open(filename + ".pickle", 'rb') as f:
        # Load AI from the file
        ai = pickle.load(f)

    return ai


if __name__ == '__main__':
    main()
