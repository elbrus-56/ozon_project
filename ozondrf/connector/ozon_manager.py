import requests

import requests
import datetime
import json
import sys
import os

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.config import OZON_API_URL, OZON_API_KEY, OZON_CLIENT_ID
from loguru import logger
import json

logger.add("ozon.log")

OZON_ORDERS_STATUSES = [
    "awaiting_registration",
    "acceptance_in_progress",
    "awaiting_approve",
    "awaiting_packaging",
    "awaiting_deliver",
    "arbitration",
    "client_arbitration",
    "delivering",
    "driver_pickup",
    "delivered",
    "cancelled",
    "not_accepted",
]

"""
awaiting_registration — ожидает регистрации,
acceptance_in_progress — идёт приёмка,
awaiting_approve — ожидает подтверждения,
awaiting_packaging — ожидает упаковки,
awaiting_deliver — ожидает отгрузки,
arbitration — арбитраж,
client_arbitration — клиентский арбитраж доставки,
delivering — доставляется,
driver_pickup — у водителя,
delivered — доставлено,
cancelled — отменено,
not_accepted — не принят на сортировочном центре,
"""


class OzonManager:
    """Ozon API Main class"""
    
    def __init__(self):
        self.client_id = OZON_CLIENT_ID
        self.api_key = OZON_API_KEY
        self.ozon_url = OZON_API_URL
        self.headers = {
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
        }
    
    def api_get(self, endpoint: str) -> dict:
        """GET request template

        Args:
            endpoint (str): endpoint to get

        Returns:
            dict: json result
        """
        try:
            r = requests.get(f"{self.ozon_url}{endpoint}", headers=self.headers)
        except Exception as e:
            logger.error(f"Error getting {endpoint} - {e}")
            return {}
        else:
            return r.json()
    
    def api_post_raw(self, endpoint: str, data: str) -> bytes:
        """POST request raw version for receiving PDFs

        Args:
            endpoint (str): endpoint
            data (str): payload (json string)

        Returns:
            bytes: response
        """

        url = f"{self.ozon_url}{endpoint}"
        try:
            r = requests.post(url, headers=self.headers, data=data)
        except Exception as e:
            logger.error(f"Error sending POST request {endpoint}  with {data}- {e}")
            return b""
        else:
            if r.status_code in [200, 201]:
                return r.content
            else:
                return b""
    
    def api_post(self, endpoint: str, data: str) -> dict:
        """POST request template, returns dict

        Args:
            endpoint (str): endpoint
            data (str): payload (json string)

        Returns:
            dict: response
        """
        url = f"{self.ozon_url}{endpoint}"
        try:
            r = requests.post(url, headers=self.headers, data=data)
        except Exception as e:
            logger.error(f"Error sending POST request {endpoint}  with {data}- {e}")
            return None
        else:
            try:
                r = json.loads(r.content)
            except Exception as e:
                logger.error(f"Error POST request returning response {endpoint} - {e}")
                return None
            return r

    def get_unfulfilled_postings(self):
        # Возвращает список необработанных отправлений
        ep = "/v3/posting/fbs/unfulfilled/list"

    def get_posting_info(self, posting_number: str) -> dict:
        # Получить информацию об отправлении по идентификатору
        """Get posting info by posting_number

        Args:
            posting_number (str): posting number

        Returns:
            dict: _description_
        """
        ep = "/v3/posting/fbs/get"
        payload = {"posting_number": posting_number}
        r = self.api_post(ep, data=json.dumps(payload))
        return r
    
    def get_orders_by_status(self, status: str = "delivering", days: int = 30) -> dict:

        """Get orders of a given status for the last 30 days period

        Args:
            status (str, optional): order status filter. Defaults to "delivering".
            days (int. optional) : period to query. Defaults to 30

        Returns:
            dict: _description_
        """
        ep = "/v3/posting/fbs/list"
        
        now = datetime.datetime.now()
        month_ago = now - datetime.timedelta(days=days)
        # date_format = "%Y-%m-%d"
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        
        payload = {
            "dir": "DESC",
            "filter": {
                "since": month_ago.strftime(date_format),
                "to": now.strftime(date_format),
                # "delivery_method_id": [],
                # "provider_id": [],
                "status": status,
                # "warehouse_id": []
            },
            "limit": 50,
            "offset": 0,
            "with": {
                "analytics_data": True,
                "barcodes": True,
                "financial_data": True,
                "translit": True,
            },
        }
        data = json.dumps(payload)
        r = self.api_post(ep, data)

        if r:
            if "code" in r:
                logger.error(f"Error: {r['message']}")
                return None
            else:
                return r
        else:
            logger.error("Error connection /v3/posting/fbs/list")
            return None

    def get_dimensions(self, product_ids: list = None) -> dict:
        """Get dimensions for a given list of product_ids

        Args:
            product_ids (list, optional): products to get WxHxD. Defaults to [].

        Returns:
            dict: product dimensions
        """
        if product_ids is None:
            product_ids = []
        
        payload = {
            "filter": {"offer_id": product_ids, "visibility": "ALL"},
            "limit": 100,
            "sort_dir": "ASC",
        }
        ep = "/v3/products/info/attributes"
        r = self.api_post(ep, data=json.dumps(payload))
        return r
    
    def get_awaiting_deliver_orders(self) -> dict:
        return self.get_orders_by_status(status="awaiting_deliver")
    
    def get_awaiting_packaging_orders(self) -> dict:
        """Shortcut to receive awaiting_packaging orders

        Returns:
            dict: response
        """
        return self.get_orders_by_status(status="awaiting_packaging")
    
    def get_awaiting_delivery_orders(self) -> dict:
        """Shortcut to receive awaiting_delivery orders

        Returns:
            dict: response
        """
        return self.get_orders_by_status(status="awaiting_deliver")
    
    def get_cancelled_orders(self) -> dict:
        """Shortcut to receive cancelled orders

        Returns:
            dict: response
        """
        return self.get_orders_by_status(status="cancelled")
    
    def get_client_cancelled_orders(self) -> dict:
        """Shortcut to receive client_cancelled orders

        Returns:
            dict: response
        """
        return self.get_orders_by_status(status="client_cancelled")
    
    def get_arbitration_orders(self) -> dict:
        """Shortcut to receive arbitration orders

        Returns:
            dict: response
        """
        return self.get_orders_by_status(status="arbitration")
    
    def get_client_arbitration_orders(self) -> dict:
        """Shortcut to receive arbitration orders

        Returns:
            dict: response
        """
        return self.get_orders_by_status(status="client_arbitration")
    
    def get_delivered_orders(self) -> dict:
        """Shortcut to receive delivered orders

        Returns:
            dict: response
        """
        return self.get_orders_by_status(status="delivered")
    
    def get_warehouses(self) -> dict:
        """Get list of registered warehouses

        Returns:
            dict: response
        """
        ep = "/v1/warehouse/list"
        payload = {}
        r = self.api_post(ep, data=json.dumps(payload))
        return r
    
    def get_delivery_methods(self, payload={}) -> dict:
        """Get delivery methods

        Args:
            payload (dict, optional): payload. Defaults to {}.

        Returns:
            dict: response
        """
        ep = "/v1/delivery-method/list"
        r = self.api_post(ep, data=json.dumps(payload))
        return r
    
    def get_labels(self, orderId: str) -> dict:
        """Get container labels list for an orderId

        Args:
            orderId (str): order id

        Returns:
            dict: response
        """
        payload = {"orderId": orderId}
        ep = "/v2/posting/fbs/act/get-container-labels"
        r = self.api_post(ep, data=json.dumps(payload))
        return r
    
    def get_act_transport_id(self, act_id: str) -> bytes:
        """Get PDF transport act for a given act_id

        Args:
            act_id (str): act id

        Returns:
            dict: response
        """
        payload = {"id": act_id}
        ep = "/v2/posting/fbs/act/get-pdf"
        r = self.api_post_raw(ep, data=json.dumps(payload))
        return r
    
    def package_labels(self, posting_number: str) -> bytes:
        """Get package labels for a posting

        Args:
            posting_number (str): posting number

        Returns:
            bytes: response
        """
        payload = {"posting_number": [posting_number]}
        ep = "/v2/posting/fbs/package-label"
        r = self.api_post_raw(ep, data=json.dumps(payload))
        return r
    
    def get_act_list(self, days: int = 30) -> dict:
        """Get list of acts for a given timespan

        Args:
            days (int, optional): period. Defaults to 30.

        Returns:
            dict: response
        """
        ep = "/v2/posting/fbs/act/list"
        now = datetime.datetime.now()
        month_ago = now - datetime.timedelta(days=days)
        
        date_format = "%Y-%m-%d"
        payload = {
            "filter": {
                "date_from": month_ago.strftime(date_format),
                "date_to": now.strftime(date_format),
            },
            "limit": 49
        }
        acts = self.api_post(ep, data=json.dumps(payload))
        return acts
    
    def create_acts(self, delivery_method_id: str, departure_date: str) -> dict:
        """Create acts for selected delivery_method_id

        Args:
            delivery_method_id (str): delivery method id,
            departure_date (str): departure date

        Returns:
            dict: response
        """
        
        ep = "/v2/posting/fbs/act/create"
        payload = {"delivery_method_id": delivery_method_id,
                   "departure_date": departure_date,
                   }

        acts = self.api_post(ep, data=json.dumps(payload))
        return acts

    def get_act_of_acceptance(self, transport_id: int) -> bytes:
        """Get PDF act of acceptance

        Args:
            transport_id (int): transport identifier

        Returns:
            dict: response
        """
        ep = "/v2/posting/fbs/digital/act/get-pdf"
        payload = {"id": transport_id,
                   "doc_type": "act_of_acceptance"
                   }

        acts = self.api_post_raw(ep, data=json.dumps(payload))
        return acts
    
    def ship(self, posting_number: str, packages=None) -> dict:
        """Ship the posting with products (awaiting_packaging->awaiting_delivery)

        Args:
            posting_number (str): posting number
            packages (list): list of products in package

        Returns:
            dict: response
        """
        if packages is None:
            packages = []
        ep = "/v4/posting/fbs/ship"
        payload = {
            "packages": packages,
            "posting_number": posting_number,
            "with": {"additional_data": True},
        }
        print(f"ship_payload: {payload}")
        posting = self.api_post(ep, data=json.dumps(payload))
        return posting
    
    def set_order_status(self, order_id, status) -> dict:
        orders = []
        return orders
