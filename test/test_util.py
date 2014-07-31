#!/usr/bin/env python3

import unittest

from pycaching import Util


class TestUtil(unittest.TestCase):

    def test_rot13(self):
        self.assertEqual(Util.rot13("Text"), "Grkg")
        self.assertEqual(Util.rot13("abc'ř"), "nop'ř")

    def test_coord_conversion(self):
        self.assertEqual(Util.to_decimal(49, 43.850), 49.73083)
        self.assertEqual(Util.to_decimal(13, 22.905), 13.38175)
        self.assertEqual(Util.to_mindec(13.38175), (13, 22.905))
        self.assertEqual(Util.to_mindec(49.73083), (49, 43.850))
