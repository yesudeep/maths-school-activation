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
from utils import SessionRequestHandler, BaseRequestHandler, hash_password
from models import Product, Customer, Invoice, Order, Phone, Location, \
    Subscription, Basket, ActivationCredentials, SubscriptionPeriod
from models import VERIFICATION_STATUS_INVALID, VERIFICATION_STATUS_VERIFIED
from models import INVOICE_STATUS_PENDING, INVOICE_STATUS_COMPLETE

try:
    import json
except ImportError:
    from django.utils import simplejson as json

logging.basicConfig(level=logging.DEBUG)

LOGIN_PAGE_URL = '/'


COUNTRIES_TUPLE = (
    ('AUS', 'Australia'),
    ('NZL', 'New Zealand'),
    ('SGP', 'Singapore'),
    ('ZAF', 'South Africa'),
)


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
            customer = Customer.get_by_key_name(self.get_current_username())

            landline = Phone.all().filter('profile = ', customer).filter('phone_type = ', 'landline').get()
            mobile = Phone.all().filter('profile = ', customer).filter('phone_type = ', 'mobile').get()

            self.render('profile.html', countries=COUNTRIES_TUPLE,
                landline=landline,
                mobile=mobile,
                customer=customer,
                location=customer.locations[0])

    def post(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            customer = Customer.get_by_key_name(self.get_current_username())
            customer.first_name = self.get_argument('first_name')
            customer.last_name = self.get_argument('last_name')

            landline_key = self.get_argument('landline_key')
            landline = db.get(db.Key(landline_key))
            landline.number = self.get_argument('landline_number')

            mobile_key = self.get_argument('mobile_key')
            mobile = db.get(db.Key(mobile_key))
            mobile.number = self.get_argument('mobile_number')

            location_key = self.get_argument('location_key')
            location = db.get(db.Key(location_key))

            location.city = self.get_argument('city')
            location.country = self.get_argument('country')
            location.state_or_province = self.get_argument('state_or_province')
            location.area_or_suburb = self.get_argument('area_or_suburb')
            location.street_name = self.get_argument('street_name')
            location.zip_code = self.get_argument('zip_code')

            db.put([customer, mobile, landline, location])

            self.get()


class RegistrationHandler(SessionRequestHandler):
    def get(self):
        if not self.is_logged_in():
            self.render('register.html', countries=COUNTRIES_TUPLE)

    def post(self):
        first_name = self.get_argument('first_name')
        last_name = self.get_argument('last_name')
        email = self.get_argument('email')
        password = self.get_argument('password')
        landline_number = self.get_argument('landline_number')
        mobile_number = self.get_argument('mobile_number')
        country = self.get_argument('country')
        city = self.get_argument('city')
        state_or_province = self.get_argument('state_or_province')
        area_or_suburb = self.get_argument('area_or_suburb')
        street_name = self.get_argument('street_name')
        zip_code = self.get_argument('zip_code')

        p = hash_password(password)

        customer = Customer(key_name=email,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            password_hash=p[0],
                            password_salt=p[1])

        #TODO: before saving the profile check if the data is not repeated
        db.put(customer)

        landline = Phone(phone_type='landline',
                         number=landline_number,
                         profile=customer)

        mobile = Phone(phone_type='mobile',
                       number=mobile_number,
                       profile=customer)

        location = Location(state_or_province=state_or_province,
                           area_or_suburb=area_or_suburb,
                           street_name=street_name,
                           zip_code=zip_code,
                           country=country,
                           city=city,
                           profile=customer)

        db.put([location, mobile, landline])

        self.do_login(email)
        self.redirect('/dashboard')


class DashboardHandler(SessionRequestHandler):
    def get(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            customer = Customer.get_by_key_name(self.get_current_username())
            self.render('dashboard.html', customer=customer)


class SelectProductsHandler(SessionRequestHandler):
    def get(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            from models import SubscriptionPeriod
            products = Product.get_all()
            subscription_periods = SubscriptionPeriod.get_all()
            self.render('select_products.html',
                products=products,
                subscription_periods=subscription_periods)

    def post(self):
        subscription_data = json.loads(self.get_argument('payload'))
        logging.info(subscription_data)

        self.set_header('Content-Type', 'application/json')
        if subscription_data:
            products = subscription_data.get('products')
            subscription_data['products'] = products.keys()
            logging.info(subscription_data)
            self.session['subscription-data'] = subscription_data
            self.write(json.dumps(dict(url='/activate/credentials')))
        else:
            self.write(json.dumps(dict(url='')))


"""
class ActivateHandler(SessionRequestHandler):
    def post(self):
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
"""

class ActivationCredentialsInputHandler(SessionRequestHandler):
    def get(self):
        subscription_data = self.session['subscription-data']
        products = db.get([db.Key(key) for key in subscription_data.get('products')])
        units = [product for product in products if 'product_keys' not in product.properties()]
        baskets = [product for product in products if 'product_keys' in product.properties()]

        logging.info(baskets)
        logging.info(units)

        self.render('activation_credentials_input.html', products=products, units=units, baskets=baskets)

    def post(self):
        # Get customer and create an invoice.
        customer = Customer.get_by_key_name(self.get_current_username())
        invoice = Invoice(customer=customer)
        invoice.put()

        # Now start processing subscription data.
        subscription_data = self.session['subscription-data']
        products = db.get([db.Key(key) for key in subscription_data.get('products')])
        period = subscription_data.get('period')
        subscription_period = SubscriptionPeriod.get_by_period(period)

        units = [product for product in products if 'product_keys' not in product.properties()]
        baskets = [product for product in products if 'product_keys' in product.properties()]

        activation_credentials_list = []
        orders = []
        for unit in units:
            subscription = Subscription.get_by_product_and_period(unit, period)

            order = Order(customer=customer, invoice=invoice, subscription=subscription)
            order.subscription_price = subscription.price
            order.subscription_general_sales_tax = subscription.general_sales_tax
            order.subscription_period_in_months = subscription.period_in_months
            order.subscription_free_period_in_months = subscription_period.free_period_in_months
            order.price = subscription.price + subscription.general_sales_tax
            orders.append(order)
            order.put()

            unit_id = unit.key().id()
            activation_credentials = ActivationCredentials()
            activation_credentials.serial_number = self.get_argument('u_%d_serial_number' % unit_id)
            activation_credentials.machine_id = self.get_argument('u_%d_machine_id' % unit_id)
            activation_credentials.order = order
            activation_credentials.product = unit
            logging.info(activation_credentials)
            activation_credentials_list.append(activation_credentials)

        for basket in baskets:
            subscription = Subscription.get_by_product_and_period(basket, period)

            order = Order(customer=customer, invoice=invoice, subscription=subscription)
            order.subscription_price = subscription.price
            order.subscription_general_sales_tax = subscription.general_sales_tax
            order.subscription_period_in_months = subscription.period_in_months
            order.subscription_free_period_in_months = subscription_period.free_period_in_months
            order.price = subscription.price + subscription.general_sales_tax
            orders.append(order)
            order.put()

            for unit in basket.products:
                basket_id = basket.key().id()
                unit_id = unit.key().id()

                activation_credentials = ActivationCredentials()
                activation_credentials.serial_number = self.get_argument('b_%d_u_%d_serial_number' % (basket_id, unit_id,))
                activation_credentials.machine_id = self.get_argument('b_%d_u_%d_machine_id' % (basket_id, unit_id,))
                activation_credentials.order = order
                activation_credentials.product = unit
                logging.info(activation_credentials)
                activation_credentials_list.append(activation_credentials)

        db.put(activation_credentials_list)
        
        invoice.total_price = sum([order.price for order in orders])
        invoice.currency = orders[0].subscription_currency
        invoice.put()
        
        self.session['activation-invoice-key'] = str(invoice.key())
        self.redirect('/activate/overview')


class ActivateOverviewHandler(SessionRequestHandler):
    def get(self):
        invoice_key = self.session.get('activation-invoice-key')
        invoice = db.get(db.Key(invoice_key))
        
        subscription_data = self.session['subscription-data']
        subscription_period = SubscriptionPeriod.get_by_period(subscription_data.get('period'))
        
        logging.info([(order.customer.first_name, unicode(order.subscription)) for order in invoice.orders])
        self.render('activate_overview.html', 
            subscription_period=subscription_period, 
            invoice=invoice, 
            return_url='%sactivate/complete' % (configuration.ROOT_URL,)
            )

    def post(self):
        # A request is sent to this handler to mark the invoice as pending.
        invoice_key = self.session.get('activation-invoice-key')
        invoice = db.get(db.Key(invoice_key))
        invoice.status = INVOICE_STATUS_PENDING
        invoice.put()
        self.set_header('Content-Type', 'application/json')
        self.write(invoice.status)


class ActivateCompleteHandler(SessionRequestHandler):
    def get(self):
        self.render('activate_complete.html')


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


class ChangePasswordHandler(SessionRequestHandler):
    def get(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            self.render('change_password.html')

    def post(self):
        if not self.is_logged_in():
            self.redirect(LOGIN_PAGE_URL)
        else:
            customer = Customer.get_by_key_name(self.get_current_username())
            if customer.is_password_correct(self.get_argument('old_password')):
                p = hash_password(self.get_argument('new_password'))
                customer.password_hash = p[0]
                customer.password_salt = p[1]
                customer.put()
            self.redirect('/dashboard')


class CheckActivationCodeGenerationHandler(BaseRequestHandler):
    def get(self):
        self.render('check_activation_code_generation.html')

    def post(self):
        from activation import calculate_activation_code
        serial_number = self.get_argument('serial_number')
        machine_id = self.get_argument('machine_id')

        logging.info(serial_number)
        logging.info(machine_id)

        if 'a_base' in self.request.arguments:
            a_base = int(self.get_argument('a_base'), 10)
        else:
            a_base = None
        activation_code = calculate_activation_code(machine_id, serial_number, a_base)
        self.set_header('Content-Type', 'text/plain')
        self.write(activation_code)


#------------------------------------------------------------------------------
# Paypal handlers.
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
        from models import Transaction, Invoice
        from pprint import pformat

        invoice_id = data.get('invoice')
        if invoice_id:
            invoice = Invoice.get_by_id(int(invoice_id, 10))

            txn = Transaction(invoice=invoice)
            txn.identifier = data.get('txn_id')
            txn.transaction_type = data.get('txn_type')
            txn.currency = data.get('mc_currency')
            txn.amount = data.get('mc_gross', data.get('mc_amount3'))
            txn.data = pformat(data)
            txn.put()

            if self.verify(data):
                r = self.process(data, txn=txn, invoice=invoice)
            else:
                r = self.process_invalid(data, txn=txn, invoice=invoice)
            if r:
                self.write(r)
            else:
                self.write('Nothing to see here.')
        else:
            # error.  invoice id was not found.
            pass

    def process(self, data, **kwargs):
        pass

    def process_invalid(self, data, **kwargs):
        pass


class PaypalIPNHandler(PaypalEndpoint):
    def process(self, data, **kwargs):
        from pprint import pformat
        logging.info('valid: ' + pformat(self.request.arguments))

        txn = kwargs['txn']
        invoice = kwargs['invoice']

        txn.verification_status = VERIFICATION_STATUS_VERIFIED
        txn.put()

        if txn.transaction_type == 'subscr_payment':
            payment_status = data.get('payment_status')
            if payment_status == 'Pending':
                invoice.status = INVOICE_STATUS_PENDING
                invoice.status_reason = data.get('pending_reason')
                invoice.put()
            elif payment_status == 'Completed':
                if data.get('receiver_email') == configuration.PAYPAL_MERCHANT_RECEIVER_EMAIL \
                       and invoice.total_price == txn.amount \
                       and txn.currency == invoice.currency:
                    invoice.status = INVOICE_STATUS_COMPLETE
                    invoice.put()
                    # Email success and activation code.
                    from workers import WORKER_MAIL_ACTIVATION_URL
                    queue_mail_task(WORKER_MAIL_ACTIVATION_URL, 
                        params=dict(
                            invoice_key = str(invoice.key())
                        ),
                        method='POST')
                else:
                    pass
                    # Email error.


    def process_invalid(self, data, **kwargs):
        from pprint import pformat
        logging.info('invalid: ' + pformat(self.request.arguments))

        txn = kwargs['txn']
        invoice = kwargs['invoice']

        txn.verification_status = VERIFICATION_STATUS_INVALID
        txn.put()




settings = {
    'debug': configuration.DEBUG,
    #'xsrf_cookies': True,
    'template_path': configuration.TEMPLATE_PATH,
}
urls = (
    (r'/', IndexHandler),
    (r'/login', LoginHandler),
    (r'/logout', LogoutHandler),
    (r'/register/?', RegistrationHandler),
    (r'/dashboard/?', DashboardHandler),
    (r'/activate/select/?', SelectProductsHandler),
    (r'/activate/credentials/?', ActivationCredentialsInputHandler),
    (r'/activate/overview/?', ActivateOverviewHandler),
    (r'/activate/complete/?', ActivateCompleteHandler),
    (r'/paypal/ipn/?', PaypalIPNHandler),
    (r'/unsubscribe/?', UnsubscriptionHandler),
    (r'/deinstall/?', DeinstallHandler),
    (r'/profile/?', ProfileHandler),
    (r'/profile/password/change/?', ChangePasswordHandler),
    (r'/deinstall/english/phonica/?', DeinstallPhonicaDinamagicHandler),
    (r'/deinstall/mathematics/dinamagic/?', DeinstallPhonicaDinamagicHandler),
    (r'/deinstall/mathematics/junior/?', DeinstallMathsEnglishHandler),
    (r'/deinstall/mathematics/primary/?', DeinstallMathsEnglishHandler),
    (r'/deinstall/mathematics/senior/?', DeinstallMathsEnglishHandler),
    (r'/deinstall/english/story/?', DeinstallMathsEnglishHandler),

    # Admin testing pages.
    (r'/_at/check/activation/code/?', CheckActivationCodeGenerationHandler),
)
application = tornado.wsgi.WSGIApplication(urls, **settings)

def main():
    from gaefy.db.datastore_cache import DatastoreCachingShim
    DatastoreCachingShim.Install()
    run_wsgi_app(application)
    DatastoreCachingShim.Uninstall()

if __name__ == '__main__':
    main()
