import os
import platform
import sys
import requests
import datetime

parent = os.path.abspath(".")
sys.path.insert(1, parent)


def creation_date(path_to_file):
    if platform.system() == "Windows":
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


class ParsingHolidays:
    def __init__(self):
        self.data = []
    
    def _check_date_to_holidays(self, date):
        """
        Проверка нерабочих дней по производственному календарю
    
        Формат даты: YYYYMMDD или YYYY-MM-DD
    
        Args: объект даты datetime
        Returns: int
    
        0 - Рабочий день.
        1 - Нерабочий день.
        100 - Ошибка в дате.
        101 - Данные не найдены.
    
        """
        try:
            response = requests.get("https://isdayoff.ru/" + str(date))
        except Exception:
            return "Ресурс не доступен"
        else:
            return int(response.text)
    
    def _count_holidays(self, year):
        start = f"{year}" + "-01-01"
        end = f"{year}" + "-12-31"
        date_format = "%Y-%m-%d"
        
        end_year = datetime.datetime.strptime(end, date_format).date()
        date = datetime.datetime.strptime(start, date_format).date()
        
        while date <= end_year:
            response = self._check_date_to_holidays(date)
            
            if response == 1:
                self.data.append(str(date))
                print(date)
                date += datetime.timedelta(days=1)
            
            else:
                date += datetime.timedelta(days=1)
                
    def parsing_holidays(self):
        now = datetime.datetime.now()
        self._count_holidays(str(now)[0:4])
        try:
            with open("connector/tasks/holidays.txt", "w") as file:
                file.write(str(self.data))
        except:
            print("Ошибка записи в файл holidays.txt")
        


    
