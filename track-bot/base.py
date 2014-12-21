from webapp2 import RequestHandler
from util import get_login_module_base_url

class BaseHandler(RequestHandler):
    def dispatch(self):
        uid = self.request.cookies.get('uid', default = None)
        if not uid:
            self.response.set_cookie(key='redirected-from', value=self.request.url, domain=self.request.server_name,
                                     comment='redirect to this url after successful log in')
            self.redirect(get_login_module_base_url(self.request.scheme))
        else:
            super(BaseHandler, self).dispatch()