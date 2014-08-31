#!/usr/bin/env python3

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
