import os
import shutil
import time
import numpy as np
from src.environments.game import Game
from src.data.data_generator import GameStore, DataGenerator



def test_game_store_loads():
    json_data = '[{"date": "2023-05-01", "player_color": true, "moves": ["a2a3", "a2a4"]}, ' \
                '{"date": "2023-05-02", "player_color": false, "moves": ["g1f3", "g8f6"]}]'
    game_store = GameStore()
    game_store.loads(json_data)
    assert len(game_store.games) == 2


def test_game_store_save():
    # Create a sample game store for testing
    game1 = Game(date='2023-05-02', player_color=Game.WHITE)
    game2 = Game(date='2023-05-02', player_color=Game.BLACK)
    game1.move('a2a3')
    game2.move('g1f3')
    game1.move('a2a4')
    game2.move('b8c6')
    game_store = GameStore([game1, game2])

    # Create a temporary file for testing
    timestamp = str(int(time.time()))  # Generate a unique timestamp
    test_dir = 'src/data/test'
    temp_file = f'{test_dir}/test_games_{timestamp}.json'
    os.makedirs(test_dir, exist_ok=True)

    # Save the game store to the temporary file
    game_store.save(temp_file)

    # Load the saved games from the temporary file
    loaded_game_store = GameStore()
    loaded_game_store.load(temp_file)
    assert len(loaded_game_store) == len(game_store)
    assert os.path.exists(temp_file)

    # Clean up the generated data file
    shutil.rmtree(test_dir)


def test_data_generator_len():
    # Create a sample dataset for testing
    game1 = Game(date='2023-05-01', player_color=Game.WHITE)
    game2 = Game(date='2023-05-02', player_color=Game.BLACK)
    dataset = GameStore([game1, game2])

    # Create a DataGenerator instance
    generator = DataGenerator(dataset, batch_size=8)

    # Perform assertions
    expected_length = len(dataset) // generator.batch_size
    assert len(generator) == expected_length


def test_data_generator_getitem():
    # Create a sample dataset for testing
    game1 = Game(date='2023-05-01', player_color=Game.WHITE)
    game2 = Game(date='2023-05-02', player_color=Game.BLACK)
    game1.move('a2a3')
    game2.move('g1f3')
    game1.move('a2a4')
    game2.move('b8c6')
    dataset = GameStore([game1, game2])

    # Create a DataGenerator instance
    generator = DataGenerator(dataset, batch_size=2)

    # Get a batch from the generator
    batch_x, batch_y = generator[0]

    # Perform assertions
    assert isinstance(batch_x, np.ndarray)  # Batch X should be a NumPy array
    assert isinstance(batch_y, tuple)  # Batch Y should be a tuple

    # Perform assertions
    assert len(batch_x) == 3  # 2 games * 1 correct augmented state
    assert len(batch_y) == 2  # 2 games
