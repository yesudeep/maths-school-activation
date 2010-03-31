#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.api import memcache
from dbhelpers import serialize_entities, deserialize_entities, MAX_COUNT, CACHE_DURATION, SerializableModel
from properties import DecimalProperty
from decimal import Decimal

CURRENCY_CHOICES = (
    'AUD',
    'USD',
)

class Product(SerializableModel):
    title = db.StringProperty()
    subtitle = db.StringProperty()
    subscription_price = DecimalProperty()
    subscription_currency = db.StringProperty(choices=CURRENCY_CHOICES, default='AUD')
    