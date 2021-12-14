
import random, math, json
from datetime import date, timedelta, datetime

HEALTHY    = 0
INFECTED   = 1
HOSPITAL   = 2
SICK_HOME  = 3
DEAD       = 4
HOSPITAL_RECOVER = 5

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

class DayStats:

    def __init__(self):
        self._new_infections = 0
        self._hospitalized = 0
        self._new_per_variant = {}
        self._positive_tests = 0
        self._positives_per_variant = {}

    def count_infection(self, variant):
        self._new_infections += 1
        vid = variant.get_id()
        self._new_per_variant[vid] = self._new_per_variant.get(vid, 0) + 1

    def count_in_hospital(self):
        self._hospitalized += 1

    def count_positive_tests(self, variant):
        self._positive_tests += 1

    def get_new_cases(self):
        return self._new_infections

    def get_new_cases_by_variant(self):
        return self._new_per_variant

    def get_positive_tests(self):
        return self._positive_tests

    def get_positive_tests_by_variant(self):
        return self._positives_per_variant

    def get_hospitalized(self):
        return self._hospitalized

class Population:

    def __init__(self, population_size, params):
        self._population = [Person() for ix in range(population_size)]
        self._params = params
        self._infected = []

    def get_incidence(self):
        return len(self._infected)

    def import_cases(self, count, variant, today):
        for ix in range(count):
            p = random.choice(self._population)
            while p.is_infected():
                p = random.choice(self._population)

            p.import_infect_with(variant, today)
            self._infected.append(p)

    def mark_cases_as_infected(self, count, variant):
        for ix in range(count):
            p = random.choice(self._population)
            while p.has_been_infected():
                p = random.choice(self._population)

            p.previously_infected_with(variant)

    def iterate(self, todays_r_reduction, today, stats, test_probability):
        infected2 = []
        for p in self._infected:
            today_r = p.get_today_r() * todays_r_reduction

            while today_r >= 1.0:
                self._infect_one_person(p, today, stats)
                today_r -= 1.0

            if random.random() <= today_r:
                self._infect_one_person(p, today, stats)

            p.iterate(today)
            if p.is_infected():
                infected2.append(p)
            if p.is_hospitalized():
                stats.count_in_hospital()
            if p.test_positive_today(today) and random.random() < test_probability:
                stats.count_positive_tests(p.get_variant())

        self._infected = infected2

    def _infect_one_person(self, index_case, today, stats):
        p = random.choice(self._population)
        while p == index_case:
            p = random.choice(self._population)

        variant = index_case.get_variant().get_when_infecting()
        was_infected = p.is_infected()
        p.infect(variant, today)
        if p.is_infected() and not was_infected:
            self._infected.append(p)
            stats.count_infection(variant)

    def pick_n_people(self, n):
        people = set()
        while len(people) < n:
            people.add(random.choice(self._population))
        return people

TIME_TO_SPLIT = Generator(avg = 5.1 + 8, var = 2)
GOOD_RECOVER_TIME = Generator(avg = 14, var = 2)
BAD_FORK_TIME = Generator(avg = 13, var = 3, lognormal = True)
BAD_RECOVER_TIME = Generator(avg = 7.5, var = 2)
TIME_TO_TEST = Generator(avg = 4, var = 2)

class Person:

    def __init__(self):
        self._state = HEALTHY
        self._variant = None
        self._recovered_variants = []
        self._days_since_infected = -1
        self._next_change = None
        self._test_positive_date = None

    def is_infected(self):
        return self._state not in (HEALTHY, DEAD)

    def has_been_infected(self):
        return bool(self._recovered_variants)

    def is_hospitalized(self):
        return self._state in (HOSPITAL, HOSPITAL_RECOVER)

    def get_variant(self):
        return self._variant

    def test_positive_today(self, today):
        return today == self._test_positive_date

    def import_infect_with(self, variant, today):
        self.infect(variant, today, check_immunity = False)

    def previously_infected_with(self, variant):
        self._recovered_variants.append(variant)

    def infect(self, variant, today, check_immunity = True):
        if self._state != HEALTHY:
            return # this person is already sick/dead, so no effect

        if check_immunity:
            for v in self._recovered_variants:
                if random.random() <= v.get_immunity_to(variant):
                    return # immunity protected this person

        self._state = INFECTED
        self._variant = variant
        self._days_since_infected = 0
        self._next_change = TIME_TO_SPLIT.next(today)
        self._test_positive_date = TIME_TO_TEST.next(today)

    def get_today_r(self):
        if self._days_since_infected == 100:
            print self._state, self._next_change
        return infection_odds_pr_day(self._variant.get_r0(), self._days_since_infected)

    def iterate(self, today):
        self._days_since_infected += 1

        if today < self._next_change:
            return

        if self._state == INFECTED:
            if random.random() <= self._variant.get_hospitalization_odds():
                self._state = HOSPITAL
                self._next_change = BAD_FORK_TIME.next(today)
            else:
                self._state = SICK_HOME
                self._next_change = GOOD_RECOVER_TIME.next(today)

        elif self._state == HOSPITAL:
            if random.random() <= self._variant.get_death_odds():
                self._state = DEAD
                self._next_change = None
            else:
                self._state = HOSPITAL_RECOVER
                self._next_change = BAD_RECOVER_TIME.next(today)

        elif self._state in (SICK_HOME, HOSPITAL_RECOVER):
            self._state = HEALTHY
            self._recovered_variants.append(self._variant)
            self._variant = None

        else:
            assert False

    def get_immunity_to(self, variant):
        risk = 1.0
        for v in self._recovered_variants:
            risk *= (1.0 - v.get_immunity_to(variant))
        return 1.0 - risk

# --- INFECTION BY DAY PROBABILITY

def infection_odds_pr_day(re, day):
    return precomputed_day_prob[day] * re

def factorial(n):
    f = 1
    for k in range(1, n + 1):
        f *= k
    return f

def poisson(v, l):
    return ((l ** v * math.e ** (-l) / factorial(v)))

# https://science.sciencemag.org/content/early/2020/11/23/science.abe2424
def prob(day):
    day -= 1
    return (poisson(day, 3) +
            (poisson(day, 5) * 0.25) +
            (poisson(day, 6) * 0.5) +
            (poisson(day, 8) * 0.5)
            ) / 2.25

precomputed_day_prob = [prob(day) for day in range(100)]

# --- OTHER STUFF

def get0(day):
    return 0.0

class DefaultVariant:

    def __init__(self, r0 = 3, theid = 'default'):
        self._r0 = r0
        self._id = theid

    def get_id(self):
        return self._id

    def get_hospitalization_odds(self):
        return 0.02

    def get_death_odds(self):
        return 0.016 / self.get_hospitalization_odds()

    def get_r0(self):
        return self._r0

    def get_immunity_to(self, variant):
        return 1.0

    def get_when_infecting(self):
        return self

    def get_metadata(self):
        return {}

class SimulationParameters:
    def __init__(self):
        self.SEASONALITY = 0.5

def seasonality(day, params):
    start = date(year = day.year, month = 1, day = 1)
    ix = (day - start).days

    if ix <= 15:
        return 0.5 + ((ix + 170) / 185.0 * params.SEASONALITY)
    elif ix <= 195:
        return 1 - ((ix - 15) / 180.0 * params.SEASONALITY)
    else:
        return 0.5 + ((ix - 195) / 185.0 * params.SEASONALITY)

def collect_variants(population, stats):
    variants = {}
    for p in population._infected:
        if not p.get_variant():
            continue

        vid = p.get_variant().get_id()
        if vid not in variants:
            variants[vid] = {'count' : 0, 'metadata' : p.get_variant().get_metadata()}
        variants[vid]['count'] = variants[vid]['count'] + 1

    for (vid, new_cases) in stats.get_new_cases_by_variant().items():
        variants[vid]['new-cases'] = new_cases
    for (vid, positives) in stats.get_positive_tests_by_variant().items():
        variants[vid]['positives'] = positives

    return variants

def debug_r(population, variants, todays_r_reduction):
    print
    for variant in variants:
        print '---', variant.get_id()
        total = 0
        for p in population.pick_n_people(100000):
            total += p.get_immunity_to(variant)
        immunity_factor = total / 100000.0
        print 'r_redux %s * r0 %s * immunity %s = %s' % (todays_r_reduction, variant.get_r0(), immunity_factor, todays_r_reduction * variant.get_r0() * (1 - immunity_factor))
        print 'immunity: ', [p.get_immunity_to(variant) for p in population.pick_n_people(10)]

    print

def simulate(start, end, population_size, already_infected = 0,
             get_imports = get0, start_variant = DefaultVariant(),
             start_incidence = 0,
             import_variant = DefaultVariant(),
             stats_file = None, get_r_reduction = get0,
             params = SimulationParameters(),
             test_probability = 1.0,
             debug_r_on_dates = set(),
    ):
    population = Population(population_size, params)
    # these cases are inactive, just immune
    population.mark_cases_as_infected(already_infected, start_variant)
    # these cases are active, and will become immune (or die)
    population.import_cases(start_incidence, start_variant, start)

    outf = open(stats_file, 'w') if stats_file else None

    today = start
    while today < end:
        stats = DayStats()
        population.import_cases(get_imports(today), import_variant, today)

        todays_r_reduction = (1.0 - get_r_reduction(today)) * seasonality(today, params)
        population.iterate(todays_r_reduction, today, stats, test_probability)

        print today, stats.get_new_cases(), population.get_incidence(), stats.get_hospitalized(), todays_r_reduction * start_variant.get_r0()

        if outf:
            outf.write(json.dumps({
                'date' : str(today),
                'new-cases' : stats.get_new_cases(),
                'incidence' : population.get_incidence(),
                'hospitalized' : stats.get_hospitalized(),
                'positives' : stats.get_positive_tests(),
                'variants' : collect_variants(population, stats),
            }))
            outf.write('\n')

        if today in debug_r_on_dates:
            debug_r(population, [v for v in [start_variant, import_variant]
                                 if v], todays_r_reduction)
        if not population.get_incidence():
            break
        today += timedelta(days = 1)
