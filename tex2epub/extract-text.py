
import sys, codecs, os
import tex2epub

fromfile = sys.argv[1]
fromdir = os.path.split(fromfile)[0]
extractor = tex2epub.TextHandler()
source = codecs.open(fromfile, 'r', 'utf-8').read()
tex2epub.parse_latex(source, tex2epub.IncludeHandler(fromdir, extractor))

print extractor.getvalue().encode('utf-8')
