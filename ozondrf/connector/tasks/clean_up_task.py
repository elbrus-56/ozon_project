import datetime
import os
import platform
import sys

from loguru import logger

parent = os.path.abspath(".")
sys.path.insert(1, parent)

from connector.config import STATIC_PATH
from connector.tusmk import TusMK
from connector.ozon_manager import OzonManager


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


class CleanUp:
    def __init__(self):
        self.om = OzonManager()
        self.tusmk = TusMK()
    
    def cleanup_task(self, days=30):
        now = datetime.datetime.now().timestamp()
        period = int(days) * 24 * 60 * 60 * 1000
        for f in os.listdir(STATIC_PATH):
            fullpath = os.path.join(STATIC_PATH, f)
            if now - creation_date(fullpath) > period:
                os.remove(fullpath)
        logger.info("Cleaned files")
        return True
