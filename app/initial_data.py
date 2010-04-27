
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
        dict(title="Maths Story",
            subtitle="Junior",
            icon_url="image/icon/128x128/cd_blue.png",
            display_rank = 1),
        dict(title="Maths Story",
            subtitle="Primary",
            icon_url="image/icon/128x128/cd_blue.png",
            display_rank = 2),
        dict(title="Maths Story",
            subtitle="Senior",
            icon_url="image/icon/128x128/cd_blue.png",
            display_rank = 3),
        dict(title="English Story",
            subtitle="English",
            icon_url="image/icon/128x128/cd_green.png",
            display_rank = 4),
        dict(title="Phonica",
            subtitle="Elementary English",
            icon_url="image/icon/128x128/cd_green.png",
            display_rank = 5),
        dict(title="Phonica",
            subtitle="Advanced English",
            icon_url="image/icon/128x128/cd_green.png",
            display_rank = 6),
        dict(title="Dinamagic",
            subtitle="Mathematics",
            icon_url="image/icon/128x128/cd_blue.png",
            display_rank = 7),
    )
    subscriptions = (
        dict(price=Decimal("29.0"),
            general_sales_tax=Decimal("0.95"),
            duration_in_months=1,
            ),
        dict(price=Decimal("49.0"),
            general_sales_tax=Decimal("0.95"),
            duration_in_months=3,
            ),
        dict(price=Decimal("149.0"),
            general_sales_tax=Decimal("0.95"),
            duration_in_months=12,
            ),
    )
    products = []
    for p in products_list:
        p['icon_url'] = MEDIA_URL + p['icon_url']
        products.append(Product(**p))
    db.put(products)

    subscriptions_list = []
    for product in products:
        for subscription in subscriptions:
            subscription['product'] = product
            subscriptions_list.append(Subscription(**subscription))
    db.put(subscriptions_list)

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

