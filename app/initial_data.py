
import configuration

from google.appengine.api import memcache
from google.appengine.ext import db
from models import Product, Customer
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
        dict(title="Phonica",
            subtitle="Advanced English",
            up_front_price=Decimal("39.0"),
            up_front_gst=Decimal("0.90"),
            billing_price=Decimal("9.90"),
            billing_gst=Decimal("0.90"),
            icon_url="image/icon/128x128/cd_green.png"),
        dict(title="Phonica",
            subtitle="Elementary English",
            up_front_price=Decimal("39.0"),
            up_front_gst=Decimal("0.90"),
            billing_price=Decimal("9.90"),
            billing_gst=Decimal("0.90"),
            icon_url="image/icon/128x128/cd_green.png"),
        dict(title="English Story",
            subtitle="English",
            up_front_price=Decimal("39.0"),
            up_front_gst=Decimal("0.90"),
            billing_price=Decimal("9.90"),
            billing_gst=Decimal("0.90"),
            icon_url="image/icon/128x128/cd_green.png"),
        dict(title="Dinamagic",
            subtitle="Mathematics",
            up_front_price=Decimal("39.0"),
            up_front_gst=Decimal("0.90"),
            billing_price=Decimal("9.90"),
            billing_gst=Decimal("0.90"),
            icon_url="image/icon/128x128/cd_blue.png"),
        dict(title="Maths Story",
            subtitle="Junior",
            up_front_price=Decimal("39.0"),
            up_front_gst=Decimal("0.90"),
            billing_price=Decimal("9.90"),
            billing_gst=Decimal("0.90"),
            icon_url="image/icon/128x128/cd_blue.png"),
        dict(title="Maths Story",
            subtitle="Primary",
            up_front_price=Decimal("39.0"),
            up_front_gst=Decimal("0.90"),
            billing_price=Decimal("9.90"),
            billing_gst=Decimal("0.90"),
            icon_url="image/icon/128x128/cd_blue.png"),
        dict(title="Maths Story",
            subtitle="Senior",
            up_front_price=Decimal("39.0"),
            up_front_gst=Decimal("0.90"),
            billing_price=Decimal("9.90"),
            billing_gst=Decimal("0.90"),
            icon_url="image/icon/128x128/cd_blue.png"),
    )
    products = []
    for p in products_list:
        p['icon_url'] = MEDIA_URL + p['icon_url']
        products.append(Product(**p))
    db.put(products)

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
    )
    customers = []
    for c in customers_list:
        customers.append(Customer(**c))
    db.put(customers)
