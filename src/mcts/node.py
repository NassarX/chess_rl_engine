import numpy as np

from src.envs.game import Game
from threading import Lock

VIRTUAL_LOSS = 1


class Node:
    """ Node from a Monte Carlo Tree.

    Attributes:
        state: Game. Game in a certain state.
        children: Array. Possible game states after applying the legal moves to
        the current state.
        parent: Node. Parent state of the current game.
        value: float. Expected reward of this node.
        visits: int. Number of times the node has been visited
        prior: float.
    """

    def __init__(self, state: Game, parent=None):
        self.state = state
        self.children = []
        self.unexpanded_actions = state.get_legal_moves()
        self.parent = parent
        self.value = 0
        self.visits = 0
        self.prior = 1
        self.vloss = 0
        self.lock = Lock()

    @property
    def is_leaf(self):
        return len(self.children) == 0

    @property
    def is_fully_expanded(self):
        return len(self.unexpanded_actions) == 0

    @property
    def is_terminal_state(self):
        return self.state.get_result() is not None

    @property
    def is_root(self):
        return self.parent is None

    def pop_unexpanded_action(self):
        return self.unexpanded_actions.pop()

    def get_ucb1(self):
        """ returns the UCB1 metric of the node. """
        C = 2
        value = 0
        if self.visits == 0:
            value = 99999999999  # Infinite to avoid division by 0
        else:
            # Vanilla MCTS
            # Return ucb1 score = vi + c * sqrt(log(N)/ni)
            value = self.value / self.visits + C * \
                    np.sqrt(np.log(self.parent.visits) / self.visits)
        return value

    def get_value(self):
        """Returns the Q + U for the node using the prior probabilities
        given by the neural network.
            U = C*Prior*sqrt(sum(son.visitis))/1+self.visits
            Q = Expected value/visits ((mean value of its children))
        Being C a constant which makes the U (exploration part of the
        equation) more important.
        """
        C = 10
        value = 0
        if self.is_root:
            value = 99999999999  # Infinite to avoid division by 0
        else:
            value = (self.value / (1 + self.visits)) + \
                    C * self.prior * \
                    (np.sqrt(np.sum([c.visits for c in self.children])) / (1 + self.visits))  # noqa: E501
        return value - self.vloss

    def get_best_child(self):
        """Get the best child of this node.
        Returns:
            best: Node. Child with the max. PUCT value.
        """
        best = np.argmax([c.get_value() for c in self.children])
        return self.children[best]
