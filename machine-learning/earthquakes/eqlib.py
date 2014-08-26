'''
Reusables snippets for the earthquake data.
'''

TIMEFORMAT = '%Y-%m-%dT%H:%M:%S.000Z'

def load_previously(filename, transform = lambda x: x):
    try:
        previously = set()
        for line in open(filename):
            line = line.strip()
            previously.add(transform(line))
    except IOError, e:
        if e.errno != 2:
            raise e

    return previously

def seen(filename, line):
    outf = open(filename, 'a')
    outf.write(line + '\n')
    outf.close()
