import os
import platform
import sys

from loguru import logger

import json
import django

parent = os.path.abspath("..")
sys.path.insert(1, parent)
sys.path.append("../..")
sys.path.append("../../connector")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "connector.settings")
django.setup()

from connector.models import Order
from connector.tusmk import TusMK
from connector.ozon_manager import OzonManager
from connector.services.packages import notify, build_packages


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


class ProcessOrder:
    
    def __init__(self):
        self.om = OzonManager()
        self.tusmk = TusMK()
    
    
    def _processing_order(self, order, packages):

        packages = self._replace_offer_id_to_product_id(order, packages)
        print(packages)
        print(order["posting_number"])
        # try:
        shipping = self.om.ship(order["posting_number"], packages)
        #     shipping = {'result': ['11111112-0031-1'],
        #                 'additional_data': [
        #
        #                     {'posting_number': '11111112-0031-1',
        #                      "products": [
        #                          {
        #                              "price": "506.000000",
        #                              "offer_id": "К00014246_1",
        #                              "name": "Выключатель 1-клавишный SchE AtlasDesign алюминий с подсветкой с/у",
        #                              "sku": 867503151,
        #                              "quantity": 2,
        #                              "mandatory_mark": [
        #                                  "",
        #                                  ""
        #                              ],
        #                              "currency_code": "RUB"
        #                          },
        #                          {
        #                              "price": "777.000000",
        #                              "offer_id": "К00023611_3",
        #                              "name": "Розетка 1-местная SchE AtlasDesign алюминий с/у б/з",
        #                              "sku": 866418193,
        #                              "quantity": 1,
        #                              "mandatory_mark": [
        #                                  ""
        #                              ],
        #                              "currency_code": "RUB"
        #                          },
        #                          {
        #                              "price": "349.000000",
        #                              "offer_id": "И00016616_1",
        #                              "name": "Розетка 1-местная SchE AtlasDesign алюминий с/у с/з",
        #                              "sku": 866417812,
        #                              "quantity": 1,
        #                              "mandatory_mark": [
        #                                  ""
        #                              ],
        #                              "currency_code": "RUB"
        #                          },
        #                          {
        #                              "price": "900.000000",
        #                              "offer_id": "И00015509_10",
        #                              "name": "Рамка 1-постовая Schneider Electric AtlasDesign алюминий",
        #                              "sku": 865380492,
        #                              "quantity": 1,
        #                              "mandatory_mark": [
        #                                  ""
        #                              ],
        #                              "currency_code": "RUB"
        #                          },
        #                          {
        #                              "price": "629.000000",
        #                              "offer_id": "Г00005449_10",
        #                              "name": "Выключатель 2-клав. SchE AtlasDesign алюминий с подсветкой",
        #                              "sku": 867503311,
        #                              "quantity": 100,
        #                              "mandatory_mark": [
        #                                  ""
        #                              ],
        #                              "currency_code": "RUB"
        #                          }], }]}
        # except:
        #     print("Заказ уже был разбит на отправления")
        
        print("shippinf:", shipping)
        
        return shipping
    
    def _replace_offer_id_to_product_id(self, order, packages):
        for product in order["products"]:
            for package in packages:
                for p in package["products"]:
                    if p["product_id"] == product["offer_id"]:
                        p["product_id"] = product["sku"]
        return packages
    
    def _create_packages_for_deliver(self, packaging):
        """
        Функция распределяет товары по упаковкам
        """
        packages = []
    
        for package in packaging:
            temp = {}
            # Cчитаем количество товаров в отправлении
            for p in package:
                if p not in temp:
                    temp[p] = 0
                temp[p] += 1
        
            list_products = []
            
            # Формируем список products
            for key, value in temp.items():
                products = {}
                products["product_id"] = key
                products["quantity"] = value
                list_products.append(products)
        
            packages.append({"products": list_products})
            
        return packages
    
    def process_orders_task(self):
        # get new (awaiting_packaging) orders
        # new_orders = self.om.get_awaiting_packaging_orders()
        
        with open("test_order.json", "r") as file:
            new_orders = json.load(file)
        
        all_shipping = []
        
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
                    notify(message)
                    logger.info(
                        f"Status changed from {exist[0].status} to {order['status']}"
                    )
            elif len(exist) == 0:
                
                # проверяем помещается ли заказ в 1 коробку
                packaging, is_packing = build_packages(order)
                print(packaging)
                print(len(packaging))
                
                
                
                custom_weight = 7000
                packaging, is_packing = build_packages(order, custom_weight)
                print(packaging)
                packages = self._create_packages_for_deliver(packaging)
                print(len(packages))
                shipping = self._processing_order(order, packages)
                print("shippinf:", shipping)
                logger.info("shipping:", shipping)
                
                
                    
                
                # ads = shipping['additional_data']
                
                # if ads:
                #     for ad in ads:
                #         ad['posting_date'] = order["shipment_date"]
                #         self._save_new_orders(order, ad)
                #         all_shipping.append(ad)
                
    

        # if len(all_shipping) > 0:
        #     logger.debug(f"all_ship: {all_shipping}")
        #     self.tusmk.register_new_order(self._modify_ozon_response(all_shipping))


if __name__ == "__main__":
    task = ProcessOrder()
    task.process_orders_task()
