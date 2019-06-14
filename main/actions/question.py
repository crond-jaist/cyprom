
#############################################################################
# "question" action for getting feedback from trainees
#
# NOTE: A command such as below can be used to send signals to the module
#       $ echo "ANSWER" | nc 127.0.0.1 10000
#############################################################################

# Local imports
from lib import SOCKET
from database_base import sqlBoard

# Local constants
QUESTION_KEY = "question"
ANSWER_KEY = "answer"

COMMENT_SUCCESS = "Question answered correctly"
COMMENT_FAILURE = "Question answered incorrectly"

class question:

        # Check action parameters
	def check(self, action):
		if QUESTION_KEY not in action:
                        print("[-] question: ERROR: Required parameter not provided: '{0}'".format(QUESTION_KEY))
			return False

		if ANSWER_KEY not in action:
                        print("[-] question: ERROR: Required parameter not provided: '{0}'".format(ANSWER_KEY))
			return False

		if isinstance(action[QUESTION_KEY], list) or isinstance(action[QUESTION_KEY], str) or isinstance(action[QUESTION_KEY], unicode):
		        if isinstance(action[ANSWER_KEY], str) or isinstance(action[ANSWER_KEY], unicode):
				return True
                        else:
                                print("[-] question: ERROR: Answer is not a string: '{0}'".format(action[ANSWER_KEY]))
                else:
                        print("[-] question: ERROR: Question is not list or string: '{0}'".format(action[QUESTION_KEY]))

		return False

        # Execute action
	def action(self, participant_name, address, action, data):

		correct_answer = action[ANSWER_KEY]

		board = sqlBoard()

		# Insert question tag and the actual question text into the database
		board.insert(participant_name, u"replied", QUESTION_KEY)
		if isinstance(action[QUESTION_KEY], list):
			for i,question in enumerate(action[QUESTION_KEY],1):
				if i == len(action[QUESTION_KEY]):
					board.insert(participant_name, QUESTION_KEY, question)
                                        print("[.]: question: {0}: Ask ({1}) '{2}'".format(participant_name, i, question))
				else:
					board.insert(participant_name, u"replied", question)
                                        print("[.]: question: {0}: Ask ({1}) '{2}'".format(participant_name, i, question))

		else:
			board.insert(participant_name, QUESTION_KEY, action[QUESTION_KEY])
                        print("[.]: question: {0}: Ask '{1}'".format(participant_name, action[QUESTION_KEY]))

		# Receive the answer
		sock = SOCKET()
                print("[.]: question: {0}: Waiting for the answer...".format(participant_name))
		recv_answer = sock.recv(participant_name,board)
                recv_answer = recv_answer.strip() # Make sure there are no white spaces before/after

		# Delete corresponding port from the database
		board.deletePort(participant_name)
		# Change type from question to message
		board.updateQuestion(participant_name)
                # Insert answer into the database
		board.insert(participant_name, ANSWER_KEY, recv_answer)

		# Check answer
		if correct_answer == recv_answer:
			board.insert(participant_name, u"message", u"Correct!")
			sock.send(b"correct")
                        print("[.]: question: {0}: Received correct answer: '{1}'".format(participant_name, recv_answer))
			return True, COMMENT_SUCCESS, data

		board.insert(participant_name, u"message", u"Wrong...")
		sock.send(b"failure")
                print("[.]: question: {0}: Received wrong answer: '{1}'".format(participant_name, recv_answer))
		return False, COMMENT_FAILURE, data
