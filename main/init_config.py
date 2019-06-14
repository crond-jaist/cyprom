
#############################################################################
# Functions related to program initialization
#############################################################################

# Standard library imports
import os,sys,glob

from logging import getLogger
logger = getLogger("CyPROM").getChild("init_config")

# Local imports
from character import decode
from file_io import read_config, read_ini_file, read_yaml_file, save_scenario
from check_target_file import check_target_file
from check_scenario import check_scenario
from parse_scenario import parse_scenario
from storyboard import Storyboard


def init_config():
	logger.info("Read config file --- Start")
	config = read_config()
	logger.info("Read config file --- Complete")

	return config

def init_targets(target_file, test):
	# Read target information file and change type from list to dictionary
	logger.info("Read target information file '{0}' --- Start".format(target_file))
	target_config = read_ini_file(target_file)

        if not target_config:
                print("[-] init_config: ERROR: Target information file is empty: '{0}'.".format(target_file))
                return False

	# Check target_config
	if not check_target_file(target_config,test):
                print("[-] init_config: ERROR: Target information file is invalid: '{0}'.".format(target_file))
                return False

	logger.info("Read target information file '{0}' --- Complete".format(target_file))

	return target_config

def init_cyris_targets(cyris_file, test):

	logger.info("Read CyRIS environment details output file '{0}' --- Start".format(cyris_file))
	range_details = read_yaml_file(cyris_file)

	target_config = {}
	participant_list = []
	range_id = range_details["range_id"]

	for host in range_details["hosts"]:
		for instance in host["instances"]:
			instance_index = instance["instance_index"]
			participant_name = u"CR{0}_{1}".format(unicode(range_id),unicode(instance_index))
			if participant_name not in participant_list:
				target_config[participant_name] = {}

			for i, guest in enumerate(instance["guests"],1):
				guest_id = u"{0}{1}".format(decode(guest["guest_id"]),unicode(i))
				target_config[participant_name][guest_id] = decode(guest["ip_addrs"]["eth0"])

	check_target_file(target_config,test)

	logger.info("Read CyRIS environment details output file '{0}' --- Complete".format(cyris_file))

	return target_config

# TODO: Review function
def init_scenario(target_config, scenarioDir):
	directory = ".tmp"

	if not os.path.isdir(scenarioDir):
			print("[-] init_config: Scenario directory doesn't exist: '{0}'.".format(scenarioDir))
			sys.exit(1)

	if not os.path.isdir(directory):
		os.mkdir(directory)
	else:
		import shutil
		shutil.rmtree(directory)
		os.mkdir(directory)

	# Read scenario-file({"scenario": key: value})
	scenarioFiles = glob.glob(os.path.join(scenarioDir,"*.yml"))
	fileList = [os.path.basename(f) for f in scenarioFiles]

	if len(scenarioFiles) == 0:
			print("[-] init_config: No valid scenario with extension '.yml' found in directory: '{0}'.".format(scenarioDir))
			sys.exit(1)

	for File,fileName in zip(scenarioFiles,fileList):
		logger.info("Read {0} --- Start".format(fileName))
		fileContent = read_yaml_file(File)

		if Storyboard.SCENARIO_KEY not in fileContent:
			print("[-] init_config: Format of scenario file not recognized: '{0}'.".format(fileName))
			sys.exit(1)

		stepList = fileContent[Storyboard.SCENARIO_KEY]
		targetList = list(list(target_config.values())[0].keys())

		# Check scenario
		if not check_scenario(stepList,targetList,fileList):
			print("[-] init_config: ERROR: Validation of scenario file failed: '{0}'".format(fileName))
			sys.exit(1)

		# Save first step
		firstStep = decode(stepList[0]["step"])

		# Change scenario from type:list to type:dict and compensate lack of scenario
		scenario = parse_scenario(stepList)
		if not scenario:
			sys.exit()

		# Save new yaml-file
		save_scenario(os.path.join(directory,fileName),firstStep,scenario)
		logger.info("Read {0} --- Complete".format(fileName))

	return fileList
