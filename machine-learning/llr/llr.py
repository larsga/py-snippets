'''
Proof of concept implementation of Ted Dunning's use of a
co-occurrence matrix together with the log likelihood ratio test to
check the significance of co-occurrence.  Will produce a set of
indicator movies for each movie.

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

# --- Loading the metadata

movies = {}
for (movieid, title, cats) in movielib.get_movies():
    movies[int(movieid)] = title

# --- 1M
# 40 gives 411,167 significant pairs, 2117 movies with no indicators
# 75 gives  51,129 significant pairs
# 100 gives 11,147 significant pairs, 3485 movies with no indicators
# 150 gives 457 significant pairs, 3820 movies with no indicators

# --- 10M
# 40 gives 3,412,561 significant pairs, 5188 movies with no indicators
# 150 gives 164,418 significant pairs, 9243 movies with no indicators

LIMIT = 40.0
total = sum(co_occurrences.values())
count = 0

# this part is not in Dunning's work, but when showing 'people who liked
# this movie also liked ...' it makes more sense to show the strongest
# indicators. the recommendations look strange otherwise.
def add_to_top_ten(m1, m2, strength):
    list = top_ten_for.get(m1, [])
    list.append((strength, m2))
    list.sort()
    list.reverse()
    top_ten_for[m1] = list[ : 10]

top_ten_for = {}
movie_indicators = {}
for ((m1, m2), coocc) in co_occurrences.items():
    rest = total - (coocc - occurrences[m2] - occurrences[m1])
                    
    k = [[coocc, occurrences[m1] - coocc],
         [occurrences[m2] - coocc, rest]]
    test = llr(k)
    if test > LIMIT:
        #print m1, m2, k, test
        #print '  ', movies[m1], ' <*> ', movies[m2]
        count += 1
        movie_indicators[m1] = movie_indicators.get(m1, []) + [m2]
        movie_indicators[m2] = movie_indicators.get(m2, []) + [m1]

        add_to_top_ten(m1, m2, test)
        add_to_top_ten(m2, m1, test)

print 'Above threshold:', count
print 'Total:', len(co_occurrences)

# co_occurrences = None # free up some memory

# counts = {}
# for (movie_id, indicators) in movie_indicators.items():
#     c = len(indicators)
#     counts[c] = counts.get(c, 0) + 1
# keys = counts.keys()
# keys.sort()

# print '0 -> %s' % (len(movies) - len(movie_indicators))
# for pair in counts.items():
#     print '%s -> %s' % pair

# --- OUTPUT
# finally, we write the indicators to a text file for indexing with a
# search engine
outf = open('indicators.txt', 'w')
for (movieid, indicators) in movie_indicators.items():
    outf.write(str(movieid) + ' ' + (' '.join(map(str, indicators))) + '\n')
outf.close()

# then write best-bets
outf = open('best-bets.txt', 'w')
for (movieid, topten) in top_ten_for.items():
    topten = [movieid for (strength, movieid) in topten]
    outf.write(str(movieid) + ' ' + (' '.join(map(str, topten))) + '\n')
outf.close()
