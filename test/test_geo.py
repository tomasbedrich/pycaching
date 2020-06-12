#!/usr/bin/env python3

import json
import logging
import unittest
from os import path
from unittest import mock

from geopy.distance import great_circle

from pycaching import Cache
from pycaching.errors import GeocodeError, BadBlockError
from pycaching.geo import Point, Polygon, Rectangle, Tile, UTFGridPoint, Block
from pycaching.geo import to_decimal
from . import NetworkedTest

_sample_caches_file = path.join(path.dirname(__file__), "sample_caches.csv")
_sample_utfgrid_file = path.join(path.dirname(__file__), "sample_utfgrid.json")


def make_tile(x, y, z, a=0, b=0, size=256):
    t = Tile(None, x, y, z)
    t.size = size
    return t, UTFGridPoint(a, b)


class TestPoint(NetworkedTest):
    def test_from_string(self):
        with self.subTest("normal"):
            self.assertEqual(Point.from_string("N 49 45.123 E 013 22.123"),
                             Point(49.75205, 13.36872))

        with self.subTest("south and west"):
            self.assertEqual(Point.from_string("S 49 45.123 W 013 22.123"),
                             Point(-49.75205, -13.36872))

        with self.subTest("lowercase"):
            self.assertEqual(Point.from_string("s 49 45.123 w 013 22.123"),
                             Point(-49.75205, -13.36872))

        with self.subTest("letter together"):
            self.assertEqual(Point.from_string("N49 45.123 E013 22.123"), Point(49.75205, 13.36872))

        with self.subTest("letter after"):
            self.assertEqual(Point.from_string("49N 45.123 013E 22.123"), Point(49.75205, 13.36872))

        with self.subTest("south and west letter after"):
            self.assertEqual(Point.from_string("49S 45.123 013W 22.123"),
                             Point(-49.75205, -13.36872))

        with self.subTest("decimal separator: comma"):
            self.assertEqual(Point.from_string("N 49 45,123 E 013 22,123"),
                             Point(49.75205, 13.36872))

        with self.subTest("degree symbol"):
            self.assertEqual(Point.from_string("N 49° 45.123 E 013° 22.123"),
                             Point(49.75205, 13.36872))

        with self.subTest("comma between lat and lon"):
            self.assertEqual(Point.from_string("N 49 45.123, E 013 22.123"),
                             Point(49.75205, 13.36872))

        with self.subTest("marginal values: zeroes"):
            self.assertEqual(Point.from_string("N 49 45.000 E 13 0.0"), Point(49.75, 13.0))

        with self.subTest("include precision"):
            self.assertIn("precision", Point(49.75, 13.0).__dict__)

        with self.assertRaises(ValueError):
            Point.from_string("123")

    def test_from_location(self):
        ref_point = Point(50.08746, 14.42125)

        with self.subTest("existing location"):
            with self.recorder.use_cassette('geo_location_existing'):
                self.assertLess(great_circle(Point.from_location(self.gc, "Prague"), ref_point).miles, 10)
                self.assertLess(great_circle(Point.from_location(self.gc, "Praha"), ref_point).miles, 10)
                self.assertLess(great_circle(Point.from_location(self.gc, "praha"), ref_point).miles, 10)

        with self.subTest("non-existing location"):
            with self.recorder.use_cassette('geo_location_nonexisting'):
                with self.assertRaises(GeocodeError):
                    Point.from_location(self.gc, "qwertzuiop")

        with self.subTest("empty request"):
            with self.recorder.use_cassette('geo_location_empty'):
                with self.assertRaises(GeocodeError):
                    Point.from_location(self.gc, "")

    def test_from_tile(self):
        """Test coordinate creation from tile"""
        p = Point.from_tile(*make_tile(8800, 5574, 14, 0, 0, 256))
        p_pos = Point(49.752879934150215, 13.359375, 0.0)

        p2 = Point.from_tile(*make_tile(8801, 5575, 14, 0, 0, 256))
        p_half = Point.from_tile(*make_tile(8800, 5574, 14, 1, 1, 2))

        # Check creation
        for att in ['latitude', 'longitude']:
            with self.subTest("assumed location: {}".format(att)):
                self.assertAlmostEqual(getattr(p, att), getattr(p_pos, att))

        with self.subTest("fractional tiles: y-axis addition"):
            self.assertEqual(Point.from_tile(*make_tile(8800, 5574, 14, 0, 32, 32)),
                             Point.from_tile(*make_tile(x=8800, y=5575, z=14)))
        with self.subTest("fractional tiles: x-axis addition"):
            self.assertAlmostEqual(Point.from_tile(*make_tile(8800, 5574, 14, 32, 0, 32)),
                                   Point.from_tile(*make_tile(x=8801, y=5574, z=14)))
        with self.subTest("fractional tiles: addition on both axes"):
            self.assertEqual(Point.from_tile(*make_tile(8800, 5574, 14, 32, 32, 32)), p2)

        with self.subTest("y increases -> latitude decreases"):
            self.assertGreater(p.latitude, p_half.latitude)
        with self.subTest("x increases -> latitude increases"):
            self.assertLess(p.longitude, p_half.longitude)

    def test_to_tile(self):
        t = make_tile(8800, 5574, 14)[0]
        point_in_t = Point(49.75, 13.36)

        with self.subTest("from tile and back"):
            self.assertEqual(Point.from_tile(t).to_tile(None, t.z), t)

        with self.subTest("random point"):
            self.assertEqual(point_in_t.to_tile(None, 14), t)

        with self.subTest("increase in latitude: decrease in y value"):
            self.assertLess(Point(50., 13.36).to_tile(None, 14).y, t.y)

        with self.subTest("increase in longitude: increase in x value"):
            self.assertGreater(Point(49.75, 14.).to_tile(None, 14).x, t.x)

    def test_format_gc(self):
        """Test Geocaching point formatting."""
        self.assertEqual(Point(49.73012, 13.40102).format_gc(), "N 49° 43.807, E 13° 24.061")
        self.assertEqual(Point(-49.73012, -13.40102).format_gc(), "S 49° 43.807, W 13° 24.061")


class TestPolygon(unittest.TestCase):
    def setUp(self):
        self.p = Polygon(*[Point(*i) for i in [
            (10., 20.), (30., -5.), (-10., -170.), (-70., 0.), (0., 40)]])

    def test_bounding_box(self):
        bb = self.p.bounding_box
        nw, se = bb.corners
        with self.subTest("Minimum latitude"):
            self.assertEqual(se.latitude, -70.)
        with self.subTest("Minimum longitude"):
            self.assertEqual(nw.longitude, -170.)
        with self.subTest("Maximum latitude"):
            self.assertEqual(nw.latitude, 30.)
        with self.subTest("Maximum longitude"):
            self.assertEqual(se.longitude, 40.)

    def test_mean_point(self):
        mp = self.p.mean_point
        with self.subTest("latitude"):
            self.assertEqual(mp.latitude, -8.0)
        with self.subTest("longitude"):
            self.assertEqual(mp.longitude, -23.0)


class TestRectangle(unittest.TestCase):
    def setUp(self):
        self.rect = Rectangle(Point(10., 20.), Point(30., -5.))

    def test_contains(self):
        inside_points = [Point(*i)
                         for i in [(10., 20.), (30., -5.), (18., 15.), (29., -1), (10., -3)]]
        outside_points = [Point(*i) for i in [(-10., -170.), (-70., 0.),
                                              (0., 40), (20., -10.), (50., 0.)]]
        for p in inside_points:
            self.assertTrue(p in self.rect)
        for p in outside_points:
            self.assertFalse(p in self.rect)

    def test_diagonal(self):
        self.assertAlmostEqual(self.rect.diagonal, 3411261.6697293497)


class TestTile(NetworkedTest):
    # see
    # http://gis.stackexchange.com/questions/8650/how-to-measure-the-accuracy-of-latitude-and-longitude
    POSITION_ACCURANCY = 3  # = up to 110 meters

    def setUp(self):
        super().setUp()
        self.tile = Tile(self.gc, 8800, 5574, 14)

    def test_download_utfgrid(self):
        """Test if downloading a UTFGrid passes without errors"""
        with self.recorder.use_cassette('geo_point_utfgrid'):
            with self.subTest("not getting .png tile first"):
                self.tile._download_utfgrid()

            with self.subTest("getting .png tile first"):
                self.tile._download_utfgrid(get_png=True)

    @mock.patch.object(Tile, '_download_utfgrid')
    def test_blocks(self, mock_utfgrid):
        """Parse locally stored grid and compare to expected results"""

        # load mock utfgrid from file
        with open(_sample_utfgrid_file, encoding="utf8") as f:
            mock_utfgrid.return_value = json.load(f)

        # load expected caches from file
        expected_caches = {}
        with open(_sample_caches_file) as f:
            for row in f:
                wp, lat, lon, pm_only = row.strip().split(",")
                expected_caches[wp] = float(lat), float(lon), bool(int(pm_only))

        for b in self.tile.blocks:
            c = Cache.from_block(b)
            self.assertIn(c.wp, expected_caches)
            if not expected_caches[c.wp][2]:  # if not PM only
                self.assertAlmostEqual(c.location.latitude, expected_caches[
                    c.wp][0], self.POSITION_ACCURANCY)
                self.assertAlmostEqual(c.location.longitude, expected_caches[
                    c.wp][1], self.POSITION_ACCURANCY)
            expected_caches.pop(c.wp)
        self.assertEqual(len(expected_caches), 0)

    def test_precision(self):
        with self.subTest("with point coorection"):
            t1 = make_tile(0, 0, 14)[0]
            p = Point(49.75, 13.36)
            self.assertAlmostEqual(t1.precision(p), 6.173474613462484)

        with self.subTest("precision is larger on greater z values"):
            t1 = make_tile(0, 0, 13)[0]
            t2 = make_tile(0, 0, 14)[0]
            self.assertGreater(t1.precision(), t2.precision())

        with self.subTest("precision is larger when tile is divided to smaller pieces"):
            t1 = make_tile(0, 0, 14)[0]
            t1.size = 10
            t2 = make_tile(0, 0, 14)[0]
            t2.size = 100
            self.assertGreater(t1.precision(), t2.precision())


class TestBlock(unittest.TestCase):
    # {descriptor: [points, midpoint, x_lim, y_lim]}
    good_cases = {9: [[(1, 1), (1, 2), (1, 3),
                       (2, 1), (2, 2), (2, 3),
                       (3, 1), (3, 2), (3, 3)],
                      UTFGridPoint(2.0, 2.0),
                      (1, 3), (1, 3)],
                  6: [[(1, 0), (1, 1),
                       (2, 0), (2, 1),
                       (3, 0), (3, 1)],
                      UTFGridPoint(2.0, 0.0),
                      (1, 3), (-1, 1)],
                  4: [[(62, 62), (62, 63),
                       (63, 62), (63, 63)],
                      UTFGridPoint(63.0, 63.0),
                      (62, 64), (62, 64)],
                  3: [[(63, 30), (63, 31), (63, 32)],
                      UTFGridPoint(64.0, 31.0),
                      (63, 65), (30, 32)],
                  2: [[(62, 0),
                       (63, 0)],
                      UTFGridPoint(63.0, -1.0),
                      (62, 64), (-2, 0)],
                  1: [[(0, 63), ],
                      UTFGridPoint(-1.0, 64.0),
                      (-2, 0), (63, 65)],
                  }
    bad_cases = {"too much points":
                 [(1, 1), (1, 2), (1, 3),
                  (2, 1), (2, 2), (2, 3),
                  (3, 1), (3, 2), (3, 3), (3, 4)],
                 "still too much points":
                     [(63, 30), (63, 31), (63, 32), (63, 33)],
                 "point missing: 9":
                     [(1, 1),         (1, 3),
                      (2, 1), (2, 2), (2, 3),
                      (3, 1), (3, 2), (3, 3)],
                 "point missing: 6":
                     [(1, 0), (1, 1),
                      (2, 0),
                      (3, 0), (3, 1)],
                 "points not aligned":
                     [(1, 1), (1, 2), (1, 3),
                      (2, 1),         (2, 3), (2, 4),
                      (3, 1), (3, 2), (3, 3)],
                 }

    def setUp(self):
        self.b = Block()
        Block.instances = []

    def _generate_blocks(self, case, num=100):
        """Generate some blocks for testing block sizes"""
        blocks = [Block() for i in range(num)]
        for block in blocks:
            block.points = self.good_cases[case][0]
        return blocks

    def test_determine_block_size(self):
        """Test if correct size is determined based on passed points"""

        with self.subTest("initial value"):
            self.assertEqual(Block.size, 3)

        with self.subTest("all blocks has 9 points"):
            blocks = self._generate_blocks(9, 100)
            Block.determine_block_size()
            self.assertEqual(Block.size, 3)
            del blocks

        with self.subTest("most blocks has 9 points, some has 6 points"):
            blocks = self._generate_blocks(9, 100) + self._generate_blocks(6, 20)
            Block.determine_block_size()
            self.assertEqual(Block.size, 3)
            del blocks

        with self.subTest("most blocks has 9 points, some has other num of points"):
            blocks = self._generate_blocks(9, 100) + self._generate_blocks(6, 20)
            blocks += self._generate_blocks(3, 10) + self._generate_blocks(1, 2)
            Block.determine_block_size()
            self.assertEqual(Block.size, 3)
            del blocks

        with self.subTest("small number of instances"):
            blocks = self._generate_blocks(9, 10)
            with self.assertLogs(level=logging.WARNING):
                Block.determine_block_size()
            self.assertEqual(Block.size, 3)
            del blocks

        with self.subTest("all blocks has 4 points"):
            blocks = self._generate_blocks(4, 100)
            with self.assertLogs(level=logging.WARNING):
                Block.determine_block_size()
            self.assertEqual(Block.size, 2)
            del blocks

        # set back to initial value
        Block.size = 3

    def test_points(self):
        """Test points operations"""

        # tested block should act as set, so create a reference set and compare contents
        ref_set = set()

        with self.subTest("empty"):
            self.assertEqual(self.b.points, ref_set)

        with self.subTest("adding one point"):
            self.b.add(UTFGridPoint(3, 4))
            ref_set.add(UTFGridPoint(3, 4))
            self.assertEqual(self.b.points, ref_set)

        with self.subTest("adding one point with automatic wrapping"):
            self.b.add((30, 40))
            ref_set.add(UTFGridPoint(30, 40))
            self.assertEqual(self.b.points, ref_set)

        with self.subTest("setting multiple points at once"):
            points = (0, 0), (1, 2), (3, 4), (1, 2), (5, 6)
            self.b.points = points
            ref_set = {UTFGridPoint(*p) for p in points}
            self.assertEqual(self.b.points, ref_set)

        with self.subTest("adding multiple points by update"):
            points = (0, 0), (10, 20), (30, 40), (10, 20), (50, 60)
            self.b.update(points)
            ref_set.update({UTFGridPoint(*p) for p in points})
            self.assertEqual(self.b.points, ref_set)

    def test_middle_point(self):
        """Check that correct middle points are returned"""
        for i, case in self.good_cases.items():
            points, mid_point, xlim, ylim = case
            with self.subTest("{} points".format(i)):
                self.b.points = points
                self.assertEqual(self.b.middle_point, mid_point)

        for description, case in self.bad_cases.items():
            with self.subTest(description):
                with self.assertRaises(BadBlockError):
                    self.b.points = case
                    self.b.middle_point

    def test_get_corrected_limits(self):
        """Check calculation of block limits when going out of the border"""
        for i, case in self.good_cases.items():
            points, mid_point, ref_xlim, ref_ylim = case
            self.b.points = points

            with self.subTest("{} points, X axis".format(i)):
                self.assertEqual(self.b._get_corrected_limits(*self.b._xlim), ref_xlim)

            with self.subTest("{} points, Y axis".format(i)):
                self.assertEqual(self.b._get_corrected_limits(*self.b._ylim), ref_ylim)


class TestModule(unittest.TestCase):
    def test_to_decimal(self):
        self.assertEqual(to_decimal(49, 43.850), 49.73083)
        self.assertEqual(to_decimal(13, 22.905), 13.38175)
