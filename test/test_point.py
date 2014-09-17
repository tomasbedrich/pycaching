#!/usr/bin/env python3

import unittest
from pycaching import Point


class TestPoint(unittest.TestCase):

    def test_from_string(self):
        with self.subTest("normal"):
            self.assertEqual(Point.from_string("N 49 45.123 E 013 22.123"), Point(49.75205, 13.36872))

        with self.subTest("south and west"):
            self.assertEqual(Point.from_string("S 49 45.123 W 013 22.123"), Point(-48.24795, -12.63128))

        with self.subTest("letter together"):
            self.assertEqual(Point.from_string("N49 45.123 E013 22.123"), Point(49.75205, 13.36872))

        with self.subTest("letter after"):
            self.assertEqual(Point.from_string("49N 45.123 013E 22.123"), Point(49.75205, 13.36872))

        with self.subTest("south and west letter after"):
            self.assertEqual(Point.from_string("49S 45.123 013W 22.123"), Point(-48.24795, -12.63128))

        with self.subTest("decimal separator: coma"):
            self.assertEqual(Point.from_string("N 49 45,123 E 013 22,123"), Point(49.75205, 13.36872))

        with self.subTest("degree symbol"):
            self.assertEqual(Point.from_string("N 49° 45.123 E 013° 22.123"), Point(49.75205, 13.36872))

        with self.subTest("coma between lat and lon"):
            self.assertEqual(Point.from_string("N 49 45.123, E 013 22.123"), Point(49.75205, 13.36872))

        with self.subTest("marginal values: zeroes"):
            self.assertEqual(Point.from_string("N 49 45.000 E 13 0.0"), Point(49.75, 13.0))

        with self.subTest("Include precision"):
            self.assertIn("precision", Point(49.75, 13.0).__dict__)

        with self.assertRaises(ValueError):
            Point.from_string("123")

    def test_from_tile(self):
        p = Point.from_tile(8800, 5574, 14)
        p_pos = Point(49.752879934150215, 13.359375, 0.0)

        with self.subTest("Assumed location"):
            self.assertEqual(p, p_pos)

        with self.subTest("Fractional tiles"):
            p2 = Point.from_tile(x=8801, y=5575, z=14)
            p_half = Point.from_tile(8800, 5574, 14, 1, 1, 2)
            self.assertEqual(Point.from_tile(8800, 5574, 14, 0, 32, 32),
                             Point.from_tile(x=8800, y=5575, z=14))
            self.assertEqual(Point.from_tile(8800, 5574, 14, 32, 0, 32),
                             Point.from_tile(x=8801, y=5574, z=14))
            self.assertEqual(Point.from_tile(8800, 5574, 14, 32, 32, 32), p2)
            # y increases -> latitude decreases
            self.assertGreater(p.latitude, p_half.latitude)
            self.assertLess(p.longitude, p_half.longitude)
            self.assertLess(p2.latitude, p_half.latitude)
            self.assertGreater(p2.longitude, p_half.longitude)

    def test_to_map_tile(self):
        t = (8800, 5574, 14)
        point_in_t = Point(49.75, 13.36)

        with self.subTest("From tile and back"):
            self.assertEqual(Point.from_tile(*t).to_map_tile(t[-1]), t)

        with self.subTest("Random point"):
            self.assertEqual(point_in_t.to_map_tile(14), t)

        with self.subTest("Directions"):
            # Increase in latitude: decrease in y value
            self.assertLess(Point(50., 13.36).to_map_tile(14)[1], t[1])
            self.assertGreater(Point(49., 13.36).to_map_tile(14)[1], t[1])
            # Increase in longitude: increase in x value
            self.assertGreater(Point(49.75, 14.).to_map_tile(14)[0], t[0])
            self.assertLess(Point(49.75, 13.).to_map_tile(14)[0], t[0])

    def test_precision_from_tile_zoom(self):
        p = Point(49.75, 13.36)

        with self.subTest("Random point"):
            self.assertEqual(p.precision_from_tile_zoom(14), 6.173474613462484)

        with self.subTest("Z value"):
            self.assertGreater(p.precision_from_tile_zoom(13),
                               p.precision_from_tile_zoom(14))
            self.assertLess(p.precision_from_tile_zoom(15),
                            p.precision_from_tile_zoom(14))

        with self.subTest("Divisor"):
            self.assertGreater(p.precision_from_tile_zoom(14, 10),
                               p.precision_from_tile_zoom(14, 100))
