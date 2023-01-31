import traceback

from adsk.core import Application
from adsk.fusion import Design

ui = Application.get().userInterface
unitsMgr = Application.get().activeProduct.unitsManager
design = Design.cast(Application.get().activeProduct)
resourceFolder = './resources'


def printTrace():
    ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
