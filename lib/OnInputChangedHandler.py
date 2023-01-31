from adsk.core import InputChangedEventHandler, InputChangedEventArgs

from .UserParameters import UserParameters
from .common.Common import printTrace


class OnInputChangedHandler(InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args: InputChangedEventArgs):
        try:
            # update parameters according to the selected thread definition
            if args.input.id == UserParameters.NOZZLE_DEFINITION_DROPDOWN.value.getId():
                UserParameters.applySelectedNozzleDefinition()
        except:
            printTrace()
