import os
import platform
import sys

from loguru import logger

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.tusmk import TusMK
from connector.ozon_manager import OzonManager
from connector.services.notify import Notify
from connector.config import TUSMK_SEND_STATUSES, TUSMK_SEND_LIST_STATUSES


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


class GetDopStatuses:
    def __init__(self):
        self.om = OzonManager()
        self.tusmk = TusMK()

    def _get_postings(self, orders: dict) -> list:
        try:
            postings = orders["result"]["postings"]
            return postings
        except:
            return None

    def _get_list_statuses(self, dop_statuses):
        """
        Функция формирует список отправлений и их статусов

        [{
            "posting_number": "0107508694-0106-1",
            "Status": "delivering",
            "shipment_date": "2023-04-03"
        }]

        """
        res = []

        for ds in dop_statuses:
            postings = self.om.get_orders_by_status(status=ds, days=21)
            postings = self._get_postings(postings)
            if postings:
                for post in postings:
                    num = post.get("posting_number")
                    shipment_date = post.get('shipment_date')
                    shipment_date = shipment_date[:10]
                    # print('num:',num)
                    r = dict(posting_number=num, Status=ds, shipment_date=shipment_date)
                    if num:
                        res.append(r)
        return res

    def get_dop_statuses(self):
        """
        Функция отправляет список отправлений и их статусов в 1с
        """
        dop_statuses = [
            "arbitration",
            "delivering",
            "delivered",
            "cancelled"
        ]
        res = self._get_list_statuses(dop_statuses)
        if res:
            self.tusmk.send_statuses(res, TUSMK_SEND_STATUSES)

    def create_statuses_report(self):
        """
        Функция проверяет наличие необработанных отправлений и
        формирует краткий отчет в виде уведомлений в телеграм и на почту
        """
        dop_statuses = [
            "awaiting_packaging",
            "awaiting_deliver"
        ]
        results = self._get_list_statuses(dop_statuses)

        postings = []

        for result in results:
            postings.append(result["posting_number"])

        if postings:
            check_list = self.tusmk.send_statuses(postings, TUSMK_SEND_LIST_STATUSES)

            if check_list and "id" not in check_list[0]:
                for posting in check_list:
                    if posting["Status"] is None:
                        message = f"Boxberry: Ежедневный контроль: Найдено необработанное отправление {posting['Number']}"
                        Notify.notify(message)
                        Notify.send_email(subject=message, message=message)
                        print(f"{message}")
                        logger.info(f"{message}")

        print("Boxberry: Ежедневный контроль выполнен успешно")
        logger.info("Boxberry: Ежедневный контроль выполнен успешно")
        print("OZON:Get_dop_statuses: Ежедневный контроль выполнен")
        Notify.notify(message="OZON:Get_dop_statuses: Ежедневный контроль выполнен")
        Notify.send_email(subject="OZON:Get_dop_statuses: Ежедневный контроль выполнен", message="OZON:Get_dop_statuses: Ежедневный контроль выполнен")

