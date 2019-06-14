
#############################################################################
# "message" action for displaying messages to trainees
#############################################################################

# Local imports
from database_base import sqlProgress, sqlLog, sqlBoard

# Local constants
MESSAGE_KEY = "message"
COMMENT_SUCCESS = "Message display succeeded"

class message:

        # Check action parameters
	def check(self, action):
		if MESSAGE_KEY in action:
                        if isinstance(action[MESSAGE_KEY], list) or isinstance(action[MESSAGE_KEY], str) or isinstance(action[MESSAGE_KEY], unicode):
			        return True
                        else:
                                print("[-] message: ERROR: Message is not a list or string: '{0}'".format(action[MESSAGE_KEY]))
                else:
                        print("[-] message: ERROR: Required parameter not provided: '{0}'".format(MESSAGE_KEY))
		return False

        # Fill in patterns with values from data field
        # TODO: Document functionality
 	def fill_paterns(self, message):
 		if isinstance(self.data, dict):
 			for key,value in self.data.items():
 				if isinstance(value, str) or isinstance(value, unicode):
 					message = message.replace("<"+key+">", value)
 				else:
 					continue
 		return message

        # Execute action
	def action(self, teamName, address, action, data):

		board = sqlBoard()
                self.data = data

		if isinstance(action[MESSAGE_KEY], list):
			for message_value in action[MESSAGE_KEY]:
                                message = self.fill_paterns(message_value)
				board.insert(teamName, MESSAGE_KEY, message)
                                print("[.] message: Display ({0}) '{1}'".format(i, message))
		else:
                        message = self.fill_paterns(action[MESSAGE_KEY])
			board.insert(teamName, MESSAGE_KEY, message)
                        print("[.] message: Display '{0}'".format(message))

		return True, COMMENT_SUCCESS, data
