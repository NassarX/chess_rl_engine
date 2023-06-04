from src.envs.game import Game

import random
import numpy as np


class RandomSimulation(object):
    """ Simulation of an agent against Other opponent """

    def __init__(self, game: Game):
        """ Parameters:
                game: Game. The game to simulate.
        """
        self.game = game

    def run(self, max_moves=100, repetitions=1):
        """ Runs the game simulation for max_moves """
        results = []
        for i in range(repetitions):
            n_mov = 0
            # While the game is not finished and the nb of moves is low
            while n_mov < max_moves and self.game.get_result() is None:
                legal_moves = self.game.get_legal_moves()
                if legal_moves:
                    self.game.move(random.choice(legal_moves))
                    n_mov += 1
                else:
                    break  # No legal moves available, exit the loop

            result = self.game.get_result()
            if result is not None:
                results.append(result)
            else:
                results.append(0)  # Draw

        return np.mean(results)
