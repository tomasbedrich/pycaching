#!/usr/bin/env python3

import unittest
from datetime import date
from pycaching.errors import ValueError
from pycaching.enums import LogType as Type
from pycaching import Log


class TestProperties(unittest.TestCase):

    def setUp(self):
        self.l = Log(type="found it", text="text", visited="2012-02-02", author="human")

    def test___str__(self):
        self.assertEqual(str(self.l), "text")

    def test_type(self):
        self.assertEqual(self.l.type, Type.found_it)

    def test_text(self):
        self.assertEqual(self.l.text, "text")

    def test_visited(self):
        self.assertEqual(self.l.visited, date(2012, 2, 2))

        with self.subTest("automatic str conversion"):
            self.l.visited = "1/30/2000"
            self.assertEqual(self.l.visited, date(2000, 1, 30))

        with self.subTest("filter invalid string"):
            with self.assertRaises(ValueError):
                self.l.visited = "now"

        with self.subTest("filter invalid types"):
            with self.assertRaises(ValueError):
                self.l.visited = None

    def test_author(self):
        self.assertEqual(self.l.author, "human")
