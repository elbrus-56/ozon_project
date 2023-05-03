import os
import sys

from django.core.management.base import BaseCommand

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.tusmk import TusMK
from connector.ozon_manager import OzonManager
from connector.config import STATIC_PATH, STATIC_URL
from connector.services.packages import sendDocument

"""
TASK
3. 
к каждому грузу озон формирует этикетку в pdf формате необходимо 
ее запросить, скачать во временный файл и затем передать в ТУС
формат 
{
    "id": "ид ТУС***********",
    "url": "..."
}
в ответ если норм
{
    "id": "ид ТУС***********",
    "status": "200"
}
"""


class Command(BaseCommand):
    def handle(self, *args, **options):

        om = OzonManager()
        tusmk = TusMK()

        orders = om.get_awaiting_delivery_orders()
        for order in orders["result"]["postings"]:
            labels = om.package_labels(order["posting_number"])
            posting_number = order["posting_number"]
            if not os.path.exists(f"{STATIC_PATH}{posting_number}.pdf"):
                with open(f"{STATIC_PATH}{posting_number}.pdf", "wb") as out:
                    out.write(labels)
                    sendDocument(f"{STATIC_PATH}{posting_number}.pdf")
                    label_url = f"{STATIC_URL}{posting_number}.pdf"
                    notify_tusmk = tusmk.got_label(posting_number, label_url)
