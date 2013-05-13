
import csv

MYSCORE = 8

datafile = 'ratings.txt'

# --- STEP 1: Load ratings
all_scores = {}
for row in csv.reader(open(datafile), delimiter = '|'):
    if row[0] == 'BeerID':
        continue

    all_scores[row[0]] = float(row[MYSCORE])

# --- STEP 2: Load ABV
all_abvs = {}
for (id, abvv) in csv.reader(open('abv.txt')):
    all_abvs[id] = min(float(abvv), 20.0)

# --- STEP 3: Merge
abvs = []
scores = []
for id in all_scores.keys():
    abvs.append(all_abvs[id])
    scores.append(all_scores[id])

# --- STEP 4: Plot
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.scatter(abvs, scores)
plt.show()
