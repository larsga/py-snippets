
import random, threading, Queue

THREADS = 8

def round(x, r = round):
    return r(x * 1000) / 1000.0

class Particle:

    def __init__(self, dimensions, fitness):
        self._dimensions = dimensions
        self._fitness = fitness

        self._pos = [random.uniform(min, max) for (min, max) in dimensions]
        self._val = self._fitness(self._pos)
        self._prev_best_val = self._val
        self._prev_best_pos = self._pos[:]

    def iterate(self):
        self._pos = [random.uniform(min, max) for (min, max) in self._dimensions]
        self._update()

    def _update(self):
        self._val = self._fitness(self._pos)
        self._update_prev()

    def _update_prev(self):
        if self._val > self._prev_best_val:
            self._prev_best_val = self._val
            self._prev_best_pos = self._pos[:]

    def _constrain(self, ix):
        self._pos[ix] = min(max(self._pos[ix], self._dimensions[ix][0]),
                            self._dimensions[ix][1])

    def show(self):
        l = ([round(self._val)] +
             map(round, self._pos[ : 5]) +
             [round(self._prev_best_val)])
        print '\t'.join(map(str, l))


def iterate_particles(queue):
    while not queue.empty():
        try:
            p = queue.get(block = False)
            p.iterate()
        except queue.Empty:
            break

class Swarm:

    def __init__(self, dimensions, fitness, particles, factory = Particle):
        self._dimensions = dimensions
        self._fitness = fitness
        self._factory = factory

        self._particles = [self.make_particle()
                           for x in range(particles)]

    def make_particle(self):
        p = self._factory(self._dimensions, self._fitness)
        p._swarm = self
        return p

    def get_particles(self):
        return self._particles

    def iterate(self):
        for p in self._particles:
            p.iterate()

    # def iterate(self):
    #     queue = Queue.Queue()
    #     for p in self._particles:
    #         queue.put(p)

    #     threads = [threading.Thread(target = iterate_particles,
    #                                 args = (queue, ))
    #                for ix in range(THREADS)]
    #     for t in threads:
    #         t.start()
    #     for t in threads:
    #         t.join()

    def show(self):
        for p in self._particles:
            p.show()

    def get_best_ever(self):
        return reduce(lambda x, y: max(x, y),
                      [p._prev_best_val for p in self._particles])


    def add_data(self, metadata):
        metadata.update({
            'algorithm' : 'crap'
        })
        return metadata
