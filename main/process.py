
#############################################################################
# Functions related to driver process management
#############################################################################

# Standard library imports
import os,sys
import glob,random
from logging import getLogger, StreamHandler, Formatter

# Local imports
from database_base import sqlProgress, sqlLog
from monitor_base import monitor
from file_io import select_scenario
from storyboard import Storyboard


# Import all .py files in the action and trigger directories
for dir in [Storyboard.TRIGGERS_DIR, Storyboard.ACTIONS_DIR]:

        # Get path of module directory, and build list of Python files within it
	modulePath = "{0}/".format(dir).replace("/",os.sep)
	files = glob.glob(modulePath + "*.py".format(dir))

        # Check whether any files were found 
        if not files:
                print("process: WARNING: No files in module directory: '{0}'".format(modulePath))

        # Import each of the files
	for file in files:
		fileName = os.path.basename(file)
		moduleName = os.path.splitext(fileName)[0]

		if moduleName != "__init__":
			exec("from " + modulePath.replace(os.sep,".") + "{0} import *".format(moduleName))

# This function is executed by some process
# argument => scenario,config,
def training(config, SCENARIOS, test_mode):
	# Setup logging
	logger = getLogger("CyPROM").getChild("process")

	# Initial settings
	teamName = config["teamName"]
	targets = config["targets"]
	points = config[Storyboard.INITIAL_SCORE_KEY]

	preAction = {}
        data = {}

	# Select the first scenario file: use the predefined file if it exists,
        # or choose randomly otherwise
	if Storyboard.INITIAL_SCENARIO in SCENARIOS:
		File = Storyboard.INITIAL_SCENARIO
	else:
		File = random.choice(SCENARIOS)

	scenario,step = select_scenario(teamName,targets,File)

	# Create objects for managing the progress and log tables
	changeProgress = sqlProgress()
	insertLog = sqlLog()

	print(Storyboard.LOG_TEMPLATE_LOW.format(teamName, "Training started"))
	logger.info(u"{0:>16} | \033[34mStart\033[0m".format(teamName))

	# Handle one step
	while True:
		# Get current step to be executed from scenario
		STEP = scenario[step]

		# Get current step content
		address = targets[STEP["target"]]
		trigger = STEP["trigger"]
		action = STEP["action"]

		if "inherit" in preAction:
			for option in [key.strip() for key in preAction["inherit"].split(",")]:
				if option not in action:
					action[option] = preAction[option]

	        print(Storyboard.LOG_TEMPLATE_LOW.format(teamName, Storyboard.STEP_TEMPLATE.format(STEP[Storyboard.LABEL_KEY], "[Executing...]")))
		logger.info(u"{0:>16} | \033[33m{1:>16} | Start\033[0m".format(teamName,step))
		logger.debug(STEP)

		# Write about step in progress table
		logger.info(u"{0:>16} | {1:>16} | Update step in progress table".format(teamName,step))
		changeProgress.updateStep(teamName,step)

                # Replace triggers in test mode (if necessary)
                allowed_test_mode_triggers = [Storyboard.NONE_VALUE, Storyboard.TIMER_VALUE, Storyboard.SIGNAL_VALUE]
		if test_mode and trigger[Storyboard.MODULE_KEY] not in allowed_test_mode_triggers:
                        print("[-] process: WARNING: Trigger module replaced in test mode: '{0}' => '{1}'".format(trigger[Storyboard.MODULE_KEY], Storyboard.NONE_VALUE)) 
			trigger[Storyboard.MODULE_KEY] = Storyboard.NONE_VALUE
                try:
                        # TODO: Could use the function 'get' to get value from dictionary
		        triggerClass = globals()[trigger[Storyboard.MODULE_KEY]]()
                except KeyError:
                        print("[-] Error: Trigger module not found: '{0}'.".format(trigger[Storyboard.MODULE_KEY]))
                        sys.exit(1)

                # Replace actions in test mode (if necessary)
                allowed_test_mode_actions = [Storyboard.TEST_VALUE, Storyboard.HINT_VALUE, Storyboard.MESSAGE_VALUE]
		if test_mode and action[Storyboard.MODULE_KEY] not in allowed_test_mode_actions:
                        print("[-] process: WARNING: Action module replaced in test mode: '{0}' => '{1}'".format(action[Storyboard.MODULE_KEY], Storyboard.TEST_VALUE))
			action[Storyboard.MODULE_KEY] = Storyboard.TEST_VALUE
                try:
		        actionClass = globals()[action[Storyboard.MODULE_KEY]]()
                except KeyError:
                        print("[-] Error: Action module not found: '{0}'.".format(trigger[Storyboard.MODULE_KEY]))
                        sys.exit(1)

		# This use for loop
		count = 0
		while True:
			# Alive monitoring
			logger.info(u"{0:>16} | {1:>16} | Alive monitoring".format(teamName,step))
			monitor(teamName, targets, test_mode)

			# Execute trigger
                        #print("[*] Execute trigger '{0}'...".format(trigger[Storyboard.MODULE_KEY]))
			logger.info(u"{0:>16} | {1:>16} | Waiting trigger {2}".format(teamName, step, trigger[Storyboard.MODULE_KEY]))
			triggerClass.trigger(teamName, trigger)

			# Alive monitoring
			logger.info(u"{0:>16} | {1:>16} | Alive monitoring".format(teamName,step))
			monitor(teamName, targets, test_mode)

			# Execute action
			logger.info(u"{0:>16} | {1:>16} | Execute action {2}".format(teamName, step, action[Storyboard.MODULE_KEY]))
			result,comment,data = actionClass.action(teamName, address, action, data)

			preAction = action

			if result:
				result = Storyboard.SUCCESS_KEY
			else:
				result = Storyboard.FAILURE_KEY

	                print(Storyboard.LOG_TEMPLATE_LOW.format(teamName, Storyboard.STEP_TEMPLATE.format(STEP[Storyboard.LABEL_KEY], comment)))
			logger.info(u"{0:>16} | \033[35m{1:>16} | {2}\033[0m".format(teamName,step,comment))

			# Calculate points
			points = points + STEP[result][Storyboard.POINTS_KEY]

			# Update points in progress tables and Write log
			logger.info(u"{0:>16} | {1:>16} | Update points in progress table and insert log".format(teamName,step))
			changeProgress.updatePoints(teamName, points)
			insertLog.insert(teamName, step, comment, points)

			# If the 'loop' key is present in 'success'/'failure' values, repeat step;
			# otherwise we use 'break' instructions to proceed to the next step
			if "loop" in STEP[result]:
				if count < int(STEP[result]["loop"]):
					count += 1
	                                print(Storyboard.LOG_TEMPLATE_LOW.format(teamName, Storyboard.STEP_TEMPLATE.format(step, "Repeat")))
					logger.info(u"{0:>16} | \033[36m{1:>16} | try again\033[0m".format(teamName,step))
					continue
			break

		del triggerClass
		del actionClass

	        #print(Storyboard.LOG_TEMPLATE_LOW.format(teamName, Storyboard.STEP_TEMPLATE.format(step, "End")))
		logger.info(u"{0:>16} | \033[33m{1:>16} | Complete\033[0m".format(teamName,step))

		# Determine the next step according to the result of the action
		if Storyboard.NEXT_SCENARIO_KEY in STEP[result]:
			if File in SCENARIOS:
				SCENARIOS.remove(File)

			File = STEP[result][Storyboard.NEXT_SCENARIO_KEY]
			scenario,step = select_scenario(teamName,targets,File)
			continue

		elif Storyboard.NEXT_KEY in STEP[result]:
			step = STEP[result][Storyboard.NEXT_KEY]

		# Handle special step values: 'COMPLETE' => end of training
		if step == Storyboard.STEP_COMPLETE:
			break
		# 'FINISH' => remove scenario from the list of not-yet executed scenarios
		elif step == Storyboard.STEP_FINISH:
			if File in SCENARIOS:
				SCENARIOS.remove(File)

			if len(SCENARIOS) == 0:
				break

			File = random.choice(SCENARIOS)
			scenario,step = select_scenario(teamName,targets,File)
		# 'REPEAT' => leave scenario in list so that it can be repeated
		elif step == Storyboard.STEP_REPEAT:
			File = random.choice(SCENARIOS)
			scenario,step = select_scenario(teamName,targets,File)

	# Write final marker (step:0) in progress and log tables
	changeProgress.updateStep(teamName)
	insertLog.insert(teamName, u"sys", Storyboard.STEP_COMPLETE, points)

	del changeProgress
	del insertLog

        print(Storyboard.LOG_TEMPLATE_LOW.format(teamName, "Training completed"))
        print(Storyboard.HEADER_TEMPLATE_BAR)
        logger.info(u"{0:>16} | \033[34mComplete\033[0m".format(teamName))
