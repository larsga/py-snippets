
Earthquake anomaly detection
----------------------------

If you try this out, please beware of running `earthquakes.py` too
often, as that will put undue strain on the vedur.is servers.

Python scripts:

 * `earthquakes.py`: captures data, adds to CSV file
 * `find-anomalies.py`: finds earthquakes bigger than 99.8 percentile
 * `sliding-window.py`: does some sliding window plots
 * `histogram.py`: does a histogram of earthquakes by size
 * `poisson.py`: finds anomalous earthquake swarms

Other:

 * `check.sh`: downloads new data, checks for new warnings
