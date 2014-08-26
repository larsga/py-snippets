
import datetime, csv, sys

# --- PARSE AND INTERPRET

TIMEFORMAT = '%Y-%m-%dT%H:%M:%S.000Z'

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

dataset = dataset[ix : ]

ix = len(dataset) - 1
while dataset[ix][0] > endtime:
    ix -= 1

dataset = dataset[ : ix + 1]

print dataset[0][0]
print dataset[-1][0]

# --- DO SLIDING AVERAGES

def hour(t):
    return t.replace(t.year, t.month, t.day, t.hour, 0, 0)

hours = []
counts = []
avgs = []
avgd = []

sizes = []
depths = []
current = hour(dataset[0][0])
for row in dataset:
    if hour(row[0]) == current:
        #sizes.append(10 ** row[1])
        sizes.append(row[1])
        depths.append(row[2])
    else:
        counts.append(len(sizes))
        hours.append(current)
        avgs.append(sum(sizes) / len(sizes))
        avgd.append(sum(depths) / len(depths))
        current = hour(row[0])

        count = 0
        sizes = []
        depths = []

# --- DO PLOTS

from matplotlib import dates as mdates
from matplotlib import pyplot

fig, ax = pyplot.subplots(1)
pyplot.plot(hours, counts)

fig.autofmt_xdate()
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
pyplot.title('Earthquake counts per hour')
pyplot.ylabel('Earthquakes per hour')
pyplot.xlabel('Time')

pyplot.show()

fig, ax = pyplot.subplots(1)
pyplot.plot(hours, avgs)
fig.autofmt_xdate()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
pyplot.title('Average earthquake magnitudes')
pyplot.ylabel('Average magnitude')
pyplot.xlabel('Time')
pyplot.show()

fig, ax = pyplot.subplots(1)
pyplot.plot(hours, avgd)
fig.autofmt_xdate()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
pyplot.title('Average earthquake depth')
pyplot.ylabel('Average depth')
pyplot.xlabel('Time')
pyplot.show()
