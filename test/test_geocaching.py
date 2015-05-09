#!/usr/bin/env python3

import os
import unittest
import pycaching
from geopy.distance import great_circle
from pycaching.errors import NotLoggedInException, LoginFailedException, GeocodeError, PMOnlyException
from pycaching import Geocaching
from pycaching import Cache
from pycaching import Point
from pycaching import Rectangle


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
            self.assertLess(great_circle(self.g.geocode("Pilsen"), pilsen).miles, 10)
            self.assertLess(great_circle(self.g.geocode("Plzeň"), pilsen).miles, 10)
            self.assertLess(great_circle(self.g.geocode("plzen"), pilsen).miles, 10)

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
            expected = ["GC41FJC", "GC17E8Y", "GC5ND9F"]
            caches = self.g.search(Point(49.733867, 13.397091), 3)
            for cache in caches:
                self.assertIn(cache.wp, expected)

        with self.subTest("pagging"):
            caches = list(self.g.search(Point(49.733867, 13.397091), 100))
            self.assertNotEqual(caches[0], caches[50])

    def test_search_quick(self):
        """Perform search and check found caches"""
        rect = Rectangle(Point(49.73, 13.38), Point(49.74, 13.40))
        caches = list(self.g.search_quick(rect))
        strict_caches = list(self.g.search_quick(rect, strict=True))
        precise_caches = list(self.g.search_quick(rect, precision=45.))

        # Check for known geocaches
        expected = ["GC41FJC", "GC17E8Y", "GC5ND9F"]
        for i in expected:
            found = False
            for c in caches:
                if c.wp == i:
                    found = True
                    break
            with self.subTest("Check if {} is in results".format(c.wp)):
                self.assertTrue(found)

        with self.subTest("Precision is in assumed range"):
            self.assertLess(caches[0].location.precision, 49.5)
            self.assertGreater(caches[0].location.precision, 49.3)

        with self.subTest("Found roughly correct amount of caches"):
            # At time of writing, there were 108 caches inside inspected tile
            self.assertLess(len(caches), 130)
            self.assertGreater(len(caches), 90)

        with self.subTest("Strict handling of cache coordinates"):
            # ...but only 12 inside this stricter area
            self.assertLess(len(strict_caches), 16)
            self.assertGreater(len(strict_caches), 7)

        with self.subTest("Precision grows when asking for it"):
            self.assertLess(precise_caches[0].location.precision, 45.)

    def test_calculate_initial_tiles(self):
        expect_tiles = [(2331, 1185, 12), (2331, 1186, 12),
                        (2332, 1185, 12), (2332, 1186, 12)]
        expect_precision = 76.06702024121832
        r = Rectangle(Point(60.15, 24.95), Point(60.17, 25.00))
        tiles, starting_precision = self.g._calculate_initial_tiles(r)
        for t in tiles:
            with self.subTest("Tile {} expected as initial tile".format(t)):
                self.assertIn(t, expect_tiles)
        with self.subTest("Expected precision"):
            self.assertAlmostEqual(starting_precision, expect_precision)

    def test_get_utfgrid_caches(self):
        """Load tiles and check if expected caches are found"""

        # load expected result
        file_path = os.path.join(os.path.dirname(__file__), "sample_caches.csv")
        expected_caches = set()
        with open(file_path) as f:
            for row in f:
                wp = row.split(',')[0]
                expected_caches.add(wp)
        n_orig = len(expected_caches)

        # load search result
        additional_caches = set()
        for c in self.g._get_utfgrid_caches((8800, 5574, 14),):
            if c.wp in expected_caches:
                expected_caches.discard(c.wp)
            else:
                additional_caches.add(c.wp)

        with self.subTest("Expected caches found"):
            self.assertLess(len(expected_caches) / n_orig, 0.2,
                            "Over 20 % of expected caches are lost.")

        with self.subTest("Unexpected caches not found"):
            self.assertLess(len(additional_caches) / n_orig, 0.2,
                            "Over 20 % of found caches are unexpected.")

    def test_bordering_tiles(self):
        """Check if geocache is near tile border"""
        # description, function parameters, set of bordering tiles
        checks = [
            ["Not on border", (8800.3, 5575.4, 14),      set()],
            ["Not on border", (8800.3, 5575.4, 14, 0.2), set()],
            ["Now inside border", (8800.3, 5575.4, 14, 0.31),
             {(8799, 5575, 14)}],
            ["Also inside border", (8800.05, 5575.4, 14), {(8799, 5575, 14)}],
            ["Inside another border", (8800.3, 5575.95, 14),
             {(8800, 5576, 14)}],
            ["A corner", (8800.05, 5575.95, 14),
             {(8799, 5576, 14), (8800, 5576, 14), (8799, 5575, 14)}]
        ]
        for description, params, output in checks:
            with self.subTest(description):
                self.assertEqual(self.g._bordering_tiles(*params), output)

    def test_get_zoom_by_distance(self):
        """Check that calculated zoom levels are correct"""
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

    def test_login_needed(self):
        with self.assertRaises(NotLoggedInException):
            self.g.load_cache("GC41FJC")

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
