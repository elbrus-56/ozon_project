import os
import sys

from loguru import logger
from py3dbp import Packer, Bin, Item

parent = os.path.abspath("..")
sys.path.insert(1, parent)

logger.add("ozon.log")


from connector.config import MAX_LENGTH, MAX_HEIGHT, MAX_DEPTH, MAX_WEIGHT
from connector.ozon_manager import OzonManager


class Package:
    def __init__(self):
        self.packer = Packer()
        self.result = True
    
    def new_bin(self, custom_weight, bin_id=0):
        """Creates new bin

        Args:
            bin_id (int, optional): bin id. Defaults to 0.
            custom_weight (float):

        Returns:
            Bin: new posting bin
        """
        
        return Bin(f"pack_{bin_id}", MAX_LENGTH, MAX_HEIGHT, MAX_DEPTH, custom_weight)
    
    def count_bins(self, products, custom_weight, max_bins=100) -> int:
        """Calculate needed count bins for a given product list

        Args:
            products (list): list of products.
            custom_weight(int): custom box weight.
            max_bins (int, optional): maximum bins allowed. Defaults to 100.
            

        Returns:
            int : count of bins needed
        """
        
        for box_no in range(max_bins):
            self.packer = Packer()
            for i in range(box_no):
                self.packer.add_bin(self.new_bin(custom_weight, box_no))
            for p in products:
                self.packer.add_item(Item(*p))
            self.packer.pack(distribute_items=True)
            for b in self.packer.bins:
                if len(b.unfitted_items) == 0:
                    return box_no
        return max_bins
    
    def pack(self, products, custom_weight, verbose=False):
        """Create list of packages for a given product list

        Args:
            products (list): product list from order.
            custom_weight(int): custom box weight.
            verbose (bool, optional): output calculations to screen. Defaults to False.

        Returns:
            list of lists : [[offer_id_1, offer_id_2], [offer_id_2, offer_id_2]]
        """
        MAX_PRODUCT_WEIGHT = 0.8 * custom_weight
        # products = [p["offer_id"], p["width"], p["height"], p["depth"], p["weight"]]
        
        # filter out heavy products to separate postings (4 goes for weight)
        if sum([p[4] for p in products]) > custom_weight:
            postings = [[p[0]] for p in products if p[4] >= MAX_PRODUCT_WEIGHT] # товары, у которых вес больше нужного
            rest_products = [p for p in products if p[4] < MAX_PRODUCT_WEIGHT] # товары у которых вес меньше нужного
        else:
            rest_products = products
            postings = []
        
        # calculate postings needed for the rest of products
        bins = self.count_bins(rest_products, custom_weight)
        
        # initialize packer
        self.packer = Packer()
        
        # add bins
        for bin_id in range(bins):
            self.packer.add_bin(self.new_bin(custom_weight, bin_id))
        
        # add products
        for p in rest_products:
            self.packer.add_item(Item(*p))
        
        # distribute products among bins
        self.packer.pack(distribute_items=True)
        
        if verbose:
            logger.debug(f"Количество упаковок :{len(self.packer.bins)})")
            # если количество упаковок более 1шт, то пока ручная обработка
            if len(self.packer.bins) > 1:
                self.result = False
            for i, b in enumerate(self.packer.bins):
                
                logger.debug((f"Упаковка {i},", b.string()))  # Печатает размер озоновской коробки
                
                logger.debug(f"Поместилось {len(b.items)} товаров")
                
                for item in b.items:
                    logger.debug(item.string())  # печатает офферИД и размеры каждого товара
                
                logger.debug(f"Не поместилось {len(b.unfitted_items)}:")
                
                for item in b.unfitted_items:
                    logger.debug("XXX", item.string())
        
        for b in self.packer.bins:
            if len(b.items) > 0:
                postings.append([item.name for item in b.items])
        return postings, self.result


def get_product_list_for_packaging(order):
    products = []
    om = OzonManager()
    
    products = [product["offer_id"] for product in order["products"]]
    product_quantities = {
        product["offer_id"]: product["quantity"] for product in order["products"]
    }
    
    dimensions = om.get_dimensions(products)  # Сделаем запрос к озону и соберем атрибуты товара вес
    
    product_dimensions = {
        o["offer_id"]: [o["width"], o["height"], o["depth"], o["weight"]]
        for o in dimensions["result"]
    }
    product_data = []
    
    for p, q in product_quantities.items():
        for i in range(q):
            product_data.append([p, *product_dimensions[p]])
    return product_data


def get_order_pcs(order):
    return sum([int(p['quantity']) for p in order['products']])


def build_packages(order, custom_weight=MAX_WEIGHT):
    package = Package()
    product_data = get_product_list_for_packaging(order)
    return package.pack(product_data, custom_weight, True)


