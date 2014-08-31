#!/usr/bin/env python3

import unittest
from pycaching import Util
from datetime import date


class TestUtil(unittest.TestCase):

    def test_rot13(self):
        self.assertEqual(Util.rot13("Text"), "Grkg")
        self.assertEqual(Util.rot13("abc'ř"), "nop'ř")

    def test_coord_conversion(self):
        self.assertEqual(Util.to_decimal(49, 43.850), 49.73083)
        self.assertEqual(Util.to_decimal(13, 22.905), 13.38175)
        self.assertEqual(Util.to_mindec(13.38175), (13, 22.905))
        self.assertEqual(Util.to_mindec(49.73083), (49, 43.850))

    def test_date_parsing(self):
        self.assertEqual(date(2000, 1, 1), Util.parse_date("2000/1/1"))
        self.assertEqual(date(2000, 1, 30), Util.parse_date("2000-1-30"))
        self.assertEqual(date(2000, 1, 30), Util.parse_date("2000/1/30"))
        self.assertEqual(date(2000, 1, 30), Util.parse_date("30/1/2000"))
        self.assertEqual(date(2000, 1, 30), Util.parse_date("1/30/2000"))
        self.assertEqual(date(2000, 1, 30), Util.parse_date("30-1-2000"))
