from django.core.management.base import BaseCommand
import sys, os, django

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.tasks.process_orders_task import ProcessOrder

"""
TASK 
I. Написать сервис, который опрашивает данные о заказах и контролирует изменение статусов заказа.

Новый заказ будет иметь статус "awaiting_packaging",
его нужно перевести в статус "awaiting_deliver" в ОЗОН если суммарные габариты ДхШхВ всех позиций заказа (с учётом кол-ва товаров в позиции)
не превышают 179х79х79 см и их суммарный вес не превышает 24.9 кг.
Так же нужно отправить сообщения в телеграмм и на почту (список email №1)

Если габариты или вес превышают указанные параметры,
то нужно разбить заказ на несколько (как можно меньше) отправлений и уже им  поставить статус "awaiting_deliver".

Сервис должен запускаться как command.
https://habr.com/ru/post/415049/

Результатом работы должна быть таблица заданий на отправку в ТУС МК json "отправления
для Озон". Нужно разработать и согласовать схему такого json.
"""


class Command(BaseCommand):
    def handle(self, *args, **options):

        # initialize Ozon and TUS MK interfaces
        ozon = ProcessOrder()
        ozon.process_orders_task()
