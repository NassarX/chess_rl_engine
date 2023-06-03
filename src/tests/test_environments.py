from src.environments.game import Game


def test_move():
    game = Game(player_color=Game.WHITE)
    assert game.move("e2e4") is True  # Valid move
    assert game.move("b2b4") is False  # Invalid move
    assert game.move("d7d6") is True  # Valid move


def test_get_legal_moves():
    game = Game(player_color=Game.WHITE)
    legal_moves = game.get_legal_moves()
    expected_moves = ['a2a3', 'a2a4', 'b1a3', 'b1c3', 'c2c3', 'c2c4', 'd2d3', 'd2d4',
                      'e2e3', 'e2e4', 'f2f3', 'f2f4', 'g1f3', 'g1h3', 'g2g3', 'g2g4',
                      'h2h3', 'h2h4']
    for move in expected_moves:
        assert move in legal_moves


def test_get_result():
    game = Game(player_color=Game.WHITE)
    assert game.get_result() is None  # Game not over yet
    game.move("e2e4")
    assert game.get_result() is None  # Game not over yet
    game.move("e7e5")
    assert game.get_result() is None  # Game not over yet
    game.move("f1c4")
    assert game.get_result() is None  # Game not over yet
    game.move("b8c6")
    assert game.get_result() is None  # Game not over yet
    game.move("d1h5")
    assert game.get_result() is None  # Game not over yet
    game.move("g7g6")
    assert game.get_result() is None  # Game not over yet


