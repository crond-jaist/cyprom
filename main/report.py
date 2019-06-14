
#############################################################################
# Functions related to reporting
#############################################################################

# Standard library imports
import glob, os

# Local imports
from database_base import sqlLog, sqlProgress
from character import encode

# Column index for team record
TEAM_NAME_COL = 0
TEAM_STEP_COL = 1
TEAM_SCORE_COL = 2

# Column index for log records
LOG_TIME_COL = 0
LOG_NAME_COL = 1
LOG_STEP_COL = 2
LOG_OUTCOME_COL = 3
LOG_SCORE_COL = 4

SKIP_UNAVAILABLE = True

def createReport():
	progress = sqlProgress()
	log = sqlLog()
	teams = progress.select()

	for team in teams:
		team_name = team[TEAM_NAME_COL]
		team_score = team[TEAM_SCORE_COL]

		print("[.] Output {0} log".format(team_name))
		with open("{0}.csv".format(team_name), "w") as f:
			logs = log.select(team_name)

                        # Get the first and last log records
			first_rec = logs[0]
			last_rec = logs[len(logs)-1]

			if len(logs) <= 1:
				print("[-] report: Log length <= 1 line.")
				return False

			if first_rec[2] != u"sys" or last_rec[2] != u"sys":
				print("[-] report: Execution finished abnormally.")
				return False

                        # Write log file header
			f.write("# Participant:\t{0}\n".format(encode(team_name)))
			f.write("# Start time:\t{0}\n# End time:\t{1}\n# Final score:\t{2}\n".format(encode(first_rec[LOG_TIME_COL]), encode(last_rec[LOG_TIME_COL]), str(team_score)))

                        # Write CSV log
			f.write("TIME,STEP,OUTCOME,SCORE\n")
                        # Don't show first and last records (TODO: Why?)
			#for record in logs[1:-1:]:
                        # Show all records
			for record in logs:
                                if SKIP_UNAVAILABLE and record[LOG_OUTCOME_COL]=="Unavailable":
                                        continue
				f.write("{0},{1},{2},{3}\n".format(encode(record[LOG_TIME_COL]), encode(record[LOG_STEP_COL]), record[LOG_OUTCOME_COL], record[LOG_SCORE_COL]))

	return True

def deleteReport():
	reports = glob.glob("*.csv")

	for report in reports:
		print("[.] Remove {0}".format(report))
		os.remove(report)
