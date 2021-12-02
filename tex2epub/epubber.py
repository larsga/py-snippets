'''
Utility to generate ebooks in epub format.
'''

import codecs, string, os, zipfile, uuid, shutil, datetime

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
    %s <!-- isbn goes here -->
    <dc:title id="epub-title-1">%s</dc:title>
    <dc:date id="epub-date-1">%s</dc:date>
    <dc:language>en-US</dc:language>
    <dc:creator id="epub-creator-1" opf:role="aut">%s</dc:creator>
    %s <!-- publisher -->
    <meta name="cover" content="cover_pages_png" />
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
    <item id="style" href="stylesheet.css" media-type="text/css" />
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" />
    <item id="cover_xhtml" href="cover.xhtml" media-type="application/xhtml+xml" />
'''

CONTENT_MID = u'''  </manifest>
  <spine toc="ncx">
    <itemref idref="cover_xhtml" linear="no" />
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
h2 { text-align: left; page-break-after: avoid }
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

    def __init__(self, filename, labelmap, toc_depth = 2, cover_image = None):
        self._filename = filename
        self._zip = zipfile.ZipFile(filename, 'w')
        self._uuid = 'urn:uuid:' + str(uuid.uuid1())
        self._toc = []
        self._current_node = None
        self._buf = None
        self._para = False # not started
        self._figures = []
        self._image_files = set()
        self._in_list_item = False
        self._in_table = False
        self._row = []
        self._labelmap = labelmap # label -> (link, title)
        self._toc_depth = toc_depth
        self._title_page = False

        self._title = None
        self._subtitle = None
        self._author = None
        self._isbn = None
        self._publisher = None

        self._write('mimetype', 'application/epub+zip')

        os.mkdir('META-INF')
        self._write('META-INF/container.xml', CONTAINER)
        self._write('META-INF/com.apple.ibooks.display-options.xml',
                    DISPLAY_OPTIONS)
        os.rmdir('META-INF')

        self._write('stylesheet.css', STYLESHEET)
        if not os.path.exists('media'):
            os.mkdir('media')

        self._cover_image = None
        if cover_image:
            shutil.copy(cover_image, 'media/' + cover_image)
            self._zip.write('media/' + cover_image)
            self._cover_image = cover_image

    def set_title(self, title):
        self._title = title.replace('--', u'\u2014')

    def set_subtitle(self, subtitle):
        self._subtitle = subtitle

    def get_title(self):
        if not self._subtitle:
            return self._title
        else:
            return self._title + ': ' + self._subtitle

    def set_author(self, author):
        self._author = author

    def set_isbn(self, isbn):
        self._isbn = isbn

    def set_publisher(self, publisher):
        self._publisher = publisher

    def start_chapter(self, title):
        if self._para:
            self._buf.write(u'</p>')
            self._para = False
        if self._current_node:
            self._finish_chapter()

        self._current_node = ToCNode(None, title)
        self._toc.append(self._current_node)
        self._current_node.set_position(len(self._toc))
        self._buf = StringIO()
        # we don't start writing the chapter here, because we don't know
        # the label yet

    def start_section(self, title):
        if self._para:
            self._buf.write(u'</p>')
            self._para = False
        self._current_node.close_up_to(self._buf, 2)

        chapter = self._toc[ -1 ]
        self._current_node = ToCNode(chapter, title)
        chapter.add_child(self._current_node)

    def start_subsection(self, title):
        if self._para:
            self._buf.write(u'</p>')
            self._para = False
        self._current_node.close_up_to(self._buf, 3)

        chapter = self._toc[ -1 ]
        section = chapter.get_children()[-1]
        self._current_node = ToCNode(section, title)
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

        if f.get_file() not in self._image_files:
            shutil.copy(os.path.join(fromdir, f._file), 'media')
            self._zip.write(f.get_file())
            os.unlink(f.get_file())
            self._image_files.add(f.get_file())

    def add_image_file(self, fileref):
        f = Figure()
        self._figures.append(f)
        f.set_graphic(fileref)
        filename = os.path.split(fileref)[-1]

        if f.get_file() not in self._image_files:
            shutil.copy(fileref, 'media/' + filename)
            self._zip.write(f.get_file())
            self._image_files.add(f.get_file())

        return f

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

    def add_title_page(self):
        self._title_page = True
        page = TITLE_PAGE % (self.get_title(), self.get_title(), self._author)
        self._write('title_page.xhtml', page.encode('utf-8'))

    def add_xhtml_blob(self, blob):
        self._current_node.start(self._buf)
        self._buf.write(blob)

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

        shutil.rmtree('media')

    def _write_cover_xhtml(self):
        cover_image = ''
        if self._cover_image:
            cover_image = '''
            <div id="cover-image">
              <img src="media/%s" alt="cover image" />
            </div>
            ''' % self._cover_image

        self._write('cover.xhtml', (u'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
  <meta name="generator" content="epubber.py" />
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="stylesheet.css" />
</head>
<body>
        %s
</body>
</html>''' % (self.get_title(), cover_image)).encode('utf-8'))

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
        ''' % (self.get_title(), self.get_title()))

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
        if node.get_depth() < self._toc_depth:
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
''' % (self._isbn or self._uuid, self.get_title()))

        if self._title_page:
            tmp.write(u'''
    <navPoint id="navPoint-0">
      <navLabel>
        <text>%s</text>
      </navLabel>
      <content src="title_page.xhtml" />
    </navPoint>
            ''' % self.get_title())

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

        if node.get_depth() < self._toc_depth:
            for child in node.get_children():
                counter = self._recurse_navpoint(child, buf, counter)

        buf.write(u'</navPoint>\n')

        return counter

    def _write_content_cpf(self):
        theid = self._isbn
        if theid:
            isbn = '<dc:identifier id="uid" opf:scheme="ISBN">%s</dc:identifier>' % theid
        else:
            self._theid = self._uuid
            isbn = ''

        publisher = ''
        if self._publisher:
            publisher = '<dc:publisher>%s</dc:publisher>' % self._publisher

        tmp = CONTENT_TOP % (theid, isbn, self.get_title(), now(), self._author,
                             publisher)
        for ix in range(1, len(self._toc) + 1):
            tmp += u'<item id="ch%s_xhtml" href="ch%s.xhtml" media-type="application/xhtml+xml" />\n' % (ix, ix)
        if self._cover_image:
            tmp += u'<item id="cover_pages_png" href="media/%s" media-type="%s" />\n' % (self._cover_image, get_media_type(self._cover_image))

        if self._title_page:
            tmp += '<item id="title_page_xhtml" href="title_page.xhtml" media-type="application/xhtml+xml" />\n'

        ix = 1
        for filename in self._image_files:
            tmp += u'<item id="fig%s" href="%s" media-type="%s" />\n' % \
                   (ix, filename, get_media_type(filename))
            ix += 1

        tmp += CONTENT_MID

        if self._title_page:
            tmp += '<itemref idref="title_page_xhtml" linear="yes" />\n'

        for ix in range(1, len(self._toc) + 1):
            tmp += u'<itemref idref="ch%s_xhtml" />\n' % ix

        tmp += CONTENT_BOTTOM % self.get_title()
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

def get_media_type(filename):
    if filename.endswith('.jpg'):
        return 'image/jpeg'
    elif filename.endswith('.png'):
        return 'image/png'
    else:
        raise Exception('Unknown media type: %s' % filename)

def now():
    timestamp = str(datetime.datetime.now())
    ix = timestamp.find('.')
    return timestamp[ : ix].replace(' ', 'T') + 'Z'
