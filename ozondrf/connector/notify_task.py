import sys
import os
import requests
import json

from ozondrf.celery import app

parent = os.path.abspath(".")
sys.path.insert(1, parent)


from connector.config import TELEGRAM_BOT_TOKEN, CHANNEL_ID, SENDER, COMMON_ADDRESSES_PROD
from django.core.mail import EmailMessage


@app.task
def send_email_task(subject, message, attachments):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=SENDER,
        to=COMMON_ADDRESSES_PROD,
    )

    if attachments:
        filename, content, mimetype = attachments
        try:
            with open(content, "rb") as file:
                content = file.read()
        except Exception:
            print(f"Файл {content} не найден")
        email.attach(filename, content, mimetype)

    email.send(fail_silently=False)


@app.task
def notify_task(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={CHANNEL_ID}&text={message}"
    r = requests.get(url)
    return r.text


@app.task
def sendDocument_task(document_file):
    document = open(document_file, "rb")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    response = requests.post(
        url, data={"chat_id": CHANNEL_ID}, files={"document": document}
    )
    content = response.content.decode("utf8")
    js = json.loads(content)
    return js
