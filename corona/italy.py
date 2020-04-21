
from datetime import date, timedelta, datetime

start = date(year = 2020, month = 1, day = 20)
initial_cases = 0

R0_BEFORE = 3.5
R0_AFTER = 1.5
BAD_SICK_ODDS = 0.16
DEATH_RATE = 0.01

POPULATION = 60 * 10**6

HOSPITAL_LIMIT = 3000
FULL_HOSPITAL_MULTIPLIER = 6.5

TEST_PROBABILITY = 0.17
IMPORTED_TEST_BOOST = 2

import_rates = [
    (date(year = 2020, month = 02, day = 01), 220),
]

def get_r0(day):
    if day <= date(year = 2020, month = 03, day = 8):
        r0 = R0_BEFORE
    else:
        r0 = R0_AFTER

    return r0

def get_death_rate(hospitalized):
    factor = FULL_HOSPITAL_MULTIPLIER if hospitalized > HOSPITAL_LIMIT else 1
    return (DEATH_RATE * factor) / BAD_SICK_ODDS

title = 'Italy - assuming R0 from 8. March = %s' % R0_AFTER
csv_file = 'italy.csv'

# Italy hospitalizations
# https://www.nbcnews.com/health/health-news/italy-has-world-class-health-system-coronavirus-has-pushed-it-n1162786
