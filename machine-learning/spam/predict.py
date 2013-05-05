
import sys, glob, operator
from email.parser import Parser
from email.header import decode_header

SAMPLES = 1000
PATTERN = '*.emlx'
PADDING = 5

class Corpus:
    def __init__(self):
        self._tokens = {}

    def spam_probability(self, token):
        t = self._tokens.get(token)
        if not t:
            return 0.5
        #print t._token, t.spam_probability()
        return t.spam_probability()
        
    def spam(self, token):
        self._count(token, Feature.spam)

    def ham(self, token):
        self._count(token, Feature.ham)

    def _count(self, token, method):
        t = self._tokens.get(token)
        if not t:
            t = Feature(token)
            self._tokens[token] = t
        method(t)

class Feature:
    def __init__(self, token):
        self._token = token
        self._spam = 0
        self._ham = 0

    def spam(self):
        self._spam += 1

    def ham(self):
        self._ham += 1

    def spam_probability(self):
        return (self._spam + PADDING) / \
            float(self._spam + self._ham + (PADDING * 2))

def compute_bayes(probs):
    product = reduce(operator.mul, probs)
    lastpart = reduce(operator.mul, map(lambda x: 1-x, probs))
    if product + lastpart == 0:
        return 0 # happens rarely, but happens
    else:
        return product / (product + lastpart)
    
def featurize(email):
    fp = open(email)
    fp.readline() # discard first garbage line
    msg = Parser().parse(fp)

    features = []
    for header in msg.keys():
        for (v, cs) in decode_header(msg[header]):
            try:
                v = v.decode(cs or 'utf-8')
            except UnicodeDecodeError:
                v = v.decode('iso-8859-1')
            for vp in v.split():
                features.append(header + ':' + vp)

    for part in msg.walk():
        if part.is_multipart():
            continue

        try:
            cs = msg.get_charset() or 'utf-8'
            data = part.get_payload(decode = True).decode(cs)
        except UnicodeDecodeError:
            data = part.get_payload(decode = True).decode('iso-8859-1')
        
        for token in data.split():
            if len(token) < 1000:
                features.append(token)

    return features

def classify(email):
    return compute_bayes([corpus.spam_probability(f) for f in featurize(email)])

# usage:
#   python predict.py <spamdir> <hamdir> <email to decide> <email to decide> ...
spamdir = sys.argv[1]
hamdir = sys.argv[2]

# corpus
corpus = Corpus()

# scan spam
for spam in glob.glob(spamdir + '/' + PATTERN)[ : SAMPLES]:
    for token in featurize(spam):
        corpus.spam(token)

# scan ham
for ham in glob.glob(hamdir + '/' + PATTERN)[ : SAMPLES]:
    for token in featurize(ham):
        corpus.ham(token)

# compute probability
for email in sys.argv[3 : ]:
    print email
    p = classify(email)
    if p < 0.2:
        print '  Spam', p
    else:
        print '  Ham', p

    # print top 10
    fs = [(f, corpus.spam_probability(f)) for f in featurize(email)]
    fs.sort(key = lambda x: x[1])
    for (f, p) in fs[ : 10]:
        print f, p
    print '...'
    
    # print bottom 10
    fs.reverse()
    for (f, p) in fs[ : 10]:
        print f, p

    
