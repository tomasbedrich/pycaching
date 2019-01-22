#!/usr/bin/env python3

import datetime
import itertools

from pycaching.util import rot13, parse_date, format_date, get_possible_attributes
from . import NetworkedTest


class TestModule(NetworkedTest):
    def test_rot13(self):
        self.assertEqual(rot13("Text"), "Grkg")
        self.assertEqual(rot13("abc'ř"), "nop'ř")

    def test_parse_date(self):
        dates = datetime.date(2014, 1, 30), datetime.date(2000, 1, 1), datetime.date(2020, 12, 13)
        patterns = ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y",
                    "%d.%m.%Y", "%d/%b/%Y", "%d.%b.%Y", "%b/%d/%Y", "%d %b %y")

        # generate all possible formats for all dates and test equality
        for date, pattern in itertools.product(dates, patterns):
            formatted_date = datetime.datetime.strftime(date, pattern)
            self.assertEqual(date, parse_date(formatted_date))

    def test_format_date(self):
        date = datetime.date(2015, 1, 30)
        cases = {
            "d. M. yyyy": "30. 1. 2015",
            "d.M.yyyy": "30.1.2015",
            "d.MM.yyyy": "30.01.2015",
            "d/M/yy": "30/1/15",
            "d/M/yyyy": "30/1/2015",
            "d/MM/yyyy": "30/01/2015",
            "dd MMM yy": "30 Jan 15",
            "dd.MM.yyyy": "30.01.2015",
            "dd.MM.yyyy.": "30.01.2015.",
            "dd.MMM.yyyy": "30.Jan.2015",
            "dd/MM/yy": "30/01/15",
            "dd/MM/yyyy": "30/01/2015",
            "dd/MMM/yyyy": "30/Jan/2015",
            "dd-MM-yy": "30-01-15",
            "dd-MM-yyyy": "30-01-2015",
            "d-M-yyyy": "30-1-2015",
            "M/d/yyyy": "1/30/2015",
            "MM/dd/yyyy": "01/30/2015",
            "MMM/dd/yyyy": "Jan/30/2015",
            "yyyy.MM.dd.": "2015.01.30.",
            "yyyy/MM/dd": "2015/01/30",
            "yyyy-MM-dd": "2015-01-30",
        }
        for user_format, ref_result in cases.items():
            self.assertEqual(format_date(date, user_format), ref_result)

    def test_get_possible_attributes(self):
        with self.recorder.use_cassette('util_attributes'):
            attributes = get_possible_attributes(session=self.session)

        with self.subTest("existing attributes"):
            for attr in "dogs", "public", "kids":
                self.assertIn(attr, attributes)

        with self.subTest("non-existing attributes"):
            self.assertNotIn("xxx", attributes)
