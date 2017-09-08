
import random

from crap import round # the base swarm model
import crap

# TUNING (parameters from
# Maurice Clerc. Standard Particle Swarm Optimisation. 15 pages. 2012.
# <hal-00764996>)
w = 0.721 # decay factor
c = 1.193 # random speed

def pick_velocity(min, max):
    magnitude = max / 10.0
    return random.uniform(-1 * magnitude, magnitude)

def mod(n, size):
    if n < 0:
        return size + n
    return n % size

class Particle(crap.Particle):

    def __init__(self, dimensions, fitness):
        crap.Particle.__init__(self, dimensions, fitness)

        self._vel = [pick_velocity(min, max) for (min, max) in dimensions]
        self._neighbours = []

    def set_neighbours(self, neighbours):
        self._neighbours = neighbours

    def iterate(self):
        for ix in range(len(self._dimensions)):
            self._vel[ix] = (
                self._vel[ix] * w +
                random.uniform(0, c) * (self._prev_best_pos[ix] - self._pos[ix]) +
                random.uniform(0, c) * (self.neighbourhood_best(ix) - self._pos[ix])
            )

            self._pos[ix] = self._pos[ix] + self._vel[ix]
            self._constrain(ix)

        self._update()

    def neighbourhood_best(self, ix, debug = False):
        best = self
        val = self._prev_best_val

        for p in self._neighbours:
            if p._prev_best_val > val:
                best = p
                val = p._prev_best_val

        return best._prev_best_pos[ix]

    def show(self):
        l = [round(self._val),
             round(self._pos[0]),
             round(self._vel[0]),
             round(self.neighbourhood_best(0)),
             round(self._prev_best_val),
             round(self._prev_best_pos[0])]
        print '\t'.join(map(str, l))

class Swarm(crap.Swarm):

    def __init__(self, dimensions, fitness, particles):
        crap.Swarm.__init__(self, dimensions, fitness, particles, Particle)

        # all topology
        # for p in self._particles:
        #     p.set_neighbours(self._particles)

        # ring topology
        for (ix, p) in enumerate(self._particles):
            p.set_neighbours([
                self._particles[mod(ix - 1, particles)],
                p,
                self._particles[mod(ix + 1, particles)]
            ])

    def add_data(self, metadata):
        metadata.update({
            'algorithm' : 'pso',
            'pso_w' : w,
            'pso_c' : c
        })
        return metadata
