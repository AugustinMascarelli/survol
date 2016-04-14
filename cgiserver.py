#!/usr/bin/env python3

import sys

# If Apache is not available or if we want to run the website
# with a specific user account.

# TODO: Do this also for Python2


if sys.version_info[0] < 3:
    # Not finished.
    import CGIHTTPServer
    import BaseHTTPServer
    from BaseHTTPServer import HTTPServer
    from CGIHTTPServer import _url_collapse_path
    class MyCGIHTTPServer(CGIHTTPServer.CGIHTTPRequestHandler):
    # class MyCGIHTTPServer(CGIHTTPRequestHandler):
      def is_cgi(self):
        collapsed_path = _url_collapse_path(self.path)
        for path in self.cgi_directories:
            if path in collapsed_path:
                dir_sep_index = collapsed_path.rfind(path) + len(path)
                head, tail = collapsed_path[:dir_sep_index], collapsed_path[dir_sep_index + 1:]
                self.cgi_info = head, tail
                return True
        return False

    server = BaseHTTPServer.HTTPServer
    handler = MyCGIHTTPServer

    handler.cgi_directories = [ 'htbin' ]
    print("Cgi directories=%s" % handler.cgi_directories)
    server = HTTPServer(('localhost', 8000), handler)
    server.serve_forever()
else:
    from http.server import CGIHTTPRequestHandler, HTTPServer
    class MyCGIHTTPServer(CGIHTTPRequestHandler):
        def is_cgi(self):
            sys.stderr.write("is_cgi self.path=%s\n" % self.path)
            # TODO: What is the equivalent of _url_collapse_path ?
            if True:
                collapsed_path = self.path
            else:
                collapsed_path = _url_collapse_path(self.path)
            for path in self.cgi_directories:
                if path in collapsed_path:
                    dir_sep_index = collapsed_path.rfind(path) + len(path)
                    head, tail = collapsed_path[:dir_sep_index], collapsed_path[dir_sep_index + 1:]
                    self.cgi_info = head, tail
                    return True
            return False

    handler = MyCGIHTTPServer
    server = HTTPServer(('localhost', 8000), handler)
    server.serve_forever()
