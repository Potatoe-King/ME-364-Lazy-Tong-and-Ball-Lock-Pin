"""Preliminary sizing checks for a ball-detent quick-release pin."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class BallLockResult:
    pin_shear_stress_mpa: float
    center_bearing_stress_mpa: float
    outer_bearing_stress_mpa: float
    shear_allowable_mpa: float
    transverse_capacity_n: float
    governing_mode: str
    transverse_margin: float
    axial_allowable_n: float | None
    axial_margin: float | None
    required_grip_mm: float


def required_diameter_for_shear(
    transverse_load_n: float,
    pin_yield_mpa: float,
    factor_of_safety: float,
    shear_planes: int,
) -> float:
    if min(transverse_load_n, pin_yield_mpa, factor_of_safety) <= 0:
        raise ValueError("Load, yield strength, and safety factor must be positive.")
    if shear_planes not in (1, 2):
        raise ValueError("Shear planes must be one or two.")
    shear_yield = pin_yield_mpa / math.sqrt(3.0)
    return math.sqrt(
        4.0 * transverse_load_n * factor_of_safety
        / (shear_planes * math.pi * shear_yield)
    )


def required_diameter_for_bearing(
    transverse_load_n: float,
    center_thickness_mm: float,
    outer_thickness_mm: float,
    bearing_allowable_mpa: float,
    factor_of_safety: float,
    shear_planes: int,
) -> float:
    if min(
        transverse_load_n,
        center_thickness_mm,
        outer_thickness_mm,
        bearing_allowable_mpa,
        factor_of_safety,
    ) <= 0:
        raise ValueError("Loads, dimensions, allowable stress, and safety factor must be positive.")
    if shear_planes == 1:
        return transverse_load_n * factor_of_safety / (
            center_thickness_mm * bearing_allowable_mpa
        )
    if shear_planes == 2:
        center_required = transverse_load_n * factor_of_safety / (
            center_thickness_mm * bearing_allowable_mpa
        )
        outer_required = transverse_load_n * factor_of_safety / (
            2.0 * outer_thickness_mm * bearing_allowable_mpa
        )
        return max(center_required, outer_required)
    raise ValueError("Shear planes must be one or two.")


def select_standard_diameter(required_mm: float, options_mm: list[float]) -> float | None:
    if required_mm <= 0:
        raise ValueError("Required diameter must be positive.")
    for value in sorted(options_mm):
        if value >= required_mm:
            return value
    return None


def analyze_pin(
    *,
    diameter_mm: float,
    transverse_load_n: float,
    axial_load_n: float,
    pin_yield_mpa: float,
    center_thickness_mm: float,
    outer_thickness_mm: float,
    total_stack_mm: float,
    grip_clearance_mm: float,
    bearing_allowable_mpa: float,
    factor_of_safety: float,
    shear_planes: int,
    axial_rating_n: float | None = None,
    axial_rating_is_allowable: bool = True,
) -> BallLockResult:
    positive = [
        diameter_mm,
        pin_yield_mpa,
        center_thickness_mm,
        outer_thickness_mm,
        total_stack_mm,
        bearing_allowable_mpa,
        factor_of_safety,
    ]
    if any(value <= 0 for value in positive) or min(transverse_load_n, axial_load_n, grip_clearance_mm) < 0:
        raise ValueError("Dimensions and properties must be positive; loads cannot be negative.")
    if shear_planes not in (1, 2):
        raise ValueError("Shear planes must be one or two.")

    area = math.pi * diameter_mm**2 / 4.0
    shear_stress = transverse_load_n / (shear_planes * area)
    shear_allowable = pin_yield_mpa / math.sqrt(3.0) / factor_of_safety
    shear_capacity = shear_planes * area * shear_allowable

    center_bearing = transverse_load_n / (center_thickness_mm * diameter_mm)
    if shear_planes == 2:
        outer_bearing = transverse_load_n / (2.0 * outer_thickness_mm * diameter_mm)
        center_capacity = center_thickness_mm * diameter_mm * bearing_allowable_mpa / factor_of_safety
        outer_capacity = 2.0 * outer_thickness_mm * diameter_mm * bearing_allowable_mpa / factor_of_safety
    else:
        outer_bearing = center_bearing
        center_capacity = center_thickness_mm * diameter_mm * bearing_allowable_mpa / factor_of_safety
        outer_capacity = center_capacity

    capacities = {
        "Pin shear": shear_capacity,
        "Center-member bearing": center_capacity,
        "Outer-lug bearing": outer_capacity,
    }
    governing_mode = min(capacities, key=capacities.get)
    transverse_capacity = capacities[governing_mode]
    transverse_margin = math.inf if transverse_load_n == 0 else transverse_capacity / transverse_load_n

    axial_allowable = None
    axial_margin = None
    if axial_rating_n is not None and axial_rating_n > 0:
        axial_allowable = axial_rating_n if axial_rating_is_allowable else axial_rating_n / factor_of_safety
        axial_margin = math.inf if axial_load_n == 0 else axial_allowable / axial_load_n

    return BallLockResult(
        pin_shear_stress_mpa=shear_stress,
        center_bearing_stress_mpa=center_bearing,
        outer_bearing_stress_mpa=outer_bearing,
        shear_allowable_mpa=shear_allowable,
        transverse_capacity_n=transverse_capacity,
        governing_mode=governing_mode,
        transverse_margin=transverse_margin,
        axial_allowable_n=axial_allowable,
        axial_margin=axial_margin,
        required_grip_mm=total_stack_mm + grip_clearance_mm,
    )


def solve_shear_relationship(
    unknown: str,
    *,
    diameter_mm: float | None,
    transverse_load_n: float | None,
    pin_yield_mpa: float,
    factor_of_safety: float | None,
    shear_planes: int,
) -> float:
    """Solve the static pin-shear relationship for one selected quantity."""
    shear_yield = pin_yield_mpa / math.sqrt(3.0)
    if shear_yield <= 0 or shear_planes not in (1, 2):
        raise ValueError("Material strength and shear-plane selection must be valid.")
    if unknown == "Pin diameter":
        return required_diameter_for_shear(
            float(transverse_load_n), pin_yield_mpa, float(factor_of_safety), shear_planes
        )
    area = math.pi * float(diameter_mm) ** 2 / 4.0
    if unknown == "Maximum transverse load":
        return shear_planes * area * shear_yield / float(factor_of_safety)
    if unknown == "Actual factor of safety":
        if transverse_load_n is None or transverse_load_n <= 0:
            raise ValueError("Transverse load must be positive.")
        return shear_planes * area * shear_yield / transverse_load_n
    raise ValueError(f"Unknown quantity: {unknown}")

