import json
import sys, os
import django
import requests

parent = os.path.abspath("..")
sys.path.insert(1, parent)
sys.path.append("../..")
sys.path.append("../../connector")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "connector.settings")
django.setup()

from connector.config import *
from django.core.mail import EmailMessage


# content = os.path.abspath("0119859129-0006-1.pdf")
# print(content)
with open("0119859129-0006-1.pdf", "rb") as file:
    content = file.read()
email = EmailMessage(
        subject="test1",
        body="test",
        from_email=SENDER,
        to=COMMON_ADDRESSES
    )
# email.attach("123.pdf", content)
email.send(fail_silently=False)

