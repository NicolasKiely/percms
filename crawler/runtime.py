''' Runtime header for crawler scripts, to simplify things '''

from . import models


class Runtime(object):
    ''' Stores argument information '''
    def __init__(self, args):
        ''' Import args passed from script executor '''
        self.website = models.Website.objects.get(domain=args['domain'])
        self.webpage = models.Webpage.objects.get(pk=args['webpage.id'])
        self.marker = models.Webpage_Mark.objects.get(pk=args['marker.id'])


    def get_webpage(self, path, create=True):
        ''' Getter for a webpage by path '''
        try:
            webpage = models.Webpage.objects.filter(
                website=self.website, path=path
            )
        except models.Webpage.DoesNotExist as ex:
            if create:
                webpage = models.Webpage(website=self.website, path=path)
                webpage.save()
            else:
                return None
        return webpage
                

    def finished(self):
        ''' Indicate successful finish of crawler '''
        self.marker.to_crawl = False
        self.marker.save()
