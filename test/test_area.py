#!/usr/bin/env python3

import unittest

from pycaching.point import Point
from pycaching.area import Polygon, Rectangle


class TestPolygon(unittest.TestCase):

    def setUp(self):
        self.p = Polygon(*[Point(*i) for i in [
            (10., 20.), (30., -5.), (-10., -170.), (-70., 0.), (0., 40)]])

    def test_bounding_box(self):
        bb = self.p.bounding_box
        sw, ne = bb.corners
        with self.subTest("Minimum latitude"):
            self.assertEqual(sw.latitude, -70.)
        with self.subTest("Minimum longitude"):
            self.assertEqual(sw.longitude, -170.)
        with self.subTest("Maximum latitude"):
            self.assertEqual(ne.latitude, 30.)
        with self.subTest("Maximum longitude"):
            self.assertEqual(ne.longitude, 40.)

    def test_mean_point(self):
        mp = self.p.mean_point
        with self.subTest("latitude"):
            self.assertEqual(mp.latitude, -8.0)
        with self.subTest("longitude"):
            self.assertEqual(mp.longitude, -23.0)

    def test_diagonal(self):
        self.assertAlmostEqual(self.p.diagonal, 15174552.821484847)


class TestRectangle(unittest.TestCase):

    def setUp(self):
        self.rect = Rectangle(Point(10., 20.), Point(30., -5.))

    def test_inside_area(self):
        inside_points = [Point(*i) for i in [
            (10., 20.), (30., -5.), (18., 15.), (29., -1), (10., -3)]]
        outside_points = [Point(*i) for i in [
            (-10., -170.), (-70., 0.), (0., 40), (20., -10.), (50., 0.)]]
        for point_list, test_func in [(inside_points, 'assertTrue'),
                                      (outside_points, 'assertFalse')]:
            for p in point_list:
                with self.subTest("Area -> point: {}".format(p)):
                    getattr(self, test_func)(self.rect.inside_area(p))
                with self.subTest("Point -> area: {}".format(p)):
                    getattr(self, test_func)(p.inside_area(self.rect))

    def test_diagonal(self):
        self.assertAlmostEqual(self.rect.diagonal, 3411261.6697135763)
