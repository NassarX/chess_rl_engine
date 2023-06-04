import numpy as np
from src.envs.game import Game
from src.agents.agent import Agent
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer as timer

from src.mcts.simulation import RandomSimulation
from src.mcts.tree import Tree
from src.mcts.node import Node

VIRTUAL_LOSS = 1


class SelfPlayTree(Tree):
    """ Monte Carlo Tree used for self playing.

    Parameters:
        root: Node or Game. Root state of the tree. You can pass a Node object
        with a Game as state or directly the game (it will make the Node).
    """

    def __init__(self, root, threads=6):
        super().__init__(root)
        self.num_threads = threads

    def search_move(self, agent, max_iters=200, verbose=False, noise=True, ai_move=False):
        """ Explores and selects the best next state to choose from the root state

        Parameters:
            agent: Player. Agent which will be used in the simulations against
            max_iters: int. Number of interactions to run the algorithm.
            verbose: bool. Whether to print the search status.
            noise: bool. Whether to add Dirichlet noise to the calc policy.
            ai_move: bool. Whether to return the move that AI will make after
            our best move
        """

        # with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
        #     for _ in range(max_iters):
        #         print("Iteration: ", _)
        #         executor.submit(self.explore_tree, node=self.root, agent=agent, verbose=verbose)

        self.explore_tree(self.root, agent=agent, verbose=verbose)

        #print("Root visits:", self.root.visits)  # Print the number of visits of the root node
        #print("Root children:", len(self.root.children))  # Print the number of children of the root node

        policy = self.compute_policy(self.root, noise=noise)
        #print("Policy:", policy)  # Print the computed policy vector
        max_val = np.argmax(policy)
        #print("Max value index:", max_val)  # Print the index of the maximum value in the policy vector

        # After the last play the opponent has played, so we use the before last one
        b_mov = Game.NULL_MOVE

        # The agent move which will be made after the last one of ours.
        agent_last_mov = Game.NULL_MOVE

        try:
            b_mov = self.root.children[max_val].state.board.move_stack[-2]
            agent_last_mov = self.root.children[max_val] \
                .state.board.move_stack[-1]
        except IndexError:
            # Should get here if it is not the agent's turn. For example, at
            # the first turn if the agent plays blacks.
            print("Exception")
            pass

        moves = str(b_mov), str(agent_last_mov)
        #print("moves", moves)

        if not ai_move:
            #print("ai")
            moves = str(agent_last_mov)
        return moves

    def explore_tree(self, node, agent, verbose=False):
        agent_copy = agent.get_copy()

        # agent_copy.connect()
        start = timer()
        current_node = self.select(node, agent)
        end = timer()
        v = self.simulate(current_node, agent)
        self.backprop(current_node, v, remove_vloss=True)

        # agent_copy.disconnect()

        elap = round(end - start, 2)
        if verbose:
            print(f"Elapsed on iteration: {elap} secs")

    def select(self, node, agent):
        current_node = node
        while not current_node.is_terminal_state:
            if not current_node.is_fully_expanded:
                current_node = self.expand(current_node, agent=agent)
                break
            else:
                current_node = current_node.get_best_child()

        # Wait if game is not updated yet
        with current_node.lock:
            current_node.vloss += VIRTUAL_LOSS

        return current_node

    def expand(self, node, agent=None):
        """
        From a given state (node), adds to itself all its children
        (game states after all the possible legal game moves are applied).
        Note that this process makes a move and assume that the game opponent
        moves after our move, resulting in the new state.

        Parameters:
            node: Node. Node which will be expanded.
            agent: Agent. that will be used to play the games.
        """
        new_state = node.state.get_copy()
        new_state.move(node.pop_unexpanded_action())
        # Move opponent
        if new_state.get_result() is None:
            bm = agent.best_move(new_state)
            new_state.move(bm)

        new_child = Node(new_state, parent=node)
        node.children.append(new_child)

        # If this node was the last one before fully expand the node
        # we calculate the priors of the children
        # (only do it once)
        #if node.is_fully_expanded:
        #   self._update_prior(node, agent)

        return new_child

    def simulate(self, node: Node, agent: Agent):
        """ Rollout from the current node until a final state.

        Parameters:
            node: Node. Game state from which the simulation will be run.
            agent: Agent. that will be used to play the games.
        Returns:
            results_sim: float, Result of the playout/predicted value from NN.
        """
        result = node.state.get_result()

        if result is None:
            # result = agent.predict_outcome(node.state)

            # Random sim
            sim = RandomSimulation(node.state.get_copy())
            result = sim.run(repetitions=500)

        return result

    def backprop(self, node: Node, value: float, remove_vloss=False):
        """ Backpropagation phase of the algorithm.

        Parameters:
            node: Node. that will be added 1 to vi and the value obtained in
                the simulation process.
            value: float, value that will be added to all the ancestors
                until root.
            remove_vloss: Remove virtual loss from the parent nodes to allow
                the exploration of the same path by other threads
        """
        with node.lock:
            node.visits += 1
            node.value += value
            if remove_vloss:
                node.vloss -= VIRTUAL_LOSS

        if node.parent is not None:
            self.backprop(node.parent, value)

    def _update_prior(self, node, agent):
        """ Update the priors of the children nodes """
        priors = agent.predict_policy(node.state, mask_legal_moves=True)
        children = reversed(node.children)
        for p, n in zip(priors, children):
            n.prior = p

    def compute_policy(self, node: Node, noise=True):
        """ Calculates the policy vector given a game state """
        # Select tau = 1 -> 0 (if number of moves > 30)
        nb_moves = len(node.state.board.move_stack)
        tau = 1
        if nb_moves >= 30:
            tau = nb_moves / (1 + np.power(nb_moves, 1.3))

        # Select argmax π(a|node) proportional to the visit count
        policy = np.array([np.power(v.visits, 1 / tau)
                           for v in node.children]) / np.power(node.visits, 1 / tau)

        # apply random noise for ensuring exploration
        if noise:
            epsilon = 0.25
            policy = (1 - epsilon) * policy + np.random.dirichlet([0.03] * len(node.children))
        return policy
