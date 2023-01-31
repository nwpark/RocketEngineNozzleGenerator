# Author-Nick Park
# Description-Generate nozzle sketch

import adsk.cam
import adsk.core
import adsk.fusion

from .lib.GenerateNozzleCommand import GenerateNozzleCommand
from .lib.common.Common import ui, design, printTrace

# maintain a global reference to command to keep its handlers alive
command = None


def run(context):
    try:
        if not design:
            ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
            return

        global command
        command = GenerateNozzleCommand()
        command.execute()

        adsk.autoTerminate(False)
    except:
        printTrace()
