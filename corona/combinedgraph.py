
import json, sys, csv
from matplotlib import pyplot as plt
from datetime import date, timedelta, datetime

START = datetime(year = 2021, month = 6, day = 1)
END   = datetime(year = 2021, month = 11, day = 1)

def parse_date(s):
    return datetime.strptime(s, '%Y-%m-%d')

def simplify(sim):
    return [(parse_date(day), data['new_cases_today'], data['new_cases_mutants'], data['DEAD'], data['hospitalized'], data['new_positives_today'])
            for (day, data) in sim]

def average(numbers):
    return sum(numbers) / float(len(numbers))

def load_file(filename):
    simulations = json.load(open(filename))
    simulations = [simplify(sim) for sim in simulations]
    by_day = []
    for ix in range(len(simulations[0])):
        date = simulations[0][ix][0]

        if date < START or date >= END:
            continue

        new_today = average([
            sim[ix][1] for sim in simulations
        ])
        new_mutants = average([
            sim[ix][2] for sim in simulations
        ])
        dead = average([
            sim[ix][3] for sim in simulations
        ])
        hospitalized = average([
            sim[ix][4] for sim in simulations
        ])
        positive = average([
            sim[ix][5] for sim in simulations
        ])
        by_day.append((date, new_today, new_mutants, dead, hospitalized, positive))

    dates = [date for (date, new_t, new_m, dead, _, _) in by_day]
    new_today = [new_t for (date, new_t, new_m, dead, _, _) in by_day]
    new_mutants = [new_m for (date, new_t, new_m, dead, _, _) in by_day]
    dead = [dead for (date, new_t, new_m, dead, _, _) in by_day]
    hospitalized = [h for (date, new_t, new_m, _, h, _) in by_day]
    positive = [p for (date, new_t, new_m, _, h, p) in by_day]

    return (dates, new_today, new_mutants, dead, hospitalized, positive)

def average(values):
    return sum(values) / float(len(values))

def smooth_average(rows, fields):
    by_date = {row['date'] : row.copy() for row in rows}

    smoothed = []
    for row in rows:
        for field in fields:
            values = [by_date.get(row['date'] + timedelta(days = offset), {}).get(field, None)
                      for offset in range(-3, 4)]
            values = filter(lambda x: x!=None, values)
            if len(values) == 7:
                row[field] = average(values)
            else:
                row[field] = None

        smoothed.append(row)

    return smoothed

def plot_csv(basefile, plots):
    # load and transform
    data = [row for row in csv.DictReader(open(basefile + '.csv'))]
    for row in data:
        row['date'] = datetime.strptime(row['date'], '%Y-%m-%d')
        for key in row.keys():
            if key != 'date':
                row[key] = int(row[key]) if row[key] != '_' else None

    rows = smooth_average(data, set([field for (field, _, _, smooth) in plots
                                     if smooth]))

    # okay
    rows = [row for row in rows if row['date'] >= START and row['date'] < END]
    if not rows:
        return

    dates = [row['date'] for row in rows]
    for (field, color, title, _) in plots:
        values = [row[field] for row in rows]
        ax1.plot(dates, values, color + '.', label = title)

def plot(filename, title, modifier, show_cases = True, show_dead = True,
         show_hospitalized = False, show_positives = False,
         show_mutants = False, show_non_mutants = False,
         show_ri = False, show_re = False):
    (dates, cases, new_mutants, dead, hospitalized, positives) = load_file('%s.json' % filename)

    if show_cases:
        ax1.plot(dates, cases, 'c' + modifier, label = 'New cases/day, ' + title)
    if show_mutants:
        ax1.plot(dates, new_mutants, 'g' + modifier, label = 'New mutants/day, ' + title)
    if show_non_mutants:
        ax1.plot(dates, [new_cases - mutants for (new_cases, mutants) in
                         zip(cases, new_mutants)
        ], 'c' + modifier, label = 'New non-mutants/day, ' + title)

    if show_positives:
        ax1.plot(dates, positives, 'b' + modifier, label = 'Positive tests/day, ' + title)

    if show_dead:
        ax1.plot(dates, dead, 'r' + modifier, label = 'Accum dead, ' + title)

    if show_hospitalized:
        ax1.plot(dates, hospitalized, 'C1' + modifier, label = 'Hospitalized, ' + title)

    if show_ri or show_re:
        ax2 = ax1.twinx()
        ax2.set_ylabel('R')
        plt.legend(loc='upper right')

        # this bit is fucked up
        data = json.load(open(filename + '.json'))[0]
        data = [(parse_date(day), obj) for (day, obj) in data]

    if show_ri:
        the_r = [obj['Ri'] for (day, obj) in data
                 if day >= START and  day < END]
        ax2.plot(dates, the_r, 'C2' + modifier, label = 'Ri')

    if show_re:
        the_r = [obj['Re'] for (day, obj) in data
                 if day >= START and  day < END]
        ax2.plot(dates, the_r, 'C3' + modifier, label = 'Re')

def plot_r(filename, modifier = ''):
    data = json.load(open(filename + '.json'))[0]
    data = [(parse_date(day), obj) for (day, obj) in data]
    dates = [day for (day, obj) in data
             if day >= START and  day < END]
    the_r = [obj['Re'] for (day, obj) in data
             if day >= START and  day < END]

    ax2 = ax1.twinx()
    ax2.set_ylabel('Re')
    plt.legend(loc='upper right')
    ax2.plot(dates, the_r, 'C2' + modifier, label = 'R')

# =====

fig, ax1 = plt.subplots()

dead = True
plot('1', '', '', show_cases = True,
     show_dead = dead, show_hospitalized = True, show_positives = True,
     show_ri = True, show_re = True)
# plot('0.4', 'base R=0.4', '--', show_cases = False,
#      show_dead = dead, show_hospitalized = True, show_positives = True)
# plot('0.7', 'base R=0.7', ':', show_cases = False,
#      show_dead = dead, show_hospitalized = True, show_positives = True)
# plot('0.7b', 'base R=0.7 + lockdown Mar 26', ':', show_cases = False,
#      show_dead = dead, show_hospitalized = True, show_positives = True)
# plot('0.1', 'base R=0.1', ':', show_cases = True,
#      show_dead = dead, show_hospitalized = True, show_positives = True)

# plot('0.6-2', 'base R=0.6 from Mar 9', '', show_cases = False,
#      show_dead = dead, show_hospitalized = True, show_positives = True)

plot_csv('norway-2021',
         [('positives',    'g',  'VG positives/day 7-day avg', True),
          #('hospitalized', 'C1', 'FHI hospitalized',            False),
         ]
)

# plot('0.6', '', '', show_cases = True,
#      show_dead = dead, show_hospitalized = False, show_positives = False,
#      show_mutants = True, show_non_mutants = True)

# plot_r('0.1')

plt.title('Norway, August 2021')

# =====

plt.legend(loc='upper left')
plt.show()
