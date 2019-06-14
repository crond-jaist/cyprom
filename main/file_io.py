
#############################################################################
# Functions related to file I/O
#############################################################################

# Standard library imports
import yaml
import os, sys

# Local imports
from character import decode
from storyboard import Storyboard

# Read configuration file
def read_config():
	fileName = "../config"

	with open(fileName,"r") as f:
		data = f.readlines()

	config = {}

	for line in data:
		line = line.strip()

                # Skip empty lines and those that start with '#'
		if line == "" or line[0] == "#":
			continue

		line = line.split()

		if line[0] == Storyboard.SCENARIO_DIRECTORY_KEY:
			config[line[0]] = line[1]
		elif line[0] == Storyboard.TARGET_FILE_KEY:
			config[line[0]] = line[1]
		elif line[0] == Storyboard.INITIAL_SCORE_KEY:
			config[line[0]] = int(line[1])
#		elif line[0] == Storyboard.PUBLIC_SERVER_KEY:
#			config[line[0]] = line[1].lower()
#		elif line[0] == Storyboard.PUBLIC_PORT_KEY:
#			config[line[0]] = int(line[1])
#		elif line[0] == Storyboard.LOG_MODE_KEY:
#			config[line[0]] = line[1]

		elif line[0] == Storyboard.MSF_SERVER:
			config[line[0]] = line[1]
		elif line[0] == Storyboard.MSF_PORT:
			config[line[0]] = line[1]
		elif line[0] == Storyboard.MSF_USER:
			config[line[0]] = line[1]
		elif line[0] == Storyboard.MSF_PASSWORD:
			config[line[0]] = line[1]
		else:
			print("[-] config: ERROR: Unknown key found: '{0}'".format(line[0]))
			sys.exit(1)

	return config

# Read target file
def read_ini_file(FILE):
	version = sys.version_info[0]

	if version == 2:
		import ConfigParser
		teamFile = ConfigParser.SafeConfigParser()
	else:
		import configparser
		teamFile = configparser.ConfigParser()

	teamFile.optionxform = str

	if not os.path.exists(FILE):
		print("[-] target: File not found: '{0}'.".format(FILE))
		sys.exit(1)

	try:
		teamFile.read(FILE)
	except Exception as error:
		print("[-] target: Error: {0}".format(error))
		sys.exit(1)

	teamConfig = {}

	# Convert section names to Unicode, then build a dictionary
	teams = teamFile.sections()
	for teamName in teams:
		teamConfig[decode(teamName)] = {}

		# Also convert section content to Unicode (should be strings)
		for target,address in teamFile.items(teamName):
			target = decode(target)
			address = decode(address)

			teamConfig[decode(teamName)][target] = address

	return teamConfig

# Read YAML file
# [{key: value,...},{key2: value,...}]
def read_yaml_file(FILE):
	with open(FILE,"r") as file:
		page = file.read()
		data = yaml.safe_load(page)

	return data

# Write dictionary to file
def save_scenario(fileName,firstStep,scenario):
	content = {Storyboard.FIRST_STEP_KEY: firstStep, Storyboard.SCENARIO_KEY: scenario}

	with open(fileName,"w") as f:
		f.write(yaml.safe_dump(content,default_flow_style=False))

# Select one scenario from the scenario file list
def select_scenario(teamName,targets,scenarioFile):
	directory = ".tmp"
	content = read_yaml_file(os.path.join(directory,scenarioFile))

	scenario = content[Storyboard.SCENARIO_KEY]

	for step, STEP in scenario.items():
		for module in [Storyboard.TRIGGER_KEY, Storyboard.ACTION_KEY]:
			for key,value in STEP[module].items():
				if not isinstance(value,unicode):
					continue

				value = value.replace("<team>", teamName)
				value = value.replace("<target>", STEP[Storyboard.TARGET_KEY])
				value = value.replace("<address>", targets[STEP[Storyboard.TARGET_KEY]])

				scenario[step][module][key] = value

	return scenario, content[Storyboard.FIRST_STEP_KEY]
