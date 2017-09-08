'''
Test driver to apply the algorithms to a toy problem.
'''

import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import random

def f1(x):
    return 1 + math.sin(2 * np.pi * x)

def f2a(x):
    return x ** 3 - 2 * x ** 2 + 1 * x - 1

def f2(x):
    return 1 + math.cos(2 * np.pi * x)

def f(x):
    return f1(x) + f2a(x)

colours = cm.rainbow(np.linspace(0, 1, 5))

count = 0
def plot(x, y):
    global count

    t = np.arange(0.0, 2.0, 0.01)
    s = [f(v) for v in t]
    plt.plot(t, s)

    #x = [random.uniform(0.0, 2.0) for ix in range(5)]
    #y = [f(v) for v in x]

    plt.plot(x, y, 'go')

    #plt.xlabel('time (s)')
    #plt.ylabel('voltage (mV)')
    plt.title('Iteration #%s' % count)
    plt.grid(True)

    count += 1
    plt.savefig("test%s.png" % str(count).zfill(3))

    #plt.show()
    plt.close()

import pso, crap, firefly, cuckoo

def show(swarm):
    x = [p._pos[0] for p in swarm._particles]
    y = [p._val for p in swarm._particles]
    swarm.show()
    plot(x, y)

swarm = cuckoo.Swarm(
    dimensions = [(0.0, 2.0)],
    fitness = lambda x: f(x[0]),
    particles = 5
)

for ix in range(20):
    print '=' * 75
    show(swarm)
    swarm.iterate()

# results = []
# for attempt_no in range(1000):
#     swarm = firefly.Swarm(
#         dimensions = [(0.0, 2.0)],
#         fitness = lambda x: f(x[0]),
#         particles = 5
#     )

#     values = []
#     for ix in range(20):
#         values.append(swarm.get_best_ever())
#         swarm.iterate()

#     print values[-1]
#     results.append(values)

# finals = [r[-1] for r in results]
# print 'Average:', sum(finals) / len(finals)

# all topology: 1.43, 1.44, 1.49
# ring topology: 1.5, 1.5, 1.5
# 10 particles: 1.72, 1.71
# crap: 1.89, 1.89, 1.89, 1.88
# firefly: 1.93, ...
