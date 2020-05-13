#encoding=utf-8

# NOTE: This code is unclean in the sense that different parts of the
# codebase communicate with each other via global variables. That was
# a quick-and-dirty way to quickly iterate this model to a point where
# it did what I wanted it to do, but it will make it unpleasant to
# work with for others. You have been warned.

import random, sys, json
from collections import namedtuple
from datetime import date, timedelta, datetime

# FIXME:
#   - output RMSE against known numbers?
#   - imported test boost has no effect (bug)
#   - what if we graph new deaths/infections per day?

import norway, china, italy, example

if len(sys.argv) > 2:
    SIMULATIONS = int(sys.argv[2])
else:
    SIMULATIONS = 100

model = norway
if len(sys.argv) >= 2:
    m = sys.argv[1]
    if m == 'norway':
        model = norway
    elif m == 'italy':
        model = italy
    elif m == 'china':
        model = italy
    elif m == 'example':
        model = example
    else:
        assert False

class Generator:
    def __init__(self, avg, var, lognormal = False):
        self._avg = avg
        self._var = var
        self._lognormal = lognormal

    def next(self, day):
        if self._lognormal:
            delta = int(random.weibullvariate(self._avg + 2, self._var))
            #delta = int(random.lognormvariate(self._avg, self._var))
        else:
            delta = int(random.gauss(self._avg, self._var))
        return day + timedelta(days = delta)

stop = date(year = 2020, month = 9, day = 1) # date.today()

# https://drive.google.com/file/d/1DqfSnlaW6N3GBc5YKyBOCGPfdqOsqk1G/view
#   average time from diagnosis to death = 14 (symptoms + 4.5 = diagnosis?)

LATENCY = Generator(avg = 5.1, var = 1)
TIME_TO_SPLIT = Generator(avg = 8, var = 2)
GOOD_RECOVER_TIME = Generator(avg = 14, var = 2)
BAD_FORK_TIME = Generator(avg = 13, var = 3, lognormal = True)
BAD_RECOVER_TIME = Generator(avg = 7.5, var = 2)
TIME_TO_TEST = Generator(avg = 4, var = 2)

BEFORE           = 'BEFORE'
SICK             = 'SICK'
SICK_GOOD        = 'SICK_GOOD'
SICK_BAD         = 'SICK_BAD'
SICK_BAD_RECOVER = 'SICK_BAD_RECOVER'
RECOVERED        = 'RECOVERED'
DEAD             = 'DEAD'

IMPORT_DAMPING = 0.1

# this will cause total number of infected people to overshoot the
# theoretical max 'predicted' by the r0, but this is actually correct
# https://twitter.com/CT_Bergstrom/status/1251999295231819778
def get_re(get_r0, day, cases):
    r0 = get_r0(day)
    immunity_factor = (1.0 - (cases / float(model.POPULATION)))
    return immunity_factor * r0

avg_days = 1 + TIME_TO_SPLIT._avg + (
    GOOD_RECOVER_TIME._avg * (1.0 - model.BAD_SICK_ODDS) +
    (BAD_FORK_TIME._avg + BAD_RECOVER_TIME._avg) * model.BAD_SICK_ODDS
)
def infection_odds_pr_day(re):
    return re / avg_days

class InfectedPerson:
    def __init__(self, infected_day, state = BEFORE, imported = False):
        self._state = state
        self._next_change = LATENCY.next(infected_day)
        self._imported = imported
        self._test_positive_date = None

    def iterate(self, day, re, hospitalized):
        if self._state in (RECOVERED, DEAD):
            return False

        infect = self.is_sick() and random.uniform(0.0, 1.0) < infection_odds_pr_day(re)

        if self._next_change > day:
            return infect

        dampen = IMPORT_DAMPING if self._imported else 1.0

        if self._state == BEFORE:
            self._state = SICK
            self._next_change = TIME_TO_SPLIT.next(day)

            # FIXME: this never runs (facepalm)
            factor = IMPORTED_TEST_BOOST if self._imported else 1
            if random.uniform(0.0, 1.0) < model.TEST_PROBABILITY * factor:
                self._test_positive_date = TIME_TO_TEST.next(day)

        elif self._state == SICK:
            if random.uniform(0.0, 1.0) < model.BAD_SICK_ODDS * dampen:
                self._state = SICK_BAD
                self._next_change = BAD_FORK_TIME.next(day)
            else:
                self._state = SICK_GOOD
                self._next_change = GOOD_RECOVER_TIME.next(day)

        elif self._state == SICK_GOOD:
            self._state = RECOVERED

        elif self._state == SICK_BAD:
            if random.uniform(0.0, 1.0) < model.get_death_rate(hospitalized):
                self._state = DEAD
            else:
                self._state = SICK_BAD_RECOVER
                self._next_change = BAD_RECOVER_TIME.next(day)

        elif self._state == SICK_BAD_RECOVER:
            self._state = RECOVERED
        else:
            assert False

        return infect

    def is_sick(self):
        return self._state in (SICK, SICK_BAD, SICK_GOOD)

def iterate(people, day, re, hospitalized):
    newly_infected = 0
    for p in people:
        if p.iterate(day, re, hospitalized):
            newly_infected += 1

    for ix in range(newly_infected):
        people.append(InfectedPerson(day))

    import_rate = 0
    for (end, rate) in model.import_rates:
        if day < end:
            import_rate = rate

    for ix in range(import_rate):
        people.append(InfectedPerson(day, SICK, imported = True))

    return (newly_infected, import_rate)

def count_by(seq, keyfunc):
    count = {}
    for v in seq:
        k = keyfunc(v)
        count[k] = count.get(k, 0) + 1
    return count

def simulate(today, get_r0, output = True):
    cases = 0
    hospitalized = 0
    by_day = []
    people = [InfectedPerson(today) for ix in range(model.initial_cases)]
    accums = {DEAD : 0, RECOVERED : 0, 'positive' : 0}
    home_infected = 0
    imported = 1

    while today <= stop:
        todays_re = get_re(get_r0, today, cases)
        if SIMULATIONS == 1:
            print today, cases, todays_re, accums[DEAD]

        (newly_infected, import_rate) = iterate(people, today, todays_re, hospitalized)
        home_infected += newly_infected
        imported += import_rate

        if output:
            print '---', today
            print 'Home %s, imported %s' % (home_infected, imported)

        count = count_by(people, lambda p: p._state)
        count['positive'] = len([
            p for p in people if p._test_positive_date == today
        ])

        accums[DEAD] = accums[DEAD] + count.get(DEAD, 0)
        accums[RECOVERED] = accums[RECOVERED] + count.get(RECOVERED, 0)
        accums['positive'] = accums['positive'] + count.get('positive', 0)
        people = [p for p in people if p._state not in (DEAD, RECOVERED)]
        assert count_by(people, lambda p: p._state).get(DEAD, 0) == 0

        hospitalized = count.get(SICK_BAD, 0)
        cases = len(people) + accums[DEAD] + accums[RECOVERED]
        count.update(accums)
        count['cases'] = cases
        if output:
            print count

        by_day.append((today, count))
        today += timedelta(days = 1)

    return by_day

# ----- CSV HANDLING
import csv

def load_csv(filename):
    rows = [row for row in csv.reader(open(filename))]
    rows = rows[1 : ] # drop header

    Row = namedtuple('Row', ('date', 'dead', 'positives', 'infected_locally',
                             'infected_abroad', 'infected_unknown', 'hospital',
                             'icu'))
    rows = [Row._make(row) for row in rows]
    return rows

# ----- PRODUCE DATA

def average_of_field(results, field):
    data = []
    for ix in range(len(results[0])):
        data.append(
            sum([by_day[ix][1].get(field, 0) for by_day in results]) / float(SIMULATIONS)
        )
    return data

if __name__ == '__main__':
    results = []
    for ix in range(SIMULATIONS):
        results.append(simulate(model.start, model.get_r0, False))
        if SIMULATIONS > 1:
            print ix + 1

if __name__ == '__main__':
    rows = load_csv(model.csv_file)
    hospitalized = average_of_field(results, SICK_BAD)
    dead = average_of_field(results, DEAD)
    cases = average_of_field(results, 'cases')
    positives = average_of_field(results, 'positive')

    # ----- DATA EXPORT

    if len(sys.argv) == 4:
        filename = sys.argv[3]
        with open(filename, 'w') as f:
            tmp = [{str(date) : data for (date, data) in by_day}
                       for by_day in results]
            json.dump(tmp, f)

# ----- PLOTTING

def prepare(rows, field):
    y = [datetime.strptime(row.date, '%Y-%m-%d') for row in rows
         if getattr(row, field) != '_']
    x = [int(getattr(row, field)) for row in rows
         if getattr(row, field) != '_']
    return (y, x)

if __name__ == '__main__':
    from matplotlib import pyplot as plt

    days = [by_day[0] for by_day in results[0]]
    plt.plot(days, hospitalized, 'g', label = u'Currently hospitalized')
    plt.plot(days, dead, 'r', label = u'Dead, accumulated')

    csv_dead = prepare(rows, 'dead')
    csv_hospital = prepare(rows, 'hospital')
    csv_positives = prepare(rows, 'positives')

    plt.plot(csv_dead[0], csv_dead[1], 'ro', label = u'Dead, accumulated')
    plt.plot(csv_hospital[0], csv_hospital[1], 'go', label = u'Currently hospitalized')
    plt.legend(loc='upper left')
    plt.title(model.title)
    plt.show()


    plt.plot(days, cases, 'r', label = u'Infected')
    plt.plot(days, positives, 'g', label = u'Tested positive')
    plt.plot(csv_positives[0], csv_positives[1], 'go', label = u'Tested positive')
    plt.legend(loc='upper left')
    plt.title(model.title)
    plt.show()
