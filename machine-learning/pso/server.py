
import json, uuid, threading, time, logging
import pso, crap, firefly, cuckoo

logger = logging.getLogger('pso')
hdlr = logging.FileHandler('pso.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

REQUIRED_EVALUATIONS = 40

from flask import Flask, request

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

app = Flask('meta-pso')

@app.route('/get-task', methods=['GET'])
def get_task():
    logger.info('GET TASK called %s' % controller.get_position())
    return json.dumps(controller.get_position())

@app.route('/answer', methods=['POST'])
def answer():
    metadata = json.loads(request.data)

    # store the data
    outf = open('results/%s.json' % uuid.uuid4(), 'w')
    outf.write(json.dumps(metadata))
    outf.close()

    pos = [metadata['cuckoo_alpha'], metadata['cuckoo_scale']]
    val = average(metadata['progress'])
    controller.add_evaluation(pos, val)

    return "OK"

# ----- MACHINERY

def average(numbers):
    return sum(numbers) / float(len(numbers))

class Controller:

    def __init__(self):
        self._pos = None
        self._evaluations = []

    def get_position(self):
        while not self._pos:
            logger.info('Waiting for a position')
            time.sleep(0.1)
        return self._pos # more complicated than this

    def fitness(self, pos):
        self._pos = pos
        self._evaluations = []

        logger.info('Evaluating %s' % pos)
        while len(self._evaluations) < REQUIRED_EVALUATIONS:
            time.sleep(0.1)

        self._pos = None
        return average(self._evaluations[:])

    def add_evaluation(self, pos, fitness):
        logger.info('pos %s fitness %s' % (pos, fitness))
        if self._pos == pos:
            self._evaluations.append(fitness)
            logger.info('Stored, %s evaluations' % len(self._evaluations))

def driver(controller):
    iterations = 100
    dimensions = [
        (0.001, 1.0), # alpha
        (0.001, 1.0), # scale
    ]
    logger.info('Dimensions: %s' % len(dimensions))
    particles = 5 #10 + int(2 * math.sqrt(len(dimensions)))
    logger.info('Particles: %s' % particles)

    implementation = pso

    for attempt in range(20):
        progress = []
        swarm = implementation.Swarm(dimensions, controller.fitness, particles)
        for ix in range(iterations):
            logger.info(str(swarm.add_data({})))
            logger.info('%s %s %s' % (ix, crap.round(swarm.get_best_ever()), '=' * 70))
            swarm.show()
            progress.append(swarm.get_best_ever())
            swarm.iterate()

        outf = open('results/%s.json' % uuid.uuid4(), 'w')
        outf.write(json.dumps(swarm.add_data({
            'problem' : 'tune-cuckoo',
            'particles' : particles,
            'dimensions': len(dimensions),
            'progress' : progress
        })) + '\n')
        outf.close()
        logger.info(str(progress))

# ----- MAIN

controller = Controller()

if __name__ == '__main__':
    t = threading.Thread(target = lambda: driver(controller))
    t.start()

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(10000)
    IOLoop.instance().start()
