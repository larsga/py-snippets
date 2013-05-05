
import csv

# def get_data():
#     return csv.reader(open('ml-100k/u.data'), delimiter = '\t')
# def get_movies():
#     return csv.reader(open('ml-100k/u.item'), delimiter = '|')

def get_data():
    return [line.strip().split('::') for line in open('ml-1m/ratings.dat')]
def get_movies():
    return [line.strip().split('::') for line in open('ml-1m/movies.dat')]
