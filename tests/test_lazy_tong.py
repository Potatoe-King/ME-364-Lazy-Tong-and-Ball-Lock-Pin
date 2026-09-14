import math
import unittest

from mechanics.lazy_tong import (
    geometry,
    preliminary_capacity,
    solve_configuration,
    synthesize_envelope,
)


class LazyTongTests(unittest.TestCase):
    def test_geometry_projection(self):
        result = geometry(4, 100.0, 60.0)
        self.assertAlmostEqual(result.axial_length_mm, 200.0, places=9)
        self.assertAlmostEqual(result.transverse_height_mm, 100.0 * math.sin(math.radians(60)), places=9)

    def test_stage_count_rounds_up(self):
        result = solve_configuration(
            "Stage count",
            axial_length_mm=900.0,
            link_length_mm=250.0,
            angle_deg=35.0,
        )
        self.assertEqual(result["stages"], 5.0)
        self.assertGreaterEqual(result["achieved_length_mm"], 900.0)

    def test_configuration_inverse(self):
        x = geometry(5, 250.0, 35.0).axial_length_mm
        result = solve_configuration(
            "Link angle",
            axial_length_mm=x,
            stages=5,
            link_length_mm=250.0,
        )
        self.assertAlmostEqual(result["angle_deg"], 35.0, places=9)

    def test_envelope_candidates_reproduce_targets(self):
        rows = synthesize_envelope(450.0, 1000.0, 220.0, 10.0, 2, 12)
        self.assertTrue(rows)
        for row in rows:
            n = int(row["stages"])
            retracted = geometry(n, row["link_length_mm"], row["retracted_angle_deg"])
            extended = geometry(n, row["link_length_mm"], row["extended_angle_deg"])
            self.assertAlmostEqual(retracted.axial_length_mm, 450.0, places=7)
            self.assertAlmostEqual(retracted.transverse_height_mm, 220.0, places=7)
            self.assertAlmostEqual(extended.axial_length_mm, 1000.0, places=7)

    def test_capacity_is_minimum_mode(self):
        result = preliminary_capacity(
            angle_deg=20.0,
            link_length_mm=250.0,
            link_width_mm=25.0,
            link_thickness_mm=4.0,
            link_yield_mpa=250.0,
            elastic_modulus_gpa=200.0,
            effective_length_factor=1.0,
            pin_diameter_mm=6.0,
            pin_yield_mpa=400.0,
            pin_shear_planes=2,
            bearing_allowable_mpa=200.0,
            factor_of_safety=2.0,
        )
        capacities = [
            result.link_yield_capacity_n,
            result.link_buckling_capacity_n,
            result.pin_shear_capacity_n,
            result.bearing_capacity_n,
        ]
        self.assertAlmostEqual(result.output_capacity_n, min(capacities), places=9)


if __name__ == "__main__":
    unittest.main()

