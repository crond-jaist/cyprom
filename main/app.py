import os,sys

version = sys.version_info[0]

if version == 2:
	import SimpleHTTPServer as http
	import SocketServer as socket
else:
	import http.server as http
	import socketserver as socket

def app(port,cd):
	os.chdir(os.path.join(cd,"public"))

	Handler = http.SimpleHTTPRequestHandler
	httpd = socket.TCPServer(("", port), Handler)

	httpd.serve_forever()
