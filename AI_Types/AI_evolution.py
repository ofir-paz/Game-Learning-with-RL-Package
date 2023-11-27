
import random
import neat
import pickle
from games.ball_game.ball_game import BallGame

generation = 0


def train_neat(config_file, num_generations: int = 100, screen_size: tuple[int, int] = (800, 600),
               display_game: bool = True, path_for_ai: str | None = None):
    # Create the game instance
    game = BallGame(screen_size)

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    # Create core evolution algorithm class
    p = neat.Population(config)

    # Create reported
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    def predict_func(*args, **kwargs):
        outputs = neat.nn.FeedForwardNetwork.activate(*args, **kwargs)

        # Return index of the maximum.
        return outputs.index(max(outputs))

    # Assign the predict function (that is what the game is using)
    neat.nn.FeedForwardNetwork.predict = predict_func

    # Run NEAT
    p.run(run_generation, num_generations, game=game, display_game=display_game)
    game.kill()

    best_ai = neat.nn.FeedForwardNetwork.create(p.best_genome, config)
    save_ai(best_ai, path_for_ai)


def run_generation(genomes, config, game: BallGame, display_game: bool = True):
    reset_generation(game, genomes, config, display_any_game=display_game)
    eval_fitness(game, genomes)


def eval_fitness(game: BallGame, genomes):
    game.game_loop()

    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = game.fitnesses[i]


def reset_generation(game: BallGame, genomes, config, display_any_game: bool = True):
    nets = []
    global generation
    generation += 1  # Increment generation counter
    genome_to_show = random.randint(0, len(genomes)-1)

    for i, (genome_id, genome) in enumerate(genomes):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0.

        show_game = i == genome_to_show and display_any_game
        game.reset_game(i, f"Generation: {generation} Genome: {i}", game_speed=1,
                        show_game=show_game, save_fitness=True, ai=nets[i])


def save_ai(ai, path_for_ai: str | None = None):
    if path_for_ai:
        with open(path_for_ai + ".pickle", 'wb') as f:
            pickle.dump(ai, f)
