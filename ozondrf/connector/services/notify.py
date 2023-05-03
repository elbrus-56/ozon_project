import os
import sys

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from loguru import logger
from connector.notify_task import send_email_task, notify_task, sendDocument_task

logger.add("ozon.log")


class Notify:

    @classmethod
    def sendDocument(cls, document_file: str) -> str:
        """Sends document to telegram CHANNEL_ID

        Args:
            document_file (str): path to binary file.

        Returns:
            str: json response
        """
        return sendDocument_task.delay(document_file)

    @classmethod
    def notify(cls, message: str) -> str:
        """Отправка уведомлений (запросов в телеграм канал для отладки)

        Args:
            message (str): сообщение для отправки

        Returns:
            str: ответ api
        """
        return notify_task.delay(message)

    @classmethod
    def send_email(cls, subject: str = None, message: str = None, attachments: tuple = None) -> None:
        """Отправка уведомлений на электронную почту

            Args:
                subject (str): тема письма
                message (str): сообщение для отправки
                attachments (tuple): вложения

            Returns:
                int: 1 if True else 0
        """
        return send_email_task.delay(subject, message, attachments)

