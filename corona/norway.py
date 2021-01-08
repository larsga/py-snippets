
from datetime import date, timedelta, datetime

start = date(year = 2020, month = 9, day = 1)
initial_cases = 100

BAD_SICK_ODDS = 0.03
DEATH_RATE = 0.0113

POPULATION = 5300000
IMMUNITY_BOOST = 1.5

# https://direkte.vg.no/nyhetsdognet/news/5e7c9f96930b6a0018b44505
HOSPITAL_LIMIT = 1000
FULL_HOSPITAL_MULTIPLIER = 5

TEST_PROBABILITY = 0.415
IMPORTED_TEST_BOOST = 2

import_rates = [
    (date(year = 2030, month = 12, day = 31), 0),
]

def get_r0(day):
    if day <= date(year = 2021, month = 1, day = 4):
        return 1.3
    return 1.0

def get_death_rate(hospitalized):
    factor = FULL_HOSPITAL_MULTIPLIER if hospitalized > HOSPITAL_LIMIT else 1
    return (DEATH_RATE * factor) / BAD_SICK_ODDS

title = 'Norway - assuming Re from 6. Dec = 1.1'
csv_file = 'norway.csv'
