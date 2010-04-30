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

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import memcache,users
from dbhelper import serialize_entities, deserialize_entities, MAX_COUNT, CACHE_DURATION, SerializableModel
from properties import DecimalProperty, Base64Property
from decimal import Decimal
from countries import ISO_ALPHA_3_CODES

AUSTRALIA_ISO_ALPHA_3_CODE = 'AUS'
DEFAULT_ISO_ALPHA_3_CODE = AUSTRALIA_ISO_ALPHA_3_CODE

CURRENCY_CHOICES = (
    'AUD',
    'USD',
)
DEFAULT_CURRENCY = 'AUD'

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


#PRODUCT_TYPE_UNIT = 'unit'        # A single atomic product unit.
#PRODUCT_TYPE_BASKET = 'basket'    # A basket collection of products.
#PRODUCT_TYPE_CHOICES = (
#    PRODUCT_TYPE_UNIT,
#    PRODUCT_TYPE_BASKET,
#)
#DEFAULT_PRODUCT_TYPE = PRODUCT_TYPE_UNIT


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

    def is_password_correct(self, password):
        from utils import hash_password
        return hash_password(password, self.password_salt) == self.password_hash


class Phone(SerializableModel):
    """Records phone/mobile number of a customer"""
    profile = db.ReferenceProperty(Profile, collection_name='phones')
    phone_type = db.StringProperty(choices=PHONE_TYPE_CHOICES, default=DEFAULT_PHONE_TYPE)
    number = db.StringProperty()


class Email(SerializableModel):
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

    #product_type = db.StringProperty(choices=PRODUCT_TYPE_CHOICES, default=DEFAULT_PRODUCT_TYPE)
    #basket = db.SelfReferenceProperty(Product, collection_name='products')

    @property
    def baskets(self):
        return Basket.gql('WHERE products = :1', self.key())

    @classmethod
    def get_all(cls, count=MAX_COUNT):
        cache_key = '%s.get_all()' % (cls.__name__,)
        entities = deserialize_entities(memcache.get(cache_key))
        if not entities:
            entities = db.GqlQuery('SELECT * FROM %s' % cls.__name__).fetch(count)
            memcache.set(cache_key, serialize_entities(entities), CACHE_DURATION)
        return entities


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
    products = db.ListProperty(db.Key)


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
    subscription_total_price = DecimalProperty()
    subscription_currency = db.StringProperty(choices=CURRENCY_CHOICES, default=DEFAULT_CURRENCY)


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

    product = db.ReferenceProperty(Product, collection_name='activation_credentials')
    order = db.ReferenceProperty(Order, collection_name='activation_credentials')
