from django.db import models


# Create your models here.
class Product(models.Model):
    offer_id = models.CharField(max_length=20)
    name = models.CharField(max_length=128)
    sku = models.CharField(max_length=30)
    quantity = models.IntegerField()
    price = models.FloatField()
    order = models.ManyToManyField("Order", related_name="product_orders")
    currency_code = models.CharField(max_length=3)
    mandatory_mark = models.CharField(max_length=30)

    class Meta:
        db_table = "ozon_products"


class Order(models.Model):
    posting_number = models.CharField(max_length=30, primary_key=True)
    order_id = models.IntegerField()
    tusmk_id = models.CharField(max_length=60, null=True)
    status = models.CharField(max_length=30)
    delivery_method_warehouse_id = models.IntegerField(null=True)
    delivery_method_tpl_provider_id = models.CharField(max_length=15, null=True)
    tracking_number = models.CharField(max_length=30, null=True)
    in_process_at = models.DateTimeField(null=True)
    shipment_date = models.DateTimeField(null=True)
    delivering_date = models.DateTimeField(null=True)
    cancellation = models.BooleanField(null=True)
    cancellation_initiator = models.CharField(max_length=15)
    customer = models.CharField(max_length=60, null=True)
    addressee = models.CharField(max_length=120, null=True)
    barcodes = models.CharField(max_length=60, null=True)
    products = models.ManyToManyField("Product", related_name="order_product")

    class Meta:
        db_table = "ozon_orders"
