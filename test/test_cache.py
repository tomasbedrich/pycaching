#!/usr/bin/env python3

import unittest

from pycaching import Cache
from pycaching import Geocaching


class TestProperties(unittest.TestCase):

    def setUp(self):
        self.c = Cache("GC12345", Geocaching())

    def test_wp(self):
        self.assertEqual(self.c.wp, "GC12345")

    def test_difficulty(self):
        self.c.difficulty = 1.5
        self.assertEqual(self.c.difficulty, 1.5)

    def test_type(self):
        self.c.cache_type = "Traditional Cache"
        self.assertEqual(self.c.cache_type, "Traditional Cache")

        with self.subTest("filter invalid"):
            with self.assertRaises(AssertionError):
                self.c.cache_type = "xxx"

    def test_description(self):
        self.c.description = "test"
        self.assertEqual(self.c.description, "test")

    def test_attributes(self):
        self.c.attributes = {attr: True for attr in ["onehour", "kids", "available"]}
        self.assertEqual(self.c.attributes, {"onehour": 1, "kids": 1, "available": 1})

        with self.subTest("filter unknown"):
            self.c.attributes = {attr: True for attr in ["onehour", "xxx"]}
            self.assertEqual(self.c.attributes, {"onehour": 1})
