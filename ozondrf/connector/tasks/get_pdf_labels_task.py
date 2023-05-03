import os
import platform
import sys

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.config import STATIC_PATH, STATIC_URL
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


class GetPdfLabels:
    
    def __init__(self):
        self.om = OzonManager()
        self.tusmk = TusMK()
    
    def get_pdf_labels_task(self):
        sending_pdfs = []
        orders = self.om.get_awaiting_delivery_orders()
        if orders:
            for order in orders["result"]["postings"]:
                posting_number = order["posting_number"]
                if not os.path.exists(f"{STATIC_PATH}{posting_number}.pdf"):
                    labels = self.om.package_labels(order["posting_number"])
                    if labels:
                        with open(f"{STATIC_PATH}{posting_number}.pdf", "wb") as out:
                            out.write(labels)
                        Notify.sendDocument(f"{STATIC_PATH}{posting_number}.pdf")
                        Notify.send_email(subject=f"PDF labels {posting_number}",
                                          attachments=(f"{posting_number}.pdf",
                                                       f"{STATIC_PATH}{posting_number}.pdf",
                                                       "application/pdf"))
                        file_name = f"{STATIC_PATH}{posting_number}.pdf"
                        sending_pdfs.append(dict(
                            posting_number=posting_number,
                            file=file_name
                        ))
            if len(sending_pdfs) > 0:
                notify_tusmk = self.tusmk.send_labels(sending_pdfs)
