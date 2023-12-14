
import random
import neat
import pickle

generation = 0


def train_neat(config_file, game_class, num_generations: int = 100, path_for_ai: str | None = None):
    # Create the game instance
    game = game_class()

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
    p.run(run_generation, num_generations, game=game)
    game.kill()

    best_ai = neat.nn.FeedForwardNetwork.create(p.best_genome, config)
    save_ai(best_ai, path_for_ai)


def run_generation(genomes, config, game):
    reset_generation(game, genomes, config)
    eval_fitness(game, genomes)


def eval_fitness(game, genomes):
    game.game_loop()

    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = game.fitnesses[get_name_formate(i+1)]


def reset_generation(game, genomes, config, display_any_game: bool = True):
    nets = []
    global generation
    generation += 1  # Increment generation counter

    for i, (genome_id, genome) in enumerate(genomes):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0.

        game.reset_game(get_name_formate(genome_num=i+1), ai=nets[i])


def save_ai(ai, path_for_ai: str | None = None):
    if path_for_ai:
        with open(path_for_ai + ".pickle", 'wb') as f:
            pickle.dump(ai, f)


def get_name_formate(genome_num: int):
    return f"Genome: {genome_num}"
