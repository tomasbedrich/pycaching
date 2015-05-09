#!/usr/bin/env python3

import unittest
from datetime import date
from pycaching.errors import ValueError
from pycaching import Cache
from pycaching import Geocaching
from pycaching import Point


class TestProperties(unittest.TestCase):

    def setUp(self):
        self.gc = Geocaching()
        self.c = Cache("GC12345", self.gc, name="Testing", cache_type="Traditional Cache", location=Point(), state=True,
                       found=False, size="micro", difficulty=1.5, terrain=5, author="human", hidden=date(2000, 1, 1),
                       attributes={"onehour": True, "kids": False, "available": True}, summary="text",
                       description="long text", hint="rot13", favorites=0, pm_only=False)

    def test___str__(self):
        self.assertEqual(str(self.c), "GC12345")

    def test___eq__(self):
        self.assertEqual(self.c, Cache("GC12345", self.gc))

    def test_geocaching(self):
        with self.assertRaises(ValueError):
            Cache("GC12345", None)

    def test_wp(self):
        self.assertEqual(self.c.wp, "GC12345")

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
                self.c.wp = "xxx"

    def test_name(self):
        self.assertEqual(self.c.name, "Testing")

    def test_type(self):
        self.assertEqual(self.c.cache_type, "Traditional")

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
                self.c.cache_type = "xxx"

    def test_location(self):
        self.assertEqual(self.c.location, Point())

        with self.subTest("automatic str conversion"):
            self.c.location = "S 36 51.918 E 174 46.725"
            self.assertEqual(self.c.location, Point.from_string("S 36 51.918 E 174 46.725"))

        with self.subTest("filter invalid string"):
            with self.assertRaises(ValueError):
                self.c.location = "somewhere"

        with self.subTest("filter invalid types"):
            with self.assertRaises(ValueError):
                self.c.location = None

    def test_state(self):
        self.assertEqual(self.c.state, True)

    def test_found(self):
        self.assertEqual(self.c.found, False)

    def test_size(self):
        self.assertEqual(self.c.size, "micro")

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
                self.c.size = "xxx"

    def test_difficulty(self):
        self.assertEqual(self.c.difficulty, 1.5)

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
                self.c.difficulty = 10

    def test_terrain(self):
        self.assertEqual(self.c.terrain, 5)

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
                self.c.terrain = -1

    def test_author(self):
        self.assertEqual(self.c.author, "human")

    def test_hidden(self):
        self.assertEqual(self.c.hidden, date(2000, 1, 1))

        with self.subTest("automatic str conversion"):
            self.c.hidden = "1/30/2000"
            self.assertEqual(self.c.hidden, date(2000, 1, 30))

        with self.subTest("filter invalid string"):
            with self.assertRaises(ValueError):
                self.c.hidden = "now"

        with self.subTest("filter invalid types"):
            with self.assertRaises(ValueError):
                self.c.hidden = None

    def test_attributes(self):
        self.assertEqual(self.c.attributes, {"onehour": True, "kids": False, "available": True})

        with self.subTest("filter unknown"):
            self.c.attributes = {attr: True for attr in ["onehour", "xxx"]}
            self.assertEqual(self.c.attributes, {"onehour": True})

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
                self.c.attributes = None

    def test_summary(self):
        self.assertEqual(self.c.summary, "text")

    def test_description(self):
        self.assertEqual(self.c.description, "long text")

    def test_hint(self):
        self.assertEqual(self.c.hint, "rot13")

    def test_favorites(self):
        self.assertEqual(self.c.favorites, 0)

    def test_pm_only(self):
        self.assertEqual(self.c.pm_only, False)
