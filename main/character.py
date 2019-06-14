
#############################################################################
# Functions related to character encoding
#############################################################################

# Change string to Unicode
def decode(word):
	if isinstance(word, str):
		return word.decode("utf-8")
	else:
		return word

# Change Unicode to string
def encode(word):
	if isinstance(word, unicode):
		return word.encode("utf-8")
	else:
		return word
