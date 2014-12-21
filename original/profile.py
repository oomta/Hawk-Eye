import os, datetime, webapp2, jinja2, logging, uuid
from google.appengine.ext import ndb
from google.appengine.api import mail
from time import gmtime, strftime, time

log = logging.getLogger(__name__)

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), extensions=['jinja2.ext.autoescape'])

message = mail.EmailMessage(sender="Dibyendu's Google App Engine Profile <iou.in.21@gmail.com>",
                            subject="A New Visitor to Your Profile")
message.to = "Dibyendu Das <iou.in.21@gmail.com>"

DEFAULT_DATASTORE_NAME = 'visitor'
USER_NAME = 'admin'
PASSWORD = 'secure'
INTERVAL_BETWEEN_SAVING_LOGS = 900  # seconds

def datastore_key(key):
    return ndb.Key('VisitorDataStore', key)

class UserData(ndb.Model):
    agent = ndb.TextProperty()
    ip = ndb.StringProperty()
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    country = ndb.StringProperty()
    geo = ndb.GeoPtProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

def save_to_datastore(key, data):
    user_data_query = UserData.query(UserData.ip == data['User-Ip'], ancestor=datastore_key(key)).order(-UserData.date)
    user_data = user_data_query.get()
    if user_data is None or (datetime.datetime.now() - user_data.date).total_seconds() > INTERVAL_BETWEEN_SAVING_LOGS:
      visitor = UserData(parent=datastore_key(key))
      visitor.agent = data['User-Agent']
      visitor.ip = data['User-Ip']
      visitor.city = data['User-City']
      visitor.state = data['User-State']
      visitor.country = data['User-Country']
      visitor.geo = ndb.GeoPt(data['User-Geo-Location'])
      visitor.put()
      if user_data is None:
        message.send()

def get_client_data(request):
    data = {}
    data['User-Agent'] = request.headers['User-Agent']
    data['User-State'] = 'west-bengal' #request.headers['X-Appengine-Region']
    data['User-City'] = 'kolkata'#request.headers['X-Appengine-City']
    data['User-Country'] = 'india' #request.headers['X-Appengine-Country']
    data['User-Geo-Location'] = '0.0, 0.0' #request.headers['X-Appengine-Citylatlong']
    data['User-Ip'] = request.remote_addr
    data['Time'] = strftime("%a, %d %b %Y %X +0000", gmtime())
    message.body = """
Hi Dibyendu,

You have a new visitor to your profile.

User-Agent : %s
User-Ip : %s
City : %s
State : %s
Country : %s
Latitude & Longitude : %s
Access Time : %s
""" % (data['User-Agent'], data['User-Ip'], data['User-City'], data['User-State'], data['User-Country'], data['User-Geo-Location'], data['Time'])
    return data

class HtmlHandler(webapp2.RequestHandler):
    def get (self, q):
      if q is None:
        q = 'index.html'
      template = JINJA_ENVIRONMENT.get_template(q)
      self.response.headers ['Content-Type'] = 'text/html'
      data = get_client_data(self.request)
      save_to_datastore(DEFAULT_DATASTORE_NAME, data)
      self.response.write(template.render({'agent': data['User-Agent'], 'state': data['User-State'], 'city': data['User-City'], 'country': data['User-Country'], 'geo': data['User-Geo-Location'], 'ip': data['User-Ip'], 'time': data['Time']}))

class PresentationHandler(webapp2.RequestHandler):
    def get (self, q):
      self.response.headers ['Content-Type'] = 'text/html'
      data = get_client_data(self.request)
      save_to_datastore(DEFAULT_DATASTORE_NAME, data)
      if q == '':
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({'agent': data['User-Agent'], 'state': data['User-State'], 'city': data['User-City'], 'country': data['User-Country'], 'geo': data['User-Geo-Location'], 'ip': data['User-Ip'], 'time': data['Time']}))
      else:
        template = JINJA_ENVIRONMENT.get_template('presentations/index.html')
        self.response.write(template.render({'query': q}))

class PresentationPdfHandler(webapp2.RequestHandler):
    def get (self, q):
      save_to_datastore(DEFAULT_DATASTORE_NAME, get_client_data(self.request))
      f = open('presentations/' + q, 'r')
      data = f.read()
      f.close()
      self.response.headers ['Content-Type'] = 'application/pdf'
      self.response.headers['Content-Disposition'] = "filename='" + q + "'"
      self.response.write(data)

class PresentationTexHandler(webapp2.RequestHandler):
    def get (self, q):
      save_to_datastore(DEFAULT_DATASTORE_NAME, get_client_data(self.request))
      f = open('presentations/' + q, 'r')
      data = f.read()
      f.close()
      self.response.headers ['Content-Type'] = 'text/tex'
      self.response.headers['Content-Disposition'] = "filename=" + q.replace(' ', '-')
      self.response.write(data)

class PaperHandler(webapp2.RequestHandler):
    def get (self, q):
      data = get_client_data(self.request)
      save_to_datastore(DEFAULT_DATASTORE_NAME, data)
      q = q.replace('-', ' ').replace('_', ' ').title() + '.pdf'
      if os.path.isfile('papers/' + q):
        f = open('papers/' + q, 'r')
        content = f.read()
        f.close()
        self.response.headers ['Content-Type'] = 'application/pdf'
        self.response.headers['Content-Disposition'] = "filename='" + q + "'"
        self.response.write(content)
      else:
        self.response.headers ['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({'agent': data['User-Agent'], 'state': data['User-State'], 'city': data['User-City'], 'country': data['User-Country'], 'geo': data['User-Geo-Location'], 'ip': data['User-Ip'], 'time': data['Time']}))

class PaperPdfHandler(webapp2.RequestHandler):
    def get (self, q):
      save_to_datastore(DEFAULT_DATASTORE_NAME, get_client_data(self.request))
      q = q[:-4]
      q = q.replace('-', ' ').replace('_', ' ').title() + '.pdf'
      f = open('papers/' + q, 'r')
      data = f.read()
      f.close()
      self.response.headers ['Content-Type'] = 'application/pdf'
      self.response.headers['Content-Disposition'] = "filename='" + q + "'"
      self.response.write(data)

class ResumeHandler(webapp2.RequestHandler):
    def get (self, q=None):
      save_to_datastore(DEFAULT_DATASTORE_NAME, get_client_data(self.request))
      f = open('resume/resume.pdf', 'r')
      data = f.read()
      f.close()
      self.response.headers ['Content-Type'] = 'application/pdf'
      self.response.headers['Content-Disposition'] = "filename='resume.pdf'"
      self.response.write(data)

class VisitorHandler(webapp2.RequestHandler):
    def get (self):
      self.response.headers ['Content-Type'] = 'text/html'
      self.response.out.write('<form method="post" style="margin:20% 0 0 34%;text-align:right;width: 300px"><label>User:</label> <input type="text" name="user"/><br><label>Pass:</label> <input type="password" name="pass"/><br><input type="submit" value="Submit"/></form>')

    def post (self):
      if self.request.get('user') == USER_NAME and self.request.get('pass') == PASSWORD:
        user_data_query = UserData.query(ancestor=datastore_key(DEFAULT_DATASTORE_NAME)).order(-UserData.date)
        user_data = user_data_query.fetch()
        self.response.headers ['Content-Type'] = 'text/html'
        self.response.write('<html><head></head><body><table border="1"><tr><th>User Agent</th><th>Ip</th><th>City</th><th>State</th><th>Country</th><th>Geo Location</th><th>Date</th></tr>')
        for data in user_data:
          self.response.write('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (data.agent, data.ip, data.city, data.state, data.country, data.geo, data.date.strftime("%a, %d %b %Y %X GMT")))
        self.response.write('</table></body></html>')
      else:
        self.response.out.write('<form method="post" style="margin:20% 0 0 34%;text-align:right;width: 300px"><label>User:</label> <input type="text" name="user"/><br><label>Pass:</label> <input type="password" name="pass"/><br><input type="submit" value="Submit"/></form>')

class Register(webapp2.RequestHandler):

    def _get_cookies(self, request):
      cookies = {}
      raw_cookies = request.headers.get("Cookie")
      if raw_cookies:
        for cookie in raw_cookies.split(';'):
            name, value = tuple(cookie.split('='))
            cookies[name] = value
      return cookies

    def get (self):
      #cookies = self._get_cookies(self.request)
      session = self.request.get('session')
      self.response.headers['Content-Type'] = 'text/txt'
      if not session:
        self.response.out.write('%s'%str(uuid.uuid4()))
      log.info(self.request.headers.get('User-Agent'))
      #for k, v in self.request:
      #  log.debug(' - %s: %s'%(str(k), str(v)))
      #if 'session_id' not in cookies:
      #  self.response.set_cookie('session_id', '1234', expires=datetime.datetime.utcfromtimestamp(time() + 86400), path='/register')
      #self.response.out.write('Hello world ...  %s  %s'%(self.request.remote_addr, session))

    def post (self):
      if self.request.get('user') == USER_NAME and self.request.get('pass') == PASSWORD:
        user_data_query = UserData.query(ancestor=datastore_key(DEFAULT_DATASTORE_NAME)).order(-UserData.date)
        user_data = user_data_query.fetch()
        self.response.headers ['Content-Type'] = 'text/html'
        self.response.write('<html><head></head><body><table border="1"><tr><th>User Agent</th><th>Ip</th><th>City</th><th>State</th><th>Country</th><th>Geo Location</th><th>Date</th></tr>')
        for data in user_data:
          self.response.write('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (data.agent, data.ip, data.city, data.state, data.country, data.geo, data.date.strftime("%a, %d %b %Y %X GMT")))
        self.response.write('</table></body></html>')
      else:
        self.response.out.write('<form method="post" style="margin:20% 0 0 34%;text-align:right;width: 300px"><label>User:</label> <input type="text" name="user"/><br><label>Pass:</label> <input type="password" name="pass"/><br><input type="submit" value="Submit"/></form>')


application = webapp2.WSGIApplication ([
  ('/(.*html)?', HtmlHandler),
  ('/presentations/(.*pdf)', PresentationPdfHandler),
  ('/presentations/(.*tex)', PresentationTexHandler),
  ('/presentations/(.*html)', PresentationHandler),
  ('/presentations/(.*)', PresentationHandler),
  ('/papers/(.*pdf)', PaperPdfHandler),
  ('/papers/(.*)', PaperHandler),
  ('/resume', ResumeHandler),
  ('/resume/(.*)', ResumeHandler),
  ('/visitor', VisitorHandler),
  ('/register', Register)
], debug=False)
