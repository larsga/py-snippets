
import operator, random
from math import sin, pi, cos, sqrt

def michaelwicz(pos, m = 10):
    parts = [sin(pos[i]) * sin((i * pos[i] * pos[i]) / pi) ** (2*m)
             for i in range(len(pos))]
    return sum(parts)

def product(numbers):
    return reduce(operator.mul, numbers)

def griewangk(pos):
    # function as given in Pham 2005 (given as griewangk3 in JSON files)
    s = sum([(x*x) / 4000.0 for x in pos])
    p = product([cos(x / sqrt(i + 1)) for (i, x) in enumerate(pos)])
    return 1 / (0.1 + (s - p) + 1)

    # function as given in Yang 2010
    # return -1 * (
    #     (1/4000.0) *
    #     sum([v * v for v in pos]) *
    #     product([cos(v / sqrt(i + 1)) + 1 for (i, v) in enumerate(pos)])
    # )
    # not a good test function because it has lots of minima that are very
    # close to 0, and these are easily found by random trial

def rosenbrock(pos):
    return -1 * sum([(1 - v) ** 2 + 100 * (pos[i+1] - v ** 2) ** 2
                     for (i, v) in enumerate(pos[: -1])])

# for ix in range(10):
#     pos = [random.uniform(0, 2) for i in range(16)]
#     print pos
#     print rosenbrock(pos)

# print rosenbrock([1] * 16)

# print griewangk([0] * 10)
# print griewangk([1] * 10)
# print griewangk([10] * 10)
# print griewangk([512] * 10)
# print griewangk([random.uniform(-512, 512) for x in range(10)])
