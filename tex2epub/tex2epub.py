'''
Conversion script for producing epub books from LaTeX source. More of a
hack than a polished utility.
'''

import sys, codecs, string, os, zipfile, uuid, shutil

TOC_DEPTH = 2

WHITESPACE = ' \n\r\t'
COMMANDCHAR = string.letters + '*%=.'

#from StringIO import StringIO
class StringIO:
    # couldn't get the built-in Python StringIO library to deal with
    # unicode strings in a sane way, so I just reimplemented it.

    def __init__(self):
        self.buflist = []

    def write(self, txt):
        self.buflist.append(txt)

    def getvalue(self):
        return u''.join(self.buflist)

    def close(self):
        self.buflist = None

def parse_latex(source, handler):
    pos = 0

    while pos < len(source):
        # first, swallow the whitespace
        start = pos
        while pos < len(source) and source[pos] in WHITESPACE:
            pos += 1

        if pos != start:
            # this means we found whitespace. in order to avoid losing
            # it entirely, we pass it to the handler
            handler.text(' ')

        if pos >= len(source):
            break
        elif source[pos] == '%':
            pos = scan_to_end_of_line(source, pos)
        elif source[pos] == '\\':
            start = pos
            if source[pos + 1] == '-':
                name = '-'
                pos += 2
            else:
                pos = scan_in(source, pos + 1, COMMANDCHAR)
                name = source[start + 1 : pos]
                if pos < len(source) and source[pos] == '\\':
                    name = '\\'
                    pos += 1

            brackets = None
            braces = None
            if pos < len(source):
                if source[pos] == '[':
                    bstart = pos
                    pos = scan_to(source, pos, ']')
                    brackets = source[bstart + 1 : pos]
                    pos += 1 # step over ']'
                if source[pos] == '{':
                    bstart = pos
                    pos = scan_to_recursively(source, pos + 1, '}', '{')
                    braces = source[bstart + 1 : pos]
                    pos += 1 # step over '}'
                if pos < len(source) and source[pos] == '{':
                    # another set of braces
                    # we don't keep these braces
                    pos = scan_to_recursively(source, pos + 1, '}', '{')
                    pos += 1 # step over final '}'

            if braces:
                braces = reparse(braces)

            if name == '%.' or name == '%,':
                # this is a hack, but never mind
                handler.command('%', braces, brackets)
                handler.text(name[-1])
            else:
                handler.command(name, braces, brackets)

        else:
            # this has to be text, then
            start = pos
            pos = scan_while_not_in(source, pos, '%\\')
            handler.text(source[start : pos])

    handler.close()

def reparse(str):
    text = TextHandler()
    parse_latex(str, FilterHandler(text))
    return text.getvalue()

def scan_to_end_of_line(source, pos):
    while pos < len(source) and source[pos] != '\n':
        pos += 1

    return pos

def scan_in(source, pos, chars):
    while pos < len(source) and source[pos] in chars:
        pos += 1

    return pos

def scan_while_not_in(source, pos, chars):
    while pos < len(source) and source[pos] not in chars:
        pos += 1

    return pos

def scan_to(source, pos, char):
    while pos < len(source) and source[pos] != char:
        pos += 1

    return pos

def scan_to_recursively(source, pos, char, nester):
    while True:
        while (pos < len(source) and source[pos] != char and
               source[pos] != nester):
            pos += 1

        if source[pos] == nester:
            pos = scan_to_recursively(source, pos + 1, char, nester) + 1
        else:
            break

    return pos

TITLE_PAGE = u'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
  <meta name="generator" content="pandoc" />
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="stylesheet.css" />
</head>
<body>
  <h1 class="title">%s</h1>
  <h2 class="author">%s</h2>
</body>
</html>
'''

CONTAINER = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="content.opf" media-type="application/oebps-package+xml" />
  </rootfiles>
</container>'''

DISPLAY_OPTIONS = '''<?xml version="1.0" encoding="UTF-8"?>
<display_options>
  <platform name="*">
    <option name="specified-fonts">true</option>
  </platform>
</display_options>'''

CONTENT_TOP = u'''<?xml version="1.0" encoding="UTF-8"?>
<package version="2.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="epub-id-1">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="epub-id-1">%s</dc:identifier>
    <dc:title id="epub-title-1">%s</dc:title>
    <dc:date id="epub-date-1"></dc:date>
    <dc:language>en-US</dc:language>
    <dc:creator id="epub-creator-1" opf:role="aut">%s</dc:creator>
    <meta name="cover" content="cover_pages_png" />
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
    <item id="style" href="stylesheet.css" media-type="text/css" />
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" />
    <item id="cover_xhtml" href="cover.xhtml" media-type="application/xhtml+xml" />
    <item id="title_page_xhtml" href="title_page.xhtml" media-type="application/xhtml+xml" />
'''

CONTENT_MID = u'''  </manifest>
  <spine toc="ncx" page-progression-direction="default">
    <itemref idref="cover_xhtml" linear="no" />
    <itemref idref="title_page_xhtml" linear="yes" />
    <itemref idref="nav" linear="yes" />
'''

CONTENT_BOTTOM = u'''  </spine>
  <guide>
    <reference type="toc" title="%s" href="nav.xhtml" />
    <reference type="cover" title="Cover" href="cover.xhtml" />
  </guide>
</package>
'''

STYLESHEET = '''/* This defines styles and classes used in the book */
body { margin: 5%; text-align: justify; font-size: medium; }
code { font-family: monospace; }
h1 { text-align: left; }
h2 { text-align: left; }
h3 { text-align: left; }
h4 { text-align: left; }
h5 { text-align: left; }
h6 { text-align: left; }
h1.title { }
h2.author { }
h3.date { }
ol.toc { padding: 0; margin-left: 1em; }
ol.toc li { list-style-type: none; margin: 0; padding: 0; }
'''

class EpubWriter:

    def __init__(self, filename, labelmap):
        self._filename = filename
        self._zip = zipfile.ZipFile(filename, 'w')
        self._uuid = 'urn:uuid:' + str(uuid.uuid1())
        self._toc = []
        self._current_node = None
        self._buf = None
        self._para = False # not started
        self._figures = []
        self._in_list_item = False
        self._in_table = False
        self._row = []
        self._labelmap = labelmap # label -> (link, title)

        self._write('mimetype', 'application/epub+zip')

        os.mkdir('META-INF')
        self._write('META-INF/container.xml', CONTAINER)
        self._write('META-INF/com.apple.ibooks.display-options.xml',
                    DISPLAY_OPTIONS)
        os.rmdir('META-INF')

        self._write('stylesheet.css', STYLESHEET)
        if not os.path.exists('media'):
            os.mkdir('media')

        if os.path.exists('cover.pages.png'):
            shutil.copy('cover.pages.png', 'media/cover.pages.png')
            self._zip.write('media/cover.pages.png')
            os.unlink('media/cover.pages.png')

    def set_title(self, title):
        self._title = title.replace('--', u'\u2014')

    def set_author(self, author):
        self._author = author

    def start_chapter(self, braces):
        if self._para:
            self._buf.write(u'</p>')
            self._para = False
        if self._current_node:
            self._finish_chapter()

        self._current_node = ToCNode(None, braces)
        self._toc.append(self._current_node)
        self._current_node.set_position(len(self._toc))
        self._buf = StringIO()
        # we don't start writing the chapter here, because we don't know
        # the label yet

    def start_section(self, braces):
        if self._para:
            self._buf.write(u'</p>')
            self._para = False
        self._current_node.close_up_to(self._buf, 2)

        chapter = self._toc[ -1 ]
        self._current_node = ToCNode(chapter, braces)
        chapter.add_child(self._current_node)

    def start_subsection(self, braces):
        if self._para:
            self._buf.write(u'</p>')
            self._para = False
        self._current_node.close_up_to(self._buf, 3)

        chapter = self._toc[ -1 ]
        section = chapter.get_children()[-1]
        self._current_node = ToCNode(section, braces)
        section.add_child(self._current_node)

    def text(self, text):
        if not self._current_node:
            return

        if self._in_table:
            self._row.append(text)
            return

        self._current_node.start(self._buf)

        if text == ' ': # if it's just whitespace we don't care
            self._buf.write(' ')
            return

        prev = False
        for ix in range(len(text)):
            ch = text[ix]
            if ch == '\n':
                if prev:
                    self._buf.write(u'</p>\n\n')
                    self._para = False
                    prev = False
                else:
                    prev = True
            else:
                if prev:
                    self._buf.write(u'\n')
                    prev = False
                if not self._para and not self._in_list_item:
                    self._buf.write(u'<p>')
                    self._para = True
                self._buf.write(ch)

        if prev:
            self._buf.write(u'\n')

    def text_bold(self, text):
        if self._in_table:
            self._row.append(u'<b>%s</b>' % text)
            return

        self._wrap_text(u'b', text)

    def text_mono(self, text):
        self._wrap_text(u'tt', text)

    def text_italics(self, text):
        self._wrap_text(u'i', text)

    def _wrap_text(self, elem, text):
        self._current_node.start(self._buf)
        if not self._para:
            self._buf.write(u'<p>')
            self._para = True

        self._buf.write(u'<%s>%s</%s>' % (elem, text, elem))

    def start_list(self):
        self._current_node.start(self._buf)
        if self._para:
            self._buf.write('</p>\n')
            self._para = False
        self._buf.write(u'<ul>')

    def item(self):
        if self._in_list_item:
            self._buf.write(u'</li>\n')
        self._buf.write(u'<li>')
        self._in_list_item = True

    def end_list(self):
        if self._in_list_item:
            self._buf.write(u'</li>\n')
        self._buf.write(u'</ul>\n')
        self._in_list_item = False

    def start_figure(self):
        self._current_node.start(self._buf)
        self._figures.append(Figure())

    def caption(self, text):
        self._figures[-1].set_caption(text)

    def graphic(self, file):
        self._figures[-1].set_graphic(file)

    def end_figure(self):
        f = self._figures[-1]
        f.end()

        self._buf.write(u'<p><img src="%s" title="%s" alt="%s" /></p>\n' %
                        (f.get_file(), f.get_caption(), f.get_caption()))

        shutil.copy(os.path.join(fromdir, f._file), 'media')
        self._zip.write(f.get_file())
        os.unlink(f.get_file())

    def start_table(self):
        self._in_table = True
        self._buf.write(u'\n<table>\n<tr>\n')

    def newline(self):
        if not self._in_table:
            return

        row = ''.join(self._row)
        cells = row.split('&')
        for cell in cells:
            self._buf.write(u'<td>' + cell + '</td>')

        self._buf.write(u'</tr>\n<tr>')
        self._row = []

    def end_table(self):
        self._in_table = False
        self._buf.write(u'\n</tr></table>\n')

    def label(self, id):
        if self._figures and self._figures[-1].is_open():
            self._figures[-1].set_label(id)
        else:
            self._current_node.set_label(id)

    def footnote(self, text):
        self._buf.write(u' (%s)' % text)

    def vref(self, label):
        # I have to finish this damn script, so just hacking this
        if self._in_table:
            (link, title) = self._labelmap[label]
            text = u'<a href="%s">%s</a>' % (link, title)
            self._row.append(text)
        elif label == 'dictionary' or label == 'fig:regions':
            self._buf.write('below')
        elif label == 'fig:vilnius':
            self._buf.write('above')
        else:
            (link, title) = self._labelmap[label]
            self._buf.write(u'<a href="%s">%s</a>' % (link, title))

    def table_of_contents(self):
        page = TITLE_PAGE % (self._title, self._title, self._author)
        self._write('title_page.xhtml', page.encode('utf-8'))

    def _finish_chapter(self):
        self._current_node.close(self._buf)
        chapter = self._current_node.get_root()
        self._write('ch%s.xhtml' % chapter.get_position(),
                    self._buf.getvalue().encode('utf-8'))
        self._buf.close()

    def close(self):
        if self._para:
            self._buf.write(u'</p>\n')
        self._finish_chapter()

        self._write_cover_xhtml()
        self._write_content_cpf()
        self._write_toc_ncx()
        self._write_nav_xhtml()
        self._zip.close()

        os.rmdir('media')

    def _write_cover_xhtml(self):
        self._write('cover.xhtml', (u'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
  <meta name="generator" content="pandoc" />
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="stylesheet.css" />
</head>
<body>
<div id="cover-image">
<img src="media/cover.pages.png" alt="cover image" />
</div>
</body>
</html>''' % self._title).encode('utf-8'))

    def _write_nav_xhtml(self):
        tmp = StringIO()
        tmp.write(u'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
  <head>
    <title>%s</title>
    <link rel="stylesheet" type="text/css" href="stylesheet.css" />
  </head>
  <body>
    <div>
      <h1 id="toc-title">%s</h1>
      <ol class="toc">
        ''' % (self._title, self._title))

        counter = 1
        for chapter in self._toc:
            counter = self._recurse_navpoint2(chapter, tmp, counter)

        tmp.write(u'''      </ol>
    </div>
  </body>
</html>''')
        self._write('nav.xhtml', tmp.getvalue().encode('utf-8'))

    def _recurse_navpoint2(self, node, buf, counter):
        buf.write(u'''<li id="toc-li-%s">
          <a href="%s">%s</a>
        </li>
''' %
                  (counter, node.get_link(), node.get_title()))
        if node.get_children():
            buf.write(u'<ol class="toc">\n')

        counter += 1
        if node.get_depth() < TOC_DEPTH:
            for child in node.get_children():
                counter = self._recurse_navpoint2(child, buf, counter)

        if node.get_children():
            buf.write(u'</ol>\n')

        return counter

    def _write_toc_ncx(self):
        tmp = StringIO()
        tmp.write(u'''<?xml version="1.0" encoding="UTF-8"?>
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
  <head>
    <meta name="dtb:uid" content="%s" />
    <meta name="dtb:depth" content="1" />
    <meta name="dtb:totalPageCount" content="0" />
    <meta name="dtb:maxPageNumber" content="0" />
    <meta name="cover" content="cover_pages_png" />
  </head>
  <docTitle>
    <text>%s</text>
  </docTitle>
  <navMap>
    <navPoint id="navPoint-0">
      <navLabel>
        <text>%s</text>
      </navLabel>
      <content src="title_page.xhtml" />
    </navPoint>
''' % (self._uuid, self._title, self._title))

        counter = 1
        for chapter in self._toc:
            counter = self._recurse_navpoint(chapter, tmp, counter)

        tmp.write(u'''  </navMap>\n</ncx>''')
        self._write('toc.ncx', tmp.getvalue().encode('utf-8'))

    def _recurse_navpoint(self, node, buf, counter):
        buf.write(u'''<navPoint id="navPoint-%s" playOrder="%s">
      <navLabel>
        <text>%s</text>
      </navLabel>
      <content src="%s" />
''' % (counter, counter, node.get_title(), node.get_link()))
        counter += 1

        if node.get_depth() < TOC_DEPTH:
            for child in node.get_children():
                counter = self._recurse_navpoint(child, buf, counter)

        buf.write(u'</navPoint>\n')

        return counter

    def _write_content_cpf(self):
        tmp = CONTENT_TOP % (self._uuid, self._title, self._author)
        for ix in range(1, len(self._toc) + 1):
            tmp += u'<item id="ch%s_xhtml" href="ch%s.xhtml" media-type="application/xhtml+xml" />\n' % (ix, ix)
        if os.path.exists('cover.pages.png'):
            tmp += u'<item id="cover_pages_png" href="media/cover.pages.png" media-type="image/png" />\n'

        ix = 1
        for fig in self._figures:
            tmp += u'<item id="fig%s" href="%s" media-type="%s" />\n' % \
                   (ix, fig.get_file(), fig.get_media_type())
            ix += 1

        tmp += CONTENT_MID

        for ix in range(1, len(self._toc) + 1):
            tmp += u'<itemref idref="ch%s_xhtml" />\n' % ix

        tmp += CONTENT_BOTTOM % self._title
        self._write('content.opf', tmp.encode('utf-8'))

    def _write(self, filename, contents):
        open(filename, 'w').write(contents)
        self._zip.write(filename)
        os.unlink(filename)

class ToCNode:

    def __init__(self, parent, title):
        self._parent = parent
        self._title = title
        self._label = None
        self._children = []
        self._started = False
        self._position = None
        self._id = None

    def get_title(self):
        return self._title

    def get_label(self):
        return self._label

    def get_id(self):
        if not self._id:
            if self._parent:
                self._id = self._parent.get_id() + '-' + str(self._position)
            else:
                self._id = 'node%s' % self._position

        return self._id

    def get_depth(self):
        if self._parent:
            return self._parent.get_depth() + 1
        return 1

    def set_label(self, id):
        self._label = id

    def get_link(self):
        if not self._parent:
            return 'ch%s.xhtml' % self._position

        return self.get_root().get_link() + '#' + self.get_id()

    def get_children(self):
        return self._children

    def add_child(self, child):
        self._children.append(child)
        child.set_position(len(self._children))

    def get_root(self):
        if self._parent:
            return self._parent.get_root()
        else:
            return self

    def get_position(self):
        return self._position

    def set_position(self, pos):
        self._position = pos

    def start(self, buf):
        if self._started:
            return

        if self._parent:
            self._parent.start(buf)

        self._started = True

        depth = self.get_depth()
        if depth == 1: # ie, we're a chapter
            buf.write(u'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
  <meta name="generator" content="pandoc" />
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="stylesheet.css" />
</head>
<body>
<div id="%s" class="section level1">
<h1>%s</h1>\n''' % (self._title, self.get_id(), self._title))

        elif depth == 2:
            buf.write(u'''
            <div id="%s" class="section level2">
            <h2>%s</h2>\n''' % (self.get_id(), self._title))

        elif depth == 3:
            buf.write(u'''
            <div id="%s" class="section level3">
            <h3>%s</h3>\n''' % (self.get_id(), self._title))

    def close(self, buf):
        self.close_up_to(buf, 1)

    def close_up_to(self, buf, level):
        if self.get_depth() >= level:
            buf.write(u'</div>\n')
            if not self._parent:
                buf.write(u'</body>\n</html>\n')

            if self.get_depth() > level:
                self._parent.close_up_to(buf, level)

    def __repr__(self):
        return '[%s %s]' % (self._title.encode('utf-8'), self._parent)

class TocBuilder:
    '''Used to build the label -> id dictionary that's later used to resolve
    vref references.'''

    def __init__(self):
        self._toc = []
        self._current_node = None
        self._in_figure = False
        self._in_table = False
        self._map = {} # label -> (id, title)

    def get_map(self):
        return self._map

    def start_chapter(self, braces):
        self._current_node = ToCNode(None, braces)
        self._toc.append(self._current_node)
        self._current_node.set_position(len(self._toc))

    def start_section(self, braces):
        chapter = self._toc[ -1 ]
        self._current_node = ToCNode(chapter, braces)
        chapter.add_child(self._current_node)

    def start_subsection(self, braces):
        chapter = self._toc[ -1 ]
        section = chapter.get_children()[-1]
        self._current_node = ToCNode(section, braces)
        section.add_child(self._current_node)

    def label(self, id):
        if not (self._in_figure or self._in_table):
            self._map[id] = (self._current_node.get_link(),
                             self._current_node.get_title())

    def start_figure(self):
        self._in_figure = True
    def end_figure(self):
        self._in_figure = False

    def start_table(self):
        self._in_table = True
    def end_table(self):
        self._in_table = False

    def set_title(self, title):
        pass
    def set_author(self, author):
        pass
    def table_of_contents(self):
        pass
    def text(self, text):
        pass
    def newline(self):
        pass
    def graphic(self, braces):
        pass
    def caption(self, braces):
        pass
    def text_mono(self, text):
        pass
    def text_bold(self, text):
        pass
    def text_italics(self, text):
        pass
    def footnote(self, text):
        pass
    def start_list(self):
        pass
    def item(self):
        pass
    def end_list(self):
        pass
    def vref(self, braces):
        pass
    def close(self):
        pass

class Figure:
    def __init__(self):
        self._label = None
        self._caption = None
        self._file = None
        self._ended = False

    def is_open(self):
        return not self._ended

    def get_file(self):
        return 'media/' + os.path.split(self._file)[-1]

    def set_graphic(self, file):
        self._file = file

    def get_caption(self):
        return self._caption

    def set_caption(self, text):
        self._caption = text

    def set_label(self, id):
        self._label = id

    def end(self):
        self._ended = True

    def get_media_type(self):
        if self._file.endswith('.jpg'):
            return 'image/jpeg'
        elif self._file.endswith('.png'):
            return 'image/png'
        else:
            raise Exception('Unknown media type: %s' % self._file)

class DocumentHandler:

    def __init__(self, epub):
        self._epub = epub

    def command(self, name, braces, brackets):
        #print name, (braces or 'None').encode('utf-8'), brackets

        if name == 'title':
            self._epub.set_title(braces)
        elif name == 'author':
            self._epub.set_author(braces)
        elif name == 'chapter':
            self._epub.start_chapter(braces)
        elif name == 'section':
            self._epub.start_section(braces)
        elif name == 'subsection':
            self._epub.start_subsection(braces)
        elif name == 'tableofcontents':
            self._epub.table_of_contents()
        elif name == 'textbf':
            self._epub.text_bold(braces)
        elif name == 'texttt':
            self._epub.text_mono(braces)
        elif name == 'textit' or name == 'emph':
            self._epub.text_italics(braces)
        elif name in ('newif', 'documentclass', 'usepackage',
                      'renewcommand*', 'rmdefault'):
            pass
        elif name == '%':
            self._epub.text('%')
        elif name == 'begin' and braces == 'itemize':
            self._epub.start_list()
        elif name == 'end' and braces == 'itemize':
            self._epub.end_list()
        elif name == 'item':
            self._epub.item()
        elif name == 'begin' and braces == 'figure':
            self._epub.start_figure()
        elif name == 'caption':
            self._epub.caption(braces)
        elif name == 'includegraphics':
            self._epub.graphic(braces)
        elif name == 'end' and braces == 'figure':
            self._epub.end_figure()
        elif name == 'begin' and braces == 'tabular':
            self._epub.start_table()
        elif name == 'end' and braces == 'tabular':
            self._epub.end_table()
        elif (name == 'begin' or name == 'end') and \
             (braces == 'center' or 'document'):
            pass # just ignore this
        elif name == 'date':
            pass # ignore this, too
        elif name == '\\':
            self._epub.newline()
        elif name == 'label':
            self._epub.label(braces)
        elif name == 'footnote':
            self._epub.footnote(braces)
        elif name == 'vref':
            self._epub.vref(braces)
        elif name == '-':
            pass # we ignore this one
        else:
            pass#print 'Unhandled command: ', name, braces

        # end figure -> file + caption + label

    def text(self, text):
        self._epub.text(text)

    def close(self):
        self._epub.close()

class TextHandler:

    def __init__(self):
        self._buf = StringIO()

    def getvalue(self):
        return self._buf.getvalue()

    def text(self, text):
        self._buf.write(text)

    def command(self, name, braces, brackets):
        if name in ('today', 'linebreak'):
            return # just ignore
        #print 'Unhandled text command: ', name, braces

    def close(self):
        pass

class FilterHandler:
    '''Takes care of turning \\v{z} into right characters, and doing if
    filtering.'''

    # ifstates:
    # 0: outside
    # 1: ifpaper
    # 2: else

    def __init__(self, handler):
        self._handler = handler
        self._mapping = {'v' : {'z' : u'\u017E', 'c' : u'\u010D',
                                's' : u'\u0161', 'C' : u'\u010C',
                                'S' : u'\u0160', 'Z' : u'\u017D',
                                ''  : u'\u02C7'},
                         'c' : {'u' : u'\u0173', 'e' : u'\u0119'},
                         '=' : {'u' : u'\u0169', 'U' : u'\u016A'},
                         '.' : {'e' : u'\u0117'}}
        self._ifstate = 0 # outside

    def command(self, name, braces, brackets):
        if self._mapping.has_key(name):
            char = self._mapping[name][braces]
            self._handler.text(char)
        elif name == 'ifpaper':
            self._ifstate = 1 # ifpaper
        elif name == 'else':
            self._ifstate = 2 # else
        elif name == 'fi':
            self._ifstate = 0 # outside
        else:
            if self._ifstate != 1: # not in ifpaper
                self._handler.command(name, braces, brackets)

    def text(self, text):
        self._handler.text(text)

    def close(self):
        self._handler.close()

class IncludeHandler:
    '''Follows include references.'''

    def __init__(self, path, handler):
        self._path = path
        self._handler = handler

    def command(self, name, braces, brackets):
        if name == 'include':
            filename = os.path.join(self._path, braces + '.tex')
            source = codecs.open(filename, 'r', 'utf-8').read()
            #print 'PARSING', filename
            parse_latex(source, self)
        else:
            #print 'COMMAND', repr(braces), repr(brackets)
            self._handler.command(name, braces, brackets)

    def text(self, text):
        #print 'TEXT', repr(text)
        self._handler.text(text)

    def close(self):
        self._handler.close()

if __name__ == '__main__':
    (fromfile, tofile) = sys.argv[1 : ]
    fromdir = os.path.split(fromfile)[0]

    # first we build the ToC and record the labels
    builder = TocBuilder()
    source = codecs.open(fromfile, 'r', 'utf-8').read()
    parse_latex(source, FilterHandler(DocumentHandler(builder)))

    # then we're ready to actually produce some epub
    handler = FilterHandler(DocumentHandler(EpubWriter(tofile, builder.get_map())))
    parse_latex(source, handler)
