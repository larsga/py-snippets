
# Covid-19 model

A simple SEIR-like model of the covid-19 epidemic, with three pre-made
configurations for Norway, Italy, and China. Requires matplotlib.

To try it out, run:

```
python simulate.py norway 1
```

First parameter chooses the configuration, second parameter the number
of simulation runs.

By editing the configurations you can change assumptions about initial
cases, imported cases, reproduction number at different times, etc etc.
You can also change the end date.

The model covers:
  * incubation time,
  * time to hospitalization,
  * time to death,
  * time to recovery,
  * herd immunity (requires setting population size), and
  * (crudely) effects of overloaded healthcare services.
