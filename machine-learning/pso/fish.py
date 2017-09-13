
import random

from crap import round # the base swarm model
import crap

# Implemented as described in https://en.wikipedia.org/wiki/Fish_School_Search
step_ind = 0
step_vol = 0
w_scale = 0

class Fish(crap.Particle):

    def __init__(self, dimensions, fitness):
        crap.Particle.__init__(self, dimensions, fitness)
        self._weight = w_scale / 2.0
        self._prev_val = self._val

    def iterate(self):
        newpos = [v + (random.uniform(-1, 1) * self._swarm._step_ind)
                  for v in self._pos]
        newval = self._fitness(newpos) # 6. Calculate fitness again
        if newval > self._val:
            self._pos = newpos
            self._val = newval

    def val_diff(self):
        return self._val - self._prev_val

    def _feed(self, biggest):
        new_weight = self._weight + self.val_diff() / biggest
        self._weight = max(1, min(w_scale / 2.0, new_weight))

class Swarm(crap.Swarm):

    def __init__(self, dimensions, fitness, particles):
        crap.Swarm.__init__(self, dimensions, fitness, particles, Fish)
        self._step_ind = step_ind
        self._step_vol = step_vol

    def iterate(self):
        # 5. Individual operator movement (&6)
        for p in self._particles:
            p.iterate()

        # 7. Run feeding operator
        biggest = abs(reduce(max, [p.val_diff() for p in self._particles]))
        for p in self._particles:
            self._feed(biggest)

        # 8. Collective-instinctive
        sum_delta_fitness = sum([p.val_diff() for p in self._particles])
        I = [(sum([p.pos_diff(ix) * p.val_diff() for p in self._particles]) /
              sum_delta_fitness) for ix in len(self._dimensions)]
        for p in self._particles:
            p._move(I)

        # 9. Collective-volitive
        sum_weights = sum([p._weight for p in self._particles])
        #barycenter = [

        # update fitness
        self._update()

    def _collective_instinctive(self):

    def _individual_movement(self):

        pass # decay the two steps

    def add_data(self, metadata):
        metadata.update({
            'algorithm' : 'fish',
            'step_ind' : step_ind,
            'step_vol' : step_vol
        })
        return metadata
