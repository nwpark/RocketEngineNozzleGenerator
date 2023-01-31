from enum import Enum
from typing import NamedTuple


class NozzleParameters(NamedTuple):
    name: str
    chamberLength: float
    chamberCylinderLength: float
    exitLength: float
    chamberRadius: float
    throatRadius: float
    exitRadius: float
    convergenceAngle: float
    convergenceRadius: float
    divergenceRadius: float


class NozzleDefinition(Enum):
    DEFAULT = NozzleParameters(
        name='default',
        chamberLength=67.23,
        chamberCylinderLength=56.23,
        exitLength=11.59,
        chamberRadius=10.48 / 2,
        throatRadius=2.62 / 2,
        exitRadius=3.23 / 2,
        convergenceAngle=30.0,
        convergenceRadius=13.68,
        divergenceRadius=1.96)

    @staticmethod
    def fromName(name: str) -> NozzleParameters:
        nozzleParams = next(
            nozzleParams for nozzleParams in NozzleDefinition if nozzleParams.value.name == name)
        return nozzleParams.value

    @staticmethod
    def getNames() -> [str]:
        return list(map(lambda nozzleParams: nozzleParams.value.name, NozzleDefinition))
