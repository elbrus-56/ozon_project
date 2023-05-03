import os
import sys

from django.core.management.base import BaseCommand

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.tasks.clean_up_task import CleanUp

"""
TASK
нужно очищать временные файлы, когда они уже не нужны
"""


class Command(BaseCommand):
    help = "Cleanup  old  static files"

    def add_arguments(self, parser):

        parser.add_argument(
            "-d",
            "--days",
            action="store",
            default=30,
            type=int,
            help="Days, older files to delete",
        )

    def handle(self, *args, **options):
        if options["days"]:
            days = options["days"]
        else:
            days = 30
        ozon = CleanUp()
        ozon.cleanup_task(days)
