#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import re
import urllib2
import logging
import unittest
import string
from types import *
from urllib import urlencode


class Util(object):

    # Useragent: which browser/platform should this script masquerade as
    useragent = "User-Agent=Mozilla/5.0 (X11; U; Linux i686; en-US; rv:666)"

    _rot13from = "abcdefghijklmnopqrstuvwxyz" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    _rot13to =   "nopqrstuvwxyzabcdefghijklm" + "NOPQRSTUVWXYZABCDEFGHIJKLM"
    rot13codeTable = string.maketrans(_rot13from, _rot13to)

    @staticmethod
    def parseRaw(raw):
        """Parses the coords in Degree Minutes format. Expecting:

        S 36 51.918 E 174 46.725 or
        N 6 52.861  W174   43.327

        Spaces do not matter. Neither does having the degree symbol.

        Returns a two tuples in dm format."""

        # Make it uppercase for consistency
        coords = raw.upper().replace("N", " ").replace("S", " ") \
            .replace("E", " ").replace("W", " ").replace("+", " ")

        try:
            m = re.match(r"\s*(-?\s*\d+)\D+(\d+[\.,]\d+)\D?\s*(-?\s*\d+)\D+(\d+[\.,]\d+)",
                coords)

            latDeg, latMin, lonDeg, lonMin = [float(part.replace(" ", "").replace(",", ".")) for part in m.groups()]

            if "S" in raw:
                latDeg *= -1
            if "W" in raw:
                lonDeg *= -1

            return ((latDeg, latMin), (lonDeg,lonMin))

        except AttributeError:
            raise ValueError("Could not parse the coordinates entered manually.")

    @staticmethod
    def urlopen(url, data=None, headers=None):
        """Makes a urllib request.

        Returns opened stream of data or None on failure."""

        # headers
        if type(headers) is not DictType:
            headers = dict()
        if "User-Agent" not in headers.keys():
            logging.debug("Faking User-Agent header: %s", Util.useragent)
            headers["User-Agent"] = Util.useragent

        # POST
        if type(data) is DictType:
            data = urlencode(data)
        logging.debug("POST data: %s", data)

        try:
            logging.debug("Making request on: %s", url)
            request = urllib2.Request(url, data, headers)
            return urllib2.urlopen(request)

        except urllib2.URLError, e:
            logging.error("Cannot access the website: %s", e)
            return None


    @staticmethod
    def rot13(text):
        """Returns a text encoded by rot13 cipher."""
        return string.translate(text, Util.rot13codeTable)


    @staticmethod
    def toDecimal(deg, min):
        """Returns a decimal interpretation of coordinate in MinDec format."""
        return round(deg + min/60, 5)


    @staticmethod
    def toMinDec(decimal):
        """Returns a DecMin interpretation of coordinate in decimal format."""
        return int(decimal), round(60 * (decimal - int(decimal)), 3)


        
class TestUtil(unittest.TestCase):

    def setUp(self):
        pass

    def test_parseRaw(self):
        self.assertEquals( Util.parseRaw("N 49 45.123 E 013 22.123"), ((49, 45.123), (13, 22.123)) )
        self.assertEquals( Util.parseRaw("S 49 45.123 W 013 22.123"), ((-49, 45.123), (-13, 22.123)) )
        self.assertEquals( Util.parseRaw("N49 45.123 E013 22.123"), ((49, 45.123), (13, 22.123)) )
        self.assertEquals( Util.parseRaw("49N 45.123 013E 22.123"), ((49, 45.123), (13, 22.123)) )
        self.assertEquals( Util.parseRaw("49S 45.123 013W 22.123"), ((-49, 45.123), (-13, 22.123)) )
        self.assertEquals( Util.parseRaw("N 49 45,123 E 013 22,123"), ((49, 45.123), (13, 22.123)) )
        self.assertEquals( Util.parseRaw(u"N 49° 45.123 E 013° 22.123"), ((49, 45.123), (13, 22.123)) )
        self.assertEquals( Util.parseRaw("N 49 45.123, E 013 22.123"), ((49, 45.123), (13, 22.123)) )
        self.assertEquals( Util.parseRaw("N 49 45.000 E 13 0.0"), ((49, 45), (13, 0)) )
        self.assertRaises( ValueError, Util.parseRaw, "123" )

    def test_urlopen(self):
        doctype = Util.urlopen("http://example.com").readline().strip()
        self.assertEquals( doctype, "<!doctype html>" )

    def test_rot13(self):
        self.assertEquals( Util.rot13("Text"), "Grkg" )
        self.assertEquals( Util.rot13("abc'ř"), "nop'ř" )

    def test_coordConversion(self):
        self.assertEquals( Util.toDecimal(49, 43.850), 49.73083 )
        self.assertEquals( Util.toDecimal(13, 22.905), 13.38175 )
        self.assertEquals( Util.toMinDec(13.38175), (13, 22.905) )
        self.assertEquals( Util.toMinDec(49.73083), (49, 43.850) )


def main():
    """The main program"""

    # logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()


if __name__ == "__main__":
    main()