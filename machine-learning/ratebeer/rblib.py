
import csv, operator
from numpy import *

USE_COUNTRY = True
USE_STYLE = True

MYSCORE = 8
COUNTRY = 11
STYLE = 14

#datafile = 'ratings.txt'
#datafile = 'gr0ve-iso.csv'

def load_as_matrix(datafile = 'ratings.txt'):
    # --- STEP 1: Identify all the features
    features = {'abv' : 0, 'colour' : 1, 'sweet' : 2, 'hoppy' : 3, 'sour' : 4,
                'alcohol' : 5}
    #            'spicy' : 5}
    fixed_dimensions = len(features)
    all_scores = []
    for row in csv.reader(open(datafile), delimiter = '|'):
        if row[0] == 'BeerID':
            continue

        if USE_COUNTRY:
            country = row[COUNTRY]
            if country not in features:
                features[country] = len(features)

        if USE_STYLE:
            style = row[STYLE]
            if style not in features:
                features[style] = len(features)

        all_scores.append(float(row[MYSCORE]))

    avg = reduce(operator.add, all_scores) / float(len(all_scores))

    # --- STEP 2: Load additional info
    abv = {}
    for (id, abvv) in csv.reader(open('abv.txt')):
        abv[id] = float(abvv)

    styledata = {}
    for row in csv.reader(open('styles.csv')):
        if row[0] == 'Style':
            continue
        styledata[row[0]] = map(float, filter(bool, row[1 : ]))

    # --- STEP 3: Transform into matrix
    parameters = []
    scores = []
    for row in csv.reader(open(datafile), delimiter = '|'):
        if row[0] == 'BeerID':
            continue

        data = [0.0] * len(features)
        if USE_COUNTRY:
            data[features[row[COUNTRY]]] = 1.0
        if USE_STYLE:
            data[features[row[STYLE]]] = 1.0
        alc = (min(abv.get(row[0], 7.5), 15.0) / 15.0)
        data[features['abv']] = alc
        (colour, sweet, hoppy, sour, spicy) = styledata[row[STYLE]]
        data[features['colour']] = colour
        data[features['sweet']] = sweet
        data[features['hoppy']] = hoppy
        data[features['sour']] = sour
        #data[features['spicy']] = spicy
        data[features['alcohol']] = (alc / 100.0) * 56.8
        parameters.append(data)

        scores.append(float(row[MYSCORE]) - avg)

    # --- STEP 4: Build header row
    # column names for the scores matrix
    columns = [''] * len(data)
    for (name, colix) in features.items():
        columns[colix] = name
    
    return (mat(scores), mat(parameters), columns)
