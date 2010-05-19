#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Datastore models for the application.
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
#
# Note:
# -----
# Issue these commands at the admin console to import preliminary data
#
#     > from initial_data import import_all
#     > import_all()

import configuration

from decimal import Decimal

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import memcache,users

from dbhelper import serialize_entities, deserialize_entities, MAX_COUNT, \
    CACHE_DURATION, SerializableModel
from properties import DecimalProperty, Base64Property
from countries import ISO_ALPHA_3_CODES
from currencies import ISO_4217_ALPHA_CODES
from pytz.gae import pytz

ALL_TIMEZONES = pytz.all_timezones
DEFAULT_TIMEZONE = 'UTC'

# Regional information.
AUSTRALIA_ISO_ALPHA_3_CODE = 'AUS'
NEW_ZEALAND_ISO_ALPHA_3_CODE = 'NZL'

if configuration.COUNTRY_CODE == AUSTRALIA_ISO_ALPHA_3_CODE:
    # Deployed for Australia
    DEFAULT_ISO_ALPHA_3_CODE = AUSTRALIA_ISO_ALPHA_3_CODE
    DEFAULT_CURRENCY = 'AUD'
    DEFAULT_TIMEZONE = 'Australia/Sydney'
elif configuration.COUNTRY_CODE == NEW_ZEALAND_ISO_ALPHA_3_CODE:
    # Deployed for New Zealand
    DEFAULT_ISO_ALPHA_3_CODE = NEW_ZEALAND_ISO_ALPHA_3_CODE
    DEFAULT_CURRENCY = 'NZD'
    DEFAULT_TIMEZONE = 'Pacific/Auckland'

CURRENCY_CHOICES = ISO_4217_ALPHA_CODES

PHONE_TYPE_CHOICES = (
    'mobile',
    'landline',
    'fax',
    'pager',
    'work',
    'home',
)
DEFAULT_PHONE_TYPE = 'mobile'


EMAIL_TYPE_CHOICES = (
    'personal',
    'home',
    'work',
    'primary',
    'secondary',
)
DEFAULT_EMAIL_TYPE = 'personal'


INVOICE_STATUS_DRAFT = 'draft'
INVOICE_STATUS_PENDING = 'pending'
INVOICE_STATUS_COMPLETE = 'complete'
INVOICE_STATUS_CHOICES = (
    INVOICE_STATUS_DRAFT,       # When a new invoice is generated
    INVOICE_STATUS_PENDING,     # User approved the invoice and payment is now pending.
    INVOICE_STATUS_COMPLETE,    # Invoice payment is complete.
)


# Payment Agents
PAYMENT_AGENT_PAYPAL = 'paypal'
PAYMENT_AGENT_CHARGIFY = 'chargify'
PAYMENT_AGENT_GOOGLE_CHECKOUT = 'google-checkout'
PAYMENT_AGENTS = (
    PAYMENT_AGENT_PAYPAL,
    PAYMENT_AGENT_CHARGIFY,
    PAYMENT_AGENT_GOOGLE_CHECKOUT,
)
DEFAULT_PAYMENT_AGENT = PAYMENT_AGENT_PAYPAL


VERIFICATION_STATUS_INVALID = 'invalid'
VERIFICATION_STATUS_VERIFIED = 'verified'
VERIFICATION_STATUS_UNKNOWN = 'unknown'
VERIFICATION_STATUS_CHOICES = (
    VERIFICATION_STATUS_VERIFIED,
    VERIFICATION_STATUS_INVALID,
    VERIFICATION_STATUS_UNKNOWN,
)
DEFAULT_VERIFICATION_STATUS = VERIFICATION_STATUS_UNKNOWN


def purge_db(fetch_count=1000):
    """
    Purges all model data in the datastore created using our models.
    """
    models = (
        ActivationCredentials,
        Basket,
        Customer,
        Email,
        Invoice,
        Location,
        Order,
        Phone,
        Product,
        Profile,
        Subscription,
        SubscriptionPeriod,
        Transaction,
    )
    for model in models:
        db.delete(model.all().fetch(fetch_count))


class Profile(polymodel.PolyModel):
    """
    This is a base polymodel for models that have contact information.
    Contact information is tied to this polymodel instead of
    specialized contact information (phone number, email, etc.)
    models (eg., CustomerPhoneNumber, PersonAddress, CompanyLocation)
    for each of these models that have contact information.
    """
    when_created = db.DateTimeProperty(auto_now_add=True)
    when_modified = db.DateTimeProperty(auto_now=True)


class Customer(Profile):
    """
    Customer information.

    Helps answer these questions:

    1. What is the name of the customer?
    2. When did the customer register?
    3. What orders has the customer placed?
    4. Which products does the customer use?
    5. Which invoices have been issued to a customer?

    """
    first_name = db.StringProperty(required=True)
    last_name = db.StringProperty(required=True)

    # basic-authentication credentials
    email = db.EmailProperty(required=True)
    password_hash = Base64Property(required=True)
    password_salt = Base64Property(required=True)
    should_reset_password = db.BooleanProperty(default=False)
    is_admin = db.BooleanProperty(default=False)
    timezone = db.StringProperty(choices=ALL_TIMEZONES, default=DEFAULT_TIMEZONE)

    def is_password_correct(self, password):
        """
        Determines whether the given password matches the one stored in the datastore.
        """
        from utils import hash_password
        return hash_password(password, self.password_salt) == self.password_hash


    def has_active_activation_credentials(self):
        """
        Determines whether the customer has active activation credentials
        that have not been deactivated previously.
        """
        active_credentials = ActivationCredentials.get_all_active_for_customer(self)
        return len(active_credentials) > 0


class Phone(SerializableModel):
    """
    Records phone numbers belonging to a profile.
    """
    profile = db.ReferenceProperty(Profile, collection_name='phones')
    phone_type = db.StringProperty(choices=PHONE_TYPE_CHOICES, default=DEFAULT_PHONE_TYPE)
    number = db.StringProperty()


class Email(SerializableModel):
    """
    Records email addresses belonging to a profile.
    """
    profile = db.ReferenceProperty(Profile, collection_name='emails')
    email_type = db.StringProperty(choices=EMAIL_TYPE_CHOICES, default=DEFAULT_EMAIL_TYPE)
    email = db.EmailProperty()


class Location(SerializableModel):
    """
    Address locations.

    Helps locate a customer.
    """
    profile = db.ReferenceProperty(Profile, collection_name='locations')
    state_or_province = db.StringProperty()
    area_or_suburb = db.StringProperty()
    street_name = db.StringProperty()
    zip_code = db.StringProperty()
    city = db.StringProperty()
    country = db.StringProperty(choices=ISO_ALPHA_3_CODES, default=DEFAULT_ISO_ALPHA_3_CODE)


class Product(polymodel.PolyModel):
    """
    Product information.

    A product can be one of two types based on its atomicity.
    
    1. Unit
    2. Basket
    
    A product that can contain one or more atomic products is called a Basket
    (see model class below).  A product that is atomic, indivisible, and
    cannot contain other products is called a Unit--even though the term "Unit"
    is never used as a model identifier, it is used as convention throughout
    the code.

    Helps answer these questions:

    1. What is the title and subtitle of the product?
    2. What describes the product?
    3. What image/icon represents this product?

    """
    title = db.StringProperty()
    subtitle = db.StringProperty()
    description = db.TextProperty()
    icon_url = db.URLProperty()
    display_rank = db.IntegerProperty()

    when_created = db.DateTimeProperty(auto_now_add=True)
    when_modified = db.DateTimeProperty(auto_now=True)
    is_deleted = db.BooleanProperty(default=False)


    @property
    def baskets(self):
        """
        Returns all the Basket entities that this product belongs to.
        """
        return Basket.gql('WHERE product_keys = :1', self.key())


    @classmethod
    def get_all(cls, count=MAX_COUNT):
        """
        Override.
        """
        cache_key = '%s.get_all()' % (cls.__name__,)
        entities = deserialize_entities(memcache.get(cache_key))
        if not entities:
            entities = db.GqlQuery('SELECT * FROM %s' % cls.__name__).fetch(count)
            memcache.set(cache_key, serialize_entities(entities), CACHE_DURATION)
        return entities


    def __unicode__(self):
        return self.title + ', ' + self.subtitle + '(id: ' + unicode(self.key().id()) + ')'


    def __str__(self):
        return self.__unicode__()


class Basket(Product):
    """
    Basket is a collective product that contains other products
    and has its own subscriptions.  A product, however, can belong
    to multiple baskets, hence, we store a list of keys belonging
    to each product contained by the basket.

    The polymodel inheritance allows a basket to:

    1. be a product itself.
    2. contain products.
    3. contain other baskets.

    Helps answer these questions:

    1. Which products are contained by this basket?

    Other questions mentioned in the Product model are also included.

    """
    product_keys = db.ListProperty(db.Key)


    @property
    def products(self):
        """
        Returns a list of member products based on the product_keys property.
        """
        return db.get(self.product_keys)


    def has_product(self, product):
        """
        Determines whether a product belongs to this basket.
        """
        return product.key() in self.product_keys


class Subscription(SerializableModel):
    """
    Subscription options available per product for the customer:

        1. Monthly
        2. Quarterly
        3. Half yearly
        4. Yearly

    Helps answer these questions:

    1. Which product is being offered under this subscription?
    2. What is the subscription price?
    3. What is the recurring payment period of the subscription?
    4. What is the general sales tax and currency?
    5. Which orders have been placed by customers to use this subscription?  (foreign relationship)

    This information is filled in by administrators.
    The same number of subscriptions with the same durations must be present for all the products
    for the current system to work.
    """
    product = db.ReferenceProperty(Product, collection_name='subscriptions')
    price = DecimalProperty()
    general_sales_tax = DecimalProperty()
    currency = db.StringProperty(choices=CURRENCY_CHOICES, default=DEFAULT_CURRENCY)
    period_in_months = db.IntegerProperty()
    
    # Can't have this here.  Blame paypal.
    #free_period_in_months = db.IntegerProperty(default=0)


    @classmethod
    def get_by_product_and_period(cls, product, period_in_months):
        """
        Fetches a subscription for the given product and period in months.
        """
        cache_key = str(product.key()) + str(period_in_months)
        subscription = deserialize_entities(memcache.get(cache_key))
        if not subscription:
            subscription = Subscription.all() \
                .filter('product = ', product) \
                .filter('period_in_months = ', period_in_months) \
                .get()
            memcache.set(cache_key, serialize_entities(subscription), CACHE_DURATION)
        return subscription


    def __unicode__(self):
        return unicode(self.product) + ', period (months): ' + unicode(self.period_in_months)


    def __str__(self):
        return self.__unicode__()



class SubscriptionPeriod(SerializableModel):
    """
    Subscription periods for the dropdown choice menu.

    (Static data model)
    
    IMPORTANT NOTE:
        Paypal's subscription buttons don't let us split subscriptions
        based on products, so we wind up clubbing the subscriptions
        and feeding Paypal the sum total price.  This, however, means that
        the customer will have to choose one of the subscription periods
        for ALL the selected products during one activation session. 
        
        This also implies that if you add a new subscription period
        you will need to ensure subscriptions with this period exist for 
        ALL the existing customer-selectable products.
        
        For example:
        
        If you have 6 products and 3 subscription periods, the number
        of subscriptions will be 6 * 3 = 18.  If you add another subscription
        period, you will need to add subscriptions with that period for each
        of those 6 products.  So, 6 * 4 = 24 subscriptions must exist.
        
        (Tricky and kludgy.  Yeah, I know.  Blame Paypal.)
    """
    period_in_months = db.IntegerProperty()
    title = db.StringProperty()
    
    # Blame paypal.
    free_period_in_months = db.IntegerProperty()

    
    @classmethod
    def get_by_period(cls, period_in_months):
        """
        Fetches a subscription period entity for the given period in months.
        """
        cache_key = unicode(period_in_months)
        subscription_period = deserialize_entities(memcache.get(cache_key))
        if not subscription_period:
            subscription_period = SubscriptionPeriod.all() \
                .filter('period_in_months = ', period_in_months) \
                .get()
            memcache.set(cache_key, serialize_entities(subscription_period), CACHE_DURATION)
        return subscription_period


    @classmethod
    def get_all(cls, count=MAX_COUNT):
        """
        Override.
        """
        cache_key = '%s.get_all()' % (cls.__name__,)
        entities = deserialize_entities(memcache.get(cache_key))
        if not entities:
            entities = SubscriptionPeriod.all().order('period_in_months').fetch(count)
            memcache.set(cache_key, serialize_entities(entities), CACHE_DURATION)
        return entities


class Invoice(SerializableModel):
    """
    Maintains invoice information for orders placed by customers.

    Helps answer these questions:

    1. What was the total price of the invoice?
    2. Who was the customer?
    3. What currency was used for invoicing?
    4. What was ordered by the customer?
    5. When was the invoice generated?
    6. How many and which transactions were used to satisfy payment for this invoice?

    """
    customer = db.ReferenceProperty(Customer, collection_name='invoices')
    total_price = DecimalProperty()
    currency = db.StringProperty(choices=CURRENCY_CHOICES, default=DEFAULT_CURRENCY)
    status = db.StringProperty(choices=INVOICE_STATUS_CHOICES, default=INVOICE_STATUS_DRAFT)
    status_reason = db.StringProperty()


class Transaction(SerializableModel):
    """
    Records transaction information obtained during the life of
    a transaction including completion codes and response information
    from a payment gateway.

    Helps answer these questions:

    1. Was the transaction successful?
    2. What was the currency used for the transaction?
    3. Who did the transaction?  (Linked via invoice)
    4. What payment agent/gateway was used for the transaction?
    5. When did this transaction occur?
    6. What was the total amount of the transaction as received in the response
       from the payment agent?

    """
    identifier = db.StringProperty()
    subscription_id = db.StringProperty()
    transaction_type = db.StringProperty()

    currency = db.StringProperty(choices=CURRENCY_CHOICES, default=DEFAULT_CURRENCY)
    amount = DecimalProperty()
    # TODO: when_completed = db.DateTimeProperty()
    payment_agent = db.StringProperty(choices=PAYMENT_AGENTS, default=DEFAULT_PAYMENT_AGENT)

    invoice = db.ReferenceProperty(Invoice, collection_name='transactions')
    verification_status = db.StringProperty(choices=VERIFICATION_STATUS_CHOICES, default=DEFAULT_VERIFICATION_STATUS)
    data = db.TextProperty()


class Order(SerializableModel):
    """
    Subscription orders
    Helps answer these questions:

    1. What product was sold to which customer?
    2. Which invoice does an order belong to?
    3. At what price was the product sold to the customer?
    4. Which orders does a subscription have?  How many users chose to pay for 3 months, 1 year, half yearly, etc?
    5. Which subscription does this order belong to?

    """
    subscription = db.ReferenceProperty(Subscription, collection_name='orders')
    customer = db.ReferenceProperty(Customer, collection_name='orders')
    invoice = db.ReferenceProperty(Invoice, collection_name='orders')

    subscription_price = DecimalProperty()
    subscription_general_sales_tax = DecimalProperty()
    subscription_period_in_months = db.IntegerProperty()
    subscription_free_period_in_months = db.IntegerProperty()
    subscription_currency = db.StringProperty(choices=CURRENCY_CHOICES, default=DEFAULT_CURRENCY)

    # Subscription price + subscription gst.
    price = DecimalProperty()


class ActivationCredentials(SerializableModel):
    """
    Activation credentials for a product that are stored per order.

    Helps answer these questions:

    1. What activation information was provided by the customer?
    2. Which order does this activation information belong to?
    3. Which product does this activation information apply to?
    4. Which customer provided this activation information? (via order.customer)

    """
    serial_number = db.StringProperty()
    machine_id = db.StringProperty()
    activation_code = db.StringProperty()
    
    deactivation_code = db.StringProperty()
    when_deactivated = db.DateTimeProperty()
    deactivation_entry_code = db.StringProperty()
    
    
    # Here product is always a unit never a basket.
    product = db.ReferenceProperty(Product, collection_name='activation_credentials')
    order = db.ReferenceProperty(Order, collection_name='activation_credentials')
    
    # Recording customer here is redundant as we can get it from order,
    # BUT this allows us to build an index on this and the machine_id fields
    # for the get_all_for_customer_and_machine_id routine.
    customer = db.ReferenceProperty(Customer, collection_name='activation_credentials')
    
    @classmethod
    def get_all_for_customer_and_machine_id(cls, customer, machine_id, count=MAX_COUNT):
        """
        Obtains a list of all the activation credentials for a given customer
        and machine ID.
        """
        cache_key = unicode(customer.key()) + machine_id
        entities = deserialize_entities(memcache.get(cache_key))
        if not entities:
            entities = ActivationCredentials.all() \
                .filter('customer = ', customer) \
                .filter('machine_id = ', machine_id) \
                .fetch(count)
            memcache.set(cache_key, serialize_entities(entities), CACHE_DURATION)
        return entities

    @classmethod
    def get_all_active_for_customer_and_machine_id(cls, customer, machine_id, count=MAX_COUNT):
        """
        Obtains a list of all the active activation credentials for a given customer
        and machine ID.
        """
        cache_key = unicode(customer.key()) + 'all_active_for_customer'
        entities = deserialize_entities(memcache.get(cache_key))
        if not entities:
            entities = ActivationCredentials.all() \
                .filter('customer = ', customer) \
                .filter('machine_id = ', machine_id) \
                .filter('deactivation_code = ', None) \
                .filter('activation_code != ', None) \
                .fetch(count)
            memcache.set(cache_key, serialize_entities(entities), CACHE_DURATION)
        return entities    

    @classmethod
    def get_all_active_for_customer(cls, customer, count=MAX_COUNT):
        """
        Obtains all the active activation credentials which have an activation
        code but do not have a deactivation code, which essentially means
        the customer will have these products activated but not deinstalled them
        as per the Website.
        """
        cache_key = unicode(customer.key()) + 'all_active_for_customer'
        entities = deserialize_entities(memcache.get(cache_key))
        if not entities:
            entities = ActivationCredentials.all() \
                .filter('customer = ', customer) \
                .filter('deactivation_code = ', None) \
                .filter('activation_code != ', None) \
                .fetch(count)
            memcache.set(cache_key, serialize_entities(entities), CACHE_DURATION)
        return entities

    def __unicode__(self):
        return unicode(self.product) + ', SN: ' + self.serial_number + ', MID: ' + self.machine_id


    def __str__(self):
        return self.__unicode__()

