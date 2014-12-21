#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Starting template for Google App Engine applications.

Use this project as a starting point if you are just beginning to build a Google
App Engine project. Remember to download the OAuth 2.0 client secrets which can
be obtained from the Developer Console <https://code.google.com/apis/console/>
and save them as 'client_secrets.json' in the project directory.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


import httplib2
import logging
import os
import pickle
import pprint

from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache

import webapp2
import jinja2

import random
import json, yaml

from base import BaseHandler
from config import app_globals


memcache.add('GOOGLE_AUTH_CSRF_TOKEN', str(random.random())[2:])


JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True, extensions=['jinja2.ext.autoescape'])



# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
To make this sample run you will need to populate the client_secrets.json file
found at:
</p>
<p>
<code>%s</code>.
</p>
<p>with information found on the <a
href="https://code.google.com/apis/console">APIs Console</a>.
</p>
""" % CLIENT_SECRETS


http = httplib2.Http(memcache)
service = discovery.build('plus', 'v1', http=http)
decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/plus.me',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

#scope = ['https://www.googleapis.com/auth/plus.me', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']

class MainHandler(webapp2.RequestHandler):

  @decorator.oauth_aware
  def get(self):
    variables = {
        'url': decorator.authorize_url(),
        'has_credentials': decorator.has_credentials()
        }
    template = JINJA_ENVIRONMENT.get_template('grant.html')
    self.response.write(template.render(variables))


class AboutHandler(webapp2.RequestHandler):

  @decorator.oauth_required
  def get(self):
    try:
      http = decorator.http()
      user = service.people().get(userId='me').execute(http=http)
      text = 'Hello, %s!' % user['displayName']

      template = JINJA_ENVIRONMENT.get_template('welcome.html')
      self.response.write(template.render({'text': text, 'data': service.people().__dict__, 'test': service.people().get(userId='me') }))
    except client.AccessTokenRefreshError:
      self.redirect('/')

class TestHandler(BaseHandler):
  def get(self):
    import datetime
    logging.info('=============================== %s'%app_globals.my1)
    template = JINJA_ENVIRONMENT.get_template('test.html')
    self.response.write(template.render({'state': memcache.get('GOOGLE_AUTH_CSRF_TOKEN')}))
    self.response.set_cookie(key='some_key', value='lol', path='/test', comment='test cookie')

class AuthHandler(webapp2.RequestHandler):
  def get(self):
    code = self.request.get('code')
    from httplib2 import Http
    from google.appengine.api import urlfetch
    from urllib import urlencode
    import json
    import datetime



    self.response.headers['Content-Type'] = 'application/json'

    
    url = 'https://accounts.google.com/o/oauth2/token'
    payload = urlencode(dict(
        code=code,
        redirect_uri='http://localhost:8080/authback',
        client_id='203314710801-2mpp31cbhpr2kgeoo57f0c8dabs3qt48.apps.googleusercontent.com',
        grant_type='authorization_code',
        client_secret='0T16ITMXBUGEplBj8PDewtek'
      )
    )
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    try:
      result = urlfetch.fetch(
        url=url,
        payload=payload,
        method=urlfetch.POST,
        headers=headers
      )
    except urlfetch.Error, e:
      logging.debug(e)
    else:
      if not self.request.get('error', default_value=None):
        data = json.loads(result.content)
        self.response.write('got auth token')
        logging.info(data)
        access_token, expires = data['access_token'], data['expires_in']
        self.response.set_cookie(key='some_key', value=data['access_token'], expires=datetime.datetime(2040, 12, 31), path='/test', comment='test cookie')
      else:
        self.response.write('omg how dare you deny')
        self.response.write('\n\n state = %s, GOOGLE_AUTH_CSRF_TOKEN = %s'%(self.request.get('state'), memcache.get('GOOGLE_AUTH_CSRF_TOKEN')))
        
      



    #rpc = urlfetch.create_rpc()
    # ... do other things ...
    #try:
      #result = rpc.get_result()
    #  if result.status_code == 200:
    #    text = result.content
        # ...
    #except urlfetch.DownloadError:
    #  pass

    






















    

    h = Http()
    headers = {'Authorization': 'OAuth ' +  access_token}
    resp, data = h.request("https://www.googleapis.com/oauth2/v2/userinfo", "GET", headers=headers)
    self.response.write('\n\nOauth Info\n\n')
    self.response.write(data)

    resp, data = h.request("https://www.googleapis.com/plus/v1/people/me", "GET", headers=headers)
    self.response.write('\n\nG+ Info\n\n')
    self.response.write(data)
    
    headers['GData-Version'] = '3.0'
    resp, data = h.request("https://www.google.com/m8/feeds/contacts/default/thin?alt=json&max-results=1000", "GET", headers=headers)
    self.response.write('\n\nContact List\n\n')
    #data = json.loads(data)
    self.response.write(data)

class FbAuthHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'application/json'

    self.response.write('Fb data\n\nCode : ')
    code = self.request.get('code')
    self.response.write(code)

    from httplib2 import Http
    from urllib import urlencode, unquote
    import json

    h = Http()    

    resp, data = h.request('https://graph.facebook.com/oauth/access_token?' + 'client_id=532876683483897&redirect_uri=http://localhost:8080/fbauthback&client_secret=73694db112e9ecf4b4fd455e28533705&code=' + code, 'GET')
    self.response.write('\n\nResponse : ')
    self.response.write(str(resp) + '\n\nData : ')
    self.response.write(data)

    
    try:
      data = json.loads(data)
    except Exception, e:
      logging.info('=======================')
      logging.info(e)
      logging.info('=======================')
    logging.info('------------------------------------')
    logging.info(data)
    logging.info('------------------------------------')

    data = dict([item.split('=') for item in data.split('&')])
    access_token = data['access_token']
    
    resp, data = h.request('https://graph.facebook.com/oauth/access_token?client_id=532876683483897&client_secret=73694db112e9ecf4b4fd455e28533705&grant_type=client_credentials', 'GET')
    self.response.write('\n\nResponse : ')
    self.response.write(str(resp) + '\n\nData : ')
    data = dict([item.split('=') for item in data.split('&')])
    self.response.write(str(data))

    resp, data = h.request('https://graph.facebook.com/debug_token?input_token=' + access_token + '&access_token=' + data['access_token'] , 'GET')
    self.response.write('\n\nResponse : ')
    self.response.write(str(resp) + '\n\nData : ')
    self.response.write(data)

    resp, data = h.request('https://graph.facebook.com/v2.0/me?fields=id,email,first_name,gender,last_name,location,name,timezone,verified,picture&format=json&suppress_http_code=1&method=GET&access_token=' + access_token , 'GET')
    self.response.write('\n\nAbout Me : \n\n')
    self.response.write(data)

class FbRespHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'application/json'
    #code = self.request.get('code')
    self.response.write('omg lol')

class GitHubAuthHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'application/json'
    code = self.request.get('code')
    from httplib2 import Http
    from urllib import urlencode
    

    h = Http()
    data = dict(redirect_uri='http://localhost:8080/githubauthback', client_id='baccad0153a85f91041f',
                code=code, client_secret='aad9fc6fbd5f9cca609c76a7b693d3f14bf56bae')
    headers = {'Accept': 'application/json'}
    resp, data = h.request('https://github.com/login/oauth/access_token', 'POST', headers=headers, body=urlencode(data))
    data = json.loads(data)
    self.response.write('Git Hub :\n\n')
    self.response.write(resp)
    self.response.write('\n\n')
    self.response.write(str(data))

    headers = {'Authorization': 'token ' + data['access_token']}
    resp, data = h.request('https://api.github.com/user', 'GET', headers=headers)
    data = json.loads(data)
    self.response.write('\n\n')
    self.response.write(resp)
    self.response.write('\n\n')
    self.response.write(str(data))

class LinkedInAuthHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'application/json'
    code = self.request.get('code')
    from httplib2 import Http
    from urllib import urlencode

    h = Http()
    headers = {'Accept': 'application/json'}
    resp, data = h.request('https://www.linkedin.com/uas/oauth2/accessToken?grant_type=authorization_code&code=' + code + '&redirect_uri=http://localhost:8080/linkedinauthback&client_id=75jim8vcqbl0il&client_secret=ClVamT0EVDsW2v1R', 'POST', headers=headers)
    token = json.loads(data)['access_token']
    headers = {'x-li-format': 'json'}
    resp, data = h.request('https://api.linkedin.com/v1/people/~?oauth2_access_token=' + token, 'GET', headers=headers)
    self.response.write('Linked In :\n\n')
    self.response.write(data)
    resp, data = h.request('https://api.linkedin.com/v1/people/~/email-address?oauth2_access_token=' + token, 'GET', headers=headers)
    self.response.write('\n\nMail : \n\n')
    self.response.write(data)




from google.appengine.api import channel
class ChannelHandler(webapp2.RequestHandler):
  def get(self, channel_id):
    token = channel.create_channel(channel_id)
    template = JINJA_ENVIRONMENT.get_template('channel.html')
    self.response.write(template.render({'token': token}))
  def post(self):
    ids = ('1', '2')
    key = self.request.get('key')
    is_pressed = self.request.get('pressed')
    time = self.request.get('time')
    id = [id for id in ids if id != self.request.get('id')][0]
    channel.send_message(id, json.dumps({'key': key, 'pressed': is_pressed, 'time': time}))
class ChannelConnectHandler(webapp2.RequestHandler):
  def post(self):
    client_id = self.request.get('from')
    logging.info('Client #%s has opened a channel'%client_id)
class ChannelDisconnectHandler(webapp2.RequestHandler):
  def post(self):
    client_id = self.request.get('from')
    logging.info('Client #%s has closed the channel'%client_id)

class TabCloseHandler(webapp2.RequestHandler):
  def post(self):
    data = self.request.get('data')
    logging.info('closed with data %s' % data)


app = webapp2.WSGIApplication(
    [
     ('/', MainHandler),
     ('/about', AboutHandler),
     ('/close', TabCloseHandler),
     ('/channel', ChannelHandler),
     (r'/channel/(\d+)', ChannelHandler),
     ('/_ah/channel/connected/', ChannelConnectHandler),
     ('/_ah/channel/disconnected/', ChannelDisconnectHandler),
     ('/test', TestHandler),
     ('/authback', AuthHandler),
     ('/fbauthback', FbAuthHandler),
     ('/fbrespback', FbRespHandler),
     ('/githubauthback', GitHubAuthHandler),
     ('/linkedinauthback', LinkedInAuthHandler),
     (decorator.callback_path, decorator.callback_handler())
    ],
    debug=True)













class MainFooHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'image/jpeg'
    from google.appengine.api import images
    xpng = open('2.jpg').read()
    ypng = open('3.png').read()
    ypng = images.resize(ypng, width=15, height=15)
    composite = images.composite([(xpng, 0, 0, 1.0, images.TOP_LEFT),
      (ypng, -1, -1, 1.0, images.BOTTOM_RIGHT)], 80, 80, output_encoding=images.JPEG) 
    self.response.out.write(composite)
    return


    

class MainFooBarHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('foo bar')




foo_app = webapp2.WSGIApplication(
    [
     ('/foo/', MainFooHandler),
     ('/foo/bar', MainFooBarHandler)
    ],
    debug=True)
