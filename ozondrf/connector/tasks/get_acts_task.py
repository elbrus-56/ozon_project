import os
import platform
import sys
import datetime

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.config import STATIC_PATH
from connector.tusmk import TusMK
from connector.ozon_manager import OzonManager
from connector.services.notify import Notify


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


class GetActs:

    def __init__(self):
        self.om = OzonManager()
        self.tusmk = TusMK()

    def _list_holidays(self):
        """
        Список нерабочих дней за текущий год
        """
        try:
            with open("../ozondrf/connector/tasks/holidays.txt", "r") as file:
                data = file.read()
        except Exception:
            return "Ошибка чтения файла или файл недоступен"
        else:
            return data

    def _check_shipment_date_to_holidays(self, date):

        """
        Функция проверяет, является ли дата отгрузки нерабочим днем.

        Args: объект даты datetime
        Returns: объект даты datetime

        """
        if str(date) not in self._list_holidays():
            return date

        else:
            while str(date) in self._list_holidays():
                date += datetime.timedelta(days=1)
            return date

    def _count_shipment_date(self):
        """
        Функция считает ближайшую дату отгрузки с учетом нерабочих дней

        """

        current_date = datetime.date.today()

        if str(current_date) in self._list_holidays():
            return self._check_shipment_date_to_holidays(current_date)

        else:

            if current_date.weekday() < 4:
                shipment_day = current_date + datetime.timedelta(days=1)
                return self._check_shipment_date_to_holidays(shipment_day)

            elif current_date.weekday() == 4:
                shipment_day = current_date + datetime.timedelta(days=3)
                return self._check_shipment_date_to_holidays(shipment_day)

    def get_acts_task(self):

        date_format = "%Y-%m-%dT%H:%M:%SZ"
        get_departure_date = self._count_shipment_date()
        departure_date = get_departure_date.strftime(date_format)
        orders = self.om.get_awaiting_delivery_orders()
        if orders:
            for order in orders["result"]["postings"]:
                act = self.om.create_acts(delivery_method_id=order["delivery_method"]["id"],
                                          departure_date=departure_date)
                act_id = act.get("result", {"id": 0})["id"]
                if act_id != 0:
                    if not os.path.exists(f"{STATIC_PATH}{act_id }.pdf"):
                        pdf = self.om.get_act_of_acceptance(transport_id=act_id)
                        if pdf:
                            try:
                                with open(f"{STATIC_PATH}{act_id}.pdf", "wb") as out:
                                    out.write(pdf)
                            except Exception:
                                print(f"Ошибка записи в файл {STATIC_PATH}{act_id}.pdf")

                            Notify.sendDocument(f"{STATIC_PATH}{act_id}.pdf")
                            Notify.send_email(subject=f"PDF act of acceptance {act_id}",
                                              attachments=(f"{act_id}.pdf",
                                                           f"{STATIC_PATH}{act_id}.pdf",
                                                           "application/pdf"))

                            self.tusmk.send_doc_to_tus(f"{STATIC_PATH}{act_id}.pdf", act_id)

                        # self.tusmk.got_act(
                        #     order["posting_number"],
                        #     act_id,
                        #     departure_date,
                        #     f"{STATIC_URL}{act_id}",
                        # )
