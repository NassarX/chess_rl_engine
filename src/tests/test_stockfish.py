import os
import shutil

import pytest

from src.data.game_store import GameStore
from src.stockfish.stockfish import Stockfish, play_game
from src.utils.stockfish_helpers import download_stockfish_binary, generate_stockfish_data


@pytest.fixture(scope='module')
def stockfish_setup():
    # Set up the stockfish instance
    stockfish = Stockfish(stockfish_bin=None,
                          dataset=GameStore(),
                          depth=1,
                          random_dep=False)
    stockfish.setup_stockfish(num_games=10)
    yield stockfish

    # Clean up after the tests
    # stockfish.cleanup()


def test_stockfish_download(stockfish_setup):
    # Test if the stockfish binary is downloaded successfully
    dest_path = "src/stockfish/bin/test"
    download_stockfish_binary(dest_path)
    assert os.path.exists(dest_path)

    # Clean up the generated data file
    shutil.rmtree(dest_path)


def test_generate_stockfish_data(stockfish_setup):
    # Test if the stockfish data generation is successful
    stockfish_setup.setup_stockfish()
    save_path = "src/data/stockfish/test_stockfish_data.json"
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
    assert os.path.exists(save_path)

    # Clean up the generated data file
    os.remove(save_path)
