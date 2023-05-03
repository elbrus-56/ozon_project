import io
import os
import sys

import django
from rest_framework import serializers

parent = os.path.abspath("..")
sys.path.insert(1, parent)
sys.path.append("../..")
sys.path.append("../../connector")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "connector.settings")
django.setup()

from connector.models import *
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer


class PayloadGetActsModel:
    def __init__(self, delivery_method_id, departure_date):
        """
        Имитируем модель django
        """
        self.delivery_method_id = delivery_method_id
        self.departure_date = departure_date

    @classmethod
    def encode_JSON(cls, delivery_method_id, departure_date):
        model = PayloadGetActsModel(delivery_method_id, departure_date)
        model_sr = PayloadGetActsSerializer(model)
        print(model_sr.data)
        return JSONRenderer().render(model_sr.data)

    @classmethod
    def decode_JSON(self, value):
        stream = io.BytesIO(value)
        data = JSONParser().parse(stream)
        serializer = PayloadGetActsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


class PayloadGetActsSerializer(serializers.Serializer):
    delivery_method_id = serializers.IntegerField()
    departure_date = serializers.DateField(format="%Y-%m-%dT%H:%M:%SZ", input_formats=["%Y-%m-%dT%H:%M:%SZ"])

    # posting_number = serializers.ListField(child=serializers.CharField())

    def validate_departure_date(self, value):
        return value.strftime("%Y-%m-%dT%H:%M:%SZ") if value else value


class NewOrderSerializer(serializers.ModelSerializer):
    tracking_number = serializers.CharField(max_length=30, allow_blank=True)
    cancellation_initiator = serializers.CharField(max_length=15, allow_blank=True)
    barcodes = serializers.DictField(child=serializers.CharField())

    class Meta:
        model = Order
        # fields = "__all__"
        exclude = ["products"]


class ProductsSerializer(serializers.ModelSerializer):
    mandatory_mark = serializers.ListSerializer(child=serializers.CharField(allow_blank=True), allow_empty=True)
    order = serializers.CharField()

    class Meta:
        model = Product
        fields = "__all__"
        # exclude = ["order"]

    def create(self, validated_data):
        order = validated_data.pop("order")
        product = Product.objects.create(**validated_data)
        product.order.add(order)
        return product
