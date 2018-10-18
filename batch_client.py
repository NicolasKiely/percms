import urllib
import urllib2
import sys
import batch_interface
import json


if len(sys.argv) == 1:
    print 'Usage: python %s <command> [parameter=value] ...' % sys.argv[0]
    print 'Try python %s batch/help to see list of functions' % sys.argv[0]
    print '\tor pythor %s batch/reload to reload functions' % sys.argv[0]
    sys.exit(0)

command = sys.argv[1]
post_arg_list = [x.split('=') for x in sys.argv[2:]]
post_args = {k:v for k,v in post_arg_list}
post_data = urllib.urlencode(post_args)
url = 'http://127.0.0.1:%s/%s' % (batch_interface.PORT, command)

print 'Querying %s' % url
response = urllib2.urlopen(url, data=post_data)
msg = json.loads(response.read())

print 'Status: ' + msg['status']
print msg['message']

