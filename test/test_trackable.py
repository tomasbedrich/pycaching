#!/usr/bin/env python3

import unittest
from pycaching import Geocaching, Trackable, Point
from pycaching.errors import ValueError as PycachingValueError, LoadError

from test.test_geocaching import _username, _password


class TestProperties(unittest.TestCase):

    def setUp(self):
        self.gc = Geocaching()
        self.t = Trackable(self.gc, "TB123AB", name="Testing", type="Travel Bug", location=Point(), owner="human",
                           description="long text", goal="short text")

    def test___str__(self):
        self.assertEqual(str(self.t), "TB123AB")

    def test___eq__(self):
        self.assertEqual(self.t, Trackable(self.gc, "TB123AB"))

    def test_tid(self):
        self.assertEqual(self.t.tid, "TB123AB")

        with self.subTest("filter invalid"):
            with self.assertRaises(PycachingValueError):
                self.t.tid = "xxx"

    def test_name(self):
        self.assertEqual(self.t.name, "Testing")

    def test_type(self):
        self.assertEqual(self.t.type, "Travel Bug")

    def test_owner(self):
        self.assertEqual(self.t.owner, "human")

    def test_description(self):
        self.assertEqual(self.t.description, "long text")

    def test_goal(self):
        self.assertEqual(self.t.goal, "short text")


class TestMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gc = Geocaching()
        cls.gc.login(_username, _password)

    def test_load(self):
        with self.subTest("tid"):
            trackable = Trackable(self.gc, "TB1KEZ9")
            self.assertEqual("Lilagul #2: SwedenHawk Geocoin", trackable.name)

        with self.subTest("trackable url"):
            url = "http://www.geocaching.com/track/details.aspx?guid=cff00ac4-f562-486e-b303-32b2d01ed386"
            trackable = Trackable(self.gc, None, url=url)
            self.assertEqual("Lilagul #2: SwedenHawk Geocoin", trackable.name)

        with self.subTest("fail lazyload"):
            trackable = Trackable(self.gc, None)
            with self.assertRaises(LoadError):
                trackable.name
