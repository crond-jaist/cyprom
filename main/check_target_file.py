
#############################################################################
# Functions related to target file verification
#############################################################################

# Check syntax of target file
def check_target_file(target_config, test):
	chk = True
	# NOTE: Be careful that duplicates are removed automatically
	for teamName, targetList in target_config.items():
		if chk:
			targetListBase = list(targetList.keys())
			addressList = []
			chk = False
		else:
			# Check whether the target name is the same
			if set(targetListBase) != set(list(targetList.keys())):
				print("[-] check_target_file: {0}: Target names inconsistent with those of other participants.".format(teamName))
				return False

		# Check the IP address format
		for target, address in targetList.items():
			block = address.split(".")

			if len(block) != 4:
				print("[-] check_target_file: {0}: Target '{1}' value is not in IPv4 format: '{2}'".format(teamName, target, address))
				return False

			for i in block:
				if i.isdigit():
					address = int(i)
				else:
					print("[-] check_target_file: {0}: Target '{1}' value contains a non-integer: '{2}'".format(teamName, target, i))
					return False

				if not 0 <= address <= 255:
					print("[-] check_target_file: {0}: Target '{1}' value contains an integer not in the range [0,255]: '{2}'".format(teamName, target, i))
					return False

                        # Do next check only if not in test mode
			if not test:
				if address in (addressList):
					print("[-] check_target_file: {0}: Target '{1}' specifies an address that has been used already: '{2}'".format(teamName, target, address))
					return False

		for address in list(targetList.values()):
			addressList.append(address)

	return True
