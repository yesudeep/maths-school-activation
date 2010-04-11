#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Website URL handlers.
# Copyright (c) 2009 happychickoo.
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import configuration
import logging
import utils
import tornado.web
import tornado.wsgi

from google.appengine.api import memcache
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from utils import SessionRequestHandler
from models import Product

logging.basicConfig(level=logging.DEBUG)

class IndexHandler(SessionRequestHandler):
    def get(self):
        self.render('index.html')

class ProfileHandler(SessionRequestHandler):
    def get(self):
        self.render('profile.html')

class RegistrationHandler(SessionRequestHandler):
    def get(self):
        self.render('registration.html')

class DashboardHandler(SessionRequestHandler):
    def get(self):
        self.render('dashboard.html')

class ActivateHandler(SessionRequestHandler):
    def get(self):
        products = Product.get_all()
        self.render('activate.html', products=products)

    def post(self):
        from django.utils import simplejson as json
        data = json.loads(self.get_argument('data'))
        logging.info(data)
        for k, v in data:
            pass

class UnsubscriptionHandler(SessionRequestHandler):
    def get(self):
        self.render('unsubscribe.html')

class DeinstallHandler(SessionRequestHandler):
    def get(self):
        self.render('deinstall.html')

class ProductActivationHandler(BaseRequestHandler):
    def get(self):
        self.render('product_activation.html')

class DeinstallPhonicaDinamagicHandler(SessionRequestHandler):
    def get(self):
        self.render('deinstall_phonica_dinamagic.html')

class DeinstallMathsEnglishHandler(SessionRequestHandler):
    def get(self):
        import random
        self.render('deinstall_maths_english.html', entry_code=random.randint(45000, 100000))

settings = {
    'debug': configuration.DEBUG,
    #'xsrf_cookies': True,
    'template_path': configuration.TEMPLATE_PATH,
}
urls = (
    (r'/', IndexHandler),
    (r'/dashboard/?', DashboardHandler),
    (r'/activate/?', ActivateHandler),
    (r'/unsubscribe/?', UnsubscriptionHandler),
    (r'/deinstall/?', DeinstallHandler),
    (r'/product/activation/?', ProductActivationHandler),
    (r'/profile/?', ProfileHandler),
    (r'/register/?', RegistrationHandler),
    (r'/deinstall/english/phonica/?', DeinstallPhonicaDinamagicHandler),
    (r'/deinstall/mathematics/dinamagic/?', DeinstallPhonicaDinamagicHandler),
    (r'/deinstall/mathematics/junior/?', DeinstallMathsEnglishHandler),
    (r'/deinstall/mathematics/primary/?', DeinstallMathsEnglishHandler),
    (r'/deinstall/mathematics/senior/?', DeinstallMathsEnglishHandler),
    (r'/deinstall/english/story/?', DeinstallMathsEnglishHandler),    
)
application = tornado.wsgi.WSGIApplication(urls, **settings)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()
    
if __name__ == '__main__':
    main()
