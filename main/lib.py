
#############################################################################
# Classes related to socket operations
#############################################################################

# Standard library imports
import socket

# Local imports
from character import decode


class SOCKET():
	def __init__(self,proto = "tcp"):
		if proto == "tcp":
			self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		elif proto == "udp":
			pass

	def server(self,port):
		self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		self.sock.bind(("localhost",port))
		return sock

	def recv(self,teamName,sqlBoard):
		self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

		PORT = 10000
		while True:
			try:
				self.sock.bind(("localhost",PORT))
				break
			except socket.error:
				PORT += 1

		sqlBoard.insert(teamName,u"port",unicode(PORT),0)

		# Receive message
		self.sock.listen(1)
		self.conn, address = self.sock.accept()

		message = self.conn.recv(1024)
		return decode(message)

	def send(self,byte):
		self.conn.sendall(byte)

	def __del__(self):
		self.conn.close()
		self.sock.close()
