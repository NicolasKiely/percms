''' Background server for running batch processes '''
import sys
import BaseHTTPServer
import percms.settings
#from SimpleHTTPServer import SimpleHTTPRequestHandler
import batch_interface
import crypto.batch
import json
import urlparse

# To add more batch modules, add them here
BATCH_MODULES = {
    'crypto': crypto.batch
}


# Map of server URL paths to callback functions
CALLBACKS = {}


# Port/Address
port = percms.settings.BATCH_PORT
bind_address = ('127.0.0.1', batch_interface.PORT)


# Load batch handler methods from modules
for app_name, module in BATCH_MODULES.iteritems():
    for member in dir(module):
        lmember = member.lower()
        if lmember.startswith('post_'):
            path = '/%s/%s' % (app_name, lmember[5:])
            CALLBACKS[path] = getattr(module, member)
            

print '\n'.join(['Loading '+s for s in CALLBACKS.keys()])


class Batch_Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    ''' Handler function for batch requests '''
    def do_POST(req):
        output = {'status': 'success', 'message': ''}
        response_code = 200
        try:
            handler = CALLBACKS[req.path.lower()]

        except KeyError as ex:
            response_code = 404
            output = {'status': 'error', 'message': 'Command not found'}

        if response_code == 200:
            req_len = int(req.headers.getheader('content-length'))
            request = req.rfile.read(req_len)
            post_args = urlparse.parse_qs(request, keep_blank_values=False) 

            args = {k: v[0] for k,v in post_args.iteritems() if v and len(v)}
            handler(**args)
            

        req.send_response(response_code)
        req.send_header('Content-type', 'application/json')
        req.end_headers()
        req.wfile.write(json.dumps(output))



Batch_Handler.protocol_version = 'HTTP/1.0'
server = BaseHTTPServer.HTTPServer(bind_address, Batch_Handler)

try:
    server.serve_forever()
except KeyboardInterrupt:
    print '\nShutting Down'

server.server_close()
