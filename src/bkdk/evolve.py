import argparse
import multiprocessing
import pickle
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
    return eval_network(net)


def eval_network(net, num_games=5):
    """Evaluate the fitness of the supplied neural network."""
    env = gym.make("bkdk/BKDK-v0")

    total_reward = 0
    for _ in range(num_games):
        observation, info = env.reset()  # XXX seed?
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


def run(config_filename, max_generations=None, num_workers=None):
    """Evolve a feed-forward neural network to play the game.

    :param config_filename: NEAT-Python configuration file.
    :param max_generations: If not None, halt the genetic algorithm
                            after this many generations.  If None, run
                            until a solution is found or extinction
                            occurs.
    :param num_workers: Number of worker processes to parallelize
                        genome evaluation across.  Defaults to one
                        per CPU.
    """
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()

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

    # Run the GA until max_generations or a solution is found.
    if num_workers == 1:
        ff = eval_genomes
    else:
        ff = neat.ParallelEvaluator(num_workers, eval_genome).evaluate
    winner = p.run(ff, max_generations)

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

    parser = argparse.ArgumentParser(description="BKDK evolver")
    parser.add_argument("--profile", action="store_true")
    parser.add_argument("configfile")
    args = parser.parse_args()

    if args.profile:
        import cProfile
        return cProfile.runctx(
            "run(args.configfile, max_generations=2, num_workers=1)",
            globals(), locals(),
            filename="evolve.stats")

    return run(args.configfile)
