import numpy as np

from src.environments.game import Game
from src.utils.encoder_decoder import get_game_history, get_game_state, get_uci_labels, get_current_game_state


def test_get_current_game_state():
    board = Game(player_color=Game.WHITE).board
    current_game_state = get_current_game_state(board)
    expected_shape = (8, 8, 14)
    assert current_game_state.shape == expected_shape

    # Check that each position has either zero or one piece
    assert np.all(np.logical_or(current_game_state == 0, current_game_state == 1))


def test_get_game_history():
    board = Game(player_color=Game.WHITE).board
    history = get_game_history(board)
    expected_shape = (8, 8, 14 * 8)
    assert history.shape == expected_shape

    # First 8 turns should be empty
    assert np.allclose(history[:, :, :14], np.zeros((8, 8, 14)))


def test_get_game_state():
    game = Game(player_color=Game.BLACK)
    game_state = get_game_state(game, flipped=True)
    expected_shape = (8, 8, 127)
    assert game_state.shape == expected_shape


def test_get_uci_labels():
    uci_labels = get_uci_labels()
    assert isinstance(uci_labels, list)
    assert len(uci_labels) == 1968
    assert 'e2e4' in uci_labels  # Example move