import multiprocessing
import neat
import pickle
import sys
from . import visualize
from .board import Board
from .player import Player


def eval_genomes(genomes, config):
    """Fitness function wrapped for Population.run()."""
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)


def eval_genome(genome, config):
    """Fitness function wrapped for ParallelEvaluator."""
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    return eval_network(net)


def eval_network(net, num_games=5, penalty_weight=0.1, verbose=False):
    """Evaluate the fitness of the supplied neural network."""
    player = Player(net.activate)
    fitness = 0
    for _ in range(num_games):
        board = Board()
        score, penalty = player.run_game(board)
        if verbose:
            print(f"score: {score}, penalty: {penalty}")
        fitness += score
        fitness -= penalty * penalty_weight
    return fitness / num_games


def run(config_filename):
    """Evolve a feed-forward neural network to play the game."""

    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_filename)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    # Run until a solution is found.
    pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), eval_genome)
    winner = p.run(pe.evaluate)

    # Save the winning genome.
    with open("winner.pkl", "wb") as fp:
        pickle.dump(winner, fp)

    # Run a game with the most fit genome.
    print("\nWinner:")
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    fitness = eval_network(winner_net, verbose=True, penalty_weight=0)
    print(f"average score: {fitness}")

    # Visualize some things.
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) == 1:
        return run(*args)

    print("usage: evolve CONFIGFILE", file=sys.stderr)
    sys.exit(1)
