
import csv, sys, numpy

sizes = []
for row in csv.reader(open(sys.argv[1])):
    if row[1] == 'size':
        continue

    size = float(row[1])
    sizes.append(size)

# PLOT A HISTOGRAM
from matplotlib import pyplot
h = pyplot.hist(sizes, 100)
pyplot.show()
