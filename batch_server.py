''' Background server for running batch processes '''
import sys
import BaseHTTPServer
import percms.settings
#from SimpleHTTPServer import SimpleHTTPRequestHandler
import batch_interface


port = percms.settings.BATCH_PORT
bind_address = ('127.0.0.1', batch_interface.PORT)


class Batch_Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    ''' Handler function for batch requests '''
    def do_POST(req):
        req.send_response(200)
        req.send_header('Content-type', 'application/json')
        req.end_headers()
        req.wfile.write('{}')



Batch_Handler.protocol_version = 'HTTP/1.0'
server = BaseHTTPServer.HTTPServer(bind_address, Batch_Handler)

try:
    server.serve_forever()
except KeyboardInterrupt:
    print '\nShutting Down'

server.server_close()
