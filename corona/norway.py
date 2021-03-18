
import re, csv
from datetime import date, timedelta, datetime

start = date(year = 2020, month = 9, day = 1)
stop = date(year = 2021, month = 5, day = 1)
initial_cases = 60

BAD_SICK_ODDS = 0.01
# we reduce the death rate from the paper by this empirical factor...
DEATH_DAMPER = 0.4 * 0.6

POPULATION = 5300000
IMMUNITY_BOOST = 1.5

# https://direkte.vg.no/nyhetsdognet/news/5e7c9f96930b6a0018b44505
HOSPITAL_LIMIT = 1000
FULL_HOSPITAL_MULTIPLIER = 5

TEST_PROBABILITY = 0.7
IMPORTED_TEST_BOOST = 2
MUTANT_R_BOOST = 0.5
MUTANT_BAD_OUTCOME_BOOST = 1.6

VACCINATION_SKEPTICS = 0.3
VACCINE_SPEED = 3.3
# alle over 18 innen slutten av august: 4183831
MAX_DOSES = 4183831 * (1.0 - VACCINATION_SKEPTICS)

import_rates = [
    (date(year = 2020, month = 9, day = 15), 9, False),
    (date(year = 2020, month = 12, day = 31), 0, False),
    (date(year = 2021, month = 1, day = 1), 60, True),
    (date(year = 2030, month = 12, day = 31), 0, False),
]

_ = date(year = 2031, month = 3, day = 17)
R0 = [
    (1.155, date(year = 2021, month = 1, day = 1)), # r0 until date
    (0.80, date(year = 2021, month = 1, day = 29)),
    (1.00, date(year = 2021, month = 3, day = 9)),
    (0.85, date(year = 2021, month = 3, day = 17)),
    (0.70, date(year = 2021, month = 3, day = 26)),
    (0.50, _),
]

def get_r0(day):
    for (rate, end) in R0:
        if day <= end:
            return rate

def get_death_rate(hospitalized, vaccinated):
    factor = FULL_HOSPITAL_MULTIPLIER if hospitalized > HOSPITAL_LIMIT else 1
    return (ifr(vaccinated) / 100.0) * factor * DEATH_DAMPER

class VaccinationProgram:

    def __init__(self):
        self._start_date = date(year = 2021, month = 1, day = 1)
        self._stop_date = date(year = 2021, month = 8, day = 31)
        self._vacc_per_day = 2450 * VACCINE_SPEED
        self._vacc_rate_inc = ((16500-2450) / (11.0 * 30)) * VACCINE_SPEED

        self._dose_one = 0
        self._dose_two = 0
        self._dose_one_buffer = [0] * 21
        self._dose_two_buffer = [0] * 7

    def do_vaccinations(self, day):
        if day < self._start_date:
            return 0

        doses = int(self._vacc_per_day) if day <= self._stop_date and self._dose_one < MAX_DOSES else 0
        self._vacc_per_day += self._vacc_rate_inc

        # how many doses do we set as first and second dose?
        second = self._dose_one_buffer.pop(0)
        first = max(doses - second, 0)

        self._dose_one += self._dose_one_buffer[14]
        self._dose_two += self._dose_two_buffer.pop(0)
        self._dose_one_buffer.append(first)
        self._dose_two_buffer.append(second)

        return doses

    def get_effectively_vaccinated(self):
        only_one = self._dose_one - self._dose_two
        return only_one * 0.33 + self._dose_two * 0.95

title = 'Norway - with B117 + vaccinations'
csv_file = 'norway.csv'

# --- population age structure

REG_AGE = re.compile('(\d+)(-| ).*')
def parse_age(alder):
    return int(REG_AGE.match(alder).group(1))

age_bands = [(parse_age(row['alder']), int(row['Personer 2020']))
    for row in csv.DictReader(open('Personer.csv'), delimiter = ';')
]
age_bands.reverse()

def get_adjusted_age_bands(vaccinated):
    bands = []
    for (low_age, count) in age_bands:
        max_vacc = count * (1 - VACCINATION_SKEPTICS)
        if max_vacc < vaccinated:
            vaccinated -= max_vacc
            bands.append((low_age, count - max_vacc)) # unvaccinated remaind
        elif vaccinated > 0:
            bands.append((low_age, count - vaccinated))
            vaccinated = 0
        else:
            bands.append((low_age, count))
    return bands

def ifr(vaccinated): # RETURNS %, NOT FRACTION!!!
    adjusted_age_bands = get_adjusted_age_bands(vaccinated)

    total = sum(count for (age, count) in adjusted_age_bands)
    if total == 0:
        return 0
    weighted_sum = 0
    for (age, count) in adjusted_age_bands:
        if age < 35:
            ifr = 0.004
        elif age < 45:
            ifr = 0.068
        elif age < 55:
            ifr = 0.23
        elif age < 65:
            ifr = 0.75
        elif age < 75:
            ifr = 2.5
        elif age < 85:
            ifr = 8.5
        else:
            ifr = 28.3

        weighted_sum += ifr * count
    return (weighted_sum / total)
