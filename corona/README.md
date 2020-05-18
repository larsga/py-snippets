
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

## Sources for model parameters

The key to making this model accurately reflect the course of the
disease is to get the time and risk parameters right. The parameters
have been set based on available research.

### Time from symptoms to death

|Source|Value|Date|Comment|
|------|-----|----|-------|
|[1](https://onlinelibrary.wiley.com/doi/pdf/10.1002/jmv.25689)|14|2020-01-24|Median|
|[3](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(20)30566-3/fulltext)|18.5|2020-03-11|Median, IQR 15-22|
|[4](https://www.medrxiv.org/content/10.1101/2020.03.09.20033357v1.full.pdf)|17.8|2020-03-13|Average, 95% 16.9–19.2|

### Incubation time

|Source|Value|Date|Comment|
|------|-----|----|-------|
|[2](https://www.acpjournals.org/doi/pdf/10.7326/M20-0504)|5.1|2020-03-10|Median, 95% CI 4.5-5.8|
|[6](https://www.mdpi.com/2077-0383/9/2/538)|5|2020-01-25|Median|
