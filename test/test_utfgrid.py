#!/usr/bin/env python3

import os
import json
import logging
import unittest

from pycaching import Geocaching
from pycaching.utfgrid import UTFGrid, GridCoordinateBlock
from pycaching.errors import Error

from test.test_geocaching import _username, _password


_this_folder = os.path.dirname(__file__)
sample_files = {i: os.path.join(_this_folder, i) for i in ["sample_caches.csv", "sample_utfgrid.json"]}


class TestUTFGrid(unittest.TestCase):

    def setUp(self):
        self.grid = UTFGrid(Geocaching(), 8800, 5574, 14)

    def test_download(self):
        """Test if downloading a tile goes nice without errors"""
        self.grid._gc.login(_username, _password)
        with self.subTest("Not getting .png tile first"):
            list(self.grid.download())
        with self.subTest("Getting .png tile first"):
            list(self.grid.download(get_png_first=True))

    def test_parse(self):
        """Parse locally stored grid and compare to expected results"""
        expected_caches = {}
        with open(sample_files["sample_caches.csv"]) as f:
            for row in f:
                wp, lat, lon = row.split(',')
                expected_caches[wp] = (float(lat), float(lon))
        with open(sample_files["sample_utfgrid.json"]) as f:
            j = json.loads(f.read())
        caches = self.grid._parse_utfgrid(j)
        for c in caches:
            with self.subTest("Cache " + wp):
                self.assertIn(c.wp, expected_caches)
                self.assertAlmostEqual(c.location.latitude, expected_caches[c.wp][0])
                self.assertAlmostEqual(c.location.longitude, expected_caches[c.wp][1])
                expected_caches.pop(c.wp)
        self.assertEqual(len(expected_caches), 0)


class TestGridCoordinateBlock(unittest.TestCase):

    # {descriptor: [points, midpoint, x_lim, y_lim]}
    good_cases = {9: [[(1, 1), (1, 2), (1, 3),
                       (2, 1), (2, 2), (2, 3),
                       (3, 1), (3, 2), (3, 3)],
                      [2.0, 2.0],
                      (1, 3), (1, 3)],
                  6: [[(1, 0), (1, 1),
                       (2, 0), (2, 1),
                       (3, 0), (3, 1)],
                      [2.0, 0.0],
                      (1, 3), (-1, 1)],
                  4: [[(62, 62), (62, 63),
                       (63, 62), (63, 63)],
                      [63.0, 63.0],
                      (62, 64), (62, 64)],
                  3: [[(63, 30), (63, 31), (63, 32)],
                      [64.0, 31.0],
                      (63, 65), (30, 32)],
                  2: [[(62, 0),
                       (63, 0)],
                      [63.0, -1.0],
                      (62, 64), (-2, 0)],
                  1: [[(0, 63)],
                      [-1.0, 64.0],
                      (-2, 0), (63, 65)],
                  }
    bad_cases = {'too much points':
                 [(1, 1), (1, 2), (1, 3),
                  (2, 1), (2, 2), (2, 3),
                  (3, 1), (3, 2), (3, 3), (3, 4)],
                 'still too much points':
                     [(63, 30), (63, 31), (63, 32), (63, 33)],
                 'point missing: 9':
                     [(1, 1),         (1, 3),
                      (2, 1), (2, 2), (2, 3),
                      (3, 1), (3, 2), (3, 3)],
                 'point missing: 6':
                     [(1, 0), (1, 1),
                      (2, 0),
                      (3, 0), (3, 1)],
                 'points not aligned':
                     [(1, 1), (1, 2), (1, 3),
                      (2, 1),         (2, 3), (2, 4),
                      (3, 1), (3, 2), (3, 3)],
                 }

    def setUp(self):
        self.grid = UTFGrid(Geocaching(), 8800, 5574, 14)
        self.grid.size = 64
        self.cb = GridCoordinateBlock(self.grid)

    def test_determine_block_size(self, *block_points):
        with self.subTest("Initial value"):
            self.assertEqual(GridCoordinateBlock.size, 3)

        with self.subTest("Initial value of instance"):
            self.assertEqual(GridCoordinateBlock(self.grid).size, 3)

        with self.subTest("No changes: same value"):
            sizes = [100] * 9 + [4] * 3 + [1]
            GridCoordinateBlock.determine_block_size(*sizes)
            self.assertEqual(GridCoordinateBlock.size, 3)

        with self.subTest("No changes: no input"):
            GridCoordinateBlock.determine_block_size()
            self.assertEqual(GridCoordinateBlock.size, 3)

        with self.subTest("Should change to 16"):
            sizes = [16] * 21 + [4]
            with self.assertLogs(level=logging.WARNING):
                GridCoordinateBlock.determine_block_size(*sizes)
            self.assertEqual(GridCoordinateBlock.size, 4)

        with self.subTest("New value of instance"):
            self.assertEqual(GridCoordinateBlock(self.grid).size, 4)

        # Set back to initial value
        GridCoordinateBlock.size = 3

    def test_add_point(self):
        """Test passing points at initialization"""
        with self.subTest("Zero points"):
            self.assertEqual(self.cb.points,
                             GridCoordinateBlock(self.grid).points)

        with self.subTest("One point"):
            self.cb.points = []
            self.cb.add((3, 4))
            self.assertEqual(self.cb.points,
                             GridCoordinateBlock(self.grid, (3, 4)).points)

        with self.subTest("Multiple points: pass directly"):
            points = [(0, 0), (1, 2), (3, 4), (1, 2), (5, 6)]
            self.cb.points = points
            self.assertEqual(self.cb.points,
                             GridCoordinateBlock(self.grid, *points).points)

        with self.subTest("Multiple points: update"):
            self.cb.points = []
            points = [(0, 0), (1, 2), (3, 4), (1, 2), (5, 6)]
            self.cb.update(points)
            self.assertEqual(self.cb.points,
                             GridCoordinateBlock(self.grid, *points).points)

    def test_get_middle_point(self):
        """Check that correct middle points are returned"""
        for case in [self.good_cases, self.bad_cases]:
            for i in case:
                if case is self.good_cases:
                    points, mid_point, xlim, ylim = self.good_cases[i]
                    with self.subTest('{} points'.format(i)):
                        self.cb.points = points
                        self.assertEqual(self.cb._get_middle_point(),
                                         mid_point)
                else:
                    with self.subTest('Malformed input: {}'.format(i)):
                        with self.assertRaises(Error):
                            self.cb.points = self.bad_cases[i]
                            self.cb._get_middle_point()

    def test_check_block(self):
        """Test block form with various passes and fails"""
        for case in [self.good_cases, self.bad_cases]:
            for i in case:
                if case is self.good_cases:
                    self.cb.points = case[i][0]
                    with self.subTest(i):
                        if i == 9:
                            self.assertEqual(self.cb._check_block(), 1, i)
                        else:
                            self.assertEqual(self.cb._check_block(), 2, i)
                else:
                    self.cb.points = case[i]
                    with self.subTest(i):
                        self.assertEqual(self.cb._check_block(), 0, i)

    def test_find_limits(self):
        """Check calculation of block limits when going out of the border"""
        for i in self.good_cases:
            points, mid_point, xlim, ylim = self.good_cases[i]
            self.cb.points = points
            for axis, limits in zip(['x', 'y'], [xlim, ylim]):
                with self.subTest('{} points, {} axis'.format(i, axis)):
                    self.assertEqual(self.cb._find_limits(axis), limits)
