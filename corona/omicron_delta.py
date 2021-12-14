'''
Model omicron and delta development in Norway.
'''

# TODO
#  - add a Vaccine variant to get partial immunity right
#  - model positive tests

import sys
import simulate
from datetime import date, timedelta, datetime

class ExclusiveVariant(simulate.DefaultVariant):
    def __init__(self, r0, theid):
        simulate.DefaultVariant.__init__(self, r0, theid)

    def get_immunity_to(self, variant):
        if self.get_id() == variant.get_id():
            return 1.0 # nobody gets the same variant twice
        else:
            return 0.2 # each variant protects 20% against the other

delta = ExclusiveVariant(6.5, 'delta')

# I don't know what omicron's R0 is, but setting it to 6 here gives a
# growth roughly in line with gov't (FHI) projections
omicron = ExclusiveVariant(6.0, 'omicron')

def get_imports(day):
    if date(2021, 11, 20) <= day <= date(2021, 12, 15):
        return 3
    return 0

def get_r_reduction(day):
    if day > date(2021, 12, 8):
        # if day > date(2021, 12, 14):
        #     return 0.8
        return 0.37
    return 0.1

# earlier registered cases: 195,807 -> real figure perhaps 320,000
# fully vaccinated: 3,714,397
# some overlap, so let's say 3,850,000 immune

simulate.simulate(
    start = date(year = 2021, month = 10, day = 15),
    end = date(year = 2022, month = 2, day = 1),
    population_size = 5300000,
    stats_file = 'omicron-delta-1stop.json',
    already_infected = 3850000,
    start_incidence = 9000,
    start_variant = delta,
    import_variant = omicron,
    get_imports = get_imports,
    get_r_reduction = get_r_reduction,
    test_probability = 0.5,
    debug_r_on_dates = set([date(year = 2021, month = 12, day = 6),
                            date(year = 2021, month = 12, day = 10),
                            date(year = 2021, month = 12, day = 15)]),
)
