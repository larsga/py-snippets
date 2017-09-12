'''
Simple implementation of a genetic algorithm, just to show the similarities
with the others. There are different ways a genetic algorithm can be
implemented. For example, using tournaments, where each individual, after
mutation, is compared with another, and the best is kept. I've experimented
with this before and it doesn't really seem to make much difference, so we
take a simpler approach here, known as (mu, lambda).

To avoid having to tune the genetic algorithm itself I let the algorithm
evolve its own meta-parameters. That gets us away from the issue of whether
the algorithm is tuned correctly, and also it's intellectually satisfiying.
'''

import random, math

from crap import round # the base swarm model
import crap

duplicate = 0.25

class Individual(crap.Particle):

    def __init__(self, dimensions, fitness):
        crap.Particle.__init__(self, dimensions, fitness)

    def iterate(self):
        # yeah, we're evolving this
        mutation_rate = self._pos[-2]
        recombination_rate = self._pos[-1]

        # recombine
        for ix in range(int(random.uniform(0, recombination_rate))):
            self._recombine()

        # mutate
        mutations = max(int(random.uniform(0, mutation_rate)), 1)
        while mutations:
            self._mutate()
            mutations -= 1

        self._update()

    def _mutate(self):
        # pick a random dimension
        d = random.choice(range(len(self._dimensions)))

        # pick a random value for it
        (low, high) = self._dimensions[d]
        self._pos[d] = random.uniform(low, high)

    def _recombine(self):
        other = random.choice(self._swarm._particles)
        for (ix, alternatives) in enumerate(zip(self._pos, other._pos)):
            self._pos[ix] = random.choice(alternatives)

    def show(self):
        l = ([round(self._val)] +
             map(round, self._pos[ : 5]) +
             [round(self._prev_best_val),
              round(self._pos[-1])]) # show the mutation rate
        print '\t'.join(map(str, l))

class Swarm(crap.Swarm):

    def __init__(self, dimensions, fitness, particles):
        # in order to evolve the mutation & recombination rate we need
        # to add those as a dimensions
        dimensions.append((1.0, math.sqrt(len(dimensions)) - 2)) # mutation
        dimensions.append((0.0, 5.0)) # recombination
        crap.Swarm.__init__(self, dimensions, fitness, particles, Individual)

    def iterate(self):
        # make a new generation
        crap.Swarm.iterate(self)

        # now, do selection
        candidates = self._particles
        candidates.sort(key = lambda p: -1 * p._val)

        # duplicate the best one
        self._particles = [self.copy(candidates[0])]

        # duplicate the best
        best = max(int(len(candidates) * duplicate), 1)
        for ix in range(best):
            self._particles.append(self.copy(candidates[ix]))

        # fill up remainder of population with survivors
        self._particles += candidates[ : len(candidates) - len(self._particles)]

        assert len(self._particles) == len(candidates) # just in case

    def add_data(self, metadata):
        metadata.update({
            'algorithm' : 'genetic',
            'genetic_duplicate' : duplicate
        })
        return metadata
