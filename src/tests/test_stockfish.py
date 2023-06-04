import os
import shutil

from src.agents.stockfish_agent import StockfishAgent
from src.envs.game import Game
from src.envs.game_store import GameStore
from src.envs.stockfish_game import StockfishGame
from src.stockfish.stockfish import Stockfish, play_game
from src.utils.stockfish_helpers import download_stockfish_binary, generate_stockfish_data


def test_stockfish_download():
    # Test if the stockfish binary is downloaded successfully
    dest_path = "src/stockfish/bin/test"
    download_stockfish_binary(dest_path)
    assert os.path.exists(dest_path)

    # Clean up the generated data file
    shutil.rmtree(dest_path)


def test_generate_stockfish_data():
    # Test if the stockfish data generation is successful
    save_path = "src/stockfish/data/test_stockfish_data.json"
    generate_stockfish_data(
        callback_game=play_game,
        dataset=GameStore(),
        stockfish_bin="src/stockfish/bin/stockfish",
        dest_path=save_path,
        depth=1,
        random_depth=False,
        num_games=1,
        workers=2
    )

    # Perform assertions
    assert os.path.exists(save_path)

    # Clean up the generated data file
    os.remove(save_path)


def test_stockfish_agent():
    # Set up the stockfish player
    stockfish_player = StockfishAgent(color=Game.BLACK, binary_path="src/stockfish/bin/stockfish")

    # Set up the stockfish game instance
    stockfish_game = StockfishGame(player_color=Game.WHITE, stockfish=stockfish_player)

    # Make a move
    stockfish_game.move(stockfish_player.best_move(stockfish_game))

    # Perform assertions
    assert isinstance(stockfish_player.best_move(stockfish_game), str)

    # Kill the stockfish player
    stockfish_game.tearup()
