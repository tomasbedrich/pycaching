#!/usr/bin/env python3

import unittest
import datetime
import itertools
from pycaching.util import rot13, parse_date, get_possible_attributes


class TestModule(unittest.TestCase):

    def test_rot13(self):
        self.assertEqual(rot13("Text"), "Grkg")
        self.assertEqual(rot13("abc'ř"), "nop'ř")

    def test_date_parsing(self):
        dates = (datetime.date(2014, 1, 30), datetime.date(2000, 1, 1), datetime.date(2020, 12, 13))
        patterns = ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y",
                    "%d.%m.%Y", "%d/%b/%Y", "%d.%b.%Y", "%b/%d/%Y", "%d %b %y")

        # generate all possible formats for all dates and test equality
        for date, pattern in itertools.product(dates, patterns):
            formatted_date = datetime.datetime.strftime(date, pattern)
            self.assertEqual(date, parse_date(formatted_date))

    def test_get_possible_attributes(self):
        attributes = get_possible_attributes()

        with self.subTest("existing attributes"):
            for attr in "dogs", "public", "kids":
                self.assertIn(attr, attributes)

        with self.subTest("non-existing attributes"):
                self.assertNotIn("xxx", attributes)
