import argparse
import multiprocessing
import pickle
import random
import sys

import gymnasium as gym
import neat

from gymnasium.spaces.utils import flatten

from . import visualize


def eval_genomes(genomes, config):
    """Fitness function wrapped for Population.run()."""
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)


def eval_genome(genome, config):
    """Fitness function wrapped for ParallelEvaluator."""
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    return eval_network(net, seed=config.random_seed)


def eval_network(net, num_games=5, seed=None):
    """Evaluate the fitness of the supplied neural network."""
    env = gym.make("bkdk/BKDK-v0")

    total_reward = 0
    for _ in range(num_games):
        observation, info = env.reset(seed=seed)
        seed = None
        terminated = truncated = False

        while not (terminated or truncated):
            inputs = flatten(env.observation_space, observation)
            outputs = net.activate(inputs)

            ranked_outputs = list(sorted(
                ((activation, index)
                 for index, activation in enumerate(outputs)),
                reverse=True))

            # Try each action in order, until either a) we performed a
            # legal move (reward > 0), in which case the board changed
            # and we need to re-run the net, or b) the episode
            # terminated or was truncated.
            for _, action in ranked_outputs:
                (observation,
                 reward,
                 terminated, truncated, info) = env.step(action)

                if terminated or truncated or reward > 0:
                    break

                # Penalize illegal moves.
                total_reward -= 1
            total_reward += reward

    env.close()
    return total_reward / num_games


class RandomSeedUpdater(neat.reporting.BaseReporter):
    def __init__(self, config):
        self._config = config

    def start_generation(self, generation):
        self._config.random_seed = random.randint(0, sys.maxsize)
        random.seed(self._config.random_seed)


def run(args):
    """Evolve a feed-forward neural network to play the game."""

    if args.num_workers is None:
        args.num_workers = multiprocessing.cpu_count()

    # Seed the random number generator, if requested.
    if args.random_seed is not None:
        random.seed(args.random_seed)

    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         args.config_filename)
    if args.population_size is not None:
        config.pop_size = args.population_size

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(RandomSeedUpdater(config))
    if not args.profile:
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(1))

    # Run the GA until max_generations or a solution is found.
    if args.num_workers == 1:
        ff = eval_genomes
    else:
        ff = neat.ParallelEvaluator(args.num_workers, eval_genome).evaluate
    winner = p.run(ff, args.max_generations)
    if args.profile:
        return

    # Save the winning genome.
    with open("winner.pkl", "wb") as fp:
        pickle.dump(winner, fp)

    # Run a game with the most fit genome.
    print("\nWinner:")
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    fitness = eval_network(winner_net)
    print(f"average score: {fitness}")

    # Visualize some things.
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="BKDK evolver")

    parser.add_argument("--max-generations", action="store",
                        help="halt the GA after MAX_GENERATIONS generations")
    parser.add_argument("--num-workers", action="store")
    parser.add_argument("--population-size", action="store",
                        help="override the configured population size")
    parser.add_argument("--profile", action="store_true",
                        help="run in Python profiler")
    parser.add_argument("--random-seed", action="store",
                        help="seed Python's random number generator")
    parser.add_argument("config_filename",
                        help="NEAT-Python configuration file")
    args = parser.parse_args()

    if args.profile:
        import cProfile
        if args.max_generations is None:
            args.max_generations = 2
        if args.num_workers is None:
            args.num_workers = 1
        if args.population_size is None:
            args.population_size = 10
        if args.random_seed is None:
            args.random_seed = 186282
        return cProfile.runctx(
            "run(args)",
            globals(), locals(),
            filename="evolve.stats")

    return run(args)
