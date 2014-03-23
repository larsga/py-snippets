
import sys

from java.io import File, StringReader
from org.apache.lucene.util import Version
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.index import Term, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BooleanQuery, TermQuery
from org.apache.lucene.search.BooleanClause import Occur
from org.apache.lucene.document import Field, Document
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute

class Document:
    def __init__(self, doc):
        self.id = doc.getValues('id')[0]
        self.title = doc.getValues('title')[0]
        self.cats = doc.getValues('cats')[0].split('|')

        i = doc.getValues('indicators')
        self.indicators = []
        if i:
            self.indicators = i[0].split()

        i = doc.getValues('bestbets')
        self.bets = []
        if i:
            self.bets = i[0].split()
            
def do_query(property, qstring, limit = 10):
    query = BooleanQuery()
    stream = analyzer.tokenStream(property, StringReader(qstring))
    stream.reset()
    attr = stream.getAttribute(CharTermAttribute)

    while stream.incrementToken():
        term = attr.toString()
        termQuery = TermQuery(Term(property, term))
        query.add(termQuery, Occur.SHOULD)

    hits = searcher.search(query, None, limit).scoreDocs
    return [Document(searcher.doc(hit.doc)) for hit in hits]

path = 'lucene-ix'
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
directory = NIOFSDirectory.open(File(path))
reader = DirectoryReader.open(directory)
searcher = IndexSearcher(reader)

if __name__ == '__main__':
    value = ' '.join(sys.argv[1 : ])
    for doc in do_query('indicators', value):
        print doc.title
