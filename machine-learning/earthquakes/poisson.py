
import datetime, csv, sys
from eqlib import *

# --- PARSE AND INTERPRET

dataset = [row for row in csv.reader(open(sys.argv[1]))]
dataset = dataset[1 : ] # ditch header
dataset = [(datetime.datetime.strptime(timestamp, TIMEFORMAT),
            float(size), float(depth), quality, lat, lng, text)
           for (timestamp, size, depth, quality, lat, lng, text)
           in dataset]

# --- CUT DOWN TO WHOLE HOURS ONLY

dataset.sort(key = lambda x: x[0])

t = dataset[0][0]
starttime = t.replace(t.year, t.month, t.day, t.hour + 1, 0, 0)

t = dataset[-1][0]
d = t.day
h = t.hour - 1
if h == -1:
    h = 23
    d = d - 1
endtime = t.replace(t.year, t.month, d, h, 59, 59, 999999)

for ix in range(len(dataset)):
    if dataset[ix][0] >= starttime:
        break

full_dataset = dataset
dataset = dataset[ix : ]

ix = len(dataset) - 1
while dataset[ix][0] > endtime:
    ix -= 1

dataset = dataset[ : ix + 1]

# print dataset[0][0]
# print dataset[-1][0]

# --- DO SLIDING AVERAGES

def hour(t):
    return t.replace(t.year, t.month, t.day, t.hour, 0, 0)

counts = []
sizes = []
current = hour(dataset[0][0])
for row in dataset:
    if hour(row[0]) == current:
        sizes.append(row[1])
    else:
        counts.append(len(sizes))
        current = hour(row[0])

        count = 0
        sizes = []

# --- ESTIMATE POISSON

import numpy
import scipy.stats

mean = numpy.mean(counts)
#print 'mean:', mean
p = scipy.stats.poisson(mean)

# for count in counts:
#     print '%s quakes, prob %s' % (count, p.pmf(count))

# --- LOAD PREVIOUS WARNED-ABOUT EVENTS

previously = load_previously('previous-windows.txt',
                             lambda line: datetime.datetime.strptime(line, TIMEFORMAT))

# --- NOW FOR N-EVENT WINDOW

n = 30
prev_alert = datetime.datetime(1999, 1, 1, 0, 0, 0)

for ix in range(len(full_dataset) - n):
    timewindow = full_dataset[ix + n][0] - full_dataset[ix][0]

    # n events in this number of seconds gives what hourly rate?
    hourly_rate = n * (3600.0 / timewindow.total_seconds())

    # print timewindow
    # print '  ', 3600.0 / timewindow.total_seconds()
    # print '  ', n * (3600.0 / timewindow.total_seconds())
    # print '  ', p.pmf(int(hourly_rate))

    if p.pmf(int(hourly_rate)) < 10.0 ** -6:
        if (full_dataset[ix][0] - prev_alert).total_seconds() >= 600 and \
           full_dataset[ix][0] not in previously:
            print full_dataset[ix][0]
            print '  ', timewindow
            print '  ', 3600.0 / timewindow.total_seconds()
            print '  ', n * (3600.0 / timewindow.total_seconds())
            print '  ', p.pmf(int(hourly_rate))

            seen('previous-windows.txt',
                 full_dataset[ix][0].strftime(TIMEFORMAT))

        prev_alert = full_dataset[ix][0]

# --- HAS ACTIVITY STOPPED?

cacheend = datetime.datetime.utcnow() - datetime.timedelta(minutes = 10)
lastq = full_dataset[-1][0]

if cacheend < lastq:
    sys.exit(0) # no worries

secs = (cacheend - lastq).total_seconds()
perhour = 3600 / float(secs)

if perhour > mean:
    # no reason to think we've stopped yet
    sys.exit(0)

prob = p.pmf(int(perhour))

if prob < 10 ** -10:
    print '%s per hour, mean: %s' % (perhour, mean)
    print '%s secs with no events' % secs
    print cacheend
    print lastq
    print '%s probability' % prob
