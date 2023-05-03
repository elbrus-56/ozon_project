import os
import platform
import sys

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.models import Order
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


class NotifyCancelled:
    
    def __init__(self):
        self.om = OzonManager()
        self.tusmk = TusMK()
    
    def notify_cancelled(self, email=False, telegram=False):
        
        # get new (awaiting_packaging) orders
        new_orders = self.om.get_cancelled_orders()
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
                        if email:
                            Notify.send_email(subject=f"Статус заказа {order['posting_number']} изменился",
                                              message=message
                                              )
                        if telegram:
                            Notify.notify(message)
                        exist[0].status = "cancelled"
                        exist[0].save()
