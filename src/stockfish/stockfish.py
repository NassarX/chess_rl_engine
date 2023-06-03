import sys
import os
from tqdm import tqdm
import argparse
import numpy as np
sys.path.append(os.path.abspath("."))

from src.stockfish.stockfish_game import StockfishGame
from src.stockfish.stockfish_player import StockfishPlayer
from src.data.game_store import GameStore
from src.utils.stockfish_helpers import download_stockfish_binary, generate_stockfish_data


def play_game(stockfish_bin, dataset, depth=1, tqbar=None, random_dep=False):
    """ Play a game of chess with stockfish and store it in the dataset.

    Args:
        stockfish_bin (str): Path to stockfish binary.
        dataset (DatasetGame): Dataset to store game in.
        depth (int): Depth to play at.
        tqbar (tqdm): Progress bar.
        random_dep (bool): Whether to play at random depth.
    """

    # Set random color
    is_white = True if np.random.random() <= .5 else False
    game_depth = depth
    player_depth = depth

    if random_dep:
        # Set random depth for game and player
        game_depth = int(np.random.normal(depth, 1))
        player_depth = int(np.random.normal(depth, 1))

    # Create game and player
    game = StockfishGame(stockfish=stockfish_bin, player_color=is_white, stockfish_depth=game_depth)
    stockfish_player = StockfishPlayer(is_white, stockfish_bin, player_depth)

    # While game is not over
    while game.get_result() is None:
        # Get best move from stockfish
        _best_move = stockfish_player.best_move(game)
        game.move(_best_move)

    # Append game to dataset
    dataset.append(game)
    if tqbar is not None:
        tqbar.update(1)

    # Kill stockfish processes
    game.tearup()
    stockfish_player.kill()


class Stockfish:
    """ Stockfish class to generate data."""

    def __init__(self, stockfish_bin=None, dataset=None, depth=1, random_dep=False):
        self.stockfish_bin = stockfish_bin
        self.dataset = dataset
        self.depth = depth
        self.random_dep = random_dep

    def setup_stockfish(self, dest_path=None, num_games=100, random_dep=False, workers=2):
        # Download stockfish binary
        if self.stockfish_bin is None:
            self.stockfish_bin = download_stockfish_binary("src/stockfish/bin")

        # Create dataset
        if self.dataset is None:
            self.dataset = GameStore()

        # Set depth
        if self.depth is None:
            self.depth = 1

        if dest_path is None:
            dest_dir = os.path.join(os.getcwd(), "src", "data", "stockfish")
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, 'dataset.json')

        # Generate data with stockfish and store in dataset at dest_path
        generate_stockfish_data(
            callback_game=play_game,
            dataset=self.dataset,
            stockfish_bin=self.stockfish_bin,
            dest_path=dest_path,
            depth=self.depth,
            random_depth=random_dep,
            num_games=num_games,
            workers=workers
        )


def main():
    parser = argparse.ArgumentParser(description="Plays some chess games,"
                                                 "stores the result and trains a model.")
    parser.add_argument('--stockfish_bin', metavar='stockfish_bin',
                        default=None,
                        help="Stockfish binary path")
    parser.add_argument('--data_path', metavar='dataset_path',
                        default=None,
                        help="Path of .JSON dataset.")
    parser.add_argument('--games', metavar='games', type=int,
                        default=10)
    parser.add_argument('--depth', metavar='depth', type=int,
                        default=1, help="Stockfish tree depth.")
    parser.add_argument('--random_depth',
                        action='store_true',
                        default=False,
                        help="Use normal distribution of depths with "
                             "mean --depth.")
    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help="Log debug messages on screen. Default false.")

    args = parser.parse_args()

    # Setup stockfish
    stockfish = Stockfish(stockfish_bin=args.stockfish_bin,
                          dataset=GameStore(),
                          depth=args.depth,
                          random_dep=args.random_depth)
    stockfish.setup_stockfish(args.data_path, args.games)


if __name__ == "__main__":
    main()
