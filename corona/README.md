
# Covid-19 model

A simple SEIR-like model of the covid-19 epidemic, with a setup for
modelling delta+omicron in Norway December-January 2021-2022. Can
store results of runs as JSON files for later analysis/graphing.

To try it out, run:

```
python omicron_delta.py
```

It runs *much* faster with pypy.

By editing the configuration you can change assumptions about initial
cases, imported cases, reproduction number at different times, etc
etc.

The model covers:
  * imported cases,
  * incubation time,
  * time to hospitalization,
  * time to death,
  * time to recovery,
  * herd immunity (requires setting population size),
  * (crudely) effects of overloaded healthcare services,
  * mutant versions of the virus,
  * (vaccination programs -- this was taken out, but will be reintroduced),
  * seasonality.

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
|[9](https://wwwnc.cdc.gov/eid/article/26/7/20-0282_article)|16.1|?|Wuhan|

### Incubation time

|Source|Value|Date|Comment|
|------|-----|----|-------|
|[2](https://www.acpjournals.org/doi/pdf/10.7326/M20-0504)|5.1|2020-03-10|Median, 95% CI 4.5-5.8|
|[6](https://www.mdpi.com/2077-0383/9/2/538)|5|2020-01-25|Median|
|[8](https://files.ssi.dk/COVID19-epi-trendogfokus-25052020-us12)|4.9|2020-05-25|Average|
|[9](https://wwwnc.cdc.gov/eid/article/26/7/20-0282_article)|4.2|?|Only 24 cases|

### Infection fatality rate

|Source|Value|Date|Comment|
|------|-----|----|-------|
|[4](https://www.medrxiv.org/content/10.1101/2020.03.09.20033357v1.full.pdf)|0.66|2020-03-13|For China, 0.39%-1.33%|
|[7](https://www.medrxiv.org/content/10.1101/2020.05.03.20089854v2.article-metrics)|0.75|2020-05-18|Meta-study.|
|[10](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7721859)|Age-stratified|2020-12-08||

In practice the theoretical IFR appears to be higher than actual
fatality, because the infected are generally younger, so for
estimation in practice CFR may be more useful.

### Time from symptoms to hospitalization

|Source|Value|Date|Comment|
|------|-----|----|-------|
|[5](https://jamanetwork.com/journals/jama/fullarticle/2761044)|7|2020-02-07|China, IQR 4-8|
|[9](https://wwwnc.cdc.gov/eid/article/26/7/20-0282_article)|1.5|?|Post-January 18, Wuhan|

### Time from hospitalization to discharge

|Source|Value|Date|Comment|
|------|-----|----|-------|
|[9](https://wwwnc.cdc.gov/eid/article/26/7/20-0282_article)|11.5|?|Wuhan|

### Time from hospitalization to death

|Source|Value|Date|Comment|
|------|-----|----|-------|
|[9](https://wwwnc.cdc.gov/eid/article/26/7/20-0282_article)|11.2|?|Wuhan|

### Time from infection until test taken

|Source|Value|Date|Comment|
|------|-----|----|-------|
|[8](https://files.ssi.dk/COVID19-epi-trendogfokus-25052020-us12)|9.4|2020-05-25|Average|

### Time from symptoms appear until recovery/death

|Source|Value|Date|Comment|
|------|-----|----|-------|
|[8](https://files.ssi.dk/COVID19-epi-trendogfokus-25052020-us12)|18|2020-05-25|Average|

### Probability of infecting others by day after own infection

[Sun et al, 2021](https://science.sciencemag.org/content/early/2020/11/23/science.abe2424). Specifically [figure 3](https://science.sciencemag.org/content/sci/371/6526/eabe2424/F4.large.jpg?width=800&height=600&carousel=1).
