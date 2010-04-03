#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import memcache,users
from dbhelper import serialize_entities, deserialize_entities, MAX_COUNT, CACHE_DURATION, SerializableModel
from properties import DecimalProperty
from decimal import Decimal

CURRENCY_CHOICES = (
    'AUD',
    'USD',
)
PHONE_NUMBER_TYPE_CHOICES = (
    'Mobile',
    'Phone',
)
TRANSACTION_MODES = (
    'direct',
    'online',        
)
PAYMENT_AGENT = (
    'paypal',
    'chargify',
    'google-checkout',
)

class Profile(polymodel.PolyModel):
    user = db.UserProperty(auto_current_user_add=True)    
    
class Customer(Profile):
    first_name = db.StringProperty(required=True)
    last_name = db.StringProperty(required=True)
    email = db.EmailProperty(required=True)
    password = db.StringProperty(required=True)
    
class PhoneNumber(db.Model):
    """Records phonenumber/mobile of a customer"""  
    profile = db.ReferenceProperty(Profile, collection_name='phone_numbers')
    phone_type = db.StringProperty(choices = PHONE_NUMBER_TYPE_CHOICES)
    phone_number = db.StringProperty()

class Location(db.Model):
    """Records the address of a customer."""
    profile = db.ReferenceProperty(Profile, collection_name='locations')    
    state_or_town = db.StringProperty()
    suburb = db.StringProperty()
    street_name = db.StringProperty()
    postal_code = db.PostalAddressProperty()
    
class ActiveProducts(db.Model):
    """each entity as active product"""   
    title = db.StringProperty()
    subtitle = db.StringProperty()
    up_front_price = DecimalProperty()
    up_front_currency = db.StringProperty(choices=CURRENCY_CHOICES, default='AUD')
    up_front_gst = DecimalProperty()
    up_front_gst_currency = db.StringProperty(choices=CURRENCY_CHOICES, default='AUD')
    billing_price = DecimalProperty()
    billing_currency = db.StringProperty(choices=CURRENCY_CHOICES, default='AUD')
    billing_gst = DecimalProperty()
    billing_gst_currency = db.StringProperty(choices=CURRENCY_CHOICES, default='AUD')
    icon_url = db.URLProperty()
    
class CustomerActivatedProducts(db.Model):
    """Records all the active products of a customer."""
    profile = db.ReferenceProperty(Profile, collection_name='active_products')
    active_products = db.ReferenceProperty(ActiveProducts, collection_name='customer_active_products') 

"""Models ahead for billing log purpose"""    
class Product(SerializableModel):
    """Displays all the products on Activate Products Page. Use dbhelper.py to import the initial data"""
    title = db.StringProperty()
    subtitle = db.StringProperty()
    up_front_price = DecimalProperty()
    up_front_currency = db.StringProperty(choices=CURRENCY_CHOICES, default='AUD')
    up_front_gst = DecimalProperty()
    up_front_gst_currency = db.StringProperty(choices=CURRENCY_CHOICES, default='AUD')
    billing_price = DecimalProperty()
    billing_currency = db.StringProperty(choices=CURRENCY_CHOICES, default='AUD')
    billing_gst = DecimalProperty()
    billing_gst_currency = db.StringProperty(choices=CURRENCY_CHOICES, default='AUD')
    icon_url = db.URLProperty()


class Order(SerializableModel):
    product = db.ReferenceProperty(Product, collection_name='orders')
    customer = db.ReferenceProperty(Customer, collection_name='orders')
    invoice = db.ReferenceProperty(Invoice, collection_name='orders')

  
class Transaction(SerializableModel):
    code = db.StringProperty()
    when_transacted = db.DateTimeProperty()
    invoice = db.ReferenceProperty(Invoice, collection_name='transactions')
    mode = db.StringProperty(choices=TRANSACTION_MODES, default='online')
    agent = db.StringProperty(choices=PAYMENT_AGENT, default='chargify')


class Invoice(SerializableModel):    
    code = db.StringProperty()
    
