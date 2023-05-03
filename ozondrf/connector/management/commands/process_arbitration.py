from django.core.management.base import BaseCommand
import sys, os, django

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.tasks.notify_arbitration_task import NotifyArbitration

"""
По статусам "arbitration", "client_arbitration", "cancelled" сервис должен
отправлять сообщение в телеграм и на почту (Список email №2). Правильно сделать отдельные
обработчики и отдельные задания для этих обработчиков (отправка telegram,email)

Заказы со статусами "cancelled" нужно удалять из таблицы ozon_orders.

При появлении заказа со статуами "arbitration", "client_arbitration", нужно отправить уведомления в телеграм и на почту (Список 2).
Повторять уведомления в 08.00 MSK каждого дня.

При любом изменении статуса отправлять оповещение в телеграм канал.
"""


class Command(BaseCommand):

    help = "Send arbitration orders notifications"

    def add_arguments(self, parser):

        parser.add_argument(
            "-e", "--email", action="store_true", default=False, help="Send email"
        )

        parser.add_argument(
            "-t",
            "--telegram",
            action="store_true",
            default=False,
            help="Notify telegram",
        )

    def handle(self, *args, **options):
        ozon = NotifyArbitration()
        ozon.notify_arbitration(options["email"], options["telegram"])
