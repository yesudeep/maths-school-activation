#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configuration
import logging
import utils
import tornado.web
import tornado.wsgi

from google.appengine.api import memcache
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from utils import BaseRequestHandler

logging.basicConfig(level=logging.DEBUG)

class IndexHandler(BaseRequestHandler):
    def get(self):
        self.render('index.html')

class ProductsHandler(BaseRequestHandler):
    def get(self):
        self.render('products.html')

class ActivationHandler(BaseRequestHandler):
    def get(self):
        self.render('activation.html')

class ProfileHandler(BaseRequestHandler):
    def get(self):
        self.render('profile.html')

class RegistrationHandler(BaseRequestHandler):
    def get(self):
        self.render('registration.html')

settings = {
    'debug': configuration.DEBUG,
    #'xsrf_cookies': True,
    'template_path': configuration.TEMPLATE_PATH,
}
urls = (
    (r'/', IndexHandler),
    (r'/products/?', ProductChoiceHandler),
    (r'/activation/?', ActivationHandler),
    (r'/profile/?', ProfileHandler),
    (r'/register/?', RegistrationHandler),
)
application = tornado.wsgi.WSGIApplication(urls, **settings)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()
    
if __name__ == '__main__':
    main()
