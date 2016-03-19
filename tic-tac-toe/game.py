'''
The basic game logic.
'''

import players

class InvalidMove(Exception):
    pass

class Game:

    def __init__(self, players, board):
        self._players = players
        for (ix, player) in enumerate(players):
            player.set_number(ix)
        self._board = board
        self._next_player = 0

    def get_next_player(self):
        if self._next_player == None:
            return None

        p = self._players[self._next_player]
        self._next_player = 1 - self._next_player
        return p

    def make_move(self, player, move):
        self._board.add_piece(move, player.get_number())
        if self._board.who_won() != None or self._board.full():
            self._next_player = None # we're done

def compute_position(row, col):
    return row * 3 + col

class Board:

    rows = [[compute_position(rowno, colno) for colno in range(3)]
            for rowno in range(3)]
    cols = [[compute_position(rowno, colno) for rowno in range(3)]
            for colno in range(3)]
    diag = [[compute_position(ix, ix) for ix in range(3)],
            [compute_position(ix, 2 - ix) for ix in range(3)]]
    winners = rows + cols + diag

    def __init__(self):
        self._positions = [None] * 9

    def add_piece(self, position, player):
        if self._positions[position] != None:
            raise InvalidMove('Cannot place piece on %s' % position)

        self._positions[position] = player

    def who_won(self):
        for positions in Board.winners:
            counts = self._count_along(positions).items()
            if len(counts) == 1:
                winner = counts[0][0]
                if winner != None:
                    return winner

    def _count_along(self, positions):
        counts = {}
        for player in [self.get_position(pos) for pos in positions]:
            counts[player] = counts.get(player, 0) + 1
        return counts

    def get_position(self, pos):
        return self._positions[pos]

    def full(self):
        for in_pos in self._positions:
            if in_pos == None:
                return False
        return True
