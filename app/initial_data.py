
import configuration

from google.appengine.api import memcache
from google.appengine.ext import db
from models import Product
from decimal import Decimal

from configuration import MEDIA_URL as media_url

MEDIA_URL = media_url
if MEDIA_URL.startswith('/'):
    MEDIA_URL = "http://%s:%s" % (configuration.SERVER_NAME, configuration.SERVER_PORT) + MEDIA_URL

def import_all():
    import_products()

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
        p = Product(**p)
        products.append(p)
    db.put(products)
