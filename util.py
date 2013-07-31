# -*- encoding: utf-8 -*-

import re
import urllib2
import logging
import unittest


class Util(object):

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
    def urlopen(url, *args, **kwargs):
        """Makes a urllib request.

        Returns opened stream of data or None on failure."""

        try:
            logging.debug("Making request on: %s", url)
            request = urllib2.Request(url, *args, **kwargs)
            return urllib2.urlopen(request)

        except urllib2.URLError, e:
            logging.error("Cannot access the website: %s", e)
            return None


        
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


def main():
    """The main program"""

    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)
    unittest.main()


if __name__ == "__main__":
    main()