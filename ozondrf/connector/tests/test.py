import json
import sys, os
import django
import requests

parent = os.path.abspath("..")
sys.path.insert(1, parent)
sys.path.append("../..")
sys.path.append("../../connector")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "connector.settings")
django.setup()

from connector.config import TUSMK_ON, TUSMK_URL, TUSMK_AUTH, TUSMK_ISAUTH, TUSMK_NEW_ORDER
import uuid
from connector.models import Order
from connector.ozon_manager import OzonManager
from loguru import logger
from connector.services.packages import notify, build_packages


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


om = OzonManager()


def _integrate_date(all_shipping: list, all_dating: list) -> list:
    """"""
    res = []
    print(all_shipping)
    print(all_dating)
    for shipping in all_shipping:
        posting_number = shipping["posting_number"]
        logger.debug(f"posting_number: {posting_number}")
        for dating in all_dating:
            # pn = dating.get(f"{posting_number}")
            logger.debug(f"dating.keys(): {dating.keys()}")
            for k, v in dating.items():
                if k == posting_number:
                    logger.debug(f" {k}, {v}")
                    shipping['posting_date'] = v
        res.append(shipping)
    return res


def process_orders_task():
    # get new (awaiting_packaging) orders
    # new_orders = om.get_awaiting_packaging_orders() # Собираем заказы со статусом "awaiting_packaging"
    
    with open("test_order.json", "r") as file:
        new_orders = json.load(file)
    
    # print(new_orders)
    
    all_shipping = []
    all_dating = []
    
    # Итерируемся по новым заказам
    for order in new_orders["result"]["postings"]:
        
        financial_data = order.get('financial_data')
        
        # чекаем, есть ли заказ в бд, получаем список QuerySet
        exist = Order.objects.filter(posting_number=order["posting_number"])
        
        # вызываем расчет упаковки, нового заказа и распаковываем получившийся результат
        packaging, is_packing = build_packages(order)
        
        print(packaging, is_packing)  # забираем offer_id 'И00015494_1'
        
        if not is_packing:  # Заказ не помещается в отправление
            
            notify(f'Заказ {order["posting_number"]} не помещается в одно отправление. Обработайте заказ вручную')
        
        else:
            
            if len(exist) > 0:  # если заказ есть в бд
                if order["status"] != exist[0].status:  # сравниваем статусы
                    message = f"""Статус заказа {order['posting_number']} изменился
                    Предыдущий статус : {exist[0].status}
                    Новый статус: {order['status']}
                    """
                    notify(message)
                    # logger.warning(
                    #     f"Status changed from {exist[0].status} to {order['status']}"
                    # )
            
            elif len(exist) == 0:  # если заказа нет в бд
                products = order["products"]
                financial_data = order['financial_data']['products']
                posting_number = order["posting_number"]
                shipment_date = order["shipment_date"]
                
                # сохраняем даты на отправления
                all_dating.append({posting_number: shipment_date})
                
                for p in products:
                    if 'product_id' not in p.keys():
                        p.update({"product_id": p["sku"]})
                
                # shipping = self.om.ship(order["posting_number"], products)
                if posting_number == '11111111-0031-1':
                    shipping = {'result': ['11111111-0031-1'],
                                'additional_data': [{'posting_number': '22222222-0031-1',
                                                     "products": [
                                                         {
                                                             "price": "506.000000",
                                                             "offer_id": "К00014246_1",
                                                             "name": "Выключатель 1-клавишный SchE AtlasDesign алюминий с подсветкой с/у",
                                                             "sku": 867503151,
                                                             "quantity": 2,
                                                             "mandatory_mark": [
                                                                 "",
                                                                 ""
                                                             ],
                                                             "currency_code": "RUB"
                                                         },
                                                         {
                                                             "price": "777.000000",
                                                             "offer_id": "К00023611_3",
                                                             "name": "Розетка 1-местная SchE AtlasDesign алюминий с/у б/з",
                                                             "sku": 866418193,
                                                             "quantity": 1,
                                                             "mandatory_mark": [
                                                                 ""
                                                             ],
                                                             "currency_code": "RUB"
                                                         },
                                                         {
                                                             "price": "349.000000",
                                                             "offer_id": "И00016616_1",
                                                             "name": "Розетка 1-местная SchE AtlasDesign алюминий с/у с/з",
                                                             "sku": 866417812,
                                                             "quantity": 1,
                                                             "mandatory_mark": [
                                                                 ""
                                                             ],
                                                             "currency_code": "RUB"
                                                         },
                                                         {
                                                             "price": "900.000000",
                                                             "offer_id": "И00015509_10",
                                                             "name": "Рамка 1-постовая Schneider Electric AtlasDesign алюминий",
                                                             "sku": 865380492,
                                                             "quantity": 1,
                                                             "mandatory_mark": [
                                                                 ""
                                                             ],
                                                             "currency_code": "RUB"
                                                         },
                                                         {
                                                             "price": "629.000000",
                                                             "offer_id": "К00030095_1",
                                                             "name": "Выключатель 2-клав. SchE AtlasDesign алюминий с подсветкой",
                                                             "sku": 867503311,
                                                             "quantity": 1,
                                                             "mandatory_mark": [
                                                                 ""
                                                             ],
                                                             "currency_code": "RUB"
                                                         }], }]}
                
                print("shippinf-до:", shipping)
                
                ads = shipping['additional_data']

                if ads:
                    for ad in ads:
                        for product in ad['products']:
                            for data in financial_data:
                                if product['sku'] == data['product_id']:
                                    product['price'] = data['old_price']
                        all_shipping.append(ad)

                print("shippinf:", shipping)
                
                # logger.warning(f"shipping: {shipping}")
            
            # not exist - add this order to database
            
            # allowed_keys = filter_order_keys()
            # filtered_order = {
            #     your_key: order[your_key] for your_key in allowed_keys
            # }
            # # create order
            # o = Order(**filtered_order)
            #
            # # add nested keys
            # o.delivery_method_warehouse_id = order["delivery_method"][
            #     "warehouse_id"
            # ]
            # o.delivery_method_tpl_provider_id = order["delivery_method"][
            #     "tpl_provider_id"
            # ]
            # o.cancellation_initiator = order["cancellation"][
            #     "cancellation_initiator"
            # ]
            # o.save()
            #
            message = f"Created new order {o.posting_number}\n"
            # subj = f"Created new order {o.posting_number}\n"
            
            # Обратная операция итерируемся по списку продуктов, находим product_id и удаляем его

            # for product in order["products"]:
            #     for data in financial_data:
            #         if product['sku'] == data['product_id']:
            #             product['price'] = data['old_price']
            #
            #     message += f"{product['offer_id']} - {product['name']} {product['quantity']} {product['price']} \n"
            #     if 'product_id' in product.keys():
            #         del product['product_id']
            #     p = Product(**product)
            #     p.save()
            #     p.order.add(o)
            #     p.save()
            
            # packages = build_packages(order)
            #
            # if not packages:
            #     notify(
            #         f'Order{order["posting_number"]} does not fit in one package'
            #     )
            # else:
            #     # print("products:", order['products'])
            #     products = order['products']
            #     for p in products:
            #         p.update({'product_id': p['sku']})
            #         print("ok")
    
    if len(all_shipping) > 0:
        
        all_shipping = _integrate_date(all_shipping, all_dating)
        logger.debug(f'all_ship: {all_shipping}')
        print("123", _modify_ozon_response(all_shipping))
        register_new_order(_modify_ozon_response(all_shipping))


# a = [{'posting_number': '11111111-0031-1', 'products': [{'price': '4137.000000', 'offer_id': 'К00027974_1', 'name': 'Лопата снеговая на колесах ЭлектроМаш', 'sku': 817569569, 'quantity': 1, 'mandatory_mark': [''], 'currency_code': 'RUB'}]},
#      {'posting_number': '22222222-0031-1', 'products': [{'price': '4137.000000', 'offer_id': 'К00027974_1', 'name': 'Лопата снеговая на колесах ЭлектроМаш', 'sku': 817569569, 'quantity': 1, 'mandatory_mark': [''], 'currency_code': 'RUB'}]}]
# b = [{'11111111-0031-1': '2023-03-24T04:00:00Z'}, {'22222222-0031-1': '2023-03-25T04:00:00Z'}]
#
# print(_integrate_date(a, b))


# def process_reorders_task():
#     """Обработанные вручную заказы"""
#     postings = om.get_awaiting_deliver_orders()  # получаем заказы со статусом awaiting_deliver
#     postings = _get_postings(postings)  # получаем список заказов
#     orders = []
#     if postings:  # если заказы существуют
#         orders = _kill_old_postings(postings)  # Проверяем заказы по базе, оставляем те, которых нет
#     _save_new_orders(orders)  # Сохраняем заказ в базе
#     tusm_orders = _make_data_for_tusm(orders)  # создаем список для ТУСМ с ценами
#     if len(tusm_orders) > 0:
#         tusmk.register_new_order(tusm_orders)


def _make_data_for_tusm():
    """ответ для тусм"""
    
    with open("test_order.json", "r") as file:
        postings = json.load(file)
    
    res = []
    if postings:
        for post in postings:
            products = post.get('products')
            posting_date = post.get('shipment_date')
            posting_date = posting_date[:10]
            financial_data = post.get('financial_data').get('products')
            
            for product in products:
                for data in financial_data:
                    if product['sku'] == data['product_id']:
                        product['price'] = data['old_price']
                        
                
                com_offer_id = None
                sku = product.get("sku")
                try:
                    com_offer_id = product.get('offer_id')
                    sku, party = _make_sku_party(com_offer_id)
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


def _make_sku_party(value: str):
    res = value.split('_')
    if len(res) == 2:
        return res[0], int(res[1])
    else:
        return None, None


def _modify_ozon_response(postings) -> str:
    # with open("test_order.json", "r") as file:
    #     postings = json.load(file)
    new_data = []
    for dat in postings:
        
        products = None
        try:
            posting_number = dat.get('posting_number')
            posting_date = dat.get('posting_date')
            posting_date = posting_date[:10]
            products = dat.get('products')
        except:
            pass
        new_products = []
        if products:
            for product in products:
                com_offer_id = None
                try:
                    com_offer_id = product.get('offer_id')
                    sku, party = _make_sku_party(com_offer_id)
                    price = product.get('price')
                    del product['sku']
                except:
                    pass
                if com_offer_id:
                    price = float(price)
                    price = float(int(price * 100)) / 100
                    product['price'] = price
                    product['sku'] = sku
                    product['party'] = party
                new_products.append(product)
        new_data.append(dict(
            posting_number=posting_number,
            products=new_products,
            posting_date=posting_date,
        ))
    return new_data


def call_tusmk(ep: str, payload: str):
    print(payload)
    url = TUSMK_URL
    if TUSMK_ISAUTH:
        headers = {"Content-Type": "application/json", "Authorization": TUSMK_AUTH}
    else:
        headers = {"Content-Type": "application/json"}
    if not TUSMK_ON:
        mock_uuid = str(uuid.uuid4())
        return [{"id": f"mock_{mock_uuid}", "status": 200, "posting_number": "11111111-0031-1"}]
    try:
        r = requests.post(url + ep, headers=headers, data=payload)
    except Exception as e:
        logger.error(f"Error posting {payload} to {url}{ep} - {e}")
        return []
    else:
        if r.status_code in [200, 201]:
            try:
                data = json.loads(r.content)
            except Exception as e:
                logger.error(f"Error decoding json {r.content} ...")
                print("url:", ep)
                print("контент:", r.content)
                return []
        else:
            data = None
        return data


def register_new_order(list_orders: list) -> bool:
    """
    register new order, receive TUS MK id, save it to database
  
    """
    
    for order in list_orders:
        logger.debug(f"{order}")
        payload = json.dumps(order, ensure_ascii=False).encode('utf-8')
        r = call_tusmk(TUSMK_NEW_ORDER, payload)
        if r:
            logger.debug(f"responce: {r}")
            res = r
            if res:
                for r in res:
                    tusmk_id = r.get("id")
                    logger.debug(f"tusmk_id: {tusmk_id}")
                    posting_number = r.get("posting_number")
                    logger.debug(f"posting_number : {posting_number}")
                    o = Order.objects.filter(posting_number=posting_number).first()
                    if o:
                        o.tusmk_id = tusmk_id
                        o.save()
                        logger.debug("Заказ успешно сохранен в базе")
                    else:
                        logger.debug("Posting_number не найден в базе")


if __name__ == "__main__":
    process_orders_task()
    # print("1", _make_data_for_tusm())
    # print("2", _modify_ozon_response())
