from google.appengine.api import modules
from config import app_globals
import re

def get_login_module_base_url(current_scheme='https'):
  host_name = modules.get_hostname(module=app_globals.login_module['name'])
  scheme = app_globals.login_module.get('protocol', None)
  scheme = scheme and scheme or current_scheme
  base_url = re.match(r"[\w\-]*\.(.*)(?=(\.[\w\-]*\.\w*$))", host_name)
  if base_url:
    base_url = base_url.groups()
    base_url = (scheme == 'https' and base_url[0].replace('.', '-dot-') or base_url[0]) + base_url[1]
  else:
    base_url = host_name
  return scheme + '://' + base_url

def uri_builder(secrets):
  query = ''
  for k, v in secrets['query_params'].iteritems():
    if k == 'scope':
      query += k + '=' + ((secrets['scope_separator'] is not None) and
                          (secrets['scope_separator'].join(secrets['query_params']['scope'])) or
                          (''.join(secrets['query_params']['scope']))) + '&'
    elif k == 'redirect_uri':
      query += k + '=' + get_login_module_base_url(None) + v + '&'
    else:
      query += k + '=' + v + '&'
  query += 'state=' + app_globals.csrf_prevention_token
  return secrets['auth_url'] + '?' + query