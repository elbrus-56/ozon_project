import os
import sys

from django.core.management.base import BaseCommand

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.tasks.get_acts_task import GetActs

"""
TASK:

озон формирует акт c отгрузками, также в pdf, он может быть сформирован в разное 
время, нужно опрашивать End Point Ozon каждые 10 мин.
Акт формируется для отгрузок на следующий день. 
Допустим в 10-00 акт пришёл. Нужно его передать в ТУС. 
также формируем временный pdf файл, передаём, формат передачи
{
id: "ваш id акта - вы формируете как угодно в строку"
date: "дата отгрузки, если таковое можно получить или +1 день от текущей даты"
"url": "..."
}
в ответ если норм
{
    "id": "",
    "status": "200"
}"45701151-0110-1"
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        ozon = GetActs()
        ozon.get_acts_task()
