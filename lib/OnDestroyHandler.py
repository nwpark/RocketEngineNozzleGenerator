import adsk.core
from adsk.core import CommandEventHandler

from .common.Common import printTrace


class OnDestroyHandler(CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            adsk.terminate()
        except:
            printTrace()
