'''
A script to capture earthquake data from vedur.is and append it to an
ever-growing CSV file.
'''

ENDPOINT = 'http://en.vedur.is/earthquakes-and-volcanism/earthquakes/'

import urllib, datetime, calendar, csv

TIMEFORMAT = '%Y-%m-%dT%H:%M:%S.000Z'

def parse(dt):
    return datetime.datetime.strptime(dt, TIMEFORMAT)

def load(f):
    try:
        rows = [row for row in csv.reader(open(f))]
        rows = rows[1 : ]
        return rows
    except IOError, e:
        if e.errno == 2:
            return []
        raise e

def fix(datetuple):
    (year, month, day, hour, min, sec) = datetuple
    return (year, month + 1, day, hour, min, sec)

def format(v):
    if isinstance(v, datetime.datetime):
        return datetime.datetime.strftime(v, TIMEFORMAT)
    else:
        return str(v)

def load_vedur_page():
    'Returns a list of (timestamp, size, depth, ...) tuples.'

    data = urllib.urlopen(ENDPOINT).read()
    for line in data.split('\n'):
        if line.startswith('VI.quakeInfo'):
            data = line.strip()
            break

    pos = data.find('[')
    data = data[pos : -1]

    records = []
    prev = 0
    while True:
        start = data.find('{', prev)
        end = data.find('}', prev)
        if start == -1:
            break

        rec = data[start : end + 1]
        rec = rec.replace('new Date(', '(')

        rec = eval(rec)

        text = '%s km %s of %s' % (rec['dL'], rec['dD'], rec['dR'])
        dt = apply(datetime.datetime, fix(rec['t']))
        records.append((dt, rec['s'], rec['dep'], rec['q'], rec['lat'],
                        rec['lon'], text))

        prev = end + 1

    return records

def merge_new_and_old(records):
    header = 'timestamp,size,depth,quality,latitude,longitude,humanReadableLocation'
    cols = header.split(',')

    # we keep old data from before the oldest quake in the new response. there
    # may still be corrections to that data coming, but we will never see them
    # anyway. then we append the data in the current request, since it's the
    # most correct data available at this point

    # find the cutoff time
    cutoffpoint = records[-1][0]

    # load the old data
    olddata = load('vedur.csv')

    # now, write old data to CSV file as far as we can
    outfile = open('vedur.csv', 'w')
    outf = csv.writer(outfile)
    outf.writerow(cols) # write the header

    for row in olddata:
        timestamp = parse(row[0])
        if timestamp >= cutoffpoint:
            break

        outf.writerow(row)

    # then, write the new data from the API request
    records.reverse()
    for row in records:
        row = [format(v) for v in row]
        outf.writerow(row)

    outfile.close()

if __name__ == '__main__':
    records = load_vedur_page()
    merge_new_and_old(records)
