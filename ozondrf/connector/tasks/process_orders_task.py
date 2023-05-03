import os
import platform
import sys

from loguru import logger

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.models import Order
from connector.tusmk import TusMK
from connector.ozon_manager import OzonManager
from connector.services.packages import build_packages
from connector.services.notify import Notify
from connector.config import CUSTOM_WEIGHT


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


class ProcessOrder:

    def __init__(self):
        self.om = OzonManager()
        self.tusmk = TusMK()

    def _processing_order(self, order, packages):
        packages = self._replace_offer_id_to_product_id(order, packages)
        try:
            shipping = self.om.ship(order["posting_number"], packages)
        except Exception:
            print("POSTING_ALREADY_SHIPPED")

        return shipping

    def _replace_offer_id_to_product_id(self, order, packages):
        for product in order["products"]:
            for package in packages:
                for p in package["products"]:
                    if p["product_id"] == product["offer_id"]:
                        p["product_id"] = product["sku"]
        return packages

    def _create_list_packages_for_delivery(self, packaging: list):
        """
        """
        packages = []

        for package in packaging:
            temp = {}
            # Считаем количество товаров в отправлении
            for p in package:
                if p not in temp:
                    temp[p] = 0
                temp[p] += 1

            list_products = []

            # Формируем список products
            for key, value in temp.items():
                products = {
                    "product_id": key,
                    "quantity": value
                }

                list_products.append(products)

            packages.append({"products": list_products})

        return packages

    def process_orders_task(self):
        # get new (awaiting_packaging) orders
        new_orders = self.om.get_awaiting_packaging_orders()

        if new_orders:
            # loop over new orders
            for order in new_orders["result"]["postings"]:

                # check if order is already in the database
                exist = Order.objects.filter(posting_number=order["posting_number"])

                if len(exist) > 0:
                    if order["status"] != exist[0].status:
                        message = f"""Статус заказа {order['posting_number']} изменился
                                      Предыдущий статус : {exist[0].status}
                                      Новый статус: {order['status']}
                                   """

                        Notify.send_email(subject=f"Статус заказа {order['posting_number']} изменился",
                                          message=message
                                          )
                        Notify.notify(message)
                        logger.info(
                            f"Status changed from {exist[0].status} to {order['status']}")

                elif len(exist) == 0:

                    # проверяем помещается ли заказ в 1 стандартную коробку 25000 г.
                    packaging, is_packing = build_packages(order)

                    if is_packing:
                        # Разбиваем заказ на отправления с требуемым весом (CUSTOM_WEIGHT).
                        # Если CUSTOM_WEIGHT убрать, то значение по умолчанию будет MAX_WEIGHT

                        packaging, is_packing = build_packages(order, CUSTOM_WEIGHT)
                        print(f"packaging: {packaging}")
                        packages = self._create_list_packages_for_delivery(packaging)
                        shipping = self._processing_order(order, packages)
                        print(f"shippinf: {shipping}")
                        logger.info(f"shipping: {shipping}")
                        Notify.notify(f'Заказ {order["posting_number"]} готов к отправке')

                    else:
                        # Разбиваем заказ на отправления требуемым весом (CUSTOM_WEIGHT).
                        # Если CUSTOM_WEIGHT убрать, то значение по умолчанию будет MAX_WEIGHT

                        packaging, is_packing = build_packages(order, CUSTOM_WEIGHT)
                        print(f"packaging: {packaging}")
                        packages = self._create_list_packages_for_delivery(packaging)
                        shipping = self._processing_order(order, packages)
                        print(f"shippinf: {shipping}")
                        logger.info(f"shipping: {shipping}")
                        Notify.notify(f'Заказ {order["posting_number"]} был разбит на несколько отправлений.'
                               f' Его нужно проверить дополнительно')
