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

        with self.assertRaises(ValueError):
            Point.from_string("123")
