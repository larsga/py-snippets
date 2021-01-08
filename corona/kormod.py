
import csv
from datetime import date, timedelta, datetime

start = date(year = 2020, month = 2, day = 15)
initial_cases = 1

R0_BEFORE = 2.7
R0_AFTER = 0.4
R0_LOCKUP = 0.9

BAD_SICK_ODDS = 0.03
DEATH_RATE = 0.0115
POPULATION = 5300000
IMMUNITY_BOOST = 1.5

# https://direkte.vg.no/nyhetsdognet/news/5e7c9f96930b6a0018b44505
HOSPITAL_LIMIT = 1000
FULL_HOSPITAL_MULTIPLIER = 5

TEST_PROBABILITY = 0.415
IMPORTED_TEST_BOOST = 2

import_rates = [
    (date(year = 2020, month = 04, day = 01), 0),
    (date(year = 2020, month = 03, day = 25), int(25 * 2 * 2 * 1.4)),
    (date(year = 2020, month = 03, day = 18), int(120 * 2 * 2 * 1.4)),
    (date(year = 2020, month = 03, day = 15), int(125 * 3 * 2 * 1.4)),
    (date(year = 2020, month = 03, day = 5), int(13 * 2 * 2 * 1.4)),
    (date(year = 2020, month = 02, day = 17), 0),
]

def get_r0(day):
    return kormod[day]

def get_death_rate(hospitalized):
    factor = FULL_HOSPITAL_MULTIPLIER if hospitalized > HOSPITAL_LIMIT else 1
    return (DEATH_RATE * factor) / BAD_SICK_ODDS

title = 'Norway - R estimated by KORMOD'
csv_file = 'norway.csv'

def clean(v):
    if v == 'inf':
        return None
    try:
        return float(v)
    except ValueError:
        return None

rows = [(row[0], clean(row[1])) for row in csv.reader(open('kormod-r.csv'))][1 : ]
kormod = {}
prev = R0_BEFORE
for (day, r) in rows:
    r = min(r, 3.0)
    kormod[datetime.strptime(day, '%Y-%m-%d').date()] = r or prev
    if r:
        prev = r
