#!/usr/bin/env python

# #
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Litrin Jiang
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

__version__ = "1.1"
import posixpath
import urllib
from cStringIO import StringIO
import os, sys
import optparse
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer

opt = optparse.OptionParser()
opt.add_option("-d", "--document-root",
               help="Define a path as portal root", default=os.getcwd())

opt.add_option("--address", default="127.0.0.1",
               help="Address to listen, 127.0.0.1 is the default")

opt.add_option("-p", "--port", default=8080, type=int,
               help="Port to listen, 8080 is the default")

opt.add_option("-b", "--browser", default=False, action="store_true",
               help="Open portal by default browser.")

(options, args) = opt.parse_args()


class Server(SimpleHTTPRequestHandler):
    server_version = "lihttpy/" + __version__

    def translate_path(self, path):
        path = path.split('?', 1)[0].split('#', 1)[0]
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')

        path = options.document_root
        for word in words:
            if word is None:
                continue
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'

        return path

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None

        displaypath = urllib.url2pathname(urllib.unquote(self.path))
        content = ['''<html><title>Directory listing for %s</title>
                <body><h2>Directory listing for %s</h2><hr><ul>
            ''' % (displaypath, displaypath)]

        if path != options.document_root:
            content.append("<li><a href='..'>..</a>")

        list.sort(key=lambda a: a.lower())
        for name in list:
            content.append('<li><a href="%s">%s</a>'
                     % (urllib.quote(name), urllib.url2pathname(name)))

        content.append("</ul><hr></body></html>")
        content = "".join(content)

        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", len(content))
        self.end_headers()

        handle = StringIO(content)
        self.copyfile(handle, self.wfile)
        handle.close()


if __name__ == '__main__':

    server_address = (options.address, options.port)
    httpd = HTTPServer(server_address, Server)

    print "Serving HTTP on", options.address, "port", options.port, "..."

    if options.browser:
        try:
            import webbrowser

            url = "http://%s:%s/" % (options.address, options.port)
            webbrowser.open(url)
        except:
            pass

    httpd.serve_forever()
