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


def eval_network(net, num_games=5, penalty_weight=0.1, verbose=False):
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
if False:
    winner_player = Player(winner_net.activate, verbose=True)
    final_board = Board()
    score, penalty = winner_player.run_game(final_board)
    print(f"final score: {score}, penalty: {penalty}")
else:
    fitness = eval_network(winner_net, verbose=True, penalty_weight=0)
    print(f"average score: {fitness}")
