#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Task queue URL handlers.
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
from utils import BaseRequestHandler, send_mail_once

WORKER_MAIL_ACTIVATION_URL = r'/worker/mail/activation/'


class MailActivationHandler(BaseRequestHandler):
    def post(self):
        from activation import calculate_activation_code
        
        invoice_key = self.get_argument('invoice_key')
        invoice = db.get(db.Key(invoice_key))
        
        activation_credentials_list = []
        for order in invoice.orders:
            for credentials in order.activation_credentials:
                credentials.activation_code = calculate_activation_code(
                    machine_id=credentials.machine_id,
                    serial_number=credentials.serial_number
                )
                activation_credentials_list.append(credentials)
        db.put(activation_credentials_list)
        customer = invoice.customer
        content = self.render_string('email/activation_code.txt', 
            activation_credentials_list=activation_credentials_list,
            customer=customer)

        send_mail_once(cache_key=invoice_key + str(customer.key()),
            worker_url=WORKER_MAIL_ACTIVATION_URL,
            body=content,
            to=customer.email,
            subject='%s Your activation codes' % configuration.MAIL_SUBJECT_PREFIX)


settings = {
    'debug': configuration.DEBUG,
    #'xsrf_cookies': True,
    'template_path': configuration.TEMPLATE_PATH,
}
urls = (
    (WORKER_MAIL_ACTIVATION_URL + r'?', MailActivationHandler),
)
application = tornado.wsgi.WSGIApplication(urls, **settings)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()
