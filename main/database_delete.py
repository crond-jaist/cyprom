
#############################################################################
# Classes related to database table removal
#############################################################################

# Local imports
from database_create import createTable


class deleteTables(createTable):
        def delete(self):
                for table in self.tables:
			print("[.] Delete {0} table".format(table))
			self.execute("drop table {0}".format(table))
