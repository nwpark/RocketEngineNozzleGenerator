from .SketchUtils import *
import math

from ..NozzleDefinitions import NozzleParameters
from ..common.Common import unitsMgr


class EngineSketch:
    def __init__(self, nozzleParameters: NozzleParameters):
        self._nozzleParameters = nozzleParameters
        self._chamberLength = nozzleParameters.chamberLength
        self._exitLength = nozzleParameters.exitLength
        self._nozzleLength = self._chamberLength + self._exitLength

    def draw(self):
        # common construction lines
        exitSymmetryLine = self._drawExitSymmetryLine()
        chamberSymmetryLine = self._drawChamberSymmetryLine(exitSymmetryLine.endSketchPoint)
        # sketch
        innerWallThickness = 0.3
        channelThickness = 1.0
        outerWallThickness = 1.0
        NozzleSketch(self._nozzleParameters, exitSymmetryLine, chamberSymmetryLine).draw()
        NozzleSketch(self._nozzleParameters, exitSymmetryLine, chamberSymmetryLine, innerWallThickness).draw()
        NozzleSketch(self._nozzleParameters, exitSymmetryLine, chamberSymmetryLine, innerWallThickness + channelThickness).draw()
        NozzleSketch(self._nozzleParameters, exitSymmetryLine, chamberSymmetryLine, innerWallThickness + channelThickness + outerWallThickness).draw()

    def _drawExitSymmetryLine(self) -> SketchLine:
        endPoint = drawSketchPoint(0, self._exitLength)
        line = drawLine(getOrigin(), endPoint, LineType.CONSTRUCTION)
        applyVerticalConstraint(line)
        applyLineDimension(line)
        return line

    def _drawChamberSymmetryLine(self, yAxisThroatPoint: SketchPoint) -> SketchLine:
        endPoint = drawSketchPoint(0, self._nozzleLength)
        line = drawLine(yAxisThroatPoint, endPoint, LineType.CONSTRUCTION)
        applyVerticalConstraint(line)
        applyLineDimension(line)
        return line


class NozzleSketch:
    def __init__(
            self,
            nozzleParameters: NozzleParameters,
            exitSymmetryLine: SketchLine,
            chamberSymmetryLine: SketchLine,
            radiusOffsetInUserUnits: float = 0):
        radiusOffset = unitsMgr.convert(radiusOffsetInUserUnits, 'mm', unitsMgr.internalUnits)
        self._exitSymmetryLine = exitSymmetryLine
        self._chamberSymmetryLine = chamberSymmetryLine
        self._chamberLength = nozzleParameters.chamberLength
        self._chamberCylinderLength = nozzleParameters.chamberCylinderLength
        self._exitLength = nozzleParameters.exitLength
        self._chamberRadius = nozzleParameters.chamberRadius + radiusOffset
        self._throatRadius = nozzleParameters.throatRadius + radiusOffset
        self._exitRadius = nozzleParameters.exitRadius + radiusOffset
        self._convergenceAngle = nozzleParameters.convergenceAngle
        self._convergenceRadius = nozzleParameters.convergenceRadius
        self._divergenceRadius = nozzleParameters.divergenceRadius
        self._sketch = getActiveSketch()
        self._exitAngle = getAngleFromOppositeAdjacent(self._exitLength, self._exitRadius - self._throatRadius)
        self._nozzleLength = self._chamberLength + self._exitLength

    def draw(self):
        # construction lines
        throatRadiusLine = self._drawThroatRadiusLine(self._exitSymmetryLine.endSketchPoint)
        chamberRadiusLine = self._drawChamberRadiusLine(self._chamberSymmetryLine.endSketchPoint)

        # geometry lines
        throatPoint = throatRadiusLine.endSketchPoint
        exitLine = self._drawExitLine(throatPoint, throatRadiusLine)
        chamberLine = self._drawChamberLine(chamberRadiusLine.endSketchPoint)
        chamberConvergenceArc = self._drawChamberConvergenceArc(chamberLine.endSketchPoint)
        chamberDivergenceArc = self._drawChamberDivergenceArc(throatPoint)
        chamberConvergenceLine = self._drawChamberConvergenceLine(chamberConvergenceArc.startSketchPoint, chamberDivergenceArc.startSketchPoint)

        # constraints
        applyTangentConstraint(chamberLine, chamberConvergenceArc)
        applyTangentConstraint(chamberConvergenceLine, chamberConvergenceArc)
        applyTangentConstraint(chamberConvergenceLine, chamberDivergenceArc)
        applyTangentConstraint(chamberDivergenceArc, exitLine)

    def _drawExitSymmetryLine(self) -> SketchLine:
        endPoint = drawSketchPoint(0, self._exitLength)
        line = drawLine(getOrigin(), endPoint, LineType.CONSTRUCTION)
        applyVerticalConstraint(line)
        applyLineDimension(line)
        return line

    def _drawChamberSymmetryLine(self, yAxisThroatPoint: SketchPoint) -> SketchLine:
        endPoint = drawSketchPoint(0, self._nozzleLength)
        line = drawLine(yAxisThroatPoint, endPoint, LineType.CONSTRUCTION)
        applyVerticalConstraint(line)
        applyLineDimension(line)
        return line

    def _drawThroatRadiusLine(self, throatYAxisPoint: SketchPoint) -> SketchLine:
        endPoint = drawSketchPoint(self._throatRadius, self._exitLength)
        line = drawLine(throatYAxisPoint, endPoint, LineType.CONSTRUCTION)
        applyLineDimension(line)
        applyHorizontalConstraint(line)
        return line

    def _drawChamberRadiusLine(self, chamberYAxisPoint: SketchPoint) -> SketchLine:
        endPoint = drawSketchPoint(self._chamberRadius, self._nozzleLength)
        line = drawLine(chamberYAxisPoint, endPoint, LineType.CONSTRUCTION)
        applyLineDimension(line)
        applyHorizontalConstraint(line)
        return line

    def _drawExitLine(self, throatPoint: SketchPoint, throatRadiusLine: SketchLine) -> SketchLine:
        endPoint = drawSketchPoint(self._exitRadius, 0)
        exitLine = drawLine(throatPoint, endPoint)
        applyAngularDimension(exitLine, throatRadiusLine)
        return exitLine

    def _drawChamberLine(self, startPoint: SketchPoint) -> SketchLine:
        endPoint = drawSketchPoint(startPoint.geometry.x, startPoint.geometry.y - self._chamberCylinderLength)
        chamberLine = drawLine(startPoint, endPoint)
        applyVerticalConstraint(chamberLine)
        return chamberLine

    def _drawChamberConvergenceArc(self, startPoint: SketchPoint) -> SketchArc:
        return drawArc(startPoint, self._convergenceRadius, ArcOrientation.Q4)

    def _drawChamberDivergenceArc(self, throatPoint: SketchPoint) -> SketchArc:
        return drawArc(throatPoint, self._divergenceRadius, ArcOrientation.Q3)

    def _drawChamberConvergenceLine(self, startPoint: SketchPoint, endPoint: SketchPoint) -> SketchLine:
        yAxisNormalLineEndPoint = drawSketchPoint(endPoint.geometry.x, endPoint.geometry.y + 0.5)
        yAxisNormalLine = drawLine(endPoint, yAxisNormalLineEndPoint, LineType.CONSTRUCTION)
        chamberConvergenceLine = drawLine(endPoint, startPoint)
        applyVerticalConstraint(yAxisNormalLine)
        applyAngularDimension(chamberConvergenceLine, yAxisNormalLine, -self._convergenceAngle)
        return chamberConvergenceLine


def getAngleFromOppositeAdjacent(opposite: float, adjacent: float) -> float:
    radians = math.atan2(opposite, adjacent)
    degrees = math.degrees(radians)
    return degrees
