# coding:utf-8

# Standard library imports
import random
from time import sleep

# Flag indicating whether to sleep when executing the test action
ENABLE_SLEEP = True

# Local constants
SUCCESS_THRESHOLD = 0.5
COMMENT_SUCCESS = "Test action success"
COMMENT_FAILURE = "Test action failure"

# Test action used for demonstration purposes
class test:

        # Check whether the action definition is correct
	def check(self, action):
		return True

        # Execute action
	def action(self, teamName, address, action, data):
		rand_val = random.random()
                if ENABLE_SLEEP:
                        sleep(rand_val)
		if rand_val < SUCCESS_THRESHOLD:
			return True, COMMENT_SUCCESS, data
		else:
			return False, COMMENT_FAILURE, data
