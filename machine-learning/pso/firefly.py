
import random, math

from crap import round # the base swarm model
import crap

# TUNING
alpha = 0.08 # randomness
beta  = 1.0  # scale
gamma = 3.0 # brightness decay

class Firefly(crap.Particle):

    def __init__(self, dimensions, fitness):
        crap.Particle.__init__(self, dimensions, fitness)

    def iterate(self):
        for firefly in self._swarm.get_particles():
            if self._val < firefly._val:
                dist = self.distance(firefly)
                attract = firefly._val / (1 + gamma * (dist ** 2)) * beta

                #print 'jiggle %s, attract %s, dist %s' % (jiggle, attract, dist)

                for ix in range(len(self._dimensions)):
                    jiggle = alpha * (random.uniform(0, 1) - 0.5)
                    diff = firefly._pos[ix] - self._pos[ix]
                    #print '  ', ix, 'jump', jiggle + (attract * diff)
                    self._pos[ix] = self._pos[ix] + jiggle + (attract * diff)
                    self._constrain(ix)

        self._update()

    def distance(self, firefly):
        dims = [(firefly._pos[ix] - v) ** 2 for (ix, v) in enumerate(self._pos)]
        return math.sqrt(sum(dims))

class Swarm(crap.Swarm):

    def __init__(self, dimensions, fitness, particles):
        crap.Swarm.__init__(self, dimensions, fitness, particles, Firefly)

    def add_data(self, metadata):
        metadata.update({
            'algorithm' : 'firefly',
            'firefly_alpha' : alpha,
            'firefly_beta' : beta,
            'firefly_gamma' : gamma
        })
        return metadata
