#!/usr/bin/env python3

import unittest
from datetime import date
from pycaching.errors import ValueError
from pycaching import Trackable
from pycaching import Geocaching
from pycaching import Point


class TestProperties(unittest.TestCase):

    def setUp(self):
        self.gc = Geocaching()
        self.t = Trackable("TB123AB", self.gc, name="Testing", type="Travel Bug", location=Point(), owner="human", description="long text", goal="short text")

    def test___str__(self):
        self.assertEqual(str(self.t), "TB123AB")

    def test___eq__(self):
        self.assertEqual(self.t, Trackable("TB123AB", self.gc))

    def test_geocaching(self):
        with self.assertRaises(ValueError):
            Trackable("TB123AB", None)

    def test_tid(self):
        self.assertEqual(self.t.tid, "TB123AB")

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
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
