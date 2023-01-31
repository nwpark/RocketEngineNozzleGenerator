from adsk.core import CommandCreatedEventArgs, NamedValues, CommandCreatedEventHandler, CommandInputs

from .OnDestroyHandler import OnDestroyHandler
from .OnExecuteHandler import OnExecuteHandler
from .UserParameters import UserParameters
from .OnInputChangedHandler import OnInputChangedHandler
from .common.Common import ui, printTrace, resourceFolder


class GenerateNozzleCommand:
    def __init__(self):
        self._commandCreatedHandler = self._CommandCreatedHandler()
        self._commandDefinition = ui.commandDefinitions.itemById('NozzleGenerator')
        if not self._commandDefinition:
            self._commandDefinition = ui.commandDefinitions.addButtonDefinition('NozzleGenerator', 'Generate Nozzle',
                                                                                'Generates a nozzle.', resourceFolder)
        self._commandDefinition.commandCreated.add(self._commandCreatedHandler)

    def execute(self):
        inputs = NamedValues.create()
        self._commandDefinition.execute(inputs)

    # Event handler for the commandCreated event.
    class _CommandCreatedHandler(CommandCreatedEventHandler):
        def __init__(self):
            super().__init__()
            self._onInputChangedHandler = None
            self._onExecuteHandler = None
            self._onExecutePreviewHandler = None
            self._onDestroyHandler = None

        def notify(self, args: CommandCreatedEventArgs):
            try:
                cmd = args.command
                cmd.isRepeatable = False

                self._onInputChangedHandler = OnInputChangedHandler()
                self._onExecuteHandler = OnExecuteHandler()
                self._onExecutePreviewHandler = OnExecuteHandler()
                self._onDestroyHandler = OnDestroyHandler()
                cmd.inputChanged.add(self._onInputChangedHandler)
                cmd.execute.add(self._onExecuteHandler)
                cmd.executePreview.add(self._onExecutePreviewHandler)
                cmd.destroy.add(self._onDestroyHandler)

                for userParameter in UserParameters.getAllParameters():
                    userParameter.addToCommandInputs(cmd.commandInputs)
            except:
                printTrace()
