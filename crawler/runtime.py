''' Runtime header for crawler scripts, to simplify things '''

from . import models
from percms import safesettings
import bs4


class Runtime(object):
    ''' Stores argument information '''
    def __init__(self, args):
        ''' Import args passed from script executor '''
        self.website = models.Website.objects.get(domain=args['domain'])
        self.webpage = models.Webpage.objects.get(pk=args['webpage.id'])
        self.marker = models.Webpage_Mark.objects.get(pk=args['marker.id'])
        self.crawler = models.Crawler.objects.get(pk=args['crawler.id'])


    def get_webpage(self, path, create=True):
        ''' Getter for a webpage by path '''
        try:
            webpage = models.Webpage.objects.get(
                website=self.website, path=path
            )
        except models.Webpage.DoesNotExist as ex:
            if create:
                webpage = models.Webpage(website=self.website, path=path)
                webpage.save()
            else:
                return None
        return webpage


    def load_dom(self):
        ''' Get webpage source html '''
        local_path = safesettings.UPLOAD_CRAWLER_PATH
        with open('%spage-%s.html' % (local_path, str(self.webpage.pk)), 'r') as fh:
            html = fh.read()
        return bs4.BeautifulSoup(html, 'html.parser')


    def mark_webpage(self, path, state_name=None, to_crawl=True):
        ''' Mark webpage to be crawled for given state'''
        webpage = self.get_webpage(path)
        if state_name:
            # Lookup state for this crawler
            state = models.Crawler_State.objects.get(
                name=state_name, config=self.crawler.config
            )
        else:
            # Default to using next state
            state = self.crawler.active_state.next_state

        marker, x = models.Webpage_Mark.objects.get_or_create(
            webpage=webpage, state=state
        )

        marker.to_crawl = to_crawl
        marker.save()
