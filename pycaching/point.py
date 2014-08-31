#!/usr/bin/env python3

import re
import geopy
from pycaching import errors
from pycaching.util import Util


class Point(geopy.Point):

    @classmethod
    def from_string(cls, string):
        """Parses the coords in Degree Minutes format. Expecting:

        S 36 51.918 E 174 46.725 or
        N 6 52.861  W174   43.327

        Spaces do not matter. Neither does having the degree symbol.

        Returns a geopy.Point instance."""

        # Make it uppercase for consistency
        coords = string.upper().replace("N", " ").replace("S", " ") \
            .replace("E", " ").replace("W", " ").replace("+", " ")

        try:
            m = re.match(r"\s*(-?\s*\d+)\D+(\d+[\.,]\d+)\D?\s*(-?\s*\d+)\D+(\d+[\.,]\d+)", coords)

            latDeg, latMin, lonDeg, lonMin = [float(part.replace(" ", "").replace(",", ".")) for part in m.groups()]

            if "S" in string:
                latDeg *= -1
            if "W" in string:
                lonDeg *= -1

            return Point(Util.to_decimal(latDeg, latMin), Util.to_decimal(lonDeg, lonMin))

        except AttributeError:
            pass

        # fallback
        try:
            return super(Point, cls).from_string(string)
        except ValueError as e:
            # wrap possible error to pycaching.errors.ValueError
            raise errors.ValueError() from e
