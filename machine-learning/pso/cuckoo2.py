#encoding=utf-8
'''
It struck me that a weakness of cuckoo search would seem to be that it
always modifies all the components in the position vector. Given how
the Lévy distribution behaves, at least one component should change
dramatically.  That may be good to begin with, but once we're homing
in that's probably excessive, so why not use the mutation rate concept
from genetic algorithms (which this very nearly is, anyway), and see
if the algorithm can tune that while running.

In practice, however, this turns out not to work, because sooner or
later the top cuckoo will get a low mutation rate, and when it does
it will soon spread to all the other cuckoos (because these will be
similar to the top cuckoo, because that one has a low mutation rate
so the copies are mostly the same, and thus nearly all of them will
be superior to the lower-scoring ones).

The Lévy distribution ensures that most of the changes are really
small, and when things break the new cuckoo is in any case discarded,
so the original algorithm is in fact very good.
'''

import random
import cuckoo, crap, levy

class Nest(cuckoo.Nest):

    def levy_flight(self):
        m = int(self._pos[-1]) # mutation rate

        p = self._swarm.make_particle()
        p._pos = self._pos[:] # copy our position

        # pick m components in the vector, and change those
        for (ix, v) in random.sample(list(enumerate(self._pos)), m):
            p._pos[ix] = v + (levy.levy_distro(2.0) * cuckoo.scale)

        for ix in range(len(self._pos)):
            p._constrain(ix)
        return p

    def show(self):
        l = ([crap.round(self._val)] +
             map(crap.round, self._pos[ : 5]) +
             [crap.round(self._pos[-1])])
        print '\t'.join(map(str, l))

    def distance(self, firefly):
        # add in mutation rate as a dimension
        dims = [(firefly._pos[ix] - v) ** 2 for (ix, v) in enumerate(self._pos)]
        return math.sqrt(sum(dims))

class Swarm(cuckoo.Swarm):

    def __init__(self, dimensions, fitness, particles):
        dimensions.append((1.0, len(dimensions))) # mutation rate
        crap.Swarm.__init__(self, dimensions, fitness, particles, Nest)

    def add_data(self, metadata):
        metadata.update({
            'algorithm' : 'cuckoo2',
            'cuckoo_alpha' : cuckoo.alpha,
            'cuckoo_scale' : cuckoo.scale
        })
        return metadata
