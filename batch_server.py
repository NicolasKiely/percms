''' Background server for running batch processes '''
import sys
import os
import BaseHTTPServer
import percms.settings
import batch_interface
import json
import urlparse
import django
import threading
import Queue
import traceback

os.environ['DJANGO_SETTINGS_MODULE'] = 'percms.settings'
django.setup()

import crypto.batch
import scripting.utils

work_queue = Queue.Queue(10)


def load_modules(batch_modules, do_reload):
    ''' Loads modules '''
    callbacks = {}

    # Load batch handler methods from modules
    for app_name, module in batch_modules.iteritems():
        if do_reload:
            reload(module)

        for member in dir(module):
            lmember = member.lower()
            if lmember.startswith('post_'):
                path = '/%s/%s' % (app_name, lmember[5:])
                callbacks[path] = getattr(module, member)

    return callbacks


class Worker_Thread(threading.Thread):
    current_job = None
    def run(self):
        try:
            logger = scripting.utils.Logging_Runtime('Batch_Server')
            while True:
                func, args = work_queue.get()
                if func==None and args==None:
                    # Exit condition
                    break
                # Call handler on args
                try:
                    self.current_job = (func, args)
                    func(logger, **args)
                    self.current_job = None

                except KeyboardInterrupt:
                    raise KeyboardInterrupt

                except Exception as ex:
                    logger.log('Unhandled Exception', traceback.format_exc())

        except KeyboardInterrupt:
            raise KeyboardInterrupt
        

# To add more batch modules, add them here
global BATCH_MODULES
BATCH_MODULES = {
    'crypto': crypto.batch
}


# Map of server URL paths to callback functions
global CALLBACKS
CALLBACKS = load_modules(BATCH_MODULES, False)


# Port/Address
port = percms.settings.BATCH_PORT
bind_address = ('127.0.0.1', batch_interface.PORT)

            

print '\n'.join(['Loading '+s for s in CALLBACKS.keys()])


class Batch_Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    ''' Handler function for batch requests '''
    def do_POST(req):
        output = {'status': 'success', 'message': ''}
        response_code = 200
        handler = None
        global CALLBACKS
        global BATCH_MODULES

        req_path = req.path.lower()
        if req_path == '/batch/help':
            output['status'] = 'info'
            message = 'Functions: '
            for k, v in CALLBACKS.iteritems():
                doc = v.__doc__ if v.__doc__ else ''
                message += '\n'+ k + '\n\t'+ doc.replace('\n', '\n\t')

            output['message'] = message

        elif req_path == '/batch/reload':
            output['message'] = 'Reloaded'

            CALLBACKS = load_modules(BATCH_MODULES, True)

        elif req_path == '/batch/jobs':
            output['status'] = 'info'
            jobs = list(work_queue.queue)
            message = ''
            for i, worker in enumerate(workers):
                if worker.current_job:
                    job_name = worker.current_job[0].__name__
                    message += 'Worker %s: %s\n' % (i, job_name)
                else:
                    message += 'Worker %s: free\n' % (i,)

            if work_queue.empty():
                message += 'Empty queue\n'

            elif work_queue.full():
                message += 'Work queue full!\n'

            message += '\n\t'.join([f.__name__ for f, a in jobs])
            output['message'] = message

        else:
            try:
                handler = CALLBACKS[req_path]

            except KeyError as ex:
                response_code = 404
                output = {'status': 'error', 'message': 'Command not found'}

            if response_code == 200:
                req_len = int(req.headers.getheader('content-length'))
                request = req.rfile.read(req_len)
                post_args = urlparse.parse_qs(request, keep_blank_values=True) 

                args = {k: v[0] for k,v in post_args.iteritems() if v and len(v)}
            

        req.send_response(response_code)
        req.send_header('Content-type', 'application/json')
        req.end_headers()
        req.wfile.write(json.dumps(output))

        if response_code == 200 and handler:
            try:
                #handler(**args)
                work_queue.put( (handler, args) )
            except Exception as ex:
                print '%s: %s' % (type(ex), ex)



Batch_Handler.protocol_version = 'HTTP/1.0'
server = BaseHTTPServer.HTTPServer(bind_address, Batch_Handler)

num_workers = 1
workers = [Worker_Thread() for i in range(0, num_workers)]
#worker = Worker_Thread()
#worker.start()
for worker in workers:
    worker.start()

try:
    server.serve_forever()
except KeyboardInterrupt:
    print '\nShutting Down'
    work_queue.put( (None, None) )
    for worker in workers:
        worker.join()

server.server_close()
