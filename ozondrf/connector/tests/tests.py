import sys, os
import django
import datetime
import json
import requests

parent = os.path.abspath("..")
sys.path.insert(1, parent)
sys.path.append("../..")
sys.path.append("../../connector")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "connector.settings")
django.setup()
#
from connector.models import Product, Order
from ozon_manager import OzonManager, OZON_ORDERS_STATUSES
from connector.service import OzonService
from helpers import notify, sendDocument
from config import STATIC_PATH, STATIC_URL
from tusmk import TusMK

#
# def tst_reprocess_orders_task():
#
#     ozon = OzonService()
#     orders = ozon.get_dop_statuses()
#     print("type:", type(orders))
#     print(orders)
#
#
# tst_reprocess_orders_task()

om = OzonManager()


# m = o.get_awaiting_delivery_orders()
# # m = o.get_orders_by_status(status="awaiting_deliver")
# with open('data.json', 'w') as fp:
#     json.dump(m, fp, indent=4, ensure_ascii=False)


# curr_date = datetime.date.today()
# data = str(curr_date)
# print((data))
# check_holiday = requests.get("https://isdayoff.ru/20230008")
# print(check_holiday.text)


def _list_holidays():
    """
    Список нерабочих дней за текущий год
    """
    try:
        with open("holidays.txt", "r") as file:
            data = file.read()
    except Exception:
        return "Ошибка чтения файла или файл недоступен"
    else:
        return data


def _check_shipment_date_to_holidays(date):
    """
    Функция проверяет, является ли дата отгрузки нерабочим днем.

    Args: объект даты datetime
    Returns: объект даты datetime

    """
    if str(date) not in _list_holidays():
        return date
    
    else:
        while str(date) in _list_holidays():
            date += datetime.timedelta(days=1)
        return date


def _count_shipment_date():
    """
    Функция считает ближайшую дату отправки с учетом нерабочих дней

    """
    
    current_date = datetime.date.today()
    print(current_date)
    print(_list_holidays())
    
    if str(current_date) in _list_holidays():
        return _check_shipment_date_to_holidays(current_date)
    
    else:
        
        if current_date.weekday() < 4:
            shipment_day = current_date + datetime.timedelta(days=1)
            return _check_shipment_date_to_holidays(shipment_day)
        
        elif current_date.weekday() == 4:
            shipment_day = current_date + datetime.timedelta(days=3)
            return _check_shipment_date_to_holidays(shipment_day)


def get_acts_task():
    tusmk = TusMK()
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    get_departure_date = _count_shipment_date()
    
    departure_date = get_departure_date.strftime(date_format)
    print("date_shipment", departure_date)
    orders = om.get_awaiting_delivery_orders()
    
    for order in orders["result"]["postings"]:
        acts = om.get_acts(delivery_method_id=order["delivery_method"]["id"],
                           departure_date=departure_date)
        
        act_id = acts.get("result", {"id": 0})["id"]
        
        if act_id != 0:
            if not os.path.exists(f"../pdf/{act_id}.pdf"):
                pdf = om.get_act_transport_id(act_id)  # pdf сырой
                try:
                    with open(f"../pdf/{act_id}.pdf", "wb") as out:
                        out.write(pdf)
                except Exception:
                    print("Ошибка записи в файл")
                sendDocument(f"../pdf/{act_id}.pdf")
                tusmk.send_doc_to_tus(f"../pdf/{act_id}.pdf", act_id)
                
                tusmk.got_act(
                    order["posting_number"],
                    act_id,
                    departure_date,
                    f"{STATIC_URL}{act_id}",
                )


print(get_acts_task())
