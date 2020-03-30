
from datetime import date, timedelta, datetime

start = date(year = 2019, month = 10, day = 1)
initial_cases = 100

R0_BEFORE = 2.6
R0_AFTER = 0.65
BAD_SICK_ODDS = 0.10
DEATH_RATE = 0.01

POPULATION = 10 ** 9
IMMUNITY_BOOST = 1.5

HOSPITAL_LIMIT = 6500
FULL_HOSPITAL_MULTIPLIER = 4

TEST_PROBABILITY = 0.3
IMPORTED_TEST_BOOST = 2

import_rates = [
]

def get_r0(day, cases):
    if day <= date(year = 2020, month = 01, day = 24):
        r0 = R0_BEFORE
    else:
        r0 = R0_AFTER

    immunity_factor = (1.0 - ((cases * IMMUNITY_BOOST) / float(POPULATION)))
    return immunity_factor * r0

def get_death_rate(hospitalized):
    factor = FULL_HOSPITAL_MULTIPLIER if hospitalized > HOSPITAL_LIMIT else 1
    return (DEATH_RATE * factor) / BAD_SICK_ODDS

title = 'China - assuming R0 post Jan 24 = %s' % R0_AFTER
csv_file = 'china.csv'
