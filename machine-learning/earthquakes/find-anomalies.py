'''
Load earthquake data, find quakes above 99.8 percentile in size. Display
only ones not reported before.
'''

import csv, sys, numpy
from eqlib import *

previously = load_previously('previous-quakes.txt')

sizes = []
for row in csv.reader(open(sys.argv[1])):
    if row[1] == 'size':
        continue

    size = float(row[1])
    sizes.append(size)

#print 'avg', numpy.mean(sizes)
#print 'stddev', numpy.std(sizes)
threshold = numpy.percentile(sizes, 99.8)
#print 'percentile', threshold

for row in csv.reader(open(sys.argv[1])):
    if row[1] == 'size':
        continue

    size = float(row[1])
    if size >= threshold and row[0] not in previously:
        print row
        seen('previous-quakes.txt', row[0])
