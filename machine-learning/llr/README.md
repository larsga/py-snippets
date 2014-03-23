
A recommendation engine in two steps: 

  1. offline analysis using a co-occurrence matrix and log likelihood
  ratio to work out which items are statistically significant
  indicators that you will want another item.

  2. a web application demonstrating recommendations by doing Lucene
  searches on the indicators produced in the previous step.

The details of how it works is explained in the slides.

To use it, download the data as for the `movielens` example, and copy
`movielib.py` into this folder.

Then run as follows:

  1. `llr.py`, which reads the ratings and computes the matrix of which
  items are indicators for which other items. Note that this step requires
  significant memory and CPU if run on the 10 million data set.

  2. `llr_index.py` (which must be run in Jython!) to produce the Lucene
  index.

  3. `jython recom-ui.py 7000`, which starts the demo UI on 
  http://localhost:7000 This requires you to install the web.py web
  framework. For example by just copying it into this folder.

The `search.py` module is used by the web application, and can also be
used as a command-line recommender.

