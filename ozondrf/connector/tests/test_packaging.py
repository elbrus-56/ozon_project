import sys, os
import django
from pprint import pprint

parent = os.path.abspath("..")
print(parent)
print()
sys.path.insert(1, parent)
sys.path.append("../..")
sys.path.append("../../connector")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "connector.settings")
django.setup()

from connector.models import Product, Order
from connector.ozon_manager import OzonManager, OZON_ORDERS_STATUSES
from connector.services.packages import Package, get_order_pcs
from connector.config import MAX_ALLOWED_ITEMS, MAX_ALLOWED_PACKAGES


def filter_order_keys() -> list:
    """Filter model fields to match order keys (flatten nested keys)

    Returns:
        list: filtered keys
    """
    list_filter = [
        "product_orders",
        "delivery_method_warehouse_id",
        "delivery_method_tpl_provider_id",
        "cancellation_initiator",
        "products",
        "tusmk_id",
        "cancellation",
        "product_orders",
    ]

    order_keys = [f.name for f in Order._meta.get_fields() if f.name not in list_filter]
    return order_keys


products = Product.objects.all()
om = OzonManager()

delivery_methods = om.get_delivery_methods(
    {"filter": {"warehouse_id": 1020000071737000}}
)


def test_build_packages(order):
    om = OzonManager()
    products = []
    products = [product["offer_id"] for product in order["products"]]
    product_quantities = {
        product["offer_id"]: product["quantity"] for product in order["products"]
    }
    dimensions = om.get_dimensions(products)
    product_dimensions = {
        o["offer_id"]: [o["width"], o["height"], o["depth"], o["weight"]]
        for o in dimensions["result"]
    }
    product_data = []
    for p, q in product_quantities.items():
        for i in range(q):
            product_data.append([p, *product_dimensions[p]])
    package = Package()
    return package.pack(product_data, False)


for status in OZON_ORDERS_STATUSES:
    orders = om.get_orders_by_status(status)
    for o in orders["result"]["postings"]:
        packages = test_build_packages(o)
        pieces = get_order_pcs(o)
        print("Заказ", o["order_id"], f"Упаковок : {len(packages)}, Штук : {pieces}")
        pprint(packages)

        if len(packages) > MAX_ALLOWED_PACKAGES:
            print(f"{o['order_id']} Не помещается в одну упаковку, такой заказ обрабатываем вручную")
        elif pieces > MAX_ALLOWED_ITEMS:
            print(f"Количество позиций в {o['order_id']} - {pieces}, такой заказ обрабатываем вручную")
        else:
            print(f'С этим заказом все в порядке, он будет обработан автоматически')
