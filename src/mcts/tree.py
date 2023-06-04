from src.agents.agent import Agent
from src.mcts.node import Node

VIRTUAL_LOSS = 1


class Tree:
    """ Monte Carlo Tree.

    Parameters:
        root: Node or Game. Root state of the tree. You can pass a Node object
        with a Game as state or directly the game (it will make the Node).
    """

    def __init__(self, root):
        if type(root) is Node:
            self.root = root
        else:
            self.root = Node(root.get_copy())

        self.root.visits = 1

    def search_move(self, agent, max_iters=200, verbose=False, noise=True, ai_move=False):
        """ Explores and selects the best next state to choose from the root
        state

        Parameters:
            agent: Player. Agent which will be used in the simulations against stockfish (the neural network).
            max_iters: int. Number of interactions to run the algorithm.
            verbose: bool. Whether to print the search status.
            noise: bool. Whether to add Dirichlet noise to the calc policy.
            ai_move: bool. Whether to return the move that AI will make after
            our best move
        """
        pass

    def explore_tree(self, node, agent, verbose=False):
        pass

    def select(self, node, agent):
        pass

    def expand(self, node, agent=None):
        pass

    def simulate(self, node: Node, agent: Agent):
        pass

    def backprop(self, node: Node, value: float, remove_vloss=False):
        pass

    def compute_policy(self, node: Node, noise=True):
        pass
