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

from decimal import Decimal
from google.appengine.api import memcache
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from utils import SessionRequestHandler, BaseRequestHandler
from models import Product, Customer, Invoice, Order


logging.basicConfig(level=logging.DEBUG)

LOGIN_PAGE_URL = '/'


class IndexHandler(SessionRequestHandler):
    def get(self):
        if self.is_logged_in():
            self.redirect('/dashboard')
        else:
            #error = self.get_argument('error')
            #if error:
            #    values = dict(error=error)
            #else:
            #    values = dict()
            #self.render('index.html', **values)
            self.render('index.html')
    
class LoginHandler(SessionRequestHandler):
    def post(self):
        email = self.get_argument('login-email')
        password = self.get_argument('login-password')
        customer = Customer.get_by_key_name(email)
        if customer:
            if customer.is_password_correct(password):
                self.do_login(email)
                self.redirect('/dashboard')
        else:
            self.redirect('/?error=login_failed')

class LogoutHandler(SessionRequestHandler):
    def get(self):
        self.do_logout()
        self.redirect(LOGIN_PAGE_URL)

class ProfileHandler(SessionRequestHandler):
    def get(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            self.render('profile.html')

class RegistrationHandler(SessionRequestHandler):
    def get(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            self.render('registration.html')

class DashboardHandler(SessionRequestHandler):
    def get(self):
        if not self.is_logged_in():
            logging.info('>>>>>>>>>>>>> ERROR: not logged in')
            self.redirect(LOGIN_PAGE_URL)
        else:
            customer = Customer.get_by_key_name(self.get_current_username())
            self.render('dashboard.html', customer=customer)

class ActivateHandler(SessionRequestHandler):
    def get(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            products = Product.get_all()
            self.render('activate.html', products=products)

    def post(self):
        from django.utils import simplejson as json
        data = json.loads(self.get_argument('data'))
        logging.info(data)


        if data:
            customer = Customer.get_by_key_name(self.get_current_username())
            invoice = Invoice(customer=customer)
            invoice.put()
            
            total_price = Decimal('0.00')
            orders = []
            for key, value in data.iteritems():
                product = db.get(db.Key(key))
                order = Order(product=product, invoice=invoice, customer=customer)
                order.serial_number = value.get('serialNumber')
                order.machine_id = value.get('machineId')
                #order.up_front_price = product.up_front_price
                #order.up_front_gst = product.up_front_gst
                order.billing_price = product.billing_price
                order.billing_gst = product.billing_gst
                order.currency = product.currency
                order.total_price = order.billing_price + order.billing_gst
                total_price += order.total_price
                logging.info(total_price)
                orders.append(order)
            db.put(orders)
            invoice.total_price = total_price
            invoice.currency = orders[0].currency
            invoice.put()
            
            logging.info('>>>>>>>>> invoice total price' + str(invoice.total_price))
            
            self.session['activation-invoice-key'] = str(invoice.key())
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(dict(url='/activate/overview')))
        else:
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(dict(url='')))


class ActivateOverviewHandler(SessionRequestHandler):
    def get(self):
        invoice_key = self.session.get('activation-invoice-key')
        invoice = db.get(db.Key(invoice_key))
        logging.info([(order.customer.first_name, order.product.title) for order in invoice.orders])
        self.render('activate_overview.html', invoice=invoice, return_url='%sactivate/complete' % (configuration.ROOT_URL,))

    def post(self):
        # A request is sent to this handler to mark the invoice as pending.
        from models import INVOICE_STATUS_PENDING
        invoice_key = self.session.get('activation-invoice-key')
        invoice = db.get(db.Key(invoice_key))
        invoice.status = INVOICE_STATUS_PENDING
        invoice.put()
        self.set_header('Content-Type', 'application/json')
        self.write(invoice.status)


class ActivateCompleteHandler(SessionRequestHandler):
    def get(self):
        self.render('activate_complete.html')


def flatten_arguments(args):
    """
    This returns a dict and hence cannot totally flatten
    the arguments list.  Ideally, one would return a list
    of 2-tuples and then urlencode that.
    """
    arguments = {}
    for k, v in args.iteritems():
        if len(v) == 1:
            arguments[k] = v[0]
        else:
            arguments[k] = v
    return arguments

class PaypalEndpoint(BaseRequestHandler):
    verify_url = configuration.PAYPAL_POST_URL
    
    def do_post(self, url, arguments):
        from google.appengine.api import urlfetch
        from urllib import urlencode
        payload = urlencode(arguments)
        logging.info(payload)
        content = urlfetch.fetch(
            url=url,
            method=urlfetch.POST,
            payload=payload
        ).content
        logging.info(content)
        return content
    
    def verify(self, data):
        arguments = {
            'cmd': '_notify-validate',
        }
        arguments.update(data)
        return self.do_post(self.verify_url, arguments) == 'VERIFIED'
        
    def post(self):
        data = flatten_arguments(self.request.arguments)
        
        if self.verify(data):
            r = self.process(data)
        else:
            r = self.process_invalid(data)
        if r:
            self.write(r)
        else:
            self.write('Nothing to see here.')
    
    def process(self, data):
        pass
    
    def process_invalid(self, data):
        pass


class PaypalIPNHandler(PaypalEndpoint):
    def process(self, data):
        from pprint import pformat
        logging.info('valid: ' + pformat(self.request.arguments))


    def process_invalid(self, data):
        from pprint import pformat
        logging.info('invalid: ' + pformat(self.request.arguments))


class UnsubscriptionHandler(SessionRequestHandler):
    def get(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            self.render('unsubscribe.html')


class DeinstallHandler(SessionRequestHandler):
    def get(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            self.render('deinstall.html')

class ProductActivationHandler(BaseRequestHandler):
    def get(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            self.render('product_activation.html')


class DeinstallPhonicaDinamagicHandler(SessionRequestHandler):
    def get(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            self.render('deinstall_phonica_dinamagic.html')


class DeinstallMathsEnglishHandler(SessionRequestHandler):
    def get(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            import random
            self.render('deinstall_maths_english.html', entry_code=random.randint(45000, 100000))


settings = {
    'debug': configuration.DEBUG,
    #'xsrf_cookies': True,
    'template_path': configuration.TEMPLATE_PATH,
}
urls = (
    (r'/', IndexHandler),
    (r'/login', LoginHandler),
    (r'/logout', LogoutHandler),
    (r'/dashboard/?', DashboardHandler),
    (r'/activate/?', ActivateHandler),
    (r'/activate/overview/?', ActivateOverviewHandler),
    (r'/activate/complete/?', ActivateCompleteHandler),
    (r'/paypal/ipn/?', PaypalIPNHandler),
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
