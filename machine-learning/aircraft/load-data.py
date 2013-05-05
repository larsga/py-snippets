'''
This script loads and cleans the data, then performs clustering on it.

To try it, just run it.

This source code is really messy. My apologies for that.
'''

import re, random, math
from pprint import pprint

REG_INTEGER = re.compile('\d+(,\d+)?')
REG_FLOAT = re.compile('\d+(.\d+)?')
REG_MACH = re.compile('Mach \d(\\.\d+)?', re.IGNORECASE)
REG_KMH = re.compile('\d+(,\d+)?(\\.\d+)? ?km/h')
REG_MPH = re.compile('\d+(,\d+)?(\\.\d+)? ?mph')
REG_WEIGHT = re.compile('\d+(,\d+)?(\\.\d+)? ?(kg|lb)')
REG_LENGTH_M = re.compile('\d+(,\d+)?(\\.\d+)? ?m')
REG_LENGTH_FT = re.compile('\d+(,\d+)?(\\.\d+)? ?ft')

def identity(v):
    return v

def clean_int(v):
    v = v.lower()
    if v.startswith('one'):
        return 1
    if v.startswith('two'):
        return 3
    if v.startswith('three'):
        return 3
    if v.startswith('four'):
        return 3
    if v.startswith('five'):
        return 5
    if v.startswith('six'):
        return 6
    if v.startswith('ten'):
        return 10
    if v.startswith('twelve'):
        return 12
    if v in ('none', '?', 'unknown'):
        return None
    
    m = REG_INTEGER.search(v)
    if not m:
        print v
    v = m.group()
    v = v.replace(',', '')
    return int(v)

def clean_float(v):
    m = REG_FLOAT.search(v)
    if not m:
        print v
    v = float(m.group())
    if v > 100000.0: # bigger than 100,000 is deeply unlikely
        return None # we really don't believe this, sorry
    return v

def clean_float_unit(v):
    if v.endswith('m'):
        try:
            return float(v[ : -1].strip())
        except ValueError:
            pass
    
    # print repr(v)

def clean_speed_mph(v):
    return float(v) * 1.609
        
def clean_speed_unit(v):
    m = REG_KMH.search(v)
    if m:
        return float(m.group()[ : -4].strip().replace(',', ''))
    m = REG_MPH.search(v)
    if m:
        return float(m.group()[ : -3].strip().replace(',', '')) * 1.6
    m = REG_MACH.search(v)
    if m:
        return float(m.group()[5 : ].strip().replace(',', '')) * 1225

    # try:
    #     float(v)
    # except:
    #     print repr(v)

def clean_weight_unit(v):
    m = REG_WEIGHT.search(v)
    if m:
        value = float(m.group()[ : -2].strip().replace(',', ''))
        if v[-2 : ] == 'lb':
            value = value * 0.4536
        return value

    # try:
    #     float(v)
    # except:
    #     print repr(v)

def clean_length(v):
    m = REG_LENGTH_FT.search(v)
    if m:
        return float(m.group()[ : -2].strip().replace(',', '')) * 0.3048
    m = REG_LENGTH_M.search(v)
    if m:
        return float(m.group()[ : -1].strip().replace(',', ''))

    # try:
    #     float(v)
    # except:
    #     print repr(v)
    
def show(v):
    print repr(v)

CLEAN = [
    ('http://dbpedia.org/property/numberBuilt', 'number_built', clean_int),
    ('http://www.w3.org/2000/01/rdf-schema#label', 'name', identity),
    ('http://dbpedia.org/property/crew', 'crew', clean_int),
    ('http://dbpedia.org/property/lengthM', 'length', clean_float),
    ('http://dbpedia.org/property/lengthMain', 'length', clean_float_unit),
    ('http://dbpedia.org/property/lengthAlt', 'length', clean_float_unit),
    ('http://dbpedia.org/property/spanM', 'wingspan', clean_float),
    ('http://dbpedia.org/property/spanMain', 'wingspan', clean_float_unit),
    ('http://dbpedia.org/property/spanAlt', 'wingspan', clean_float_unit),
    ('http://dbpedia.org/property/spanAlt', 'wingspan', clean_float_unit),
    ('http://dbpedia.org/property/maxSpeedKmh', 'maxspeed', clean_float),
    ('http://dbpedia.org/property/maxSpeedMain', 'maxspeed', clean_speed_unit),
    ('http://dbpedia.org/property/maxSpeedAlt', 'maxspeed', clean_speed_unit),
    ('http://dbpedia.org/property/maxSpeedMph', 'maxspeed', clean_speed_mph),
    ('http://dbpedia.org/property/emptyWeightMain', 'emptyweight', clean_weight_unit),
#useless: ('http://dbpedia.org/property/emptyWeightAlt', 'emptyweight', store),
    ('http://dbpedia.org/property/emptyWeightKg', 'emptyweight', clean_float),
    ('http://dbpedia.org/property/heightMain', 'height', clean_float_unit),
    ('http://dbpedia.org/property/heightAlt', 'height', clean_float_unit),
    ('http://dbpedia.org/property/heightM', 'height', clean_float),
    ('http://dbpedia.org/property/ceilingMain', 'ceiling', clean_length),
    ('http://dbpedia.org/property/ceilingAlt', 'ceiling', clean_length),
    ('http://dbpedia.org/property/ceilingM', 'ceiling', clean_float),
    ]
cleaners = {}
for (prop, p, cleaner) in CLEAN:
    cleaners[prop] = (p, cleaner)
KEEPERS = set(['http://dbpedia.org/property/emptyWeightMain',
               'http://dbpedia.org/property/emptyWeightAlt'])

class AircraftModel:
    
    def show(self):
        print self.uri
        for attr in allattrs:
            print '  ', attr, ': ', getattr(self, attr)

    def has_data(self):
        for attr in allattrs:
            if attr == 'name':
                continue

            if getattr(self, attr) == 0.0:
                return False
            
        return True

    def distance(self, other):
        if isinstance(other, AircraftModel) or isinstance(other, Centroid):
            sum = 0.0
            count = 0
            for attr in cmpattrs:
                v1 = getattr(self, attr) / maxes[attr]
                v2 = getattr(other, attr) / maxes[attr]
                if v1 and v2:
                    sum += (v1 - v2) ** 2
                    count += 1

            if not count:
                return 0.0 # they're the same, as far as we can tell :-(
            return math.sqrt(sum / count)

        else:
            return other.distance(self)

    def __repr__(self):
        return "<model %s>" % self.uri

class Centroid:

    def __init__(self, number, model = None):
        self.number = number
        self.members = []
        if model:
            for attr in cmpattrs:
                setattr(self, attr, getattr(model, attr))

    def add(self, member):
        self.members.append(member)

    def remove(self, member):
        self.members.remove(member)
            
    def __repr__(self):
        return 'cluster%s' % self.number

    def show(self):
        print self, len(self.members)
        for attr in cmpattrs:
            print '  ', attr, ': ', getattr(self, attr)
        print
        for member in self.members:
            print member.uri

    def recompute(self):
        for attr in cmpattrs:
            sum = 0.0
            count = 0
            for m in self.members:
                if getattr(m, attr):
                    sum += getattr(m, attr)
                    count += 1

            if count:
                setattr(self, attr, float(sum) / float(count))
            else:
                setattr(self, attr, 0.0)

class Cluster:

    def __init__(self, number, members = None):
        self.number = number
        self.members = members or []

    def add(self, member):
        if isinstance(member, AircraftModel):
            self.members.append(member)
        else:
            self.members += member.members
            
    def __repr__(self):
        return 'cluster%s' % self.number

    def show(self):
        print self, len(self.members)
        # for attr in cmpattrs:
        #     print '  ', attr, ': ', getattr(self, attr)
        # print
        for member in self.members:
            print member.uri

    def recompute(self):
        for attr in cmpattrs:
            sum = 0.0
            count = 0
            for m in self.members:
                if getattr(m, attr):
                    sum += getattr(m, attr)
                    count += 1

            if count:
                setattr(self, attr, float(sum) / float(count))
            else:
                setattr(self, attr, 0.0)

    def distance(self, other):
        if isinstance(other, AircraftModel):
            others = [other]
        else:
            others = other.members

        sum = 0.0
        count = 0
        for m1 in self.members:
            for m2 in others:
                sum += m1.distance(m2)
                count += 1

        return sum / count
                
temp = {}
models = {}
for line in open('data.txt'):
    line = line.strip()
    pos1 = line.find(' ')
    pos2 = line.find(' ', pos1 + 1)

    s = line[ : pos1]
    p = line[pos1 + 1 : pos2]
    o = line[pos2 + 1 : ]

    model = models.get(s)
    if not model:
        model = AircraftModel()
        model.uri = s
        models[s] = model

    if p in KEEPERS:
        try:
            temp[s + ',' + p] = float(o)
        except ValueError:
            pass # discard value, carry on

    if cleaners.has_key(p):
        (p, c) = cleaners[p]
        value = c(o)
        if value is not None:
            setattr(model, p, value)

for model in models.values():
    main = temp.get(model.uri + ',http://dbpedia.org/property/emptyWeightMain')
    alt = temp.get(model.uri + ',http://dbpedia.org/property/emptyWeightAlt')
    if main and alt:
        ratio = main / alt
        if ratio > 0.453 and ratio < 0.455:
            # main = kg, alt = lb
            model.emptyweight = main
        elif ratio > 2.1 and ratio < 2.3:
            # main = lb, alt = kg
            model.emptyweight = alt
        # else:
        #     print main, alt, ratio

allattrs = set()
for (prop, attr, cleaner) in CLEAN:
    allattrs.add(attr)
cmpattrs = [attr for attr in allattrs if attr not in ('name', 'number_built')]
    
maxes = {}
for model in models.values():
    for attr in allattrs:
        try:
            v = getattr(model, attr)
            maxes[attr] = max(maxes.get(attr), v)
        except AttributeError:
            setattr(model, attr, 0.0)

pprint(maxes)

for model in models.values():
    if model.maxspeed == 780000.0:
        model.show()

allmodels = [model for model in models.values()
             if model.uri.startswith('http://') and model.has_data()]
        
# for model in allmodels:
#     model.show()
# print len(allmodels)

# ===== K-MEANS CLUSTERING =============================================
K = 5
centroids = []
for x in range(K):
    c = random.choice(allmodels)
    while c in centroids:
        c = random.choice(allmodels)
    
    centroids.append(Centroid(x, c))

# # print "===== INITIAL CENTROIDS"
# # for c in centroids:
# #     c.show()

for model in allmodels:
    model.cluster = None

while True:
    changed = 0
    for model in allmodels:
        best = None
        bestdist = 10000.0
        for c in centroids:
            dist = model.distance(c)
            if dist < bestdist:
                best = c
                bestdist = dist

        if model.cluster != best:
            if model.cluster:
                model.cluster.remove(model)
            model.cluster = best
            model.cluster.add(model)
            changed += 1
        #print model.uri, best

    print "%d changed" % changed
    for c in centroids:
        c.recompute()
        #c.show()

    if not changed:
        break

for c in centroids:
    print
    print '=' * 75
    c.show()

# ===== AGGLOMERATIVE CLUSTERING =============================================
# clusters = 1
# allobjects = allmodels[:]

# while True:
#     bestdist = 100000.0
#     bestpair = None
#     for m1 in allobjects:
#         for m2 in allobjects:
#             if m1 == m2:
#                 continue
#             d = m1.distance(m2)
#             if d < bestdist:
#                 bestdist = d
#                 bestpair = (m1, m2)

#     (m1, m2) = bestpair
#     print
#     print m1
#     print m2
    
#     c = Cluster(clusters)
#     clusters += 1
#     c.add(m1)
#     c.add(m2)
#     #c.recompute()

#     c.show()

#     allobjects.remove(m1)
#     allobjects.remove(m2)
#     allobjects.append(c)

#     print "Craft: ", len([o for o in allobjects if isinstance(o, AircraftModel)])
#     print "Total:", len(allobjects)
    
#     raw_input()
