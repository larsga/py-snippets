
import json
import matplotlib.pyplot as plt

by_algorithm = {}

ff_gamma = 9.42669783093377
ff_alpha = 0.010568480664692403
ff_alpha2 = 0.022086897176915976
ff_gamma2 = 10.0
cuckoo_a = 0.1
cuckoo_g = 0.01

for line in open('all_results.json'):
    results = json.loads(line)

    if results['problem'] == 'cityhotels2':
       results['problem'] = 'cityhotels'
       results['algorithm'] = 'pso_267'

    if (results['problem'] != 'cityhotels' or
        ('cuckoo_alpha' in results and results['cuckoo_alpha'] != cuckoo_a) or
        ('cuckoo_gamma' in results and results['cuckoo_gamma'] != cuckoo_g)):
        # ('firefly_gamma' in results and results['firefly_gamma'] not in (ff_gamma, ff_gamma2)) or
        # ('firefly_alpha' in results and results['firefly_alpha'] not in (ff_alpha, ff_alpha2))):
        continue

    # if (results['problem'] != 'cityhotels' or
    #     #results['algorithm'] == 'cuckoo' or
    #     ('firefly_gamma' in results and results['firefly_gamma'] != ff_gamma) or
    #     ('firefly_alpha' in results and results['firefly_alpha'] != ff_alpha) or
    #     ('cuckoo_alpha' in results and results['cuckoo_alpha'] != c_alpha) or
    #     ('cuckoo_scale' in results and results['cuckoo_scale'] != c_scale)):
    #     continue

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

color = {'pso' : 'g', 'firefly' : 'r', 'crap' : 'b', 'cuckoo' : 'c',
         'pso_267' : 'm', 'genetic': 'y'}

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
