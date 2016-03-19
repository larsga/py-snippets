'''
Implementations of the players.
'''

import random, operator, math

class Player:

    def set_number(self, number):
        self._number = number

    def get_number(self):
        return self._number

    def get_move(self, board):
        pass

    def done(self, winner):
        pass

    def save(self):
        pass

class Random(Player):

    def get_move(self, board):
        return random.randint(0, 8)

class Clever(Player):

    def get_move(self, board):
        # does some winner have len=2 and {None : 1}? if so, prefer that
        blocker = None # can we block the opponent?
        for positions in board.winners:
            counts = board._count_along(positions)
            #print counts
            if len(counts) == 2 and counts.get(None) == 1:
                if counts.get(self._number) == 2:
                    w = self._find_open(board, positions)
                    return w
                elif blocker == None:
                    blocker = self._find_open(board, positions)

        if blocker != None:
            return blocker
        return random.randint(0, 8)

    def _find_open(self, board, positions):
        for pos in positions:
            if board.get_position(pos) == None:
                return pos

class Experience:

    def __init__(self, wins = 0, draws = 0, losses = 0):
        self._wins = wins
        self._losses = losses
        self._draws = draws

# {0: 89296, 1: 2772, None: 7932} 10, -1, -10
# {0: 88899, None: 11101}         100, -1, -100
    def get_score(self):
        return self._wins * 100 + self._draws * -1 + self._losses * -100

    def win(self):
        self._wins += 1

    def draw(self):
        self._draws += 1

    def lose(self):
        self._losses += 1

    def __str__(self):
        return '%s,%s,%s' % (self._wins, self._draws, self._losses)

class LearningPlayer(Player):

    def __init__(self, file, klass = Experience):
        self._file = file
        self._klass = klass
        try:
            self._outcomes = [[self._parse(s) for s in line.strip().split()]
                              for line in open(self._file)]
        except IOError, e:
            print "Can't load %s" % file, e
            self._outcomes = [[klass() for x in range(9)]
                              for y in range(3 ** 9)]

        self._moves_made = []

    def _parse(self, statestr):
        state = map(int, statestr.split(','))
        return self._klass(state[0], state[1], state[2])

    def get_move(self, board):
        number = self._compute_board_number(board)
        print 'board no', number
        best = None
        score = -10000000000000
        for (ix, choice) in enumerate(self._outcomes[number]):
            if board.get_position(ix) != None: # position occupied
                continue
            print ix, str(choice), choice.get_score()
            if choice.get_score() > score:
                best = ix
                score = choice.get_score()
        self._moves_made.append((number, best))
        return best

    def done(self, winner):
        for (boardstate, move) in self._moves_made:
            if winner == None:
                self._outcomes[boardstate][move].draw()
            elif winner == self._number:
                self._outcomes[boardstate][move].win()
            else:
                self._outcomes[boardstate][move].lose()

        self._moves_made = []

    def save(self):
        outf = open(self._file, 'w')
        for state in self._outcomes:
            outf.write(' '.join([str(e) for e in state]))
            outf.write('\n')
        outf.close()

    def _compute_board_number(self, board):
        return reduce(operator.add, [(3 ** ix) * num(content) for
                                     (ix, content) in
                                     enumerate(board._positions)])

def num(content):
    if content == None:
        return 0
    return content + 1

class BanditPlayer(LearningPlayer):

    def __init__(self, file):
        LearningPlayer.__init__(self, file, BanditExperience)

    def get_move(self, board):
        number = self._compute_board_number(board)

        print 'board no', number

        best = None
        best_avg = -100000000
        total_plays = sum([c.get_plays() for c in self._outcomes[number]])

        for (ix, choice) in enumerate(self._outcomes[number]):
            if board.get_position(ix) != None:
                continue
            avg_est = choice.get_best_possible_average(total_plays)
            print ix, str(choice), choice.get_average(), avg_est

            if avg_est > best_avg:
                best_avg = avg_est
                best = ix

        self._moves_made.append((number, best))
        return best

class BanditExperience(Experience):

    def get_plays(self):
        return self._wins + self._draws + self._losses

    def get_average(self):
        # here we assume payout is wins: 1, draws: 0, losses: -1
        if self.get_plays() == 0:
            return 0.0
        return (self._wins - self._losses) / float(self.get_plays())

    def get_best_possible_average(self, total):
        if self.get_plays() == 0:
            return 1.0 # this is the best the average could possibly be
        return self.get_average() + math.sqrt(2 * math.log(total) / self.get_plays())
