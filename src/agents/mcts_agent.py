from src.mcts.self_play import SelfPlayTree
from src.agents.agent import Agent
from src.envs.game import Game


class MCTSAgent(Agent):
    """ AI agent which will play chess using the Monte Carlo Tree Search.

    Params:
        color: bool, Color of the player.
     """

    def __init__(self, color):
        super().__init__(color)

    def best_move(self, game: Game, max_iters=900, verbose=False) -> str:
        """ Finds and returns the best possible move (UCI encoded)

        Parameters:
            game: Game. Current game before the move of this agent is made.
            max_iters: The max number of iterations of the MCTS algorithm.
            verbose: Whether to print the search information.

        Returns:
            str. UCI encoded movement.
        """
        best_move = '00000'  # Null move
        if game.get_result() is None:
            current_tree = SelfPlayTree(game)
            best_move = current_tree.search_move(self, max_iters=max_iters, verbose=verbose)
            #print("Best move: ", best_move)

        return best_move

    def get_copy(self):
        """ Returns a copy of this agent """
        return MCTSAgent(self.color)