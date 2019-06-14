
#############################################################################
# "No operation" trigger (for internal use mainly)
#############################################################################

# Trigger class definition
class none:

        # Check trigger parameters
	def check(self,trigger):
		return True

        # Execute trigger
	def trigger(self,teamName,trigger):
		pass
