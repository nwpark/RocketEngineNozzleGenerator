import math

from adsk.core import Point3D, CommandEventArgs, CommandEventHandler
from adsk.fusion import FeatureOperations, SketchPoint, Component

from .UserParameters import UserParameters
from .common.Common import printTrace, ui, design
from .sketch.SketchUtils import createNewComponent, extrudeProfile, createXYSketch, createCylinder
from .sketch.NozzleSketch import NozzleSketch, EngineSketch


class OnExecuteHandler(CommandEventHandler):
    def __init__(self):
        super().__init__()
        self._boltThickness = 0.25

    def notify(self, args: CommandEventArgs):
        try:
            # TODO: different behavior if preview (set `args.isValidResult = False` when rendering preview)
            # ui.messageBox(args.firingEvent.name)
            UserParameters.updateValuesFromCommandInputs(args.firingEvent.sender.commandInputs)
            self.run()
            args.isValidResult = True
        except:
            printTrace()

    def run(self):
        EngineSketch(UserParameters.getNozzleParameters()).draw()
