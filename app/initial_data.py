#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from models import Product, Basket, Customer, Subscription, SubscriptionPeriod
from models import Order, ActivationCredentials, Invoice, Transaction, Location, Phone, Email, Profile
from decimal import Decimal

from configuration import MEDIA_URL as media_url

MEDIA_URL = media_url
if MEDIA_URL.startswith('/'):
    MEDIA_URL = "http://%s:%s" % (configuration.SERVER_NAME, configuration.SERVER_PORT) + MEDIA_URL


def import_all():
    """
    Imports all the initial data into the datastore.
    
    Do not call this function multiple times as the data 
    will be duplicated in the datastore.
    """
    import_products()
    import_customers()
    import_subscription_periods()


def clear_all(fetch_count=1000):
    """
    Clears all models created using the initial data.
    """
    models = (
        Customer,
        Product, 
        Subscription,
        SubscriptionPeriod
    )
    for model in models:
        db.delete(model.all().fetch(fetch_count))


def import_subscription_periods():
    subscription_periods_list = (
        dict(
            title='Monthly',
            period_in_months=1
        ),
        dict(
            title='Quarterly',
            period_in_months=3
        ),
        dict(
            title='Yearly',
            period_in_months=12
        ),
    )
    
    subscription_periods = []
    for subscription_period in subscription_periods_list:
        subscription_periods.append(SubscriptionPeriod(**subscription_period))
    db.put(subscription_periods)


def import_products():
    math_story_junior = Product(title="Maths Story",
        subtitle="Junior",
        icon_url=MEDIA_URL + "image/icon/128x128/cd_blue.png",
        display_rank=3)
    math_story_primary = Product(title="Maths Story",
        subtitle="Primary",
        icon_url=MEDIA_URL + "image/icon/128x128/cd_blue.png",
        display_rank=4)
    math_story_senior = Product(title="Maths Story",
        subtitle="Senior",
        icon_url=MEDIA_URL + "image/icon/128x128/cd_blue.png",
        display_rank=5)
    english_story = Product(title="English Story",
        subtitle="English",
        icon_url=MEDIA_URL + "image/icon/128x128/cd_green.png",
        display_rank=6)
    
    products = [math_story_junior, math_story_primary, math_story_senior, english_story]
    db.put(products)

    baskets = (
        Basket(
            title='All Maths',
            subtitle='Product collection',
            icon_url=MEDIA_URL + 'image/icon/128x128/cd_bunch.png',
            display_rank=0,
            product_keys=[math_story_junior.key(), math_story_primary.key(), math_story_senior.key()]
        ),
        Basket(
            title='All Maths + English',
            subtitle='Product collection',
            icon_url=MEDIA_URL + 'image/icon/128x128/cd_bunch.png',
            display_rank=0,
            product_keys=[math_story_junior.key(), math_story_primary.key(), math_story_senior.key(), english_story.key()]
        ),
    )
    db.put(baskets)

    subscriptions_list = (
        dict(price=Decimal("29.0"),
            general_sales_tax=Decimal("0.95"),
            period_in_months=1,
            ),
        dict(price=Decimal("49.0"),
            general_sales_tax=Decimal("0.95"),
            period_in_months=3,
            free_period_in_months=1,
            ),
        dict(price=Decimal("149.0"),
            general_sales_tax=Decimal("0.95"),
            period_in_months=12,
            free_period_in_months=2,
            ),
    )

    # Now that we have keys assigned to the products, 
    # assign to each product a bunch of subscriptions
    # and batch-dump into the datastore.
    subscriptions = []
    for product in products:
        for subscription in subscriptions_list:
            subscription['product'] = product
            subscriptions.append(Subscription(**subscription))
    for basket in baskets:
        for subscription in subscriptions_list:
            subscription['product'] = basket
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

