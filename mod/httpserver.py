"""wrap SimpleHTTPServer and prevent Ctrl-C stack trace output"""

import SimpleHTTPServer
import SocketServer

import log

try :
    log.colored(log.GREEN, 'serving on http://localhost:8000 (Ctrl-C to quit)')
    httpd = SocketServer.TCPServer(('localhost', 8000), SimpleHTTPServer.SimpleHTTPRequestHandler)
    httpd.serve_forever()
except KeyboardInterrupt:
    log.colored(log.GREEN, '\nhttp server stopped')
    exit(0)

