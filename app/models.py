#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import memcache,users
from dbhelper import serialize_entities, deserialize_entities, MAX_COUNT, CACHE_DURATION, SerializableModel
from properties import DecimalProperty, Base64Property
from decimal import Decimal

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
    """Records the address of a customer."""
    profile = db.ReferenceProperty(Profile, collection_name='locations')
    state_or_province = db.StringProperty()
    area_or_suburb = db.StringProperty()
    street_name = db.StringProperty()
    zip_code = db.StringProperty()
    city = db.StringProperty()
    country = db.StringProperty()


class Product(SerializableModel):
    """
    Product information.

    Helps answer these questions:

    1. What is the title and subtitle of the product?
    2. What describes the product?
    3. How much is the up-front sales price of the product?
    4. How much is the up-front sales tax applied?
    5. What currency is in use?
    6. How much is the *monthly* billing price for the product?
    7. How much sales tax will be applied on the billing price?
    8. What image/icon represents this product?

    Developer's Note:
    -----------------
    Kindly issue these commands at the admin console to import preliminary data

        > from initial_data import import_all
        > import_all()

    """
    title = db.StringProperty()
    subtitle = db.StringProperty()
    description = db.TextProperty()
    #up_front_price = DecimalProperty()
    #up_front_gst = DecimalProperty()
    billing_price = DecimalProperty()
    billing_gst = DecimalProperty()
    currency = db.StringProperty(choices=CURRENCY_CHOICES, default=DEFAULT_CURRENCY)
    icon_url = db.URLProperty()


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
    #when_completed = db.DateTimeProperty()
    payment_agent = db.StringProperty(choices=PAYMENT_AGENTS, default=DEFAULT_PAYMENT_AGENT)

    invoice = db.ReferenceProperty(Invoice, collection_name='transactions')
    verification_status = db.StringProperty(choices=VERIFICATION_STATUS_CHOICES, default=DEFAULT_VERIFICATION_STATUS)
    data = db.TextProperty()


class Order(SerializableModel):
    """
    Activation order
    Helps answer these questions:

    1. What product was sold to which customer?
    2. Which invoice does an order belong to?
    3. At what price was the product sold to the customer?

    """
    product = db.ReferenceProperty(Product, collection_name='orders')
    customer = db.ReferenceProperty(Customer, collection_name='orders')
    invoice = db.ReferenceProperty(Invoice, collection_name='orders')

    #up_front_price = DecimalProperty()
    #up_front_gst = DecimalProperty()
    billing_price = DecimalProperty()
    billing_gst = DecimalProperty()
    total_price = DecimalProperty()
    currency = db.StringProperty(choices=CURRENCY_CHOICES, default=DEFAULT_CURRENCY)

    serial_number = db.StringProperty()
    machine_id = db.StringProperty()
    activation_code = db.StringProperty()

