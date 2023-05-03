import sys
import os

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from ozondrf.celery import app

from connector.tasks.get_acts_task import GetActs
from connector.tasks.get_pdf_labels_task import GetPdfLabels
from connector.tasks.clean_up_task import CleanUp
from connector.tasks.get_dop_statuses_task import GetDopStatuses
from connector.tasks.notify_arbitration_task import NotifyArbitration
from connector.tasks.notify_cancelled_task import NotifyCancelled
from connector.tasks.notify_client_arbitration_task import NotifyClientArbitration
from connector.tasks.process_orders_task import ProcessOrder
from connector.tasks.process_reorders_task import ProcessReorders


@app.task
def cleanup_task(days=30):
    task = CleanUp()
    return task.cleanup_task(days=days)


@app.task
def process_orders_task():
    task = ProcessOrder()
    return task.process_orders_task()


@app.task
def process_reorders_task():
    task = ProcessReorders()
    return task.process_reorders_task()


@app.task
def notify_cancelled(email=True, telegram=True):
    task = NotifyCancelled()
    return task.notify_cancelled(email=email, telegram=telegram)


@app.task
def notify_arbitration(email=True, telegram=True):
    task = NotifyArbitration()
    return task.notify_arbitration(email=email, telegram=telegram)


@app.task
def notify_client_arbitration(email=True, telegram=True):
    task = NotifyClientArbitration()
    return task.notify_client_arbitration(email=email, telegram=telegram)


@app.task
def get_pdf_labels_task():
    task = GetPdfLabels()
    task.get_pdf_labels_task()


@app.task
def get_dop_statuses_task():
    task = GetDopStatuses()
    task.get_dop_statuses()


@app.task
def create_statuses_report_task():
    task = GetDopStatuses()
    task.create_statuses_report()


@app.task
def get_acts_task():
    task = GetActs()
    task.get_acts_task()


app.autodiscover_tasks()
