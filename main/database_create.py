
#############################################################################
# Classes related to database table creation
#############################################################################

# Standard library imports
from Queue import Queue

# Local imports
from database_base import databaseBaseClass
from character import decode,encode
from storyboard import Storyboard

# Manage table creation
class createTable(databaseBaseClass,object):
	# Get table-list in database
	def __init__(self):
		super(createTable,self).__init__()
		query = u"select name from sqlite_master where type='table'"
		Ltables = self.execute(query)

		tables = []
		for t in Ltables:
			tables.append(decode(t[0]))

		self.tables = tables

	# Check table-name is alreay exist or not
	# If table exist, return False
	def checkTable(self,table):
		if table in self.tables:
			self.logger.info(u"{0} table already exists".format(table))
			return True
		return False

	# Create table
	def create(self, table, query):
		self.execute(query.format(table))
		self.logger.info(u"Create {0} table --- Complete".format(table))

	# Delete table before create table
	def createDel(self,table,query):
		if self.checkTable(table):
			self.execute(u"drop table {0}".format(table))
			self.logger.info(u"Delete {0} table --- Complete".format(table))

		self.create(table,query)

	# Create config table
	def createConfigTable(self,config):
		query = u"create table {0}(\
			key varchar(32) not NULL default 'False',\
			value varchar(32) not NULL default 'False'\
		)"

		self.createDel(self.config,query)

		for key,value in config.items():
			query = u"insert into {0} values(?,?)".format(self.config)
			self.commit_exec(query,(key,value))
	# Ceate log table
	def createLogTable(self):
		if self.checkTable(self.log):
			count = 1
			while True:
				if self.checkTable(self.log + unicode(count)):
					count += 1
				else:
					query = u"alter table {0} rename to {1}".format(self.log,self.log + unicode(count))
					self.execute(query)
					self.logger.info(u"Rename old log table {0}".format(self.log+unicode(count)))
					break

                # We need a workaround to allow use of format for header names,
                # and also later for '{0}' on first line
		query = u"create table {0}" + u"(time varchar(32) not NULL, team varchar(16) not NULL, step varchar(16) not NULL, result varchar(8) not NULL, {0} integer not NULL)".format(Storyboard.POINTS_KEY)

		self.create(self.log, query)

	# Create board table
	def createBoardTable(self):
		query = u"create table {0}(\
			time varchar(32) not NULL,\
			team varchar(16) not NULL,\
			type varchar(16) not NULL,\
			message varchar(128) not NULL,\
			visible integer not NULL default 0\
		)"

		self.createDel(self.board,query)

	# Create progress table
	def createProgressTable(self, teams, initial_points):
                # No workaround needed here, since 'format' was used already in the original function
		query = u"create table {0}(\
			teamID varchar(8) not NULL,\
			team varchar(16) not NULL,\
			step varchar(16) not NULL default 'sys',\
			{1} integer not NULL default {2}\
		)".format(self.progress, Storyboard.POINTS_KEY, initial_points)

		self.createDel(self.progress, query)

		for i,team in enumerate(teams,1):
			query = u"insert into {0}(teamID,team) values(?,?)".format(self.progress)
			self.commit_exec(query, (unicode(i), team))

	# Create server state table
	def createStateTable(self,teamConfig):
		query = u"create table {0}(\
			team varchar(16) not NULL,\
			target varchar(16) not NULL,\
			address varchar(16) not NULL,\
			state integer not NULL\
		)"

		self.createDel(self.state,query)

		for team,targets in teamConfig.items():
			for target,address in targets.items():
				query = u"insert into {0} values(?,?,?,1)".format(self.state)

				self.commit_exec(query,(team,target,address))

	# Create scenario table
	def createScenario(self,scenario,firstStep):
                # We need a workaround to allow use of format for header names,
                # and also later for '{0}' on first line 
		query = u"create table {0}" + u"({0} varchar(16) not NULL, {1} varchar(256) not NULL, {2} varchar(16) not NULL, {3} varchar(16) not NULL)".format(Storyboard.STEP_KEY, Storyboard.LABEL_KEY, Storyboard.SUCCESS_KEY, Storyboard.FAILURE_KEY)

		self.createDel(self.scenario,query)

		queue = Queue()
		done = [Storyboard.STEP_COMPLETE]
		step = firstStep

		while True:
			label = scenario[step][Storyboard.LABEL_KEY]
			success = scenario[step][Storyboard.SUCCESS_KEY][Storyboard.NEXT_KEY]
			failure = scenario[step][Storyboard.FAILURE_KEY][Storyboard.NEXT_KEY]

			query = u"insert into {0} values(?,?,?,?)".format(self.scenario)

			self.commit_exec(query, (step, label, success, failure))

			done.append(step)

			if success not in done:
				queue.put(success)
			if failure not in done:
				queue.put(failure)

			if queue.empty():
				break
			else:
				step = queue.get()

	def __call__(self, config, teamConfig, initial_points):
		self.createConfigTable(config)
		self.createProgressTable(list(teamConfig.keys()), initial_points)
		self.createLogTable()
		self.createBoardTable()
		self.createStateTable(teamConfig)
#		self.createScenario(scenario,firstStep)
