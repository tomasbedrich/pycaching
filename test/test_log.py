#!/usr/bin/env python3

import unittest
from datetime import date
from pycaching.log import Log, Type
from pycaching.errors import ValueError as PycachingValueError


class TestLog(unittest.TestCase):

    def setUp(self):
        self.l = Log(type=Type.found_it, text="text", visited="2012-02-02", author="human")

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
            with self.assertRaises(PycachingValueError):
                self.l.visited = "now"

        with self.subTest("filter invalid types"):
            with self.assertRaises(PycachingValueError):
                self.l.visited = None

    def test_author(self):
        self.assertEqual(self.l.author, "human")


class TestType(unittest.TestCase):

    def test_from_filename(self):
        with self.subTest("valid types"):
            self.assertEqual(Type.found_it, Type.from_filename("2"))
            self.assertEqual(Type.visit, Type.from_filename("75"))

        with self.subTest("special valid types"):
            self.assertEqual(Type.visit, Type.from_filename("1001"))
            self.assertEqual(Type.publish_listing, Type.from_filename("1003"))

        with self.subTest("invalid type"):
            with self.assertRaises(PycachingValueError):
                Type.from_filename("6666")
