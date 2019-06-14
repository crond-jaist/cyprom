
#############################################################################
# Functions related to argument parsing
#############################################################################

# Standard library imports
import argparse

# Local application imports
from storyboard import Storyboard

# Parse input arguments using the 'argparse' library
def parse_args():
	parser = argparse.ArgumentParser(
		usage = "./%(prog)s [options]",
		formatter_class = argparse.RawTextHelpFormatter,
                add_help = False)

        #parser._optionals.title = "Optional arguments"

	parser.add_argument(
		"-h", "--help",
		action = "help",
		help = "Show this help message and exit"
	)
	parser.add_argument(
		"--version",
		action="version",
		version="You are currently using CyPROM version " + Storyboard.CYPROM_VERSION + ".",
                help = "Show the version number and exit\n "
	)
	parser.add_argument(
		"-s", "--scenario",
		type = str,
		default = False,
		help = "Specify the scenario directory"
	)
	parser.add_argument(
		"-t", "--target",
		type = str,
		default = False,
		help = "Specify the target information file"
	)
	parser.add_argument(
		"-c", "--cyris",
		type = str,
		default = False,
		help = "Specify the CyRIS range details file\n "
	)
	parser.add_argument(
		"--test",
		action = "store_true",
		help = "Run CyPROM in TEST mode\n "
	)
	parser.add_argument(
		"-d", "--delete-tables",
		action = "store_true",
		help = "Remove all tables from the log database"
	)
	parser.add_argument(
		"-o", "--output-reports",
		action = "store_true",
		help = "Output the scenario log reports"
	)
#	parser.add_argument(
#		"--remove",
#		action = "store_true",
#		help = "Delete all the log reports"
#	)

	args = parser.parse_args()

	return args
