from datetime import datetime

import chess
import chess.svg
from IPython.display import SVG, display


class Game:
    """This is the base class to represent a game. It contains a python-chess board which holds the
    moves made, the player color (POV of the game) and the date when the game was played. Also, this class implements
    the logic to get the state of the game (`get_result()` or `get_legal_moves()`). **After each call to the `move()`
    method, the turn will be switched**. This is intended as a way to allow users to decouple the agent play logic
    from this class (though you can extend this class, being `AgentGame` or `StockfishGame` examples of this).
    """
    NULL_MOVE = '00000'
    WHITE = chess.WHITE
    BLACK = chess.BLACK

    def __init__(self, board=None, player_color=chess.WHITE, date=None):
        """Initializes the game."""
        if board is None:
            self.board = chess.Board()
        else:
            self.board = board
        self.player_color = player_color

        self.date = date
        if self.date is None:
            self.date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def move(self, movement):
        """ Makes a move.
        Params:
            movement: str, Movement in UCI notation (f2f3, g8f6...)
        Returns:
            success: boolean. Whether the move could be executed
        """
        # This is to prevent python-chess to put a illegal move in the
        # move stack before launching the exception
        success = False
        if movement in self.get_legal_moves():
            self.board.push(chess.Move.from_uci(movement))
            success = True
        return success

    def get_legal_moves(self, final_states=False):
        """ Gets a list of legal moves in the current turn.
        Parameters:
            final_states: bool. Whether copies of the board after executing
            each legal movement are returned.
        """
        moves = [m.uci() for m in self.board.legal_moves]
        if final_states:
            states = []
            for m in moves:
                gi = self.get_copy()
                gi.move(m)
                states.append(gi)
            moves = (moves, states)
        return moves

    def get_history(self):
        moves = [x.uci() for x in self.board.move_stack]
        res = self.get_result()
        return {'moves': moves,
                'result': res,
                'player_color': self.player_color,
                'date': self.date}

    def get_fen(self):
        return self.board.board_fen()

    def set_fen(self, fen):
        self.board.set_board_fen(fen)

    @property
    def turn(self):
        """ Returns whether is white turn."""
        return self.board.turn

    def get_copy(self):
        return Game(board=self.board.copy())

    def reset(self):
        self.board.reset()

    def free(self):
        """ This method will be implemented by children. This will serve
        as a way to disconnect from the engine or free resources but without
        destroying the object
        """
        pass

    def get_result(self):
        """ Returns the result of the game for the white pieces. None if the
        game is not over. This method checks if the game ends in a draw due
        to the fifty-move rule. Threefold is not checked because it can
        be too slow.
        """
        result = None
        if self.board.can_claim_fifty_moves() or self.board.is_insufficient_material():
            result = 0  # Draw
        elif self.board.is_checkmate():
            if self.board.turn == chess.WHITE:
                result = 1  # Whites win
            else:
                result = -1  # Whites don't win
        return result

    def __len__(self):
        return len(self.board.move_stack)

    def plot_board(self, save_path=None):
        """ Plots the current state of the board. This is useful for debug/log
        purposes while working outside a notebook

        Parameters:
            save_path: str, where to save the image. None if you want to plot
            on the screen only
        """
        # Generate SVG representation of the board
        svg = chess.svg.board(board=self.board)

        # Display the SVG using IPython's display function
        display(SVG(svg))
