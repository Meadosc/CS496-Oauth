#CS496 Mobile and Web development HW4
# Cord Meados 2017

# [START imports]
from google.appengine.ext.webapp import template #Django
import os #Django
from google.appengine.api import urlfetch
import webapp2
import string
import urllib
import random
import json

#Constatants
CLIENT_ID = '362935595119-o0grnh36hbunrrfvakuh0duoi8clpv47.apps.googleusercontent.com'
CLIENT_SECRET = 'ASdcpzNg3AM1zhR0hi0sskTR'
REDIRECT_URI = 'https://cs496-oauth-183823.appspot.com/oauth'

class MainPage(webapp2.RequestHandler):
    def get(self):
	    #Create random string for authentication
        random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])

        url_linktext = 'Provide Access'
        #build URL for google request and direct user
        url = "https://accounts.google.com/o/oauth2/v2/auth?"
        url = url + "scope=email"
        url = url + "&access_type=offline"
        url = url + "&include_granted_scopes=true"
        url = url + "&state="
        url = url + random_string
        url = url + "&redirect_uri=https://cs496-oauth-183823.appspot.com/oauth"
        url = url + "&response_type=code"
        url = url + "&client_id=362935595119-o0grnh36hbunrrfvakuh0duoi8clpv47.apps.googleusercontent.com"

        template_values = {'url': url}

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))

class OAuthHandler(webapp2.RequestHandler):
    def get(self):
        auth_code = self.request.GET['code']
        state = self.request.GET['state']
        post_body = {
            'code': auth_code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
            }

        pload = urllib.urlencode(post_body)
        headers = {'Content-Type':'application/x-www-form-urlencoded'}
        result = urlfetch.fetch(
            url="https://www.googleapis.com/oauth2/v4/token",
   		 	payload = pload,
    		method = urlfetch.POST,
    		headers = headers)

        json_result = json.loads(result.content)

        headers = {'Authorization': 'Bearer ' + json_result['access_token']}
        result = urlfetch.fetch(
            url="https://www.googleapis.com/plus/v1/people/me",
            method = urlfetch.GET,
            headers=headers)

		#check that all data is there, else send "noAccount message"
        json_result = json.loads(result.content)
        exist_fname = False
        exist_lname = False
        exist_gplink = False
        existaccount = False
        for x in json_result:
            if x == 'name':
                if x[0]:
                    exist_fname = True
                if x[0]:
                    exist_lname = True
            if x == 'url':
                exist_gplink = True

        if (exist_fname and exist_lname and exist_gplink): #if all is well, list values
            first_name = json_result['name']['givenName']
            last_name = json_result['name']['familyName']
            gplink = str(json_result['url'])
            existaccount = True
            template_values = {'fname': first_name,
                               'lname': last_name,
                               'gplink': gplink,
                               'gplink_name': "Visit Profile",
                               'state': state}
        else:
            template_values = {'noAccount': "You do not have a Google+ account", 'state': state}

        path = os.path.join(os.path.dirname(__file__), 'templates/oauth.html')
        self.response.out.write(template.render(path, template_values))
# [END main_page]


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/oauth',OAuthHandler)
], debug=True)
# [END app] 