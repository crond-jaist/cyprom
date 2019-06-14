
#############################################################################
# Functions related to scenario parsing
#############################################################################

# Local imports
from character import decode
from storyboard import Storyboard

# Determine the default next step to be executed
def default_next_step(result, stepList, i):

	# Check whether this is the last scenario step
	if i == len(stepList) - 1:
                # For the last step in a scenario, we consider 'FINISH' to be the default id,
                # no matter what was the result of the action execution
		return Storyboard.STEP_FINISH

	# Otherwise, we consider the default step to be the next step in the scenario
	else:
		return decode(stepList[i+1][Storyboard.STEP_KEY])

# Reformat scenario from list to dictionary
def parse_scenario(stepList):
	# Create and empty dictionary
	scenario = {}

	for i,STEP in enumerate(stepList):
		step = decode(STEP[Storyboard.STEP_KEY])

		scenario[step] = {}

		# Add basic step content (scalars) to scenario dictionary
                basic_keys = [Storyboard.TARGET_KEY]
		for key in basic_keys:
			scenario[step][key] = STEP[key]

                # Add optional keys to scenario dictionary, or default values if not provided
                #optional_keys = [Storyboard.LABEL_KEY, Storyboard.TRIGGER_KEY]

		# Check whether a label is included
		if Storyboard.LABEL_KEY in STEP:
                        # Add step label to scenario step
			scenario[step][Storyboard.LABEL_KEY] = STEP[Storyboard.LABEL_KEY]
		else:
                        # Otherwise use step id as default label value
			scenario[step][Storyboard.LABEL_KEY] = STEP[Storyboard.STEP_KEY]

		# Check whether a trigger is included
		if Storyboard.TRIGGER_KEY in STEP:
                        # Add trigger content to scenario step (use Unicode for values)
			scenario[step][Storyboard.TRIGGER_KEY] = {}
			for key,value in STEP[Storyboard.TRIGGER_KEY].items():
				scenario[step][Storyboard.TRIGGER_KEY][key] = decode(value)

		else:
                        # Otherwise use NONE as default module value
			scenario[step][Storyboard.TRIGGER_KEY] = {Storyboard.MODULE_KEY: Storyboard.NONE_VALUE}

		# Add complex step content (lists) to scenario dictionary
                complex_keys = [Storyboard.ACTION_KEY]
                for complex_key in complex_keys:
		        scenario[step][complex_key] = {}
		        for key, value in STEP[complex_key].items():
			        scenario[step][complex_key][key] = decode(value)

		# Add the outcome step content to scenario dictionary
                outcome_keys = [Storyboard.SUCCESS_KEY, Storyboard.FAILURE_KEY]
		for result in outcome_keys:
			scenario[step][result] = {}

			# Handle case when step includes 'success' or 'failure' keys
			if result in STEP:
				# Handle case when the 'success'/'failure' key values are a dictionary
				# STEP = {..., "success": {next:..., points: ...}, "failure": {...}}
				if isinstance(STEP[result],dict):

					# Handle 'next' key that specifies a next step
					if Storyboard.NEXT_KEY in STEP[result]:
						scenario[step][result][Storyboard.NEXT_KEY] = decode(STEP[result][Storyboard.NEXT_KEY])
					# Handle 'scenario' key that specifies a next scenario file
					elif Storyboard.NEXT_SCENARIO_KEY in STEP[result]:
						scenario[step][result][Storyboard.NEXT_SCENARIO_KEY] = decode(STEP[result][Storyboard.NEXT_SCENARIO_KEY])
					# Handle case when next step is not specified
					else:
						scenario[step][result][Storyboard.NEXT_KEY] = default_next_step(result, stepList, i)

					# Handle 'points' key that specifies points to be awarded for completing the step
					if Storyboard.POINTS_KEY in STEP[result]:
						scenario[step][result][Storyboard.POINTS_KEY] = STEP[result][Storyboard.POINTS_KEY]
					else:
						scenario[step][result][Storyboard.POINTS_KEY] = 0

					# Handle 'loop' key that specifies the step should be repeated N time
					if Storyboard.LOOP_KEY in STEP[result]:
						scenario[step][result][Storyboard.LOOP_KEY] = STEP[result][Storyboard.LOOP_KEY]

				# Handle case when the 'success'/'failure' key values are NOT a dictionary
				# success: step, NOT success: {...}
				else:
					scenario[step][result][Storyboard.NEXT_KEY] = decode(STEP[result])
					scenario[step][result][Storyboard.POINTS_KEY] = 0

			# Handle case when 'success'/'failure' keys are not specified
			else:
				scenario[step][result][Storyboard.NEXT_KEY] = default_next_step(result,stepList,i)
				scenario[step][result][Storyboard.POINTS_KEY] = 0

	# Determine whether there was any step duplication by comparing the length of
        # the 'stepList' and 'scenario' dictionaries
	if len(stepList) != len(scenario):
		print("[-] parse: Step duplication detected => abort.")
		return False

	return scenario
