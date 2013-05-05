
A demonstration of k-means clustering and agglomerative clustering
using data about aircraft from DBpedia.

The first step is to get the data, which you do by running

    python get-data.py

This will produce data.txt, which is the raw data.


After the data has been downloaded, simply run it with

    python load-data.py

That will do k-means clustering. Look at the source code (bottom) to
replace it with agglomerative clustering.