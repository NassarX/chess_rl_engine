import chess
import chess.engine
import logging
from src.environments.game import Game
from src.environments.player import Player

# Remove annoying warnings of the engine.
chess.engine.LOGGER.setLevel(logging.ERROR)


class StockfishPlayer(Player):
    """ AI using Stockfish to play a game of chess.
    Params:
        color: bool, Color of the player.
        binary_path: str, Path to the Stockfish binary.
        thinking_time: float, Time in seconds to think about the next move.
        search_depth: int, Depth of the search tree.
    """

    def __init__(self, color: bool, binary_path: str, thinking_time=0.01, search_depth=5):
        super().__init__(color)
        self.engine = chess.engine.SimpleEngine.popen_uci(binary_path)

        self.thinking_time = thinking_time
        self.search_depth = search_depth

    def best_move(self, game: Game):
        """ Returns the best move for the current game state.
        Params:
            game: Game, Game to play.
        Returns:
            str, Best move in UCI notation.
        """

        # Page 77 of http://web.ist.utl.pt/diogo.ferreira/papers/ferreira13impact.pdf
        # gives some study about the relation of search depth vs ELO.
        result = self.engine.play(game.board, chess.engine.Limit(depth=5))
        return result.move.uci()

    def kill(self):
        self.engine.quit()
