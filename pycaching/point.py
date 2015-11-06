#!/usr/bin/env python3

import math
import re
import geopy
from pycaching.errors import ValueError as PycachingValueError, GeocodeError
from pycaching.util import to_decimal


class Point(geopy.Point):

    def __new__(cls, *args, **kwargs):
        precision = kwargs.pop("precision", None)
        self = super(Point, cls).__new__(cls, *args, **kwargs)
        self.precision = precision
        return self

    @classmethod
    def from_location(cls, geocaching, location):
        res = geocaching._request("api/geocode", params={"q": location}, expect="json")

        if res["status"] != "success":
            raise GeocodeError(res["msg"])

        return cls(float(res["data"]["lat"]), float(res["data"]["lng"]))

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

            return cls(to_decimal(latDeg, latMin), to_decimal(lonDeg, lonMin))

        except AttributeError:
            pass

        # fallback
        try:
            return super(cls, cls).from_string(string)
        except ValueError as e:
            # wrap possible error to pycaching.errors.ValueError
            raise PycachingValueError() from e

    @classmethod
    def from_block(cls, block):
        return cls.from_tile(block.tile, block.middle_point)

    @classmethod
    def from_tile(cls, tile, point=None):
        """Calculate location from web map tile coordinates

        Parameter represents a map tile coordinates as specified in
        Google Maps JavaScript API [1].  Optional parameter point
        determine position inside the tile, starting from northwest
        corner. Its x and y coords are in range [0, tile.size].
        This code is modified from OpenStreetMap Wiki [2].

        [1] https://developers.google.com/maps/documentation/javascript/maptypes#MapCoordinates
        [2] http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
        """

        if point:
            dx = float(point.x) / tile.size
            dy = float(point.y) / tile.size
        else:
            dx, dy = 0, 0

        n = 2.0 ** tile.z
        lon_deg = (tile.x + dx) / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (tile.y + dy) / n)))
        lat_deg = math.degrees(lat_rad)
        p = cls(lat_deg, lon_deg)
        p.precision = p.precision_from_tile_zoom(tile.z, tile.size)
        return p

    def to_tile_coords(self, zoom, fractions=False):
        """Calculate web map tile where point is located

        Return x, y, z.  If fractions, return x and y as floats.  This
        code is modified from OpenStreetMap Wiki [1].

        [1] http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames

        """
        lat_deg = self.latitude
        lon_deg = self.longitude
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = (lon_deg + 180.0) / 360.0 * n
        ytile = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
        if not fractions:
            xtile = int(xtile)
            ytile = int(ytile)
        return xtile, ytile, zoom

    def precision_from_tile_zoom(self, z, divisor=256):
        """Calculate (x-axis) coordinate precision from web map tile

        Parameters z is map zoom value.  Divisor denotes how many pixels
        there are in a tile.  Assume spherical earth.

        Return precision in meters.

        """
        lat = self.latitude
        diam = geopy.distance.ELLIPSOIDS["WGS-84"][0] * 1e3 * 2
        tile_length = math.pi * diam * math.cos(math.radians(lat)) * 2 ** (-z)
        return tile_length / divisor

    def distance(self, point):
        """Return distance from this point to another point in meters"""
        return geopy.distance.distance(self, point).meters

    def inside_area(self, area):
        """Check if point is inside given area"""
        return area.inside_area(self)

    def __format__(self, format_spec):
        return "{:{}}".format(str(self), format_spec)
