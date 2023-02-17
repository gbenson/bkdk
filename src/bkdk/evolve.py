import neat
import pickle
from .board import Board
from .player import Player


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        genome.fitness = 0
        for _ in range(5):
            genome.fitness += eval_network(net)


def eval_network(net):
    player = Player(net.activate)
    fitness = 0
    for _ in range(5):  # XXX make configurable?
        board = Board()
        score, penalty = player.run_game(board)
        fitness += score
        fitness -= penalty / 10  # XXX make configurable?
    return fitness


# Load configuration.
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     "neat.cfg")

# Create the population, which is the top-level object for a NEAT run.
p = neat.Population(config)

# Add a stdout reporter to show progress in the terminal.
p.add_reporter(neat.StdOutReporter(False))

# Run until a solution is found.
winner = p.run(eval_genomes)

# Save the winning genome.
with open("winner.pkl", "wb") as fp:
    pickle.dump(winner, fp)

# Run a game with the most fit genome.
print('\nWinner:')
winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
eval_network(winner_net)
