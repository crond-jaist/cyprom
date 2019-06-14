
#############################################################################
# "signal" trigger for allowing control via external input
#
# NOTE: A command such as below can be used to send signals to the module
#       $ echo "SIGNAL" | nc 127.0.0.1 10000
#############################################################################

# Local imports
from lib import SOCKET
from database_base import sqlBoard

# Local constants
MODULE_NAME = u"signal"
MESSAGE_KEY = "message" # Optional parameter
DEFAULT_MESSAGE = u"Signal received!"
SOCKET_MESSAGE = b"complete"

# Trigger class definition
class signal:
        
        # Check trigger parameters
	def check(self, trigger):
		return True

        # Execute trigger
	def trigger(self, teamName, trigger):
		if MESSAGE_KEY in trigger:
			message = trigger[MESSAGE_KEY]
		else:
			message = DEFAULT_MESSAGE

		board = sqlBoard()
		sock = SOCKET()

		board.insert(teamName, MODULE_NAME, message)
                print("[.] signal: {0}: Waiting for signal ...".format(teamName))
		response = sock.recv(teamName, board)
                print("[.] signal: {0}: Received signal: {1}".format(teamName, response))

		board.deletePort(teamName)
		board.hideClick(teamName)

		sock.send(SOCKET_MESSAGE)
                print("[.] signal: {0}: Message: {1}".format(teamName, message))
