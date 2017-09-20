''' Communication interface with batch server '''
import urllib2
import urllib

PORT = 8010


def request(app, method, args):
    data = urllib.urlencode(args)
    url = 'http://127.0.0.1:%s/%s/%s' % (PORT, app, method)
    request = urllib2.urlopen(url, data)
    return request.read()
