from django.core.management.base import BaseCommand

"""
После отправки акта нужно подтвердить отгрузку в ОЗОН (у них это называется
запрос тайм-слота) и уведомить ТУС о получении тайм-слота по этому акту.
примерный json
{
    id: "ваш id акта "
    date: ""
    timeslot: ""
    status: ""
}
в ответ если норм
{
    "id": "",
    "status": "200"
}
 

"""


class Command(BaseCommand):
    help = "Get reception timeslot"

    def handle(self, *args, **options):
        print("?Not implemented in Ozon API yet?")
