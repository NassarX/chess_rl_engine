from src.envs.game import Game


class Agent:
    """ This class contains the necessary methods all chess
        agent objects must implement.
    """

    def __init__(self, color):
        if type(self) is Agent:
            raise Exception('Cannot create Agent Abstract class.')
        self.color = color

    def best_move(self, game: Game) -> str:
        """Makes the agent to make a move in the game. The agent should also
                pass the turn when it finishes (aka. notify the other players).
        """
        raise Exception('Abstract class.')

    def get_copy(self):
        """ Returns a copy of the agent."""
        raise Exception('Abstract class.')