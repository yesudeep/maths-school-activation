#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.api import memcache
from dbhelper import serialize_entities, deserialize_entities, MAX_COUNT, CACHE_DURATION, SerializableModel
from properties import DecimalProperty
from decimal import Decimal

CURRENCY_CHOICES = (
    'AUD',
    'USD',
)

class Product(SerializableModel):
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
    