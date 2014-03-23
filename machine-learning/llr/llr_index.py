'''
This script reads the output of llr.py and uses it to index up the
movie data in Lucene so that we can use Lucene to make recommendations.
Must be run with Jython.
'''

import movielib

from java.io import File
from org.apache.lucene.util import Version
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.index import IndexWriterConfig, IndexWriter
from org.apache.lucene.document import Field, Document
from org.apache.lucene.analysis.standard import StandardAnalyzer

# --- OPEN SEARCH INDEX
path = "lucene-ix"
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
directory = NIOFSDirectory.open(File(path))
cfg = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
cfg.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
iwriter = IndexWriter(directory, cfg)

# --- START INDEXING
print 'Loading metadata'
movies = {}
for (movieid, title, cats) in movielib.get_movies():
    movies[movieid] = (title, cats)

print 'Loading best bets'
bets = {}
for line in open('best-bets.txt'):
    row = line.split()
    id = row[0]
    b = row[1 : -1] # -1 is because we're including the movie itself
    b.reverse()
    bets[id] = b
    
print 'Indexing'
for line in open('indicators.txt'):
    row = line.split()
    movieid = row[0]
    print movieid
    indicators = row[1 : ]

    (title, cats) = movies[movieid]
    best = bets.get(movieid)

    doc = Document()
    doc.add(Field('id', movieid, Field.Store.YES, Field.Index.NOT_ANALYZED))
    doc.add(Field('title', title, Field.Store.YES, Field.Index.ANALYZED))
    doc.add(Field('cats', cats, Field.Store.YES, Field.Index.ANALYZED))
    doc.add(Field('indicators', ' '.join(indicators), Field.Store.YES,
                  Field.Index.ANALYZED))
    if best:
        doc.add(Field('bestbets', ' '.join(best), Field.Store.YES,
                      Field.Index.ANALYZED))
    iwriter.addDocument(doc)

    del movies[movieid] # mark as indexed

print 'Indexing remainder'
for (movieid, (title, cats)) in movies.items():
    doc = Document()
    doc.add(Field('id', movieid, Field.Store.YES, Field.Index.NOT_ANALYZED))
    doc.add(Field('title', title, Field.Store.YES, Field.Index.ANALYZED))
    doc.add(Field('cats', cats, Field.Store.YES, Field.Index.ANALYZED))
    iwriter.addDocument(doc)

print 'Committing'
iwriter.commit()
iwriter.close()
directory.close()
