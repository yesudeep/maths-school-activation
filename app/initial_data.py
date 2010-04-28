#!/usr/bin/env python
# -*- coding: utf-8 -8-
# Initial data to be imported.
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
#
# Note:
# -----
# Issue these commands at the admin console to import preliminary data
#
#     > from initial_data import import_all
#     > import_all()

import configuration

from google.appengine.api import memcache
from google.appengine.ext import db
from models import Product, Customer, Subscription
from decimal import Decimal

from configuration import MEDIA_URL as media_url

MEDIA_URL = media_url
if MEDIA_URL.startswith('/'):
    MEDIA_URL = "http://%s:%s" % (configuration.SERVER_NAME, configuration.SERVER_PORT) + MEDIA_URL

def import_all():
    import_products()
    import_customers()

def import_products():
    products_list = (    
        dict(title="All Maths",
            subtitle="Product collection",
            icon_url="image/icon/128x128/cd_bunch.png",
            display_rank=1),
        dict(title="All Maths + English",
            subtitle="Product collection",
            icon_url="image/icon/128x128/cd_bunch.png",
            display_rank=2),
        dict(title="Maths Story",
            subtitle="Junior",
            icon_url="image/icon/128x128/cd_blue.png",
            display_rank=3),
        dict(title="Maths Story",
            subtitle="Primary",
            icon_url="image/icon/128x128/cd_blue.png",
            display_rank=4),
        dict(title="Maths Story",
            subtitle="Senior",
            icon_url="image/icon/128x128/cd_blue.png",
            display_rank=5),
        dict(title="English Story",
            subtitle="English",
            icon_url="image/icon/128x128/cd_green.png",
            display_rank=6),
        dict(title="Phonica",
            subtitle="Elementary English",
            icon_url="image/icon/128x128/cd_green.png",
            display_rank=7),
        dict(title="Phonica",
            subtitle="Advanced English",
            icon_url="image/icon/128x128/cd_green.png",
            display_rank=8),
        dict(title="Dinamagic",
            subtitle="Mathematics",
            icon_url="image/icon/128x128/cd_blue.png",
            display_rank=9),
    )
    subscriptions_list = (
        dict(price=Decimal("29.0"),
            general_sales_tax=Decimal("0.95"),
            period_in_months=1,
            ),
        dict(price=Decimal("49.0"),
            general_sales_tax=Decimal("0.95"),
            period_in_months=3,
            ),
        dict(price=Decimal("149.0"),
            general_sales_tax=Decimal("0.95"),
            period_in_months=12,
            ),
    )

    # Batch-dump products into the datastore.
    products = []
    for p in products_list:
        p['icon_url'] = MEDIA_URL + p['icon_url']
        products.append(Product(**p))
    db.put(products)

    # Now that we have keys assigned to the products, 
    # assign to each product a bunch of subscriptions
    # and batch-dump into the datastore.
    subscriptions = []
    for product in products:
        for subscription in subscriptions_list:
            subscription['product'] = product
            subscriptions.append(Subscription(**subscription))
    db.put(subscriptions)

def import_customers():
    from utils import hash_password
    p = hash_password('example')
    customers_list = (
        dict(
            key_name='yesudeep@gmail.com',
            first_name='Yesudeep',
            last_name='Mangalapilly',
            email='yesudeep@gmail.com',
            password_hash=p[0],
            password_salt=p[1],
            ),        
        dict(
            key_name='tanuj.hattangdi@gmail.com',
            first_name='Tanuj',
            last_name='Hattangdi',
            email='tanuj.hattangdi@gmail.com',
            password_hash=p[0],
            password_salt=p[1],
            ),
        dict(
            key_name='aswad.r@gmail.com',
            first_name='Aswad',
            last_name='Rangnekar',
            email='aswad.r@gmail.com',
            password_hash=p[0],
            password_salt=p[1],            
            ),
        dict(
            key_name='dreamzr4u@gmail.com',
            first_name="Raj",
            last_name="Singh",
            email="dreamzr4u@gmail.com",
            password_hash=p[0],
            password_salt=p[1],
            ),
    )
    customers = []
    for c in customers_list:
        customers.append(Customer(**c))
    db.put(customers)

