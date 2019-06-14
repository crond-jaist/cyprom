
#############################################################################
# Functions related to basic monitoring functionality
#############################################################################

# Standard library imports
import socket
from time import sleep

from logging import getLogger
logger = getLogger("CyPROM").getChild("monitor")

# Local application imports
from database_base import sqlState, sqlLog
from monitor_service import monitor_service
from storyboard import Storyboard

#############################################################################
# List of supported services for monitoring (entries can be added as needed)
# NOTE: Related functions must be defined in the file 'monitor_service.py'
services = {
	Storyboard.TCP_KEY: {
		Storyboard.SSH_KEY: {
			Storyboard.PORT_KEY: 22,
			Storyboard.FUNCTION_KEY: None
                },
		Storyboard.HTTP_KEY: {
			Storyboard.PORT_KEY: 80,
			Storyboard.FUNCTION_KEY: Storyboard.HTTP_KEY
		}
	},

        # NOTE: UDP protocol is not yet supported
	Storyboard.UDP_KEY: {
		"sample": {
			Storyboard.PORT_KEY: 5000,
			Storyboard.FUNCTION_KEY: None
		}
	}
}
#############################################################################


def check_port(address, proto, service):

        #print("check_port: address={} proto={} service={}".format(address, proto, service))

        # TODO: Handle also UDP protocol
        #if proto == Storyboard.TCP_KEY:
	#	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	#	sock.settimeout(2)

        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sock.settimeout(2)
	port = services[proto][service][Storyboard.PORT_KEY]

	try:
		sock.connect((address, port))
        # Timeout => Destination host cannot be reached
	except socket.timeout:
		sock.close()
                #print("check_port: Destination cannot be reached: {0}:{1}".format(address, port))
		return 0
        # Connection refused => Port is not open
	except socket.error:
		sock.close()
                #print("check_port: Port is not open: {0}:{1}".format(address, port))
		return -1
	except Exception:
		sock.close()
                #print("check_port: Connect exception: {0}:{1}".format(address, port))
		return -2

	sock.close()

        # Code below is only executed if a function name is associated to the port/service in the dictionary 'services'
	if services[proto][service][Storyboard.FUNCTION_KEY]:

		mod = monitor_service()
                # Execute the function in the monitor_service class associated to the port/service;
                # target address is provided as argument
                #print("[.] check_port: Execute function: {}".format("check = mod.{0}('{1}')".format(services[proto][service][Storyboard.FUNCTION_KEY], address)))
                exec("check = mod.{0}('{1}')".format(services[proto][service][Storyboard.FUNCTION_KEY], address))

		if not check:
			return -1

        #print("check_port: Connection succeeded: {0}:{1}".format(address, port))
        return 1

def check(teamName,config,out=False):
	state = sqlState()
	log = sqlLog()

	flag = True
	for target,address in config.items():
                # Check if server name contains service as prefix
                # TODO: Should revise
		if len(target.split(u"-")) <= 2:
			service = target.split(u"-")[0]
		else:
			result = check_port(address, Storyboard.TCP_KEY, Storyboard.SSH_KEY)
			if result == 0:
				state.updateState(teamName,target,0)
				continue
			else:
				state.updateState(teamName,target,1)
			continue

		for proto, service_dict in services.items():
                        # Handle service differently if expressed with upper or lower case letters:
                        # 1) If service name appears as such in the dictionary, consider it a warning
                        # TODO: Improve method
			if service in service_dict:
				result = check_port(address, proto, service.lower())
				if result == 1:
					state.updateState(teamName,target,1)
				elif result == 0:
					if out:
						logger.error(u"{0:>16} | {1} Not Found".format(teamName,target))
					state.updateState(teamName,target,0)
				else:
					if out:
						#logger.error(u"{0:>16} | {1} : {2} Unavailable".format(teamName,target,service))
						print("[-]: monitor_base: WARNING: {0}: Target '{1}': Service unavailable: '{2}'".format(teamName,target,service))
					state.updateState(teamName,target,-1)

                        # 2) If service name transformed to lower case appears in the dictionary, consider it an error
			elif service.lower() in service_dict:
				result = check_port(address, proto, service.lower())
				if result == 1:
					state.updateState(teamName,target,1)
				elif result == 0:
					if out:
						logger.error(u"{0:>16} | {1} Not Found".format(teamName,target))
					state.updateState(teamName,target,0)
					flag = False
				else:
					if out:
						#logger.error(u"{0:>16} | {1} : {2} Unavailable".format(teamName,target,service))
						print("[-]: monitor_base: ERROR: {0}: Target '{1}': Service unavailable: '{2}'".format(teamName,target,service))
					log.insert(teamName,u"sys",u"Unavailable",0)
					state.updateState(teamName,target,-2)
					flag = False
			else:
				continue
			break
		else:
			result = check_port(address, Storyboard.TCP_KEY, Storyboard.SSH_KEY)
			if result == 0:
				state.updateState(teamName,target,0)
			else:
				state.updateState(teamName,target,1)

	return flag

def monitor(teamName,targets,test):
	while True:
		if test or check(teamName,targets,True):
			break

		sleep(5)

def monitorAll(teamConfig,test):
	while True:

                if test:
                        break

		flag = True
		for teamName in teamConfig:
			if not check(teamName,teamConfig[teamName],True):
				flag = False

		if flag:
			break

def monitorProcess(teamConfig):
        # TODO: Should add check for test argument?!
	for teamName in teamConfig:
		check(teamName,teamConfig[teamName])
