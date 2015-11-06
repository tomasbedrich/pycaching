#!/usr/bin/env python3

import logging
import unittest
import json
from unittest import mock
from os import path

from pycaching import Geocaching, Cache
from pycaching.tile import Tile, Block, UTFGridPoint
from pycaching.errors import BadBlockError

from test.test_geocaching import _username, _password

_sample_caches_file = path.join(path.dirname(__file__), "sample_caches.csv")
_sample_utfgrid_file = path.join(path.dirname(__file__), "sample_utfgrid.json")


class TestTile(unittest.TestCase):

    # see http://gis.stackexchange.com/questions/8650/how-to-measure-the-accuracy-of-latitude-and-longitude
    POSITION_ACCURANCY = 3  # = up to 110 meters

    @classmethod
    def setUpClass(cls):
        cls.gc = Geocaching()
        cls.gc.login(_username, _password)

    def setUp(self):
        self.tile = Tile(self.gc, 8800, 5574, 14)

    def test_download_utfgrid(self):
        """Test if downloading a UTFGrid passes without errors"""

        with self.subTest("not getting .png tile first"):
            self.tile._download_utfgrid()

        with self.subTest("getting .png tile first"):
            self.tile._download_utfgrid(get_png=True)

    @mock.patch.object(Tile, '_download_utfgrid')
    def test_blocks(self, mock_utfgrid):
        """Parse locally stored grid and compare to expected results"""

        # load mock utfgrid from file
        with open(_sample_utfgrid_file) as f:
            mock_utfgrid.return_value = json.load(f)

        # load expected caches from file
        expected_caches = {}
        with open(_sample_caches_file) as f:
            for row in f:
                wp, lat, lon, pm_only = row.strip().split(",")
                expected_caches[wp] = float(lat), float(lon), bool(int(pm_only))

        for b in self.tile.blocks:
            c = Cache.from_block(self.gc, b)
            self.assertIn(c.wp, expected_caches)
            if not expected_caches[c.wp][2]:  # if not PM only
                self.assertAlmostEqual(c.location.latitude, expected_caches[c.wp][0], self.POSITION_ACCURANCY)
                self.assertAlmostEqual(c.location.longitude, expected_caches[c.wp][1], self.POSITION_ACCURANCY)
            expected_caches.pop(c.wp)
        self.assertEqual(len(expected_caches), 0)


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
                self.assertEqual(self.b._get_corrected_limits(self.b._xlim), ref_xlim)

            with self.subTest("{} points, Y axis".format(i)):
                self.assertEqual(self.b._get_corrected_limits(self.b._ylim), ref_ylim)
