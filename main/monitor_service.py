
#############################################################################
# Implementation of advanced monitoring functionality
#
# NOTE: The file 'monitor_base.py' contains the association between service
#       names and the functions below in the dictionary 'services'
#############################################################################

# Third-party library imports
import requests

class monitor_service():

        # Check the "http" service
	def http(self, address):

                # Build URL for service checking
		url = "http://" + address
                try:
		        response = requests.get(url)
                except:
                        print("[-] monitor_service: http: Service check failed")
                        return False

                # TODO: More complex checks are possible
                
                print("[+] monitor_service: http: Service check succeeded")
		return True
