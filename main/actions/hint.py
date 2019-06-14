
#############################################################################
# "hint" action for displaying hints to trainees
#############################################################################

# Local imports
from database_base import sqlProgress, sqlLog, sqlBoard

# Local constants
HINT_KEY = "hint"
COMMENT_SUCCESS = "Hint display succeeded"

class hint:

        # Check action parameters
	def check(self, action):
		if HINT_KEY in action:
		        if isinstance(action[HINT_KEY], list) or isinstance(action[HINT_KEY], str) or isinstance(action[HINT_KEY], unicode):
			        return True
                        else:
                                print("[-] hint: ERROR: Hint is not a list or string: '{0}'".format(action[HINT_KEY]))
                else:
                        print("[-] message: hint: Required parameter not provided: '{0}'".format(HINT_KEY))
                return False

        # Execute action
	def action(self, teamName, address, action, data):

		# Get now step
		progress = sqlProgress()
		step = progress.selectNowStep(teamName)
		del progress

		# Get counter for repetitions so far (1st time => 0, 2nd time => 1, etc.)
		log = sqlLog()
		count = log.countStep(teamName, step)
		del log

		board = sqlBoard()

		if isinstance(action[HINT_KEY], list):

			# Display all hints if repetitions exceed the number of hints
			if len(action[HINT_KEY]) <= count:
				count = len(action[HINT_KEY]) - 1

			for i in range(count + 1):
				board.insert(teamName, HINT_KEY, action[HINT_KEY][i])
                                print("[.] hint: Display ({0}) '{1}'".format(i+1, action[HINT_KEY][i]))
		else:
			board.insert(teamName, HINT_KEY, action[HINT_KEY])
                        print("[.] hint: Display '{0}'".format(action[HINT_KEY]))

		return True, COMMENT_SUCCESS, data
