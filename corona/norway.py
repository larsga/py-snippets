
from datetime import date, timedelta, datetime

start = date(year = 2020, month = 2, day = 15)
initial_cases = 1

R0_BEFORE = 2.6
R0_AFTER = 1.3
BAD_SICK_ODDS = 0.05
DEATH_RATE = 0.012

POPULATION = 5300000
IMMUNITY_BOOST = 1.5
LOCKUP = date(year = 2022, month = 05, day = 01)

# https://direkte.vg.no/nyhetsdognet/news/5e7c9f96930b6a0018b44505
HOSPITAL_LIMIT = 1000
FULL_HOSPITAL_MULTIPLIER = 5

TEST_PROBABILITY = 0.4
IMPORTED_TEST_BOOST = 2

import_rates = [
    (date(year = 2020, month = 03, day = 31), 0),
    (date(year = 2020, month = 03, day = 24), 25 * 2),
    (date(year = 2020, month = 03, day = 17), 120 * 2),
    (date(year = 2020, month = 03, day = 14), 125 * 3),
    (date(year = 2020, month = 03, day = 2), 13 * 2),
    (date(year = 2020, month = 02, day = 17), 0),
]

def get_r0(day, cases):
    if day <= date(year = 2020, month = 03, day = 13):
        r0 = R0_BEFORE
    elif day >= LOCKUP:
        r0 = 2.6
    else:
        r0 = R0_AFTER

    immunity_factor = (1.0 - ((cases * IMMUNITY_BOOST) / float(POPULATION)))
    return immunity_factor * r0

def get_death_rate(hospitalized):
    factor = FULL_HOSPITAL_MULTIPLIER if hospitalized > HOSPITAL_LIMIT else 1
    return (DEATH_RATE * factor) / BAD_SICK_ODDS

title = 'Norway - assuming R0 from 13. March = %s' % R0_AFTER
csv_file = 'norway.csv'
