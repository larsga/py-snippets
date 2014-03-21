'''
Implementation of Ted Dunning's use of a co-occurrence matrix together with
the log likelihood ratio test to check the significance of co-occurrence.
Will produce a set of indicator movies for each movie.

At the moment this is a work in progress.

http://tdunning.blogspot.no/2008/03/surprise-and-coincidence.html
'''

from math import log, sqrt

# ----- COMPUTE CO-OCCURRENCES

import movielib

occurrences = {} # movieid -> count (how many times has this movie appeared)
co_occurrences = {} # (movie1, movie2) -> count (times occurred together)

def process_user(movies):
    # all these movies appeared together. that is, they were all liked
    # by the same user
    for movieid in movies:
        occurrences[movieid] = occurrences.get(movieid, 0) + 1

    for m1 in movies:
        for m2 in movies:
            if m1 < m2:
                co_occurrences[(m1, m2)] = co_occurrences.get((m1, m2), 0) + 1

cur_user = None
cur_ratings = []
for (userid, movieid, rating, timestamp) in movielib.get_data():
    if userid != cur_user:
        print userid, len(cur_ratings), len(occurrences), len(co_occurrences)
        process_user(cur_ratings)
        cur_user = userid
        cur_ratings = []

    rating = float(rating)
    movieid = int(movieid)

    if rating >= 3:
        cur_ratings.append(movieid)

# ----- LOG LIKELIHOOD COMPUTATION

def allsum(k):
    return k[0][0] + k[1][0] + k[0][1] + k[1][1]

def all_h(k):
    total = 0
    sum = float(allsum(k))
    for row in k:
        for v in row:
            if v != 0:
                total += v / sum * log(v / sum)
    return total

def rowsum(k):
    return (k[0][0] + k[0][1], k[1][0] + k[1][1])

def colsum(k):
    return (k[0][0] + k[1][0], k[0][1] + k[1][1])

def pair_h(k):
    total = 0
    all = float(sum(k))
    for v in k:
        if v != 0:
            total += v / all * log(v / all)
    return total

def llr(k):
    return sqrt(2 * allsum(k) * (all_h(k) - pair_h(rowsum(k)) - pair_h(colsum(k))))

# k[0][0]: A and B appear together
# k[0][1]: A appears, but not B
# k[1][0]: B appears, but not A
# k[1][1]: neither appears
# k = [(13.0, 1000.0),
#      (1000.0, 100000.0)]

# print llr(k)

# k = [(1.0, 0.0),
#      (0.0, 10000.0)]

# print llr(k)

# k = [(1.0, 0.0),
#      (0.0, 2.0)]

# print llr(k)

# k = [(10.0, 0.0),
#      (0.0, 100000.0)]

# print llr(k)

movies = {}
for (movieid, title, cats) in movielib.get_movies():
    movies[int(movieid)] = title

# 40 gives 411167 significant pairs, 2117 movies with no indicators
# 75 gives  51129 significant pairs
# 100 gives 11147 significant pairs, 3485 movies with no indicators
# 150 gives 457 significant pairs, 3820 movies with no indicators
LIMIT = 150.0
total = sum(co_occurrences.values())
count = 0

movie_indicators = {}

for ((m1, m2), coocc) in co_occurrences.items():
    rest = total - (coocc - occurrences[m2] - occurrences[m1])
                    
    k = [[coocc, occurrences[m1] - coocc],
         [occurrences[m2] - coocc, rest]]
    test = llr(k)
    if test > LIMIT:
        print m1, m2, k, test
        print '  ', movies[m1], ' <*> ', movies[m2]
        count += 1
        movie_indicators[m1] = movie_indicators.get(m1, []) + [m2]
        movie_indicators[m2] = movie_indicators.get(m2, []) + [m1]

print 'Above threshold:', count
print 'Total:', len(co_occurrences)

co_occurrences = None # free up some memory

counts = {}

for (movie_id, indicators) in movie_indicators.items():
    c = len(indicators)
    counts[c] = counts.get(c, 0) + 1

keys = counts.keys()
keys.sort()

print '0 -> %s' % (len(movies) - len(movie_indicators))
# for pair in counts.items():
#     print '%s -> %s' % pair
