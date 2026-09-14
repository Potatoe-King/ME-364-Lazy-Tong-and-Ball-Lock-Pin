"""Unit conversions used by both device designers.

The calculation modules use N, mm, MPa, and GPa internally.
"""

from dataclasses import dataclass


LBF_TO_N = 4.4482216152605
IN_TO_MM = 25.4
KSI_TO_MPA = 6.894757293168
MSI_TO_GPA = 6.894757293168
N_TO_LBF = 1.0 / LBF_TO_N
MM_TO_IN = 1.0 / IN_TO_MM
MPA_TO_KSI = 1.0 / KSI_TO_MPA
GPA_TO_MSI = 1.0 / MSI_TO_GPA


@dataclass(frozen=True)
class Units:
    name: str
    length: str
    force: str
    stress: str
    modulus: str

    @property
    def is_si(self) -> bool:
        return self.name == "SI"

    def length_to_si(self, value: float) -> float:
        return value if self.is_si else value * IN_TO_MM

    def length_from_si(self, value: float) -> float:
        return value if self.is_si else value * MM_TO_IN

    def force_to_si(self, value: float) -> float:
        return value if self.is_si else value * LBF_TO_N

    def force_from_si(self, value: float) -> float:
        return value if self.is_si else value * N_TO_LBF

    def stress_to_si(self, value: float) -> float:
        return value if self.is_si else value * KSI_TO_MPA

    def stress_from_si(self, value: float) -> float:
        return value if self.is_si else value * MPA_TO_KSI

    def modulus_to_si(self, value: float) -> float:
        return value if self.is_si else value * MSI_TO_GPA

    def modulus_from_si(self, value: float) -> float:
        return value if self.is_si else value * GPA_TO_MSI


SI = Units("SI", "mm", "N", "MPa", "GPa")
US = Units("US customary", "in", "lbf", "ksi", "Msi")


def get_units(name: str) -> Units:
    return SI if name == "SI" else US

