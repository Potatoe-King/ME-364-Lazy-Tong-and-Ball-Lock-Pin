"""Ideal geometry and preliminary strength checks for a lazy-tong linkage."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class LazyTongGeometry:
    stages: int
    link_length_mm: float
    angle_deg: float
    axial_length_mm: float
    transverse_height_mm: float


@dataclass(frozen=True)
class LazyTongCapacity:
    output_capacity_n: float
    governing_mode: str
    link_yield_capacity_n: float
    link_buckling_capacity_n: float
    pin_shear_capacity_n: float
    bearing_capacity_n: float


def geometry(stages: int, link_length_mm: float, angle_deg: float) -> LazyTongGeometry:
    if stages < 1:
        raise ValueError("The number of stages must be at least one.")
    if link_length_mm <= 0:
        raise ValueError("Link length must be positive.")
    if not 0 < angle_deg < 90:
        raise ValueError("The link angle must be between 0 and 90 degrees.")
    theta = math.radians(angle_deg)
    return LazyTongGeometry(
        stages=stages,
        link_length_mm=link_length_mm,
        angle_deg=angle_deg,
        axial_length_mm=stages * link_length_mm * math.cos(theta),
        transverse_height_mm=link_length_mm * math.sin(theta),
    )


def solve_configuration(
    unknown: str,
    *,
    axial_length_mm: float | None = None,
    stages: int | None = None,
    link_length_mm: float | None = None,
    angle_deg: float | None = None,
) -> dict[str, float]:
    """Solve x = n L cos(theta) for one unknown.

    Stage count is rounded upward because a physical design needs a whole number
    of complete stages. The returned achieved length uses that integer count.
    """
    if unknown == "Axial length":
        result = geometry(int(stages), float(link_length_mm), float(angle_deg))
        return {"axial_length_mm": result.axial_length_mm}

    if unknown == "Link length":
        theta = math.radians(float(angle_deg))
        denominator = int(stages) * math.cos(theta)
        if axial_length_mm is None or axial_length_mm <= 0 or denominator <= 0:
            raise ValueError("The supplied dimensions do not define a positive link length.")
        return {"link_length_mm": axial_length_mm / denominator}

    if unknown == "Link angle":
        if axial_length_mm is None or axial_length_mm <= 0:
            raise ValueError("Axial length must be positive.")
        denominator = int(stages) * float(link_length_mm)
        ratio = axial_length_mm / denominator
        if not 0 < ratio < 1:
            raise ValueError("Axial length must be less than nL and greater than zero.")
        return {"angle_deg": math.degrees(math.acos(ratio))}

    if unknown == "Stage count":
        theta = math.radians(float(angle_deg))
        per_stage = float(link_length_mm) * math.cos(theta)
        if axial_length_mm is None or axial_length_mm <= 0 or per_stage <= 0:
            raise ValueError("The supplied values do not define a positive stage count.")
        continuous = axial_length_mm / per_stage
        count = math.ceil(continuous)
        return {
            "stage_count_continuous": continuous,
            "stages": float(count),
            "achieved_length_mm": count * per_stage,
        }

    raise ValueError(f"Unknown quantity: {unknown}")


def synthesize_envelope(
    retracted_length_mm: float,
    extended_length_mm: float,
    retracted_height_mm: float,
    minimum_angle_deg: float,
    minimum_stages: int = 1,
    maximum_stages: int = 20,
) -> list[dict[str, float]]:
    """Find integer-stage geometries satisfying an exact retracted envelope.

    The supplied retracted height is interpreted as the pivot-to-pivot height of
    one symmetric stage, not the outside dimension of real hardware.
    """
    if min(retracted_length_mm, extended_length_mm, retracted_height_mm) <= 0:
        raise ValueError("Envelope dimensions must be positive.")
    if extended_length_mm <= retracted_length_mm:
        raise ValueError("Extended length must exceed retracted length.")
    if not 0 < minimum_angle_deg < 90:
        raise ValueError("Minimum angle must be between 0 and 90 degrees.")
    if minimum_stages < 1 or maximum_stages < minimum_stages:
        raise ValueError("The stage search range is invalid.")

    candidates: list[dict[str, float]] = []
    for n in range(minimum_stages, maximum_stages + 1):
        per_stage_retracted = retracted_length_mm / n
        link_length = math.hypot(per_stage_retracted, retracted_height_mm)
        total_flat_length = n * link_length
        if extended_length_mm >= total_flat_length:
            continue
        theta_r = math.degrees(math.atan2(retracted_height_mm, per_stage_retracted))
        theta_e = math.degrees(math.acos(extended_length_mm / total_flat_length))
        if theta_e >= theta_r or theta_e < minimum_angle_deg:
            continue
        extended_height = link_length * math.sin(math.radians(theta_e))
        candidates.append(
            {
                "stages": float(n),
                "link_length_mm": link_length,
                "retracted_angle_deg": theta_r,
                "extended_angle_deg": theta_e,
                "extended_height_mm": extended_height,
                "stroke_mm": extended_length_mm - retracted_length_mm,
                "expansion_ratio": extended_length_mm / retracted_length_mm,
            }
        )
    return candidates


def preliminary_capacity(
    *,
    angle_deg: float,
    link_length_mm: float,
    link_width_mm: float,
    link_thickness_mm: float,
    link_yield_mpa: float,
    elastic_modulus_gpa: float,
    effective_length_factor: float,
    pin_diameter_mm: float,
    pin_yield_mpa: float,
    pin_shear_planes: int,
    bearing_allowable_mpa: float,
    factor_of_safety: float,
) -> LazyTongCapacity:
    """Estimate axial output capacity at one configuration.

    This is an ideal, centered, in-plane estimate. It checks link yielding,
    Euler buckling about the weak axis, pin shear, and link bearing. It does not
    check joint tear-out, pin bending, eccentricity, fatigue, or lateral loads.
    """
    values = [
        link_length_mm,
        link_width_mm,
        link_thickness_mm,
        link_yield_mpa,
        elastic_modulus_gpa,
        effective_length_factor,
        pin_diameter_mm,
        pin_yield_mpa,
        bearing_allowable_mpa,
        factor_of_safety,
    ]
    if any(value <= 0 for value in values):
        raise ValueError("All dimensions, properties, and safety factors must be positive.")
    if pin_shear_planes not in (1, 2):
        raise ValueError("Pin shear planes must be one or two.")
    if not 0 < angle_deg < 90:
        raise ValueError("Angle must be between 0 and 90 degrees.")

    theta = math.radians(angle_deg)
    area = link_width_mm * link_thickness_mm
    i_weak = min(
        link_width_mm * link_thickness_mm**3 / 12.0,
        link_thickness_mm * link_width_mm**3 / 12.0,
    )
    link_yield_force = link_yield_mpa * area / factor_of_safety
    e_mpa = elastic_modulus_gpa * 1000.0
    buckling_force = (
        math.pi**2 * e_mpa * i_weak / (effective_length_factor * link_length_mm) ** 2
    ) / factor_of_safety
    pin_area = math.pi * pin_diameter_mm**2 / 4.0
    pin_shear_yield_mpa = pin_yield_mpa / math.sqrt(3.0)
    pin_shear_force = (
        pin_shear_planes * pin_area * pin_shear_yield_mpa / factor_of_safety
    )
    bearing_force = (
        bearing_allowable_mpa * pin_diameter_mm * link_thickness_mm / factor_of_safety
    )

    link_to_output = 2.0 * math.cos(theta)
    capacities = {
        "Link yielding": link_to_output * link_yield_force,
        "Link buckling": link_to_output * buckling_force,
        "Pin shear": link_to_output * pin_shear_force,
        "Link bearing": link_to_output * bearing_force,
    }
    governing_mode = min(capacities, key=capacities.get)
    output_capacity = capacities[governing_mode]
    return LazyTongCapacity(
        output_capacity_n=output_capacity,
        governing_mode=governing_mode,
        link_yield_capacity_n=capacities["Link yielding"],
        link_buckling_capacity_n=capacities["Link buckling"],
        pin_shear_capacity_n=capacities["Pin shear"],
        bearing_capacity_n=capacities["Link bearing"],
    )
