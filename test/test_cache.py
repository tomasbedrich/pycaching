#!/usr/bin/env python3

import unittest
from datetime import date

from pycaching import Cache
from pycaching import Geocaching
from pycaching import Point


class TestProperties(unittest.TestCase):

    def setUp(self):
        self.gc = Geocaching()
        self.c = Cache("GC12345", self.gc, name="Testing", cache_type="Traditional Cache", location=Point(), state=True,
                       found=True, size="micro", difficulty=1.5, terrain=5, author="human", hidden=date(2000, 1, 1),
                       attributes={"onehour": True, "kids": False, "available": True}, summary="text",
                       description="long text", hint="rot13", favorites=1)

    def test___str__(self):
        self.assertEqual(str(self.c), "GC12345")

    def test___eq__(self):
        self.assertEqual(self.c, Cache("GC12345", self.gc))

    def test_wp(self):
        self.assertEqual(self.c.wp, "GC12345")

    def test_name(self):
        self.assertEqual(self.c.name, "Testing")

    def test_type(self):
        self.assertEqual(self.c.cache_type, "Traditional Cache")

        with self.subTest("filter invalid"):
            with self.assertRaises(AssertionError):
                self.c.cache_type = "xxx"

    def test_location(self):
        self.assertEqual(self.c.location, Point())

        with self.subTest("filter invalid"):
            with self.assertRaises(AssertionError):
                self.c.location = "somewhere"

    def test_state(self):
        self.assertEqual(self.c.state, True)

    def test_found(self):
        self.assertEqual(self.c.found, True)

    def test_size(self):
        self.assertEqual(self.c.size, "micro")

        with self.subTest("filter invalid"):
            with self.assertRaises(AssertionError):
                self.c.size = "xxx"

    def test_difficulty(self):
        self.assertEqual(self.c.difficulty, 1.5)

        with self.subTest("filter invalid"):
            with self.assertRaises(AssertionError):
                self.c.difficulty = 10

    def test_terrain(self):
        self.assertEqual(self.c.terrain, 5)

        with self.subTest("filter invalid"):
            with self.assertRaises(AssertionError):
                self.c.terrain = -1

    def test_author(self):
        self.assertEqual(self.c.author, "human")

    def test_hidden(self):
        self.assertEqual(self.c.hidden, date(2000, 1, 1))

        with self.subTest("filter invalid"):
            with self.assertRaises(AssertionError):
                self.c.hidden = "now"

    def test_attributes(self):
        self.assertEqual(self.c.attributes, {"onehour": True, "kids": False, "available": True})

        with self.subTest("filter unknown"):
            self.c.attributes = {attr: True for attr in ["onehour", "xxx"]}
            self.assertEqual(self.c.attributes, {"onehour": True})

    def test_summary(self):
        self.assertEqual(self.c.summary, "text")

    def test_description(self):
        self.assertEqual(self.c.description, "long text")

    def test_hint(self):
        self.assertEqual(self.c.hint, "rot13")

    def test_favorites(self):
        self.assertEqual(self.c.favorites, 1)
