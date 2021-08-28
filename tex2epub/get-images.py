
import sys, codecs, os
import tex2epub

class ImageExtractor:

    def __init__(self):
        self._images = []

    def command(self, name, braces, brackets):
        if name == 'illustration' or name == 'illustrationW':
            self._images.append(braces)

    def text(self, text):
        pass

    def close(self):
        pass

fromfile = sys.argv[1]
fromdir = os.path.split(fromfile)[0]
extractor = ImageExtractor()
source = codecs.open(fromfile, 'r', 'utf-8').read()
tex2epub.parse_latex(source, tex2epub.IncludeHandler(fromdir, extractor))

chapters = set()
for image in extractor._images:
    (dir, file) = os.path.split(image)
    chapters.add(dir)

    print '%s,%s' % (len(chapters), file)
