import math
import unittest

from mechanics.ball_lock import (
    analyze_pin,
    required_diameter_for_shear,
    select_standard_diameter,
    solve_shear_relationship,
)


class BallLockTests(unittest.TestCase):
    def test_double_shear_stress(self):
        result = analyze_pin(
            diameter_mm=10.0,
            transverse_load_n=1000.0,
            axial_load_n=100.0,
            pin_yield_mpa=600.0,
            center_thickness_mm=8.0,
            outer_thickness_mm=6.0,
            total_stack_mm=20.0,
            grip_clearance_mm=0.5,
            bearing_allowable_mpa=200.0,
            factor_of_safety=2.0,
            shear_planes=2,
            axial_rating_n=500.0,
            axial_rating_is_allowable=True,
        )
        expected = 1000.0 / (2.0 * math.pi * 10.0**2 / 4.0)
        self.assertAlmostEqual(result.pin_shear_stress_mpa, expected, places=9)
        self.assertAlmostEqual(result.required_grip_mm, 20.5, places=9)
        self.assertAlmostEqual(result.axial_margin, 5.0, places=9)

    def test_shear_inverse(self):
        diameter = required_diameter_for_shear(1500.0, 600.0, 2.0, 2)
        maximum = solve_shear_relationship(
            "Maximum transverse load",
            diameter_mm=diameter,
            transverse_load_n=None,
            pin_yield_mpa=600.0,
            factor_of_safety=2.0,
            shear_planes=2,
        )
        self.assertAlmostEqual(maximum, 1500.0, places=9)

    def test_standard_size_rounds_up(self):
        self.assertEqual(select_standard_diameter(7.1, [5.0, 6.0, 8.0, 10.0]), 8.0)
        self.assertIsNone(select_standard_diameter(12.0, [5.0, 6.0, 8.0, 10.0]))

    def test_ultimate_axial_rating_gets_safety_factor(self):
        result = analyze_pin(
            diameter_mm=8.0,
            transverse_load_n=500.0,
            axial_load_n=200.0,
            pin_yield_mpa=600.0,
            center_thickness_mm=8.0,
            outer_thickness_mm=6.0,
            total_stack_mm=20.0,
            grip_clearance_mm=0.5,
            bearing_allowable_mpa=200.0,
            factor_of_safety=2.0,
            shear_planes=2,
            axial_rating_n=1000.0,
            axial_rating_is_allowable=False,
        )
        self.assertAlmostEqual(result.axial_allowable_n, 500.0, places=9)
        self.assertAlmostEqual(result.axial_margin, 2.5, places=9)


if __name__ == "__main__":
    unittest.main()

