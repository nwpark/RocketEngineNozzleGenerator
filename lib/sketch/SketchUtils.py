import math
from enum import Enum

from adsk.core import Point3D, ValueInput, Matrix3D, Application
from adsk.fusion import Sketch, Component, Profile, FeatureOperations, ExtrudeFeature, SketchCurve, SketchLine, \
    SketchPoint, DimensionOrientations, SketchArc

from ..common.Common import design, ui


class LineType(Enum):
    NORMAL = 1
    CONSTRUCTION = 2


class ArcOrientation(Enum):
    Q1 = 1
    Q2 = 2
    Q3 = 3
    Q4 = 4


# Getters --------------------------------------------------------------------------------------------------------------


def getActiveSketch() -> Sketch:
    return Sketch.cast(Application.get().activeEditObject)


def getOrigin() -> SketchPoint:
    return getActiveSketch().originPoint


# Drawing --------------------------------------------------------------------------------------------------------------


def drawSketchPoint(x: float, y: float) -> SketchPoint:
    sketch = getActiveSketch()
    point = Point3D.create(x, y, 0)
    return sketch.sketchPoints.add(point)


def drawLine(startPoint: SketchPoint, endPoint: SketchPoint, lineType: LineType = LineType.NORMAL) -> SketchLine:
    sketch = getActiveSketch()
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(startPoint, endPoint)
    line.isConstruction = lineType == LineType.CONSTRUCTION
    return line


def drawArc(startPoint: SketchPoint, radius: float, orientation: ArcOrientation) -> SketchArc:
    sketch = getActiveSketch()
    startPointX, startPointY = startPoint.geometry.x, startPoint.geometry.y
    centerPoint = Point3D.create(startPointX - radius, startPointY, 0)
    sweepAngle = math.radians(45.0)
    if orientation == ArcOrientation.Q2 or orientation == ArcOrientation.Q3:
        centerPoint = Point3D.create(startPointX + radius, startPointY, 0)
    if orientation == ArcOrientation.Q3 or orientation == ArcOrientation.Q4:
        sweepAngle = math.radians(-45.0)
    arc = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(centerPoint, startPoint, sweepAngle)
    applyDistanceDimension(startPoint, arc.centerSketchPoint)
    return arc


# Constraints ----------------------------------------------------------------------------------------------------------


def applyAngularDimension(lineA: SketchLine, lineB: SketchLine, angle: float = None):
    sketch = getActiveSketch()
    textPoint = getAngularDimensionTextPoint(lineA, lineB)
    angularDimension = sketch.sketchDimensions.addAngularDimension(lineA, lineB, textPoint, True)
    if angle is not None:
        angularDimension.parameter.value = angle


def getAngularDimensionTextPoint(lineA: SketchLine, lineB: SketchLine) -> Point3D:
    startPointA, startPointB = lineA.startSketchPoint.geometry, lineB.startSketchPoint.geometry
    endPointA, endPointB = lineA.endSketchPoint.geometry, lineB.endSketchPoint.geometry
    if startPointA.isEqualTo(startPointB) or startPointA.isEqualTo(endPointB):
        return startPointB
    return startPointA


def applyLineDimension(line: SketchLine):
    applyDistanceDimension(line.startSketchPoint, line.endSketchPoint)


def applyDistanceDimension(startPoint: SketchPoint, endPoint: SketchPoint):
    sketch = getActiveSketch()
    textPoint = getDistanceDimensionTextPoint(startPoint.geometry, endPoint.geometry)
    orientation = DimensionOrientations.AlignedDimensionOrientation
    sketch.sketchDimensions.addDistanceDimension(startPoint, endPoint, orientation, textPoint, True)


def getDistanceDimensionTextPoint(p1: Point3D, p2: Point3D, distance: float = -0.05) -> Point3D:
    midPoint = Point3D.create((p1.x + p2.x) / 2, (p1.y + p2.y) / 2, 0)
    if p2.x - p1.x == 0:
        return Point3D.create(midPoint.x + distance, midPoint.y, 0)
    if p2.y - p1.y == 0:
        return Point3D.create(midPoint.x, midPoint.y + distance, 0)

    slope = (p2.y - p1.y) / (p2.x - p1.x)
    normal_slope = -1 / slope
    delta_x = distance / ((normal_slope ** 2 + 1) ** 0.5)
    delta_y = delta_x * normal_slope
    if p1.x <= p2.x:
        return Point3D.create(midPoint.x + delta_x, midPoint.y + delta_y, 0)
    else:
        return Point3D.create(midPoint.x - delta_x, midPoint.y - delta_y, 0)


def applyVerticalConstraint(line: SketchLine):
    sketch = getActiveSketch()
    sketch.geometricConstraints.addVertical(line)


def applyHorizontalConstraint(line: SketchLine):
    sketch = getActiveSketch()
    sketch.geometricConstraints.addHorizontal(line)


def applyTangentConstraint(curveA: SketchCurve, curveB: SketchCurve):
    sketch = getActiveSketch()
    sketch.geometricConstraints.addTangent(curveA, curveB)


# Legacy ---------------------------------------------------------------------------------------------------------------


def createNewComponent() -> Component:
    allOccurrences = design.rootComponent.occurrences
    newOccurrence = allOccurrences.addNewComponent(Matrix3D.create())
    if newOccurrence.component is None:
        raise ('New component failed to create', 'New Component Failed')
    return newOccurrence.component


def createXYSketch(component: Component) -> Sketch:
    return component.sketches.add(component.xYConstructionPlane)


def createXZSketch(component: Component) -> Sketch:
    return component.sketches.add(component.xZConstructionPlane)


def createCylinder(component: Component, center: Point3D, diameter: float, height: float):
    sketch = createXYSketch(component)
    profile = drawCircle(sketch, center, diameter)
    extrudeProfile(component, profile, height)


def drawCircle(sketch: Sketch, center: Point3D, diameter: float) -> Profile:
    sketch.sketchCurves.sketchCircles.addByCenterRadius(center, diameter / 2)
    return sketch.profiles.item(0)


def createSketchByPlane(component: Component, plane) -> Sketch:
    planeInput = component.constructionPlanes.createInput()
    planeInput.setByOffset(plane, ValueInput.createByReal(0))
    plane = component.constructionPlanes.add(planeInput)
    sketch = component.sketches.add(plane)
    sketch.isVisible = False
    return sketch


def createSketchAlongPath(component: Component, path: SketchCurve, distance: float) -> Sketch:
    planeInput = component.constructionPlanes.createInput()
    planeInput.setByDistanceOnPath(path, ValueInput.createByReal(distance))
    plane = component.constructionPlanes.add(planeInput)
    sketch = component.sketches.add(plane)
    sketch.isVisible = False
    return sketch


def createRelativePoint(relativeTo: Point3D, x: float, y: float, z: float) -> Point3D:
    return Point3D.create(relativeTo.x + x, relativeTo.y + y, relativeTo.z + z)


def extrudeProfile(component: Component, profile: Profile, extentDistance: float,
                   operation=FeatureOperations.NewBodyFeatureOperation) -> ExtrudeFeature:
    extrudes = component.features.extrudeFeatures
    extrudeInput = extrudes.createInput(profile, operation)
    extrudeInput.setDistanceExtent(False, ValueInput.createByReal(extentDistance))
    return extrudes.add(extrudeInput)
