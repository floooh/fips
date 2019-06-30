"""
    wrap SimpleHTTPServer and prevent Ctrl-C stack trace output

    NOTE: this is no longer used, instead npm's http-server, because
    this offers a more fully-features HTTP server.
"""

import sys

if sys.version_info > (3, 0):
    import http.server as SimpleHTTPServer
    import socketserver as SocketServer
else:
    import SimpleHTTPServer
    import SocketServer

import log

try :
    log.colored(log.GREEN, 'serving on http://localhost:8000 (Ctrl-C to quit)')
    SocketServer.TCPServer.allow_reuse_address = True
    httpd = SocketServer.TCPServer(('localhost', 8000), SimpleHTTPServer.SimpleHTTPRequestHandler)
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.shutdown()
    httpd.server_close()
    log.colored(log.GREEN, '\nhttp server stopped')
    exit(0)

