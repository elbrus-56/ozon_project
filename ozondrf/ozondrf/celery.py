import os
import sys
from celery import Celery
from celery.schedules import crontab

parent = os.path.abspath(".")
sys.path.insert(1, parent)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ozondrf.settings")
app = Celery("ozondrf")
app.config_from_object("django.conf:settings", namespace="CELERY")


# заносим таски в очередь
app.conf.beat_schedule = {
    "process_orders_task": {
        "task": "connector.task.process_orders_task",
        "schedule": crontab(
            minute="*"
        ),  # по умолчанию выполняет каждую минуту, очень гибко
    },
    "process_reorders_task": {
        "task": "connector.task.process_reorders_task",
        "schedule": crontab(
            minute="*"
        ),  # по умолчанию выполняет каждую минуту, очень гибко
    },
    "cleanup_task": {
        "task": "connector.task.cleanup_task",
        "schedule": crontab(
            minute="*/15"
        ),  # по умолчанию выполняет каждую минуту, очень гибко
    },
    "notify_cancelled": {
        "task": "connector.task.notify_cancelled",
        "schedule": crontab(
            minute="*/2"
        ),  # по умолчанию выполняет каждую минуту, очень гибко
    },
    "notify_arbitration": {
        "task": "connector.task.notify_arbitration",
        "schedule": crontab(
            minute="*/2"
        ),  # по умолчанию выполняет каждую минуту, очень гибко
    },
    "notify_client_arbitration": {
        "task": "connector.task.notify_client_arbitration",
        "schedule": crontab(
            minute="*/2"
        ),  # по умолчанию выполняет каждую минуту, очень гибко
    },
    "get_pdf_labels_task": {
        "task": "connector.task.get_pdf_labels_task",
        "schedule": crontab(
            minute="*/2"
        ),  # по умолчанию выполняет каждую минуту, очень гибко
    },
    "get_acts_task": {
        "task": "connector.task.get_acts_task",
        "schedule": crontab(
            minute="*"
        ),  # по умолчанию выполняет каждую минуту, очень гибко
    },  # настраивается
    "get_dop_statuses_task": {
        "task": "connector.task.get_dop_statuses_task",
        "schedule": crontab(
            minute="*/30"
        ),  # по умолчанию выполняет каждую минуту, очень гибко
    },  # настраивается
    "create_statuses_report_task": {
        "task": "connector.task.create_statuses_report_task",
        "schedule": crontab(
            # minute="*"
            hour="4, 9", minute="0, 0"
        ),  # по умолчанию выполняет каждую минуту, очень гибко
    },  # настраивается
    "parsing_holidays": {
        "task": "connector.task.parsing_holidays",
        "schedule": crontab(
            0, 0, day_of_month="31", month_of_year="12"
        ),  # по умолчанию выполняет каждую минуту, очень гибко
    },  # настраивается
}
