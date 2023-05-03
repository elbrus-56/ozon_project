import os
import platform
import sys

from loguru import logger

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.tusmk import TusMK
from connector.ozon_manager import OzonManager
from connector.serializers import *


def creation_date(path_to_file):
    if platform.system() == "Windows":
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


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


class ProcessReorders:

    def __init__(self):
        self.om = OzonManager()
        self.tusmk = TusMK()

    def _get_postings(self, orders: dict) -> list:
        try:
            postings = orders["result"]["postings"]
            return postings
        except:
            return None

    def _kill_old_postings(self, postings: list):
        """Убиваем заказы, которые уже получены"""
        new_postings = []
        for order in postings:
            exist = Order.objects.filter(posting_number=order["posting_number"])
            if not exist:
                new_postings.append(order)
        return new_postings

    def _save_new_orders(self, new_orders):

        for order in new_orders:

            allowed_keys = filter_order_keys()
            filtered_order = {your_key: order[your_key] for your_key in allowed_keys}
            filtered_order["delivery_method_warehouse_id"] = order["delivery_method"]["warehouse_id"]
            filtered_order["delivery_method_tpl_provider_id"] = order["delivery_method"]["tpl_provider_id"]
            filtered_order["cancellation_initiator"] = order["cancellation"]["cancellation_initiator"]

            serializer = NewOrderSerializer(data=filtered_order)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            message = 'saving to base new order - ' + filtered_order["posting_number"]
            logger.info(message)

            for product in order["products"]:
                product["order"] = filtered_order["posting_number"]

                serializer = ProductsSerializer(data=product)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                del product["order"]

                message = 'saving to base new Product - ' + product["name"]
                logger.info(message)

    def _make_sku_party(self, value: str):
        res = value.split('_')
        if len(res) == 2:
            return res[0], int(res[1])
        else:
            return None, None

    def _make_data_for_tusm(self, postings: list) -> list:
        """ответ для тусм"""

        res = []
        if postings:
            for post in postings:
                products = post.get('products')
                posting_date = post.get('shipment_date')
                posting_date = posting_date[:10]
                for product in products:
                    com_offer_id = None
                    sku = product.get("sku")
                    try:
                        com_offer_id = product.get('offer_id')
                        sku, party = self._make_sku_party(com_offer_id)
                        price = product.get('price')
                        del product['sku']
                    except:
                        price = 0.0
                        pass
                    if com_offer_id:
                        price = float(price)
                        price = float(int(price * 100)) / 100
                        product['price'] = price
                        product['sku'] = sku
                        product['party'] = party

                res.append(dict(
                    posting_number=post['posting_number'],
                    products=products,
                    posting_date=posting_date
                ))

        return res

    def process_reorders_task(self) -> None:
        """Обработанные вручную заказы"""
        postings = self.om.get_awaiting_deliver_orders()
        postings = self._get_postings(postings)
        orders = []
        if postings:
            orders = self._kill_old_postings(postings)
        self._save_new_orders(orders)
        tusm_orders = self._make_data_for_tusm(orders)
        if len(tusm_orders) > 0:
            self.tusmk.register_new_order(tusm_orders)
