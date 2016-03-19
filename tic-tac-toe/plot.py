
scores = {'x\n' : -1, 'o\n' : 1, '\n' : 0}

def summarize(file):
    summary = []
    total = 0
    count = 0
    for line in open(file):
        count += 1
        total += scores[line]

        if count == 1000:
            summary.append(total / float(count))
            total = 0
            count = 0
    return summary

bandit = summarize('bandit-log.txt')#[:10]
simple = summarize('log.txt')#[:10]

import matplotlib.pyplot as plt
plt.plot(range(len(bandit)), bandit, range(len(bandit)), simple)
plt.show()
