'''
This script retrieves the raw data from DBpedia. Run only once.
'''

import codecs
import sparql

ENDPOINT = 'http://dbpedia.org/sparql'
PREFIXES = '''
prefix dbp: <http://dbpedia.org/resource/>
prefix dbpo: <http://dbpedia.org/ontology/>
prefix dc: <http://dublincore.org/documents/2012/06/14/dcmi-terms/>
'''

def q(query):
    return sparql.query(ENDPOINT, PREFIXES + query).fetchall()

def q_get(query):
    row = sparql.query(ENDPOINT, PREFIXES + query).fetchone()
    # FIXME: need to handle no values, somehow
    (a, ) = row
    return a[0]

def q_row(query):
    rows = sparql.query(ENDPOINT, PREFIXES + query).fetchall()
    if rows:
        return rows[0]
    else:
        return None

def count(type):
    query = "SELECT DISTINCT count(*) WHERE {?s a %s}" % type
    result = q(query)
    return int(result[0][0].value)

def out(val):
    try:
        return val.encode('utf-8')
    except AttributeError:
        return str(val)

query = '''
select distinct ?s ?p ?o
where {
  { ?s dbpo:type dbp:Multirole_combat_aircraft. }
  UNION
  { ?s dc:subject <http://dbpedia.org/resource/Category:AWACS_aircraft> }
  UNION
  { ?s a <http://dbpedia.org/ontology/Aircraft> }

  ?s ?p ?o.
}
'''
outf = codecs.open('data.txt', 'w', 'utf-8')
for row in q(query):
    outf.write(' '.join(map(unicode, row)) + '\n')
outf.close()
