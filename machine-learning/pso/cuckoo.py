#encoding=utf-8

import random, math

from crap import round # the base swarm model
import crap
import levy # Lévy distribution

# TUNING
alpha = 0.1  # proportion of nests to discard
scale = 0.01 # scale from Lévy number down to coordinate system

class Nest(crap.Particle):

    def __init__(self, dimensions, fitness):
        crap.Particle.__init__(self, dimensions, fitness)

    def iterate(self):
        cuckoo = self.levy_flight()
        cuckoo._update() # evaluate

        nestix = random.choice(range(len(self._swarm._particles)))
        nest = self._swarm._particles[nestix]
        if nest._val < cuckoo._val:
            nest._pos = cuckoo._pos[:]
            nest._val = cuckoo._val
            nest._update_prev()

    def levy_flight(self):
        cuckoo = self._swarm.make_particle()
        cuckoo._pos = [v + (levy.levy_distro(2.0) * scale) for v in self._pos]
        for ix in range(len(self._pos)):
            cuckoo._constrain(ix)
        return cuckoo

    def distance(self, firefly):
        dims = [(firefly._pos[ix] - v) ** 2 for (ix, v) in enumerate(self._pos)]
        return math.sqrt(sum(dims))

class Swarm(crap.Swarm):

    def __init__(self, dimensions, fitness, particles):
        crap.Swarm.__init__(self, dimensions, fitness, particles, Nest)

    def add_data(self, metadata):
        metadata.update({
            'algorithm' : 'cuckoo',
            'cuckoo_alpha' : alpha,
            'cuckoo_scale' : scale
        })
        return metadata

    def iterate(self):
        crap.Swarm.iterate(self)

        self._particles.sort(key = lambda p: -1 * p._val)
        cutoff = max(int(len(self._particles) * alpha), 1)
        self._particles = self._particles[ : -1 * cutoff]

        for ix in range(cutoff):
            self._particles.append( self.make_particle() )
