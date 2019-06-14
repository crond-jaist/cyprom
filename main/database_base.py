
#############################################################################
# Classes related to basic database functionality
#############################################################################

# Standard library imports
import sqlite3
import datetime
import os, sys

from logging import getLogger
logger = getLogger("CyPROM").getChild("database")

# Local imports
from storyboard import Storyboard

# Initialization via super class
class databaseBaseClass:
        
	def __init__(self):
		#######################################################
		# Table Name ##########################################

		self.database = u"training.db"

		File = os.path.basename(sys.argv[0])
		if File in ["index.py","api.py","server.py"]:
			self.database = os.path.join(u"main",self.database)

		self.progress = u"progress"
		self.config = u"config"
		self.system = u"system"
		self.log = u"log"
		self.board = u"board"
		self.state = u"state"
		self.scenario = Storyboard.SCENARIO_KEY

		#######################################################
		#######################################################

		self.logger = logger

		# Connect database
		logger.debug(u"Connect with database:{0}".format(self.database))
		try:
                        # Increase the timeout to 15 s (default is 5 s) in order to allow for more concurrency
                        # (useful with the test action module with sleep disabled, which exists immediately)
			# self.connect = sqlite3.connect(self.database)
			self.connect = sqlite3.connect(self.database, timeout=15)
			self.cursor = self.connect.cursor()
		except Exception as error:
			logger.error(u"Error connecting with database '{0}': {1}".format(self.database, error))
			sys.exit(1)

	# Execute SQL insert and update query
	def commit_exec(self,query,Tuple=()):
		logger.debug(u"SQL : {0}".format(query.replace(u"\t","")))
		logger.debug(Tuple)
		try:
			self.cursor.execute(query,Tuple)
			self.connect.commit()
		except Exception as error:
			self.connect.rollback()
			#logger.error("commit_exec: Failure of SQL execution: {0}.".format(error))
                        print("[-] database_base: ERROR: Failed to commit record: {0}".format(error))
                        print("[-] database_base: => You may want to increase the timeout in sqlite3.connect()")
                        # TODO: Other solution except increasing timeout?! For the moment don't exit on error
			#sys.exit(1)

	# Execute SQL select, drop and create query
	def execute(self,query,Tuple=()):
		logger.debug(u"SQL : {0}".format(query.replace(u"\t","")))
		logger.debug(Tuple)
		try:
			self.cursor.execute(query,Tuple)
			data = self.cursor.fetchall()
		except Exception as error:
			logger.error("execute: Failure of SQL execution: {0}.".format(error))
			sys.exit(1)

		return data

	# Close connection with database
	def __del__(self):
		self.cursor.close()
		self.connect.close()
		logger.debug("Close connection with database")

# Manage the 'state' table
class sqlState(databaseBaseClass):
	def updateState(self,teamName,target,status):
		query = u"update {0} set state=? where team=? and target=?".format(self.state)
		self.commit_exec(query,(status,teamName,target))

	# Return 'False' in case there is an invalid value in any column
	# Meaning of state codes:
        #   0 => Unable to confirm network connectivity (ping)
        #   -1,-2 => Service is not operating normally
	def selectState(self,teamName=False):
		if teamName:
			query = u"select count(target) from {0} where team=? and state<>1".format(self.state)
			result = self.execute(query,(teamName,))
		else:
			query = u"select count(target) from {0} where state = 0 or state = -2".format(self.state)
			result = self.execute(query)

		if result[0][0] == 0:
			return True

		return False

	# Get all states
	def select(self):
		query = u"select team,target,state from {0} order by target".format(self.state)

		return self.execute(query)

# Manage the 'progress' table
class sqlProgress(databaseBaseClass):
	def updateStep(self,teamName,step="sys"):
		query = u"update {0} set step=? where team=?".format(self.progress)
		self.commit_exec(query,(step,teamName))

	def updatePoints(self, teamName, points):
		query = u"update {0} set {1}=? where team=?".format(self.progress, Storyboard.POINTS_KEY)
		self.commit_exec(query, (points, teamName))

	def select(self):
		query = u"select team,step,{0} from {1} order by {0} desc".format(Storyboard.POINTS_KEY, self.progress)
		return self.execute(query)

	def selectTeam(self):
		query = u"select team from {0} order by team".format(self.progress)
		return self.execute(query)

	def selectNowStep(self,teamName):
		query = u"select step from {0} where team=?".format(self.progress)
		return self.execute(query,(teamName,))[0][0]

# Manage the 'log' table
class sqlLog(databaseBaseClass):
	def insert(self, teamName, step, comment, points):
		time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

		query = u"insert into {0} values(?,?,?,?,?)"\
		.format(self.log)

		self.commit_exec(query, (time, teamName, step, comment, points))

	def select(self,teamName=False):
		if teamName:
			query = u"select * from {0} where team=? order by time,team".format(self.log)
			result = self.execute(query,(teamName,))
		else:
			query = u"select * from {0} order by time,team".format(self.log)
			result = self.execute(query)

		return result

	def countStep(self,teamName,step):
		query = u"select count(*) from {0} where team=? and step=?".format(self.log)

		result = self.execute(query,(teamName,step))

		return result[0][0]

# Manage the 'board' table
class sqlBoard(databaseBaseClass):
	# Change type from 'question' to 'replied'
	def updateQuestion(self,teamName):
		query = u"update {0} set type='replied' where team=? and type='question'".format(self.board)
		self.commit_exec(query,(teamName,))

	# Get all the viewable data
	def select(self,teamName):
		if teamName:
			query = u"select time,team,type,message from {0} where visible=1 and team=?".format(self.board)
			return self.execute(query,(teamName,))
		else:
			query = u"select time,team,type,message from {0} where visible=1".format(self.board)

		return self.execute(query)

	# Insert a record
	def insert(self,team,mtype,message,visible=1):
		time = datetime.datetime.now().strftime("%H:%M")

		query = u"insert into {0} values(?,?,?,?,?)".format(self.board)
		self.commit_exec(query,(time,team,mtype,message,visible))

	# Get port on which the system is waiting for an answer
	def selectPort(self,teamName):
		query = u"select message from {0} where type='port' and team=?".format(self.board)
		return self.execute(query,(teamName,))

	# Delete port information
	def deletePort(self,teamName):
		query = "delete from {0} where type='port' and team=?".format(self.board)
		self.commit_exec(query,(teamName,))

	# Change type 'click' to invisible
	def hideClick(self,teamName):
		query = "update {0} set visible=0 where visible=1 and type='click' and team=?".format(self.board)
		self.commit_exec(query,(teamName,))

# Manage the 'scenario'
class sqlScenario(databaseBaseClass):
	def select(self):
		query = "select * from {0}".format(self.scenario)

		return self.execute(query)

# Manage the configuration
class sqlConfig(databaseBaseClass):
	def getMsf(self):
		query = "select * from {0} where key like '{1}%'".format(self.config, Storyboard.MSF_SQL_PREFIX)
		config = {}

		for i in self.execute(query):
			config[i[0]] = i[1]

		return config
