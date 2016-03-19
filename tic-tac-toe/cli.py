'''
Primitive command-line interface to the game.
'''

import sys
import game
import players

PIECES = 'ox'

class CLIBoard(game.Board):

    def display(self):
        for (ix, in_pos) in enumerate(self._positions):
            if in_pos == None:
                print '.',
            else:
                print PIECES[in_pos],

            if ix % 3 == 2:
                print

        print

class CLIHuman(players.Player):

    def get_move(self, board):
        move = -1
        while move not in range(9):
            print 'Where to you want to place your piece [0-8]?',
            try:
                move = int(raw_input().strip())
            except ValueError:
                pass
        return move

def run_game(players):
    board = CLIBoard()
    g = game.Game(players, board)
    next_player = g.get_next_player()
    while next_player:
        board.display()

        ok = False
        while not ok:
            try:
                move = next_player.get_move(board)
                g.make_move(next_player, move)
                ok = True
            except game.InvalidMove:
                pass #print 'INVALID MOVE!'

        next_player = g.get_next_player()

    board.display()

    winner = board.who_won()
    if winner != None:
        print 'WINNER: ', PIECES[winner]
        logfile.write(PIECES[winner])
    else:
        print 'DRAW!'
    logfile.write('\n')

    for player in players:
        player.done(winner)

    return winner

def train(player1, player2, n):
    counts = {}
    for ix in range(n):
        winner = run_game([player1, player2])
        counts[winner] = counts.get(winner, 0) + 1

    print counts
    player1.save()
    player2.save()

logfile = open('log.txt', 'w')

#train(CLIHuman(), players.BanditPlayer(sys.argv[1]), 1)
#train(players.LearningPlayer(sys.argv[1]), CLIHuman(), 1)
#train(players.BanditPlayer(sys.argv[1]), CLIHuman (), 1)
#train(players.BanditPlayer(sys.argv[1]), players.Clever(), 100000)

# {0: 90979, 1: 699, None: 8322}
# {0: 91192, 1: 696, None: 8112}
# {0: 91755, 1: 674, None: 7571}
#train(players.BanditPlayer(sys.argv[1]), players.Clever(), 100000)
# {0: 15422, 1: 40120, None: 44458}
#train(players.Clever(), players.BanditPlayer(sys.argv[1]), 100000)

# {0: 87428, 1: 1402, None: 11170}
# {0: 92381, 1: 749, None: 6870}
# {0: 92403, 1: 677, None: 6920}
train(players.LearningPlayer(sys.argv[1]), players.Clever(), 100000)
# {0: 19134, 1: 39217, None: 41649}
#train(players.Clever(), players.LearningPlayer(sys.argv[1]), 100000)

# {0: 39542, 1: 524, None: 59934}
#train(players.BanditPlayer('bandit.txt'),
#      players.LearningPlayer('learner.txt'), 100000)

# {0: 8415, 1: 7220, None: 84365}
#train(players.LearningPlayer('learner.txt'),
#      players.BanditPlayer('bandit.txt'), 100000)

# {0: 3302, 1: 1805, None: 94893}
# train(players.LearningPlayer('learner2.txt'),
#       players.BanditPlayer('bandit2.txt'), 100000)

# {0: 38001, 1: 2393, None: 59606}
# train(players.BanditPlayer('bandit2.txt'),
#       players.LearningPlayer('learner2.txt'), 100000)

logfile.close()
