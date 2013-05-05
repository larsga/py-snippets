'''
Trying out k-nearest neighbours for recommendations, to see if that
produces better results.
'''

from math import sqrt
from movielib import *

# --- Configuration

k = 50
theuser = 6041 #944

# --- Distance measures
def avg(numbers, n = 2):
    return (sum(numbers) + (3.0 * n)) / float(len(numbers) + n)

def minkowski(rating1, rating2, r = 3):
    """Computes the Minkowski distance.
    Both rating1 and rating2 are dictionaries of the form
    {'The Strokes': 3.0, 'Slightly Stoopid': 2.5}"""
    
    distance = 0
    commonRatings = False
    for key in rating1:
        if key in rating2:
            distance += pow(abs(rating1[key] - rating2[key]), r)
            commonRatings = True
    if commonRatings:
        return pow(float(distance),  1/r)
    else:
        return 1000000 #Indicates no ratings in common

def pearson(rating1, rating2):
    sum_xy = 0
    sum_x = 0
    sum_y = 0
    sum_x2 = 0
    sum_y2 = 0
    n = 0
    for key in rating1:
        if key in rating2:
            n += 1
            x = rating1[key]
            y = rating2[key]
            sum_xy += x * y
            sum_x += x
            sum_y += y
            sum_x2 += x ** 2
            sum_y2 += y ** 2
            
    # now compute denominator
    if n == 0:
        return 1000000
    denominator = (sqrt(sum_x2 - (sum_x**2) / n) *
                  sqrt(sum_y2 -(sum_y**2) / n))
    if denominator == 0:
        return 100000000
    else:
        sim = (sum_xy - (sum_x * sum_y) / n) / denominator
        return 1.0 - sim

def lmg_rmse(rating1, rating2):
    max_rating = 5.0
    sum = 0
    count = 0
    for (key, rating) in rating1.items():
        if key in rating2:
            sum += (rating2[key] - rating) ** 2
            count += 1

    if not count:
        return 1000000 # no common ratings, so distance is huge
    
    return sqrt(sum / float(count)) + (max_rating / count)

distance = lmg_rmse
    
# --- Load user ratings
users = {} # userid -> {movie : rating, movie : rating, ...}
for (user, movie, rating, time) in get_data():
    user = int(user)
    movie = int(movie)
    
    ratings = users.get(user)
    if not ratings:
        ratings = {}
        users[user] = ratings

    ratings[movie] = int(rating)

# --- Find k nearest neighbours
neighbours = []
theratings = users[theuser]
for (user, ratings) in users.items():
    if user == theuser:
        continue

    neighbours.append((distance(theratings, ratings), user, ratings))

neighbours.sort()
neighbours = neighbours[ : k]

# --- Load movies
movies = {}
for row in get_movies():
    movie = int(row[0])
    title = row[1]
    movies[movie] = title

# --- Go through neighbours
neigh_ratings = {} # movie -> [r1, r2, r3]
for ix in range(k):
    (dist, user, ratings) = neighbours[ix]
    
    print "===== %s ==================================================" % ix
    print "User #", user, ", distance:", dist
    #print 'minkowski', minkowski(theratings, ratings)
    #print 'pearson', pearson(theratings, ratings)
    
    for (movie, rating) in ratings.items():
        common = ''
        if theratings.has_key(movie):
            common = '   YOUR: %s' % theratings[movie]
        if common:
            print movies[movie], rating, common

        rs = neigh_ratings.get(movie)
        if not rs:
            rs = []
            neigh_ratings[movie] = rs
        rs.append(rating)

# --- Find highest averages
averages = [(avg(ratings), movie) for (movie, ratings) in neigh_ratings.items()]
averages.sort()
averages.reverse()

print "===== RECOMMENDATIONS =================================================="
count = 0
for (average, movie) in averages:
    if movie in theratings:
        continue

    print movies[movie], average
    count += 1
    if count > 10:
        break

print "===== DON'T SEE THESE! ================================================="
count = 0
averages.reverse()
for (average, movie) in averages:
    if movie in theratings:
        continue

    print movies[movie], average
    count += 1
    if count > 10:
        break
