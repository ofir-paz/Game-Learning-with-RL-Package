"""

"""

import time
import random
from collections import namedtuple, deque
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from games.ball_game.ball_game import BallGame
from AI_Types.AI import AI


GAME_NAME = 'q-learn'
ENOUGH_POINTS = 50_000
MEMORY_SIZE = 100_000       # size of memory buffer
NUM_STEPS_FOR_UPDATE = 4    # perform a learning update every C time steps
SAMPLE_SIZE = 128           # Size of sample
TAU = 0.99                  # Update Q target function softly
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state'])


class Memory(deque):
    def get_sample(self):
        sample_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        experiences = random.sample(self, SAMPLE_SIZE)
        sample = list(map(lambda var: torch.tensor(var, device=sample_device), zip(*experiences)))

        return sample


def train_qnet(screen_size, num_episodes=300, lr=1e-3, gamma=0.995,
               epsilon=0.98, eps_end=0.005, eps_decay=0.96, print_learning_curve=True):
    mem_buff = Memory(maxlen=MEMORY_SIZE)
    game = BallGame(screen_size)
    q_net_target = AI(game.STATE_FEATURES, game.NUM_ACTIONS)
    q_net = AI(game.STATE_FEATURES, game.NUM_ACTIONS)
    average_point_history = []

    criterion = nn.SmoothL1Loss()
    optimizer = torch.optim.Adam(q_net.parameters(), lr=lr)

    for episode in range(num_episodes):
        total_points = 0.
        num_timesteps = 0

        game.reset_game(GAME_NAME, f'Q-Episode: {episode + 1}', game_speed=2.,
                        show_game=True)
        while True:
            state, action, reward, next_state, is_done = perform_time_step(q_net, game, epsilon)
            experience = Experience(state, action, reward, next_state)
            mem_buff.append(experience)

            if is_need_update(mem_buff, num_timesteps):
                learning_step(q_net_target, q_net, mem_buff, gamma, criterion, optimizer)

            total_points += reward
            num_timesteps += 1

            if num_timesteps % 500 == 0:
                print(f"\r[Episode: {episode+1}] Time step: {num_timesteps+1}", end='')

            # Episode finished
            if is_done or total_points > ENOUGH_POINTS:
                time.sleep(0.2)
                break

        epsilon = get_new_eps(epsilon, eps_decay, eps_end)
        average_point_history.append(total_points/num_timesteps)
        print()
        if total_points > ENOUGH_POINTS:
            print(f"Learning terminated! Successfully learned the game in {episode+1} episodes!")
            break

    plot_learning_curve(average_point_history)
    game.kill()


def perform_time_step(q_net: AI, game: BallGame, epsilon: float):
    state = game.get_state(GAME_NAME)
    action = choose_action(state, game.NUM_ACTIONS, q_net, epsilon)
    game.make_action(GAME_NAME, action)
    reward = game.get_reward(GAME_NAME, action)
    next_state = game.get_state(GAME_NAME)
    is_done = game.is_lose(GAME_NAME)

    return state, action, reward, next_state, is_done


def choose_action(state, num_actions: int, q_net: AI, epsilon: float):
    if epsilon < np.random.uniform():
        action = q_net.predict(state)
    else:
        action = np.random.choice(num_actions)

    return action


def get_new_eps(epsilon: float, eps_decay=0.995, eps_end=0.01):
    return max(epsilon * eps_decay, eps_end)


def is_need_update(mem_buff: Memory, iteration: int):
    return len(mem_buff) > SAMPLE_SIZE and iteration % NUM_STEPS_FOR_UPDATE == 0


def learning_step(q_net_target, q_net, mem_buff, gamma, criterion, optimizer):
    sample = mem_buff.get_sample()
    y_targets = evaluate_targets(q_net_target, sample, gamma)
    y_predicts = evaluate_predicts(q_net, sample)

    # backward + optimize
    optimizer.zero_grad()
    loss = criterion(y_predicts, y_targets)
    loss.backward()
    optimizer.step()

    soft_update_target(q_net_target, q_net)


def evaluate_targets(q_net_target: AI, sample, gamma=0.995):
    _, _, rewards, next_states = sample

    with torch.no_grad():
        max_qsa, _ = torch.max(q_net_target(next_states), dim=1)

    y_targets = rewards + (next_states != 'lose') * gamma * max_qsa

    return y_targets


def evaluate_predicts(q_net: AI, sample):
    states, actions, _, _ = sample
    y_predicts = q_net(states)[torch.arange(SAMPLE_SIZE), actions]
    return y_predicts


def soft_update_target(q_net_target: AI, q_net: AI):
    # Soft update of the target network's weights
    # θ′ ← τ θ + (1 −τ )θ′
    q_net_target_dict = q_net_target.state_dict()
    q_net_dict = q_net.state_dict()

    for key in q_net_target_dict:
        q_net_target_dict[key] = q_net_target_dict[key] * TAU + (1-TAU) * q_net_dict[key]

    q_net_target.load_state_dict(q_net_target_dict)


def plot_learning_curve(average_point_history, rolling_window=5):
    rh = average_point_history
    xs = np.arange(len(average_point_history))
    df = pd.DataFrame(rh)
    rolling_mean = df.rolling(rolling_window).mean()

    plt.figure(figsize=(8, 5), facecolor='white')

    plt.plot(xs, rh, linewidth=1, color='cyan')
    plt.plot(xs, rolling_mean, linewidth=2, color='magenta')

    text_color = 'black'

    ax = plt.gca()
    ax.set_facecolor('black')
    plt.grid()
    plt.title("Total Point History", color=text_color, fontsize=30)
    plt.xlabel('Episode', color=text_color, fontsize=20)
    plt.ylabel('Total Points', color=text_color, fontsize=20)
    ax.tick_params(axis='x', colors=text_color)
    ax.tick_params(axis='y', colors=text_color)
    plt.show()
