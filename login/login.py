import logging
import os
import pickle
import pprint

import webapp2
import jinja2

import random
import datetime

from webapp2_extras.securecookie import SecureCookieSerializer


from google.appengine.api import urlfetch
from urllib import urlencode, unquote
import yaml, json

from google.appengine.api import memcache
from util import get_login_module_base_url, uri_builder

from config import app_globals
from time import time, gmtime
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True, extensions=['jinja2.ext.autoescape'])
JINJA_ENVIRONMENT.globals['uri_builder'] = uri_builder

client_secret = yaml.load(open(app_globals.client_secrets_file, 'r').read())

def get_timezone(latlng):
  tzinfo, retry = None, False
  payload = {'location' : latlng, 'timestamp' : int(time())}
  key = client_secret['google']['api'].get('key', None)
  if key:
    payload['key'] = key
  payload = urlencode(payload)
  try:
    result = urlfetch.fetch(
      url = client_secret['google']['api']['timezone'] + '?' + payload,
      method = urlfetch.GET
    )
  except urlfetch.Error, e:
    logging.warn(e.message)
    retry = True
  else:
    data = json.loads(result.content)
    if data['status'] != 'OK':
      logging.warn("google's timezone api returned status : " + data['status'])
      if data['status'] in ('OVER_QUERY_LIMIT', 'UNKNOWN_ERROR'):
        retry = True
    else:
      tzinfo = {'offset': data['rawOffset'], 'id': data['timeZoneId']}
  return tzinfo, retry

def get_latlng(address):
  latlng, retry = None, False
  payload = {'address' : address}
  key = client_secret['google']['api'].get('key', None)
  if key:
    payload['key'] = key
  payload = urlencode(payload)
  try:
    result = urlfetch.fetch(
      url = client_secret['google']['api']['geocoding'] + '?' + payload,
      method = urlfetch.GET
    )
  except urlfetch.Error, e:
    logging.warn(e.message)
    retry = True
  else:
    data = json.loads(result.content)
    if data['status'] != 'OK':
      logging.warn("google's geocoding api returned status : " + data['status'])
      if data['status'] in ('OVER_QUERY_LIMIT', 'UNKNOWN_ERROR'):
        retry = True
    else:
      count, lat, lng = 0, 0.0, 0.0
      for result in data['results']:
        location = result['geometry']['location']
        lat += float(location['lat'])
        lng += float(location['lng'])
        count += 1
      lat /= count
      lng /= count
      latlng = str(lat) + ',' + str(lng)
  return latlng, retry

class LoginPageHandler(webapp2.RequestHandler):
  def get(self):
    #post_login_redirect_url = self.request.cookies.get('redirected-from', default = self.request.scheme + '://' + self.request.server_name)
    login_error_message = self.request.cookies.get('login-error', default = None)
    self.response.delete_cookie('login-error')    
    template = JINJA_ENVIRONMENT.get_template('login.html')
    #self.response.delete_cookie('redirected-from')
    self.response.write(template.render({'client_secret': client_secret, 'error_message': login_error_message}))
    





def set_cookie(self):
    cookie_val = self.request.cookies.get('uid', default = None)
    serializer = SecureCookieSerializer(app_globals.secure_cookie_pass_phrase)
    self.response.write('cookie value is %s (raw) & %s (deserialized)'%(cookie_val, serializer.deserialize('uid', cookie_val)))
    current_time = gmtime()
    self.response.set_cookie(key = 'uid', value = serializer.serialize('uid', 'lollolo'), path = '/',
      expires = datetime(current_time.tm_year + app_globals.login_cookie_expiry, current_time.tm_mon, current_time.tm_mday))
    self.response.write('----------------------------------')
    #self.response.set_cookie(key='some_key', value='lol', path='/test', comment='test cookie')



class GoogleCallBackHandler(webapp2.RequestHandler):
  def __parse_data(self, data):
    info = {}
    info['id'] = data['id']
    info['email'] = data.get('email', None)
    info['name'] = data.get('name', None)
    if not info['name']:
      info['name'] = (data.get('given_name', '') + ' ' + data.get('family_name', '')).strip()
      info['name'] = info['name'] and info['name'] or None
    info['url'] = data.get('link', None)
    info['gender'] = data.get('gender', None)
    info['picture'] = data.get('picture', None)
    info['location'] = data.get('gplus_info', None)
    info['location'] = info['location'] and info['location'].get('placesLived', None) or None
    if info['location']:
      for location in info['location']:
        if location.get('primary', False):
          info['location'] = location.get('value', None)
          break
    if info['location'] is None:
      info['location'] = {'latlng': self.request.headers.get('X-Appengine-Citylatlong', default = None), 'retry': False}
    else:
      latlng, retry = get_latlng(info['location'])
      latlng = retry and info['location'] or latlng
      info['location'] = {'latlng': latlng, 'retry': retry}
    if not info['location']['retry']:
      tzinfo, retry = get_timezone(info['location']['latlng'])
      info['timezone'] = {'tzinfo': tzinfo, 'retry': retry}
    return info

  def get(self):
    self.response.headers['Content-Type'] = 'application/json'
    login_page_url = get_login_module_base_url(self.request.scheme)
    code, state = self.request.get('code'), self.request.get('state')

    if state != app_globals.csrf_prevention_token:
      self.response.set_cookie(key = 'login-error', value = app_globals.token_mismatch_message)
      self.redirect(login_page_url)
      return

    payload = urlencode(dict(
        code = code,
        redirect_uri = login_page_url + client_secret['google']['auth']['query_params']['redirect_uri'],
        client_id = client_secret['google']['auth']['query_params']['client_id'],
        grant_type = 'authorization_code',
        client_secret = client_secret['google']['token']['client_secret']
      )
    )
    try:
      result = urlfetch.fetch(
        url = client_secret['google']['token']['token_url'],
        payload = payload,
        method = urlfetch.POST,
        headers = {'content-type': 'application/x-www-form-urlencoded'}
      )
    except urlfetch.Error, e:
      logging.warn(e.message)
      self.response.set_cookie(key = 'login-error', value =
        app_globals.url_fetch_error_message.format(url = client_secret['google']['token']['token_url']))
      self.redirect(login_page_url)
      return
    else:
      if not self.request.get('error', default_value=None):
        data = json.loads(result.content)
        access_token, expires = data['access_token'], data['expires_in']
      else:
        self.response.set_cookie(key = 'login-error', value = app_globals.user_denial_message)
        self.redirect(login_page_url)
        return

    rpc = urlfetch.create_rpc()
    urlfetch.make_fetch_call(
      rpc,
      url = client_secret['google']['api']['plus_info_url'],
      method = urlfetch.GET,
      headers = {'Authorization': 'OAuth ' +  access_token}
    )

    try:
      result = urlfetch.fetch(
        url = client_secret['google']['api']['oauth_info_url'],
        method = urlfetch.GET,
        headers = {'Authorization': 'OAuth ' +  access_token}
      )
    except urlfetch.Error, e:
      logging.warn(e.message)
      self.response.set_cookie(key = 'login-error', value =
        app_globals.url_fetch_error_message.format(url = client_secret['google']['api']['oauth_info_url']))
      self.redirect(login_page_url)
      return
    else:
      data = json.loads(result.content)

    try:
      result = rpc.get_result()
    except urlfetch.Error, e:
      logging.warn(e.message)
      self.response.set_cookie(key = 'login-error', value =
        app_globals.url_fetch_error_message.format(url = client_secret['google']['api']['plus_info_url']))
      self.redirect(login_page_url)
      return
    else:
      data['gplus_info'] = json.loads(result.content)
      data = self.__parse_data(data)
      self.response.write('\n\n=============  google data  ================\n')
      self.response.write(str(data))

    #self.response.set_cookie(key='some_key', value=data['access_token'], expires=datetime.datetime(2040, 12, 31), path='/test', comment='test cookie')


class FacebookCallBackHandler(webapp2.RequestHandler):
  def __parse_data(self, data):
    info = {}
    info['id'] = data['id']
    info['email'] = data.get('email', None)
    info['name'] = data.get('name', None)
    if not info['name']:
      info['name'] = (data.get('first_name', '') + ' ' + data.get('last_name', '')).strip()
      info['name'] = info['name'] and info['name'] or None
    info['url'] = data.get('link', None)
    info['gender'] = data.get('gender', None)
    info['picture'] = data.get('additional_picture', None)
    info['picture'] = info['picture'] and info['picture'].get('data', None) or None
    if info['picture']:
      if info['picture'].get('is_silhouette', True):
        info['picture'] = None
      else:
        info['picture'] = info['picture'].get('url', None)
    info['location'] = data.get('location', None)
    info['location'] = info['location'] and info['location'].get('name', None) or None
    if info['location'] is None:
      info['location'] = {'latlng': self.request.headers.get('X-Appengine-Citylatlong', default = None), 'retry': False}
    else:
      latlng, retry = get_latlng(info['location'])
      latlng = retry and info['location'] or latlng
      info['location'] = {'latlng': latlng, 'retry': retry}
    if not info['location']['retry']:
      tzinfo, retry = get_timezone(info['location']['latlng'])
      info['timezone'] = {'tzinfo': tzinfo, 'retry': retry}
    return info

  def get(self):
    self.response.headers['Content-Type'] = 'application/json'
    login_page_url = get_login_module_base_url(self.request.scheme)
    code, state = self.request.get('code'), self.request.get('state')
    if state != app_globals.csrf_prevention_token:
      self.response.set_cookie(key = 'login-error', value = app_globals.token_mismatch_message)
      self.redirect(login_page_url)
      return

    payload = urlencode(dict(
        code = code,
        redirect_uri = login_page_url + client_secret['facebook']['auth']['query_params']['redirect_uri'],
        client_id = client_secret['facebook']['auth']['query_params']['client_id'],
        client_secret = client_secret['facebook']['token']['client_secret']
      )
    )
    try:
      result = urlfetch.fetch(
        url = client_secret['facebook']['token']['token_url'],
        payload = payload,
        method = urlfetch.POST,
        headers = {'content-type': 'application/x-www-form-urlencoded'}
      )
    except urlfetch.Error, e:
      logging.warn(e.message)
      self.response.set_cookie(key = 'login-error', value =
        app_globals.url_fetch_error_message.format(url = client_secret['facebook']['token']['token_url']))
      self.redirect(login_page_url)
      return
    else:
      if not self.request.get('error', default_value = None):
        data = dict([item.split('=') for item in result.content.split('&')])
        access_token, expires = data['access_token'], data['expires']
      else:
        self.response.set_cookie(key = 'login-error', value = app_globals.user_denial_message)
        self.redirect(login_page_url)
        return

    payload = '&'.join([k+'='+str(v) for k,v in client_secret['facebook']['api']['picture']['query'].items()])
    payload += '&access_token=' + access_token
    rpc = urlfetch.create_rpc()
    urlfetch.make_fetch_call(
      rpc,
      url = client_secret['facebook']['api']['picture']['url'] + '?' + payload,
      method = urlfetch.GET
    )

    payload = urlencode(dict(
        fields = ','.join(client_secret['facebook']['api']['info']['fields']),
        format = 'json',
        access_token = access_token
      )
    )
    try:
      result = urlfetch.fetch(
        url = client_secret['facebook']['api']['info']['url'] + '?' + payload,
        method = urlfetch.GET
      )
    except urlfetch.Error, e:
      logging.warn(e.message)
      self.response.set_cookie(key = 'login-error', value =
        app_globals.url_fetch_error_message.format(url = client_secret['facebook']['api']['info']['url']))
      self.redirect(login_page_url)
      return
    else:
      data = json.loads(result.content)

    try:
      result = rpc.get_result()
    except urlfetch.Error, e:
      logging.warn(e.message)
      self.response.set_cookie(key = 'login-error', value =
        app_globals.url_fetch_error_message.format(url = client_secret['facebook']['api']['picture']['url']))
      self.redirect(login_page_url)
      return
    else:
      data['additional_picture'] = json.loads(result.content)
      data = self.__parse_data(data)
      self.response.write('\n\n=============  facebook data  ================\n')
      self.response.write(str(data))

class GithubCallBackHandler(webapp2.RequestHandler):
  def __parse_data(self, data):
    info = {}
    info['id'] = data['id']
    info['email'] = data.get('email', None)
    info['name'] = data.get('name', None)
    info['gender'] = data.get('gender', None)
    info['url'] = data.get('html_url', None)
    info['picture'] = data.get('avatar_url', None)
    info['location'] = data.get('location', None)
    if info['location'] is None:
      info['location'] = {'latlng': self.request.headers.get('X-Appengine-Citylatlong', default = None), 'retry': False}
    else:
      latlng, retry = get_latlng(info['location'])
      latlng = retry and info['location'] or latlng
      info['location'] = {'latlng': latlng, 'retry': retry}
    if not info['location']['retry']:
      tzinfo, retry = get_timezone(info['location']['latlng'])
      info['timezone'] = {'tzinfo': tzinfo, 'retry': retry}
    return info

  def get(self):
    self.response.headers['Content-Type'] = 'application/json'
    login_page_url = get_login_module_base_url(self.request.scheme)
    code, state = self.request.get('code'), self.request.get('state')
    if state != app_globals.csrf_prevention_token:
      self.response.set_cookie(key = 'login-error', value = app_globals.token_mismatch_message)
      self.redirect(login_page_url)
      return

    payload = urlencode(dict(
        code = code,
        redirect_uri = login_page_url + client_secret['github']['auth']['query_params']['redirect_uri'],
        client_id = client_secret['github']['auth']['query_params']['client_id'],
        client_secret = client_secret['github']['token']['client_secret']
      )
    )
    try:
      result = urlfetch.fetch(
        url = client_secret['github']['token']['token_url'],
        payload = payload,
        method = urlfetch.POST,
        headers = {'Accept': 'application/json'}
      )
    except urlfetch.Error, e:
      logging.warn(e.message)
      self.response.set_cookie(key = 'login-error', value =
        app_globals.url_fetch_error_message.format(url = client_secret['github']['token']['token_url']))
      self.redirect(login_page_url)
      return
    else:
      if not self.request.get('error', default_value=None):
        access_token = json.loads(result.content)['access_token']
      else:
        self.response.set_cookie(key = 'login-error', value = app_globals.user_denial_message)
        self.redirect(login_page_url)
        return

    try:
      result = urlfetch.fetch(
        url = client_secret['github']['api']['user_info_url'],
        method = urlfetch.GET,
        headers = {'Authorization': 'token ' + access_token, 'Accept': 'application/vnd.github.v3+json'}
      )
    except urlfetch.Error, e:
      logging.warn(e.message)
      self.response.set_cookie(key = 'login-error', value =
        app_globals.url_fetch_error_message.format(url = client_secret['github']['api']['user_info_url']))
      self.redirect(login_page_url)
      return
    else:
      data = self.__parse_data(json.loads(result.content))
      self.response.write('\n\n=============  github data  ================\n')
      self.response.write(str(data))

class LinkedinCallBackHandler(webapp2.RequestHandler):
  def __parse_data(self, data):
    info = {}
    info['id'] = data['id']
    info['email'] = data.get('emailAddress', None)
    info['name'] = (data.get('firstName', '') + ' ' + data.get('lastName', '')).strip()
    info['name'] = info['name'] and info['name'] or None
    info['gender'] = data.get('gender', None)
    info['url'] = data.get('publicProfileUrl', None)
    info['picture'] = data.get('pictureUrl', None)
    info['location'] = data.get('location', None)
    info['location'] = info['location'] and info['location'].get('name', None) or None
    if info['location'] is None:
      info['location'] = {'latlng': self.request.headers.get('X-Appengine-Citylatlong', default = None), 'retry': False}
    else:
      latlng, retry = get_latlng(info['location'])
      latlng = retry and info['location'] or latlng
      info['location'] = {'latlng': latlng, 'retry': retry}
    if not info['location']['retry']:
      tzinfo, retry = get_timezone(info['location']['latlng'])
      info['timezone'] = {'tzinfo': tzinfo, 'retry': retry}
    return info

  def get(self):
    self.response.headers['Content-Type'] = 'application/json'
    login_page_url = get_login_module_base_url(self.request.scheme)
    code, state = self.request.get('code'), self.request.get('state')
    if state != app_globals.csrf_prevention_token:
      self.response.set_cookie(key = 'login-error', value = app_globals.token_mismatch_message)
      self.redirect(login_page_url)
      return

    payload = urlencode(dict(
        code = code,
        redirect_uri = login_page_url + client_secret['linkedin']['auth']['query_params']['redirect_uri'],
        client_id = client_secret['linkedin']['auth']['query_params']['client_id'],
        client_secret = client_secret['linkedin']['token']['client_secret'],
        grant_type = 'authorization_code'
      )
    )
    try:
      result = urlfetch.fetch(
        url = client_secret['linkedin']['token']['token_url'],
        payload = payload,
        method = urlfetch.POST,
        headers = {'Accept': 'application/json'}
      )
    except urlfetch.Error, e:
      logging.warn(e.message)
      self.response.set_cookie(key = 'login-error', value =
        app_globals.url_fetch_error_message.format(url = client_secret['linkedin']['token']['token_url']))
      self.redirect(login_page_url)
      return
    else:
      if not self.request.get('error', default_value=None):
        access_token = json.loads(result.content)['access_token']
      else:
        self.response.set_cookie(key = 'login-error', value = app_globals.user_denial_message)
        self.redirect(login_page_url)
        return

    def linkedin_field_formatter(x):
      key = x.keys()[0]
      return key + ':(' + ','.join(map(lambda x: type(x) == dict and linkedin_field_formatter(x) or x, x[key])) + ')'

    payload = ':(' + ','.join(map(lambda x: type(x) == dict and linkedin_field_formatter(x) or x,
      client_secret['linkedin']['api']['user_info']['fields'])) + ')?'
    payload += 'oauth2_access_token=' + access_token
    try:
      result = urlfetch.fetch(
        url = client_secret['linkedin']['api']['user_info']['url'] + payload,
        method = urlfetch.GET,
        headers = {'x-li-format': 'json'}
      )
    except urlfetch.Error, e:
      logging.warn(e.message)
      self.response.set_cookie(key = 'login-error', value =
        app_globals.url_fetch_error_message.format(url = client_secret['linkedin']['api']['user_info']['url']))
      self.redirect(login_page_url)
      return
    else:
      data = self.__parse_data(json.loads(result.content))
      self.response.write('\n\n=============  linkedin data  ================\n')
      self.response.write(str(data))

class FbRespHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'application/json'
    #code = self.request.get('code')
    self.response.write('omg lol')

class CloseHandler(webapp2.RequestHandler):
  def post(self):
    logging.info('-=-=-=-=-=-=-=-')





application = webapp2.WSGIApplication([('/', LoginPageHandler)], debug=True)

callbacks = webapp2.WSGIApplication(
    [
     (client_secret['google']['auth']['query_params']['redirect_uri'], GoogleCallBackHandler),
     (client_secret['facebook']['auth']['query_params']['redirect_uri'], FacebookCallBackHandler),
     (client_secret['github']['auth']['query_params']['redirect_uri'], GithubCallBackHandler),
     (client_secret['linkedin']['auth']['query_params']['redirect_uri'], LinkedinCallBackHandler),
     ('/fbrespback', FbRespHandler),
     ('/close', CloseHandler)
    ],
    debug=True)