
#############################################################################
# Functions related to job creation
#############################################################################

# Standard library imports
from multiprocessing import Process

# Local imports
from process import training
from storyboard import Storyboard

# Create jobs
def create_jobs(teamConfig, initial_points, scenarioFiles, test):
	jobs = []

	id = 0
	for teamName,targets in teamConfig.items():
		config = {}
		config["teamName"] = teamName
		config["targets"] = targets
		config[Storyboard.INITIAL_SCORE_KEY] = initial_points

		jobs.append(Process(target=training, args=(config, scenarioFiles, test)))

		id += 1

	return jobs
