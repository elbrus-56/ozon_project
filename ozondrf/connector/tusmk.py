import json
import os
import sys
import uuid

import requests
from loguru import logger

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.config import TUSMK_ON, TUSMK_URL, TUSMK_AUTH, TUSMK_ISAUTH,\
    TUSMK_NEW_ORDER, TUSMK_SEND_PDF_LABEL
from connector.models import Order


class TusMK:
    """Placeholder class to interact with TUS MK"""
    
    def call_tusmk(self, ep: str, payload: str):
        url = TUSMK_URL
        if TUSMK_ISAUTH:
            headers = {"Content-Type": "application/json", "Authorization": TUSMK_AUTH}
        else:
            headers = {"Content-Type": "application/json"}
        if not TUSMK_ON:
            mock_uuid = str(uuid.uuid4())
            return [{"id": f"mock_{mock_uuid}", "status": 200}]
        try:
            r = requests.post(url + ep, headers=headers, data=payload)
        except Exception as e:
            logger.error(f"Error posting {payload} to {url}{ep} - {e}")
            return []
        else:
            if r and r.status_code in [200, 201]:
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
    
    def call_tusmk_file(self, ep: str, data, files):
        url = TUSMK_URL
        # headers = {"Content-Type": "application/pdf"}
        if not TUSMK_ON:
            mock_uuid = str(uuid.uuid4())
            return {"id": f"mock_{mock_uuid}", "status": 200}
        try:
            # r = requests.post(url + ep,data=data,files=files)
            r = requests.post(url + ep, files=files)
        except Exception as e:
            logger.error(f"Error posting {data} to {url}{ep} - {e}")
            return {}
        else:
            if r.status_code in [200, 201]:
                data = json.loads(r.content)
            else:
                data = None
            return data
    
    def tusmk2ozon_posting(self, tusmk_id: str) -> str:
        # tusmk_id = e2a95e9f-a327-11ed-995c-18c04dddf3f5
        try:
            o = Order.objects.filter(tusmk_id=tusmk_id).first()
        except Exception as e:
            return 0
        else:
            return o.posting_number
    
    def ozon2tusmk_posting(self, ozon_posting_number: str) -> str:
        o = Order.objects.filter(posting_number=ozon_posting_number).first()
        if o:
            return o.tusmk_id
        else:
            return 0
    
    def register_new_order(self, orders: list) -> None:
        """
        register new order, receive TUS MK id, save it to database

        """
        print("orders:", orders)
        payload = json.dumps(orders, ensure_ascii=False).encode('utf-8')
        print('payload_to_1c:', payload)
        r = self.call_tusmk(TUSMK_NEW_ORDER, payload)
        if r:
            print("responce:", r)
            res = r
            print("res:", res)
            if res:
                for r in res:
                    tusmk_id = r.get("id")
                    print('tusmk_id:', tusmk_id)
                    posting_number = r.get("posting_number")
                    o = Order.objects.filter(posting_number=posting_number).first()
                    if o:
                        o.tusmk_id = tusmk_id
                        o.save()
                        print("TUSMK_ID сформирован и добавлен")
                    else:
                        print("ошибка формирования TUSMK_ID")
    
    def got_label(self, posting_number: str, label_url: str) -> bool:
        """Notify label received for order id tusmk_id and send label url

        Args:
            tusmk_id (str): tusmk_id
            label_url (str): label_url

        Returns:
            bool: _description_
        """
        tusmk_id = self.ozon2tusmk_posting(posting_number)
        #  заглушка
        return False
        r = self.call_tusmk("/got_label", {"id": tusmk_id, "url": label_url})
        if "id" in r and r.get("status") == "200":
            return True
        else:
            return False
    
    def send_labels(self, data: list) -> bool:
        res = dict()
        rdata = dict()
        i = 1
        for dat in data:
            fname = 'file' + str(i)
            i += 1
            document = open(dat["file"], "rb")
            res[dat['posting_number']] = document
            rdata[fname] = dat['posting_number'] + '.pdf'
        
        r = self.call_tusmk_file(TUSMK_SEND_PDF_LABEL, data=rdata, files=res)
        if r:
            if r.get("status") == "200":
                return True
        return False
    
    def send_doc_to_tus(self, file_name, act_id):
        file_type = f"{act_id}.pdf"
        fi = f"{act_id}"
        rdata = {file_type: file_type}
        document = open(file_name, "rb")
        res = {fi: document}
        r = self.call_tusmk_file(TUSMK_SEND_PDF_LABEL, data=rdata, files=res)
        if r:
            if r.get("status") == "200":
                return True
        return False
    
    def send_statuses(self, statuses: list, url: str):
        data = json.dumps(statuses)
        return self.call_tusmk(url, payload=data)

    # def check_statuses(self, postings: list) -> list:
    #     data = json.dumps(postings)
    #     return self.call_tusmk(TUSMK_SEND_LIST_STATUSES, payload=data)

    
    def got_act(
            self, posting_number: str, act_id: str, delivery_date: str, act_url: str
    ):
        """Notify act created for order is tusmk_id and send act url

        Args:
            tusmk_id (str): tusmk id
            act_id (str): act id
            delivery_date (str): Date
            act_url (str): act PDF url

        Returns:
            _type_: _description_
        """
        tusmk_id = self.ozon2tusmk_posting(posting_number)

        r = self.call_tusmk(
            "/got_act",
            {
                "id": tusmk_id,
                "act_id": act_id,
                "date": delivery_date,
                "url": act_url,
            },
        )

        if "id" in r and r.get("status") == "200":
            return True
        else:
            return False
    
    def got_timeslot(self, tusmk_id, act_id, date, timeslot, status):
        return False
        r = self.call_tusmk(
            "/got_timeslot",
            {
                "id": tusmk_id,
                "act_id": act_id,
                "date": date,
                "timeslot": timeslot,
                "status": status,
            },
        )
        if "id" in r and r.get("status") == "200":
            return True
        else:
            return False
