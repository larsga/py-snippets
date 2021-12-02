
import re, csv
from datetime import date, timedelta, datetime

start = date(year = 2021, month = 6, day = 1)
stop = date(year = 2021, month = 11, day = 1)
initial_cases = 1200

PREVIOUSLY_INFECTED = 125563 # ie, before start date

BAD_SICK_ODDS = 0.01
# we reduce the death rate from the paper by this empirical factor...
DEATH_DAMPER = 0.4 * 0.6

POPULATION = 5300000
IMMUNITY_BOOST = 1.5

# https://direkte.vg.no/nyhetsdognet/news/5e7c9f96930b6a0018b44505
HOSPITAL_LIMIT = 1000
FULL_HOSPITAL_MULTIPLIER = 1

TEST_PROBABILITY = 0.7
IMPORTED_TEST_BOOST = 2
MUTANT_R_FACTOR = 0.5
MUTANT_BAD_OUTCOME_BOOST = 1.6

VACCINATION_SKEPTICS = 0.1
VACCINE_SPEED = 3.7
# alle over 18: 4183831
# alle over 16: 4303931
# alle over 12: 4543931
MAX_DOSES = 4543931 * (1.0 - VACCINATION_SKEPTICS) # alle over 12
MAX_DOSES = 4303931 * (1.0 - VACCINATION_SKEPTICS) # alle over 16
VACCINATION_START = date(year = 2021, month = 1, day = 1)
VACCINATION_END = date(year = 2021, month = 10, day = 30)

import_rates = [
    (date(year = 2020, month = 9, day = 15), 9, False),
    (date(year = 2020, month = 12, day = 31), 0, False),
    (date(year = 2021, month = 1, day = 1), 60, True),
    (date(year = 2030, month = 12, day = 31), 0, False),
]

_ = date(year = 2031, month = 3, day = 17)
R0 = [
    (1.25 * 2, date(year = 2021, month = 7, day = 1)), # r0 until date
    (1.35 * 2, date(year = 2021, month = 7, day = 7)), # r0 until date
    (1.70 * 2, date(year = 2021, month = 7, day = 15)), # r0 until date
    (2.10 * 2, date(year = 2021, month = 8, day = 15)), # r0 until date
    (3.00 * 2, _),
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
        self._start_date = VACCINATION_START
        self._stop_date = VACCINATION_END
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

# Source https://www.ssb.no/statbank/table/10211/
age_bands = [
    (100, 1119),
    (95, 9661),
    (90, 34450),
    (85, 71765),
    (80, 113715),
    (75, 176382),
    (70, 259452),
    (65, 275272),
    (60, 307223),
    (55, 331899),
    (50, 371931),
    (45, 376148),
    (40, 347515),
    (35, 356323),
    (30, 374224),
    (25, 370923),
    (20, 340829),
    (15, 318622),
    (10, 324769),
    (5, 315295),
    (0, 290063)
]

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
