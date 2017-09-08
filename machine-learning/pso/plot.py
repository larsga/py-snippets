
import json
import matplotlib.pyplot as plt

by_algorithm = {}

ff_gamma = 3.0
for line in open('all_results.json'):
    results = json.loads(line)
    if (results['problem'] != 'cityhotels' or
        ('firefly_gamma' in results and results['firefly_gamma'] != ff_gamma)):
        continue

    # t = range(len(results['progress']))
    # plt.plot(t, results['progress'], color = 'g')
    alg = results['algorithm']
    all = by_algorithm.get(alg, [])
    all.append(results['progress'])
    by_algorithm[alg] = all

averages = {}
for (alg, all) in by_algorithm.items():
    averages[alg] = [sum([progress[ix] for progress in all]) / len(all)
                     for ix in range(len(all[0]))]

color = {'pso' : 'g', 'firefly' : 'r', 'crap' : 'b', 'cuckoo' : 'c'}

for (alg, all) in by_algorithm.items():
    print alg, len(all)

t = range(len(averages.items()[0][1]))
for (alg, avg) in averages.items():
    plt.plot(t, avg, color = color[alg], label = alg)
#plt.plot(t, firefly, color = 'r')

#plt.xlabel('time (s)')
#plt.ylabel('voltage (mV)')
#plt.title('Iteration #%s' % count)
plt.grid(True)

#plt.savefig("countries.png")

plt.legend()
plt.show()
plt.close()
