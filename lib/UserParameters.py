from enum import Enum

from adsk.core import ValueInput, CommandInputs, BoolValueCommandInput, IntegerSliderCommandInput, ValueCommandInput, \
    CommandInput, DropDownStyles, DropDownCommandInput

from .NozzleDefinitions import NozzleDefinition, NozzleParameters
from .common.Common import unitsMgr, resourceFolder, ui


class _UserParameter:
    def __init__(self, id: str, name: str):
        self._id = id
        self._name = name
        pass

    def getValue(self):
        pass

    def setValue(self, value):
        pass

    def setValueFromCommandInput(self, commandInput: CommandInput):
        pass

    def addToCommandInputs(self, commandInputs: CommandInputs):
        pass

    def getId(self) -> str:
        return self._id


class _UserDimensionParameter(_UserParameter):
    def __init__(self, id, name: str, unitType: str, initValue: float):
        super().__init__(id, name)
        self._unitType = unitType
        self._valueInSelfUnits = initValue
        self._commandInput = ValueCommandInput.cast(None)

    def getValue(self) -> float:
        # dimensions must be used with internal units
        return unitsMgr.convert(self._valueInSelfUnits, self._unitType, unitsMgr.internalUnits)

    def setValue(self, value):
        self._valueInSelfUnits = value
        self._commandInput.value = unitsMgr.convert(value, self._unitType, unitsMgr.internalUnits)

    def setValueFromCommandInput(self, commandInput: ValueCommandInput):
        # evaluateExpression returns value in internal units
        valueInInternalUnits = unitsMgr.evaluateExpression(commandInput.expression, self._unitType)
        self._valueInSelfUnits = unitsMgr.convert(valueInInternalUnits, unitsMgr.internalUnits, self._unitType)

    def addToCommandInputs(self, commandInputs: CommandInputs):
        self._commandInput = commandInputs.addValueInput(self._id, self._name, self._unitType,
                                    ValueInput.createByReal(self.getValue()))


class _UserBoolParameter(_UserParameter):
    def __init__(self, id: str, name: str, initValue: bool):
        super().__init__(id, name)
        self._value = initValue

    def getValue(self) -> bool:
        return self._value

    def setValueFromCommandInput(self, commandInput: BoolValueCommandInput):
        self._value = commandInput.value

    def addToCommandInputs(self, commandInputs: CommandInputs):
        commandInputs.addBoolValueInput(self._id, self._name, True, resourceFolder, self._value)


class _UserIntegerSliderParameter(_UserParameter):
    def __init__(self, id: str, name: str, min: int, max: int):
        super().__init__(id, name)
        self._min = min
        self._max = max
        self._value = min

    def getValue(self) -> int:
        return self._value

    def setValueFromCommandInput(self, commandInput: IntegerSliderCommandInput):
        self._value = commandInput.valueOne

    def addToCommandInputs(self, commandInputs: CommandInputs):
        commandInputs.addIntegerSliderCommandInput(self._id, self._name, self._min, self._max, False)


class UserDropDownParameter(_UserParameter):
    def __init__(self, id: str, name: str, dropDownOptions: [str], defaultOption: str):
        super().__init__(id, name)
        self._dropDownInput: DropDownCommandInput = DropDownCommandInput.cast(None)
        self._dropDownOptions = dropDownOptions
        self._defaultOption = defaultOption

    def getValue(self) -> str:
        return self._dropDownInput.selectedItem.name

    def setValueFromCommandInput(self, commandInput: IntegerSliderCommandInput):
        pass

    def addToCommandInputs(self, commandInputs: CommandInputs):
        self._dropDownInput = commandInputs.addDropDownCommandInput(self._id, self._name,
                                                                    DropDownStyles.TextListDropDownStyle)
        for option in self._dropDownOptions:
            self._dropDownInput.listItems.add(option, option == self._defaultOption)


class UserParameters(Enum):
    NOZZLE_DEFINITION_DROPDOWN = UserDropDownParameter('nozzleDefinitionDropdownId', 'Nozzle Definition', NozzleDefinition.getNames(), NozzleDefinition.DEFAULT.value.name)
    CHAMBER_LENGTH = _UserDimensionParameter('chamberLengthId', 'chamberLength', 'mm', NozzleDefinition.DEFAULT.value.chamberLength)
    CHAMBER_CYLINDER_LENGTH = _UserDimensionParameter('chamberCylinderId', 'chamberCylinderLength', 'mm', NozzleDefinition.DEFAULT.value.chamberCylinderLength)
    EXIT_LENGTH = _UserDimensionParameter('exitLengthId', 'exitLength', 'mm', NozzleDefinition.DEFAULT.value.exitLength)
    CHAMBER_RADIUS = _UserDimensionParameter('chamberRadiusId', 'chamberRadius', 'mm', NozzleDefinition.DEFAULT.value.chamberRadius)
    THROAT_RADIUS = _UserDimensionParameter('throatRadiusId', 'throatRadius', 'mm', NozzleDefinition.DEFAULT.value.throatRadius)
    EXIT_RADIUS = _UserDimensionParameter('exitRadiusId', 'exitRadius', 'mm', NozzleDefinition.DEFAULT.value.exitRadius)
    CONVERGENCE_ANGLE = _UserDimensionParameter('convergenceAngleId', 'convergenceAngle', 'deg', NozzleDefinition.DEFAULT.value.convergenceAngle)
    CONVERGENCE_RADIUS = _UserDimensionParameter('convergenceRadiusId', 'convergenceRadius', 'mm', NozzleDefinition.DEFAULT.value.convergenceRadius)
    DIVERGENCE_RADIUS = _UserDimensionParameter('divergenceRadiusId', 'divergenceRadius', 'mm', NozzleDefinition.DEFAULT.value.divergenceRadius)

    @staticmethod
    def applySelectedNozzleDefinition():
        name = UserParameters.NOZZLE_DEFINITION_DROPDOWN.value.getValue()
        nozzleDefinition = NozzleDefinition.fromName(name)
        UserParameters.CHAMBER_LENGTH.value.setValue(nozzleDefinition.chamberLength)
        UserParameters.EXIT_LENGTH.value.setValue(nozzleDefinition.exitLength)
        UserParameters.CHAMBER_RADIUS.value.setValue(nozzleDefinition.chamberRadius)
        UserParameters.THROAT_RADIUS.value.setValue(nozzleDefinition.throatRadius)
        UserParameters.EXIT_RADIUS.value.setValue(nozzleDefinition.exitRadius)
        UserParameters.CONVERGENCE_ANGLE.value.setValue(nozzleDefinition.convergenceAngle)
        UserParameters.CONVERGENCE_RADIUS.value.setValue(nozzleDefinition.convergenceRadius)
        UserParameters.DIVERGENCE_RADIUS.value.setValue(nozzleDefinition.divergenceRadius)

    @staticmethod
    def getNozzleParameters() -> NozzleParameters:
        return NozzleParameters(
            UserParameters.NOZZLE_DEFINITION_DROPDOWN.value.getValue(),
            UserParameters.CHAMBER_LENGTH.value.getValue(),
            UserParameters.CHAMBER_CYLINDER_LENGTH.value.getValue(),
            UserParameters.EXIT_LENGTH.value.getValue(),
            UserParameters.CHAMBER_RADIUS.value.getValue(),
            UserParameters.THROAT_RADIUS.value.getValue(),
            UserParameters.EXIT_RADIUS.value.getValue(),
            UserParameters.CONVERGENCE_ANGLE.value.getValue(),
            UserParameters.CONVERGENCE_RADIUS.value.getValue(),
            UserParameters.DIVERGENCE_RADIUS.value.getValue())

    @staticmethod
    def getAllParameters() -> [_UserParameter]:
        return list(map(lambda param: param.value, UserParameters))

    @staticmethod
    def fromId(id: str) -> _UserParameter:
        return next(param for param in UserParameters.getAllParameters() if param.getId() == id)

    @staticmethod
    def updateValuesFromCommandInputs(commandInputs: CommandInputs):
        for i in range(commandInputs.count):
            commandInput = commandInputs.item(i)
            userParameter = UserParameters.fromId(commandInput.id)
            userParameter.setValueFromCommandInput(commandInput)
