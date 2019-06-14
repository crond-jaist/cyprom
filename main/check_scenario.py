
#############################################################################
# Functions related to scenario verification
#############################################################################

# Standard library imports
import os, glob

# Local imports
from character import decode
from storyboard import Storyboard

# Check whether input is a string (standard or Unicode)
def check_string(string):
	if isinstance(string,str) or isinstance(string,unicode):
		return True

	return False

# Check the syntax of trigger and action modules
# 'options' represents the content of 'trigger' or 'action' definitions
def check_module(options, module):
	# Check whether 'options' is a dictionary
	if not isinstance(options, dict):
		print("[-] '{0}' is not a dictionary.".format(module))
		return False

	# Handle the 'module' option
	if Storyboard.MODULE_KEY in options:

                # Check module type; initialize module directory if OK
                if module == Storyboard.ACTION_KEY:
                        module_dir = Storyboard.ACTIONS_DIR
                elif  module == Storyboard.TRIGGER_KEY:
                        module_dir = Storyboard.TRIGGERS_DIR
                else:
                        print("[-] check_scenario: Unknown module type '{0}'.".format(module))
                        return False

		try:
                        #print '\n'.join(sys.path)
                        # TODO: Try to use the 'imp' module for import instead of command line
                        #       https://leemendelowitz.github.io/blog/how-does-python-find-packages.html
                        # NOTE: For the command below to work, the file '__init__.py' needs to be
                        #       placed in target directories to make them "packages"
                        command = "from {0}.{1} import *".format(module_dir, options[Storyboard.MODULE_KEY])
			exec(command)
		except:
			print("[-] {0}: Failed to import module '{1}'.".format(module, options[Storyboard.MODULE_KEY]))
			return False

		try:
			moduleClass = locals()[options[Storyboard.MODULE_KEY]]()
		except:
			print("[-] {0}: Could not instantiate module '{1}'.".format(module, options[Storyboard.MODULE_KEY]))
			return False

		if not moduleClass.check(options):
			print("[-] {0}: An error was detected in the settings of module '{1}'.".format(module, options[Storyboard.MODULE_KEY]))
			return False
		del moduleClass
	else:
		print(options)
		print("[-] {0}: No 'module' option found.".format(module))
		return False

	return True

# Check format of action outcome definitions in scenario
# scenarioResult = {next: ... , points: ..., etc. } or ... (next step id as scalar)
def check_result(scenarioResult, steps, fileList):

	# Handle the case when scenarioResult is a dictionary
	if isinstance(scenarioResult, dict):
		# Check whether unknown elements are included
		for elem in scenarioResult:
                        # TODO: Should include loop key? But what it is useful for?
			if elem not in [Storyboard.NEXT_KEY, Storyboard.POINTS_KEY, Storyboard.NEXT_SCENARIO_KEY]:
				print("[-] check_scenario: ERROR: Found unknown key in outcome definition: '{0}'.".format(elem))
				return False

		# Case of 'next'
		if Storyboard.NEXT_KEY in scenarioResult:
			# Check whether 'next' value is a string
			if not check_string(scenarioResult[Storyboard.NEXT_KEY]):
				print("[-] next: Value is not a string: '{0}'.".format(scenarioResult[Storyboard.NEXT_KEY]))
				return False

			# Check whether 'next' value is either a step id or a file name
			if (scenarioResult[Storyboard.NEXT_KEY] not in steps) and (scenarioResult[Storyboard.NEXT_KEY] not in fileList):
                                print("[-] check_scenario: Key '{0}' value is not a known step id or scenario file: '{1}'.".format(Storyboard.NEXT_KEY, scenarioResult[Storyboard.NEXT_KEY]))
				return False

		# Case of next 'scenario'
                # TODO: To remove?!
		if Storyboard.NEXT_SCENARIO_KEY in scenarioResult:
                        # Check whether 'scenario' value is a string
			if not check_string(scenarioResult[Storyboard.NEXT_SCENARIO_KEY]):
				print("[-] scenario: Value is not a string: '{0}'.".format(scenarioResult[Storyboard.NEXT_SCENARIO_KEY]))
				return False
                        
                        # Check whether the scenario file exists
			if scenarioResult[Storyboard.NEXT_SCENARIO_KEY] not in fileList:
				print("[-] scenario: Value is not a known scenario file: '{0}'.".format(scenarioResult[Storyboard.NEXT_SCENARIO_KEY]))
				return False

		# Case of 'points'
		if Storyboard.POINTS_KEY in scenarioResult:
			# Check whether 'points' value is an integer
			if not isinstance(scenarioResult[Storyboard.POINTS_KEY], int):
				print("[-] check_scenario: ERROR: Key '{0}' value is not an integer: '{1}'".format(Storyboard.POINTS_KEY, scenarioResult[Storyboard.POINTS_KEY]))
				return False

		# Case of 'loop'
		if Storyboard.LOOP_KEY in scenarioResult:
			# Check whether 'loop' value is an integer
			if not isinstance(scenarioResult[Storyboard.LOOP_KEY], int):
                                print("[-] loop: Value is not an integer: '{0}'.".format(scenarioResult[Storyboard.LOOP_KEY]))
				return False

		return True

	# Handle the case when scenarioResult is a string
        # TODO: Add handling of scenario files?!
	elif check_string(scenarioResult):
		if scenarioResult in steps:
			return True

                print("[-] next: Value is an unknown step id: '{0}'.".format(scenarioResult))
		return False

	# Otherwise the format is unknown
	print("[-] Unknown format for scenario result: '{0}'.".format(result))
	return False

# Check scenario syntax
# scenario is format:list
def check_scenario(scenario, targetList, fileList):

	# Required step keys
	required_keys = [Storyboard.STEP_KEY, Storyboard.TARGET_KEY, Storyboard.ACTION_KEY]

	# Optional step keys
	optional_keys = [Storyboard.LABEL_KEY, Storyboard.TRIGGER_KEY]

	# Step outcome (result) keys
	outcome_keys = [Storyboard.SUCCESS_KEY, Storyboard.FAILURE_KEY]

	# Predefined scenario step ids
	steps = [Storyboard.STEP_COMPLETE, Storyboard.STEP_FINISH, Storyboard.STEP_REPEAT]

	for i,STEP in enumerate(scenario,1):
		# Check whether 'step' is defined
		if "step" not in STEP:
			print(STEP)
			print("[-] check_scenario: Not defined for step #{0}.".format(str(i)))
			return False

		if not check_string(STEP["step"]):
			print(STEP)
			print("[-] check_scenario: Id is not a string for step#{0}.".format(str(i)))
			return False

	for STEP in scenario:
		# Check whether all required keys in 'step' are present
		for key in required_keys:
			if key not in STEP:
				print("[-] check_scenario: ERROR: Step '{0}' doesn't contain required key: '{1}'".format(STEP["step"],key))
				return False

			# Check whether step label and target values are strings
			if key in [Storyboard.LABEL_KEY, Storyboard.TARGET_KEY]:
				if not check_string(STEP[key]):
					print(STEP)
					print("[-] check_scenario: Step '{0}' key '{1}' value is not a string.".format(STEP["step"],key))
					return False

		# Check whether unsupported elements are present
		for elem in STEP:
			if elem not in required_keys + optional_keys + outcome_keys:
				print(STEP)
				print("[-] check_scenario: Step '{0}' contains an unsupported key: '{1}'.".format(STEP["step"],elem))
				return False

		# Check whether target value exists
		if decode(STEP["target"]) not in targetList:
			print("[-] check_scenario: Step '{0}' target does not exist: '{1}'.".format(STEP["step"],STEP["target"]))
			return False

		# Check syntax of 'action' definition
		if not check_module(STEP["action"],"action"):
			print("[-] check_scenario: Step '{0}' contains an incorrect action.".format(STEP["step"]))
			return False

		# Check syntax of 'trigger' definition (note that it's possible to omit it)
		if "trigger" in STEP:
			if not check_module(STEP["trigger"],"trigger"):
				print("[-] Step '{0}' contains an incorrect trigger.".format(STEP["step"]))
				return False

                # If all checks are positive, append the step to list
		steps.append(STEP["step"])

	# Other operations that follow the processing of steps
	for STEP in scenario:
		# Check syntax of results ('success' or 'failure')
		for result in outcome_keys:
			# It's possible to omit 'success' and/or 'failure' keys
			if result in STEP:
				if not check_result(STEP[result],steps,fileList):
					print("[-] check_scenario: Step '{0}' contains an incorrect value for the result key '{1}'.".format(STEP["step"],result))
					return False

	return True
