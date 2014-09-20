#!/usr/bin/env python3

import os
import json
import unittest
import pycaching
from pycaching.errors import LoginFailedException, GeocodeError, PMOnlyException
from pycaching import Geocaching
from pycaching import Cache
from pycaching import Point


# please DO NOT CHANGE!
_username, _password = "cache-map", "pGUgNw59"


class TestGeocaching(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = Geocaching()
        cls.g.login(_username, _password)

    def test_geocode(self):
        pilsen = Point(49.74774, 13.37752)
        with self.subTest("existing location"):
            self.assertEqual(self.g.geocode("Pilsen"), pilsen)
            self.assertEqual(self.g.geocode("Plzeň"), pilsen)
            self.assertEqual(self.g.geocode("plzen"), pilsen)

        with self.subTest("non-existing location"):
            with self.assertRaises(GeocodeError):
                self.g.geocode("qwertzuiop")

        with self.subTest("empty request"):
            with self.assertRaises(GeocodeError):
                self.g.geocode("")

    @classmethod
    def tearDownClass(cls):
        cls.g.logout()


class TestLoading(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = Geocaching()
        cls.g.login(_username, _password)

    def test_search(self):
        with self.subTest("normal"):
            expected = ["GC41FJC", "GC17E8Y", "GC1ZAQV"]
            caches = self.g.search(Point(49.733867, 13.397091), len(expected))
            for wp, cache in zip(expected, caches):
                self.assertEqual(wp, cache.wp)

        with self.subTest("pagging"):
            caches = self.g.search(Point(49.733867, 13.397091), 25)
            res = [c for c in caches]
            self.assertNotEqual(res[0], res[20])

    def test_search_quick(self):
        """Perform search and check from logs that things go well"""
        p0 = Point(49.73, 13.38)
        p1 = Point(49.74, 13.40)
        caches = list(self.g.search_quick(p0, p1))
        expected = ["GC41FJC", "GC17E8Y", "GC1ZAQV"]
        for i in expected:
            found = False
            for c in caches:
                if c.wp == i:
                    found = True
                    break
            self.assertTrue(found)
        self.assertLess(caches[0].location.precision, 49.5)
        self.assertGreater(caches[0].location.precision, 49.3)
        # At time of writing, there were 108 caches inside inspected tile
        self.assertLess(len(caches), 130)
        self.assertGreater(len(caches), 90)
        # But only 12 inside this stricter area
        new_caches = list(self.g.search_quick(p0, p1, strict=True))
        self.assertLess(len(new_caches), 16)
        self.assertGreater(len(new_caches), 7)
        newer_caches = list(self.g.search_quick(p0, p1, strict=True))
        self.assertEqual(len(new_caches), len(newer_caches))
        newest_caches = list(self.g.search_quick(p0, p1, precision=45.))
        self.assertLess(newest_caches[0].location.precision, 45.)

    def test_bordering_tiles(self):
        with self.subTest("Not on border"):
            self.assertEqual(
                len(self.g._bordering_tiles(8800.3, 5575.4, 14)), 0)
        with self.subTest("Not on border"):
            self.assertEqual(
                len(self.g._bordering_tiles(8800.3, 5575.4, 14, 0.2)), 0)
        with self.subTest("Now inside border"):
            self.assertEqual(
                self.g._bordering_tiles(8800.3, 5575.4, 14, 0.31),
                {(8799, 5575, 14)})
        with self.subTest("Also inside border"):
            self.assertEqual(
                self.g._bordering_tiles(8800.05, 5575.4, 14),
                {(8799, 5575, 14)})
        with self.subTest("Inside another border"):
            self.assertEqual(
                self.g._bordering_tiles(8800.3, 5575.95, 14),
                {(8800, 5576, 14)})
        with self.subTest("A corner"):
            self.assertEqual(
                self.g._bordering_tiles(8800.05, 5575.95, 14),
                {(8799, 5576, 14), (8800, 5576, 14), (8799, 5575, 14)})

    def test_get_utfgrid_caches(self):
        """Load tiles and check if expected caches are found"""
        folder = os.path.dirname(__file__)
        file_name = "sample_caches"
        file_path = os.path.abspath(os.path.join(folder, file_name))
        expected_caches = set()
        with open(file_path) as f:
            for row in f:
                wp = row.split(',')[0]
                expected_caches.add(wp)
        n_orig = len(expected_caches)
        additional_caches = set()
        for c in self.g._get_utfgrid_caches((8800, 5574, 14),):
            if c.wp in expected_caches:
                expected_caches.discard(c.wp)
            else:
                additional_caches.add(c.wp)
        self.assertLess(len(expected_caches) / n_orig, 0.2,
                        "Over 20 % of caches are lost.  This could be " \
                        + "natural, but failing anyway.")
        self.assertLess(len(additional_caches) / n_orig, 0.2,
                        "Over 20 % unexpected caches found.  This could be " \
                        + "natural, but failing anyway.")

    def test_get_zoom_by_distance(self):
        with self.subTest("World map zoom level"):
            self.assertEqual(
                self.g._get_zoom_by_distance(40e6, 0., 1., 'le'), 0)
        with self.subTest("Next level"):
            self.assertEqual(
                self.g._get_zoom_by_distance(40e6, 0., 1., 'ge'), 1)
        with self.subTest("Tile width greater or equal to 1 km"):
            self.assertEqual(
                self.g._get_zoom_by_distance(1e3, 49., 1., 'le'), 14)
        with self.subTest("More accurate than 10 m"):
            self.assertEqual(
                self.g._get_zoom_by_distance(10., 49., 256, 'ge'), 14)
        with self.subTest("Previous test was correct"):
            p = Point(49., 13.)
            self.assertGreater(p.precision_from_tile_zoom(13), 10)
            self.assertLess(p.precision_from_tile_zoom(14), 10)

    def test_load_cache(self):
        with self.subTest("normal"):
            cache = self.g.load_cache("GC4808G")
            self.assertTrue(isinstance(cache, Cache))
            self.assertEqual("GC4808G", cache.wp)

        with self.subTest("non-ascii chars"):
            cache = self.g.load_cache("GC4FRG5")
            self.assertTrue(isinstance(cache, Cache))
            self.assertEqual("GC4FRG5", cache.wp)

        with self.subTest("PM only"):
            with self.assertRaises(PMOnlyException):
                self.g.load_cache("GC3AHDM")

    def test_load_cache_quick(self):
        cache = self.g.load_cache_quick("GC4808G")
        self.assertTrue(isinstance(cache, Cache))
        self.assertEqual("GC4808G", cache.wp)

    @classmethod
    def tearDownClass(cls):
        cls.g.logout()


class TestLazyLoading(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.g = Geocaching()
        cls.g.login(_username, _password)

    def test_load_cache(self):
        with self.subTest("normal"):
            cache = Cache("GC4808G", self.g)
            self.assertEqual("Nekonecne ticho", cache.name)

        with self.subTest("non-ascii chars"):
            cache = Cache("GC4FRG5", self.g)
            self.assertEqual("Entre l'arbre et la grille.", cache.hint)

    @classmethod
    def tearDownClass(cls):
        cls.g.logout()


class TestLoginOperations(unittest.TestCase):

    def setUp(self):
        self.g = Geocaching()

    def test_login(self):
        with self.subTest("bad username"):
            with self.assertRaises(LoginFailedException):
                self.g.login("", "")

        with self.subTest("good username"):
            self.g.login(_username, _password)

        with self.subTest("good username already logged"):
            self.g.login(_username, _password)

        with self.subTest("bad username automatic logout"):
            with self.assertRaises(LoginFailedException):
                self.g.login("", "")

    def test_get_logged_user(self):
        self.g.login(_username, _password)
        self.assertEqual(self.g.get_logged_user(), _username)

    def test_logout(self):
        self.g.login(_username, _password)
        self.g.logout()
        self.assertIsNone(self.g.get_logged_user())

    def tearDown(self):
        self.g.logout()


class TestPackage(unittest.TestCase):

    def test_login(self):
        pycaching.login(_username, _password)
