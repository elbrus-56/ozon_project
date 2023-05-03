import requests
from loguru import logger

SMSC_LOGIN = "login"  # логин клиента
SMSC_PASSWORD = "password"  # пароль
SMSC_URL = "https://smsc.ru/sys/send.php"

SMSC_POST = False  # использовать метод POST
SMSC_HTTPS = False  # использовать HTTPS протокол
SMSC_CHARSET = "utf-8"  # кодировка сообщения (windows-1251 или koi8-r), по умолчанию используется utf-8
SMSC_DEBUG = False  # флаг отладки

message_1 = "Заказ № {order_number} готов к выдаче. Телефон: 88001005441. МК Электро"
message_2 = "Спасибо за покупку! Будем рады Вашему отзыву: https://mkelektro.ru/rev"


def check_status_order():
    """Функция проверяет доставлен ли заказ в ПВЗ"""
    url = "https://api.boxberry.ru/json.php?method=ListStatuses&token=d6f33e419c16131e5325cbd84d5d6000&ImId=XXXXXX"


class SMSService:

    def __init__(self):
        self.login = SMSC_LOGIN
        self.password = SMSC_PASSWORD
        self.url = SMSC_URL

    def send_sms(self, message: str, phone_number: int):
        """
        Функция отправляет СМС уведомления

        Args:
            message (str): текст отправляемого сообщения.
            phone_number (int): номер телефона получателя в формате 79998887766

        Returns:
            dict: response
        """
        data = {
            "login": self.login,
            "psw": self.password,
            "phones": 0,
            "mes": message
        }
        try:
            r = requests.post(self.url, data=data)
        except Exception as e:
            logger.error(f"Error sending POST request {self.url}  with {data}- {e}")
            return None
        else:
            try:
                r = json.loads(r.content)
            except Exception as e:
                logger.error(f"Error POST request returning response {self.url} - {e}")
                return None
            return r


# Вспомогательная функция, эмуляция тернарной операции ?:
def ifs(cond, val1, val2):
    if cond:
        return val1
    return val2


class SMS(object):

    # Метод отправки SMS
    #
    # обязательные параметры:
    #
    # phones - список телефонов через запятую или точку с запятой
    # message - отправляемое сообщение
    #
    # необязательные параметры:
    #
    # translit - переводить или нет в транслит (1,2 или 0) time - необходимое время доставки в виде строки (
    # DDMMYYhhmm, h1-h2, 0ts, +m) id - идентификатор сообщения. Представляет собой 32-битное число в диапазоне от 1
    # до 2147483647. format - формат сообщения (0 - обычное sms, 1 - flash-sms, 2 - wap-push, 3 - hlr, 4 - bin,
    # 5 - bin-hex, 6 - ping-sms, 7 - mms, 8 - mail, 9 - call, 10 - viber, 11 - soc) sender - имя отправителя (Sender
    # ID). query - строка дополнительных параметров, добавляемая в URL-запрос ("valid=01:00&maxsms=3")
    #
    # возвращает массив (<id>, <количество sms>, <стоимость>, <баланс>) в случае успешной отправки
    # либо массив (<id>, -<код ошибки>) в случае ошибки

    def send_sms(self, phones, message, translit=0, time="", id=0, format=0, sender=False, query=""):
        formats = ["flash=1", "push=1", "hlr=1", "bin=1", "bin=2", "ping=1", "mms=1", "mail=1", "call=1", "viber=1",
                   "soc=1"]

        m = self._smsc_send_cmd("send", "cost=3&phones=" + quote(phones) + "&mes=" + quote(message) + \
                                "&translit=" + str(translit) + "&id=" + str(id) + ifs(format > 0,
                                                                                      "&" + formats[format - 1], "") + \
                                ifs(sender == False, "", "&sender=" + quote(str(sender))) + \
                                ifs(time, "&time=" + quote(time), "") + ifs(query, "&" + query, ""))

        # (id, cnt, cost, balance) или (id, -error)

        if SMSC_DEBUG:
            if m[1] > "0":
                print("Сообщение отправлено успешно. ID: " + m[0] + ", всего SMS: " + m[1] + ", стоимость: " + m[
                    2] + ", баланс: " + m[3])
            else:
                print("Ошибка №" + m[1][1:] + ifs(m[0] > "0", ", ID: " + m[0], ""))

        return m

    @staticmethod
    def _smsc_send_cmd(cmd, arg=""):
        url = ifs(SMSC_HTTPS, "https", "http") + "://smsc.ru/sys/" + cmd + ".php"
        _url = url
        arg = "login=" + quote(SMSC_LOGIN) + "&psw=" + quote(
            SMSC_PASSWORD) + "&fmt=1&charset=" + SMSC_CHARSET + "&" + arg

        i = 0
        ret = ""

        while ret == "" and i <= 5:
            if i > 0:
                url = _url.replace("smsc.ru/", "www" + str(i) + ".smsc.ru/")
            else:
                i += 1

            try:
                if SMSC_POST or len(arg) > 2000:
                    data = urlopen(url, arg.encode(SMSC_CHARSET))
                else:
                    data = urlopen(url + "?" + arg)

                ret = str(data.read().decode(SMSC_CHARSET))
            except:
                ret = ""

            i += 1

        if ret == "":
            if SMSC_DEBUG:
                print("Ошибка чтения адреса: " + url)
            ret = ","  # фиктивный ответ

        return ret.split(",")
