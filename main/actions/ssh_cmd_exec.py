
#############################################################################
# "ssh_cmd_exec" action implementing lightweight command execution via SSH
#############################################################################

# Third party imports
import paramiko

# Local constants
USER_KEY = "user"
PASSWORD_KEY = "password"
COMMAND_KEY = "command"

DEFAULT_USER = "root"
DEFAULT_PASSWORD = "admin"

COMMENT_ACCESS_SUCCESS = "SSH access succeeded"
COMMENT_ACCESS_FAILURE = "SSH access failed"
COMMENT_COMMAND_SUCCESS = "SSH command execution succeeded"
COMMENT_COMMAND_FAILURE = "SSH command execution failed"

class ssh_cmd_exec:

	# Check action parameters
        def check(self,action):

                # All parameters are optional, so no checking done
		return True

        # Execute action
	def action(self, team_name, address, action, data):

                # Check if user information is provided as option or via the data
		if USER_KEY in action:
			user = action[USER_KEY]
		elif USER_KEY in data:
			user = data[USER_KEY]
		else:
			user = DEFAULT_USER

                # Check if password information is provided as option or via the data
		if PASSWORD_KEY in action:
			password = action[PASSWORD_KEY]
		elif PASSWORD_KEY in data:
			password = data[PASSWORD_KEY]
		else:
			password = DEFAULT_PASSWORD

                # Set up a paramiko SSH client
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.WarningPolicy())

                # Try to connect
		try:
			client.connect(address,username=user,password=password)
		except paramiko.ssh_exception.AuthenticationException:
			client.close()
			return False, COMMENT_ACCESS_FAILURE, data

		if COMMAND_KEY not in action:
			return True, COMMENT_ACCESS_SUCCESS, data
		else:
			for command in action[COMMAND_KEY]:
                                # Execute command remotely
				stdin,stdout,stderr = client.exec_command(command)

                                # Count lines to determine if error was encountered
                                # TODO: Improve detection mechanism
				count1 = 0
				count2 = 0
				for line in stdout:
					count1 += 1
				for line in stderr:
					print line
					count2 += 1

				if count1 == 0 and count2 != 0:
                                        client.close()
					return False, COMMENT_COMMAND_FAILURE, {}

		client.close()
		return True, COMMENT_COMMAND_SUCCESS, stdout
