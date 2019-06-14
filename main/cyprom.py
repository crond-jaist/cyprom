#! /usr/bin/env python

#############################################################################
# Main program file for the CyPROM scenario progression management system
#############################################################################

# Standard library imports
import os, sys, time
from multiprocessing import Process
from logging import getLogger, StreamHandler, Formatter

# Get directory path for program
filePass = os.path.join(os.getcwd(),__file__)
fileDir = os.path.split(filePass)[0]
# Change current directory
os.chdir(fileDir)

# Local imports
from database_create import createTable
from create_jobs import create_jobs
from database_base import sqlLog
from parse_args import parse_args
from init_config import init_config, init_targets, init_cyris_targets, init_scenario
from monitor_base import monitorAll, monitorProcess
from app import app
from database_delete import deleteTables
from report import createReport
from report import deleteReport
from storyboard import Storyboard


# Set up logging
def setup_logging(verbose):
	# normal
	if verbose == "low":
		level = 30
		template = "%(asctime)s | %(message)s"
	elif verbose in ["normal","high"]:
		template = "%(asctime)s | %(levelname)7s | %(process)5s | %(message)s"

		if verbose == "normal":
			level = 20
		else:
			level = 10
	else:
		print("[-] Unknown log mode : {0}".format(verbose))
		print("[-] Unknown log mode is low, normal or high")
		sys.exit()

	global logger

	logger = getLogger("CyPROM")
	logger.setLevel(level)

	handler = StreamHandler()
	handler.setLevel(level)

	# If log-level is debug, show milli second
	if verbose == "high":
		handler_format = Formatter(template)
	else:
		handler_format = Formatter(template,datefmt="%H:%M:%S")

	handler.setFormatter(handler_format)

	logger.addHandler(handler)

# Main function
def main():

        # Display program banner
        print Storyboard.SEPARATOR3
        print "CyPROM v%s: Cybersecurity scenario progression management system" % (Storyboard.CYPROM_VERSION)
        print Storyboard.SEPARATOR3

	# Parse command-line arguments
	args = parse_args()

	# Initialize config
	config = init_config()

	# Setup logging
        # TODO: Restore log levels
        config["LogMode"] = "low"
	setup_logging(config["LogMode"])

        ###########################################################
        # Database & reporting operations (will exit on completion)

        # NOTE: For checking we use boolean argument values stored by the parser

	# Delete all tables in the database (delete-tables option)
	if args.delete_tables:
                print("[*] Deleting database tables...")
		logger.info("Delete all tables --- Start")
		delTable = deleteTables()
		delTable.delete()
		logger.info("Delete all tables --- Complete")
		sys.exit()

	# Output training reports (output-reports option)
	if args.output_reports:
                print("[*] Creating training reports...")
		logger.info("Create report --- Start")
		if createReport():
			logger.info("Create report --- Complete")
			sys.exit()
		else:
			print("[-] cyprom: ERROR: Could not create training report.")
			sys.exit()

	# Delete all the log files (.csv)
        # TODO: Restore functionality?
	#if args.remove:
        #        print("[*] Removing training reports...")
	#	logger.info("Remove all report --- Start")
	#	deleteReport()
	#	logger.info("Remove all report --- Complete")
        #        # TODO: Check return value to decide if message needs to be printed
        #        #print("[*] No log files found")
	#	sys.exit()

        ###########################################################
        # Normal operation mode

        start_time = time.time()

	logger.info("Initialize --- Start")

	# Initialize team
	if args.cyris:
		teamConfig = init_cyris_targets(args.cyris,args.test)
	else:
		if args.target:
			teamConfig = init_targets(args.target, args.test)
		else:
			teamConfig = init_targets(config[Storyboard.TARGET_FILE_KEY], args.test)

        if not teamConfig:
                print("[-] cyprom: ERROR: Could not read the target file => abort")
                sys.exit(1)

	if args.test:
		for teamName in teamConfig:
			for target in teamConfig[teamName]:
				teamConfig[teamName][target] = u"127.0.0.1"

	# Initialize scenario
	if args.scenario:
                print("[*] Executing scenario(s) in directory '{0}'...".format(args.scenario))
		scenarioFiles = init_scenario(teamConfig,args.scenario)
	else:
                print("[*] Executing scenario(s) in directory '{0}'...".format(config["ScenarioDirectory"]))
		scenarioFiles = init_scenario(teamConfig, config["ScenarioDirectory"])

	# Setup database
	logger.info("Set up Database --- Start")

	setupDatabase = createTable()
	setupDatabase(config, teamConfig, config[Storyboard.INITIAL_SCORE_KEY])
	del setupDatabase

	logger.info("Set up Database --- Complete")

	# Check connection with targets
	logger.info("Check connection with targets --- Start")

	monitorAll(teamConfig,args.test)

	logger.info("Check connection with targets --- Complete")

	# Create jobs usesd for fork-process-parameter
	jobs = create_jobs(teamConfig, config[Storyboard.INITIAL_SCORE_KEY], scenarioFiles, args.test)

	logger.info("Initialize --- Complete")

	# Write log about training-start
	insertLog = sqlLog()
	for teamName in teamConfig:
		insertLog.insert(teamName, "sys", "START", config[Storyboard.INITIAL_SCORE_KEY])
	del insertLog

        logger.info("\033[31mStart training\033[0m")

	if config["LogMode"] == "low":
		print(Storyboard.HEADER_TEMPLATE_BAR)
		print(Storyboard.HEADER_TEMPLATE_LOW.format("PARTICIPANT","PROGRESSION"))
		print(Storyboard.HEADER_TEMPLATE_BAR)
	elif config["LogMode"] == "normal":
		logger.info("\033[37;44;1m{0:^8} | {1:^7} | {2:^5} | {3:^16} | {4: <16} |\033[0m".format("TIME","LEVEL","PID","TEAM",""))
	else:
		logger.info("\033[37;44;1m{0:^23} | {1:^7} | {2:^5} | {3:^16} | {4: <16} |\033[0m".format("TIME","LEVEL","PID","TEAM",""))

	# Fork process
	for job in jobs:
		job.start()

        # TODO: Restore server functionality
#	if config["PublicServer"] == "on":
#		server = Process(target=app,args=(config["PublicPort"],fileDir))
#		server.start()

	try:
		while True:
			flag = False
			for job in jobs:
				if job.is_alive():
					flag = True

			if flag:
				monitorProcess(teamConfig)
			else:
				break
	except KeyboardInterrupt:
		logger.warning("Forced quit.")

	# Wait child-process
	for job in jobs:
		job.join()

	logger.info("\n\033[31mTraining completed.\033[0m")

#	if config["PublicServer"] == "on":
#		print("")
#		print("\nTraining has finished. Press Ctrl+C to end server program execution.")

        end_time = time.time()
        print("[*] Training session finished (total duration: {:.2f} s)".format(end_time - start_time))

if __name__ == "__main__":
	main()
