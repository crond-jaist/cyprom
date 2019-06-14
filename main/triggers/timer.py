
#############################################################################
# "timer" trigger for allowing delayed execution of actions
#############################################################################

# Standard library imports
from time import sleep

# Local constants
DELAY_KEY = "delay"

# Trigger class definition
class timer:

        # Check trigger parameters
	def check(self, trigger):

                # Check whether mandatory parameter exists
		if DELAY_KEY in trigger:

                        # Check whether the parameter value is an integer 
			if isinstance(trigger[DELAY_KEY], int):
				return True

                print("[-] timer: ERROR: Mandatory parameter not provided or invalid: '{0}'".format(DELAY_KEY))
		return False

        # Execute trigger
	def trigger(self, teamName, trigger):
                print("[.] timer: {0}: Sleeping for {1} s ...".format(teamName, trigger[DELAY_KEY]))
		sleep(trigger[DELAY_KEY])
