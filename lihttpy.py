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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import socket
import optparse
import mimetypes


class Content:
    HttpHeader = '''\
HTTP/1.1 %s %s
Context-Type: %s
Server: lihttpy
Context-Length: '''

    Path = None

    def __init__(self, document_root, path):
        self.Path = path
        if "/" != path:
            self.RealPath = "%s%s" % (document_root, self.Path)
        else:
            self.RealPath = document_root

    def build(self):
        try:
            if os.path.isfile(self.RealPath):
                f = open(self.RealPath, "r")
                body = "".join(f.readlines())
                f.close()
                mime = mimetypes.guess_type(self.RealPath)[0]
            else:
                body = self.index()
                mime = "text/html"

            header = self.HttpHeader % (200, "OK", mime)
            return self._format_content(header, body)

        except:
            return self.error(404, "NOT FOUND")

    def index(self):

        if "/" != self.Path:
            file_list = ["<li><a href='../'>..</a>"]
            path = self.Path

        else:
            file_list = []
            path = ""

        for i in os.listdir(self.RealPath):
            file_list.append("<li><a href='%s/%s'>%s</a>" % (path, i, i))

        return "<html><ul>%s</ul></html>" % '\n'.join(file_list)

    def _format_content(self, header, body):
        return "%s %d\n\n%s\n\n" % (header, len(body), body)

    def error(self, code, desc):
        header = self.HttpHeader % (code, desc, "text/html")
        body = "%s %s" % (code, desc)

        return self._format_content(header, body)


class HttpServer:
    Options = None
    Socket = None
    Signal = True

    def __init__(self, options):
        self.Options = options

    def shutdown(self):
        self.Signal = False

    def start(self):
        self.build_socket()
        # Loop
        while self.Signal:
            try:
                (connection, client) = self.Socket.accept()
                self.do_transcation(connection, client)
            except socket.error, e:
                print "Connection fail!"
            finally:
                connection.close()

        self.Socket.shutdown()

    def do_transcation(self, connection, client):
        PACKAGE_LENGTH = 1 << 9
        data = connection.recv(PACKAGE_LENGTH)
        (method, path, protocol) = self.get_reciver(data)

        content = Content(self.Options.document_root, path)
        response = content.build()

        connection.send(response)

    def build_socket(self):
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = (self.Options.address, self.Options.port)
        print self.Options
        self.Socket.bind(port)
        self.Socket.listen(2)

    def get_reciver(self, data):
        request_body = data.split("\r\n")
        return tuple(request_body[0].split(" "))


if __name__ == '__main__':
    opt = optparse.OptionParser()
    opt.add_option("-d", "--document-root",
                   help="Define a path as portal root", default=os.getcwd())

    opt.add_option("--address", default="127.0.0.1",
                   help="Address to listen, 127.0.0.1 is the default")

    opt.add_option("-p", "--port", default=8080, type=int,
                   help="Port to listen, 8080 is the default")

    (options, args) = opt.parse_args()

    print options
    a = HttpServer(options)
    a.start()
