''' Background server for running batch processes '''
import sys
import BaseHTTPServer
import percms.settings
from SimpleHTTPServer import SimpleHTTPRequestHandler


#if len(sys.argv) != 2:
#    print 'Usage: python %s <port #>' % sys.argv[0]
#    sys.exit(0)
port = percms.settings.BATCH_PORT

bind_address = ('127.0.0.1', port)


class Batch_Handler(SimpleHTTPRequestHandler):
    pass


Batch_Handler.protocol_version = 'HTTP/1.0'
server = BaseHTTPServer.HTTPServer(bind_address, Batch_Handler)

server.serve_forever()
