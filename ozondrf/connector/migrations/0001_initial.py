# Generated by Django 4.1.3 on 2023-01-08 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "posting_number",
                    models.CharField(max_length=30, primary_key=True, serialize=False),
                ),
                ("order_id", models.IntegerField()),
                ("status", models.CharField(max_length=30)),
                ("delivery_method_warehouse_id", models.IntegerField(null=True)),
                (
                    "delivery_method_tpl_provider_id",
                    models.CharField(max_length=15, null=True),
                ),
                ("tracking_number", models.CharField(max_length=30, null=True)),
                ("in_process_at", models.DateTimeField(null=True)),
                ("shipment_date", models.DateTimeField(null=True)),
                ("delivering_date", models.DateTimeField(null=True)),
                ("cancellation", models.BooleanField(null=True)),
                ("cancellation_initiator", models.CharField(max_length=15)),
                ("customer", models.CharField(max_length=60, null=True)),
                ("addressee", models.CharField(max_length=120, null=True)),
                ("barcodes", models.CharField(max_length=60, null=True)),
            ],
            options={
                "db_table": "ozon_orders",
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("offer_id", models.CharField(max_length=20)),
                ("name", models.CharField(max_length=128)),
                ("sku", models.CharField(max_length=30)),
                ("quantity", models.IntegerField()),
                ("price", models.FloatField()),
                ("currency_code", models.CharField(max_length=3)),
                ("mandatory_mark", models.CharField(max_length=30)),
                (
                    "order",
                    models.ManyToManyField(
                        related_name="product_orders", to="connector.order"
                    ),
                ),
            ],
            options={
                "db_table": "ozon_products",
            },
        ),
        migrations.AddField(
            model_name="order",
            name="products",
            field=models.ManyToManyField(
                null=True, related_name="order_product", to="connector.product"
            ),
        ),
    ]
