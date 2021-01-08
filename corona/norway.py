
from datetime import date, timedelta, datetime

start = date(year = 2020, month = 2, day = 15)
initial_cases = 1

R0_BEFORE = 2.7
R0_AFTER = 0.4
R0_LOCKUP = 0.53
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
    (date(year = 2020, month = 12, day = 31), 0),
    (date(year = 2020, month = 10, day = 31), 25),
    (date(year = 2020, month = 10, day = 5), 10),
    (date(year = 2020, month = 9, day = 15), 0),
    #(date(year = 2020, month = 04, day = 01), 0),
    (date(year = 2020, month = 03, day = 25), int(25 * 2 * 2 * 1.4)),
    (date(year = 2020, month = 03, day = 18), int(120 * 2 * 2 * 1.4)),
    (date(year = 2020, month = 03, day = 15), int(125 * 3 * 2 * 1.4)),
    (date(year = 2020, month = 03, day = 5), int(13 * 2 * 2 * 1.4)),
    (date(year = 2020, month = 02, day = 17), 0),
]

def get_r0(day):
    if day <= date(year = 2020, month = 03, day = 13):
        r0 = R0_BEFORE
    elif day <= date(year = 2020, month = 03, day = 15):
        r0 = 1.4 # people infecting others in same household

    # second wave
    elif day >= date(year = 2020, month = 10, day = 29):
        r0 = 1.3
    elif day >= date(year = 2020, month = 10, day = 26):
        r0 = 1.6
    elif day >= date(year = 2020, month = 9, day = 15):
        r0 = 2.1
    elif day >= date(year = 2020, month = 9, day = 7):
        r0 = 1.5
    # elif day >= date(year = 2020, month = 8, day = 1):
    #     r0 = 1.3

    elif day >= date(year = 2020, month = 05, day = 19):
        r0 = R0_LOCKUP + 0.4 # lockup going even further
    elif day >= date(year = 2020, month = 05, day = 13):
        r0 = R0_LOCKUP + 0.2 # lockup going even further
    elif day >= date(year = 2020, month = 04, day = 27):
        r0 = R0_LOCKUP # lockup going too far

    # SPECIAL EASTER RATE
    # elif day in (date(year = 2020, month = 04, day = 04),
    #              date(year = 2020, month = 04, day = 05),
    #              date(year = 2020, month = 04, day = 9),
    #              date(year = 2020, month = 04, day = 10),
    #              date(year = 2020, month = 04, day = 11),
    #              date(year = 2020, month = 04, day = 12)):
    #     r0 = 1.3 # easter weekend infection rate

    # elif day >= date(year = 2020, month = 05, day = 11):
    #     r0 = R0_AFTER
    # elif day >= date(year = 2020, month = 04, day = 20):
    #     r0 = 1.3
    # elif day >= date(year = 2020, month = 04, day = 27):
    #     r0 = 1.5
    else:
        r0 = R0_AFTER

    return r0

def get_death_rate(hospitalized):
    factor = FULL_HOSPITAL_MULTIPLIER if hospitalized > HOSPITAL_LIMIT else 1
    return (DEATH_RATE * factor) / BAD_SICK_ODDS

title = 'Norway - assuming Re from 29. October = 1.3'
csv_file = 'norway.csv'
