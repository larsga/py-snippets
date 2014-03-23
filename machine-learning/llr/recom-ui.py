
import web, os
import search

urls = (
    '/', 'Index',
    '/search', 'Search',
    '/movie/(\d+)', 'Movie',
    '/like', 'Like',
    '/likes', 'ShowLikes',
    '/removelike', 'RemoveLikes',
    )

def nocache():
    web.header("Content-Type","text/html; charset=utf-8")
    web.header("Pragma", "no-cache");
    web.header("Cache-Control", "no-cache, no-store, must-revalidate, post-check=0, pre-check=0");
    web.header("Expires", "Tue, 25 Dec 1973 13:02:00 GMT");
    
class Index:
    def GET(self):
        nocache()
        return render.index()

class Search:
    def GET(self):
        nocache()
        query = web.input().get('query')
        return render.search(search.do_query('title', query))

class Movie:
    def GET(self, movieid):
        nocache()
        print 'LIKED', getattr(session, 'liked', '')
        doc = search.do_query('id', movieid)[0]

        #recoms = search.do_query('indicators', movieid)
        recoms = [search.do_query('id', movieid)[0] for movieid in doc.bets]
        
        if hasattr(session, 'liked'):
            youlike = search.do_query('indicators', session.liked)
        else:
            youlike = []
        return render.movie(doc, recoms, youlike)

class Like:
    def POST(self):
        nocache()
        movieid = web.input().get('movie')
        # using a set to avoid duplicates
        unique = set([movieid] + getattr(session, 'liked', '').split())
        session.liked = ' '.join(unique)
        web.seeother(web.ctx.homedomain + "/movie/" + movieid)

class ShowLikes:
    def GET(self):
        nocache()
        ids = getattr(session, 'liked', []).split()
        return render.showlikes([search.do_query('id', movieid)[0]
                                 for movieid in ids])

class RemoveLikes:
    def POST(self):
        nocache()

        if web.input().get('clear'):
            session.liked = ''
        else:
            for r in web.input().keys():
                if r.startswith('movie_'):
                    id = r[len('movie_') : ]

                    liked = session.liked.split()
                    liked.remove(id)

                    session.liked = ' '.join(liked)

        web.seeother(web.ctx.homedomain + '/likes')
        
        
render = web.template.render(os.path.join('.', 'templates/'),
                             base = "base")
web.config.session_parameters['cookie_path'] = '/'
web.config.session_parameters['max_age'] = (24 * 60 * 60) * 30 # 30 days
app = web.application(urls, globals(), autoreload = False)
session = web.session.Session(app, web.session.DiskStore('sessions'))
app.run()
