#!/usr/bin/env python3

import math
import re
import logging
import weakref
import itertools
import geopy
import geopy.distance
import geopy.format
from statistics import mean
from collections import namedtuple
from pycaching.errors import ValueError as PycachingValueError, GeocodeError, BadBlockError, Error
from pycaching.util import lazy_loaded


def to_decimal(deg, min):
    """Convert coordinates from degrees minutes to decimal degrees format."""
    return round(deg + min / 60, 5)


class Point(geopy.Point):
    """A point on earth defined by its latitude, longitude and possibly more attributes.

    Subclass of `geopy.Point <http://geopy.readthedocs.org/en/latest/index.html#geopy.point.Point>`_.
    """

    def __new__(cls, *args, **kwargs):
        precision = kwargs.pop("precision", None)
        self = super(Point, cls).__new__(cls, *args, **kwargs)
        self.precision = precision
        return self

    @classmethod
    def from_location(cls, geocaching, location):
        """Return a :class:`.Point` instance from geocoded location.

        :param .Geocaching geocaching: Reference to :class:`.Geocaching` instance, used to do
            a geocoding request.
        :param str location: Location to geocode.
        :raise .GeocodeError: If location cannot be geocoded (not found).
        """
        res = geocaching._request("api/geocode", params={"q": location}, expect="json")

        if res["status"] != "success":
            raise GeocodeError(res["msg"])

        return cls(float(res["data"]["lat"]), float(res["data"]["lng"]))

    @classmethod
    def from_string(cls, string):
        """Return a :class:`.Point` instance from coordinates in degrees minutes format.

        This method can handle various malformed formats. Example inputs are:

        - :code:`S 36 51.918 E 174 46.725` or
        - :code:`N 6 52.861  w174   43.327`

        :param str string: Coordinates to parse.
        :raise .ValueError: If string cannot be parsed as coordinates.
        """

        # Convert to uppercase to simplify hemisphere comparisons
        string = string.upper()
        coords = string.replace("N", " ").replace("S", " ") \
            .replace("E", " ").replace("W", " ").replace("+", " ")

        try:
            m = re.match(r"\s*(-?\s*\d+)\D+(\d+[\.,]\d+)\D?\s*(-?\s*\d+)\D+(\d+[\.,]\d+)", coords)

            latDeg, latMin, lonDeg, lonMin = [
                float(part.replace(" ", "").replace(",", ".")) for part in m.groups()]

            if "S" in string:
                latDeg *= -1
                latMin *= -1
            if "W" in string:
                lonDeg *= -1
                lonMin *= -1

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
        """Return a new :class:`.Point` instance from :class:`.Block` instance.

        :param .Block block: UTFGrid block.
        """
        return cls.from_tile(block.tile, block.middle_point)

    @classmethod
    def from_tile(cls, tile, tile_point=None):
        """Return a new :class:`.Point` instance from :class:`.Tile` instance.

        .. seealso:: http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames

        :param .Tile tile: Map tile.
        :param .UTFGridPoint tile_point: Optional point inside a tile.
        """

        if tile_point:
            dx = float(tile_point.x) / tile.size
            dy = float(tile_point.y) / tile.size
        else:
            dx, dy = 0, 0

        n = 2.0 ** tile.z
        lon_deg = (tile.x + dx) / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (tile.y + dy) / n)))
        lat_deg = math.degrees(lat_rad)
        p = cls(lat_deg, lon_deg)
        p.precision = tile.precision(p)
        return p

    def to_tile(self, geocaching, zoom):
        """Return a new :class:`.Tile` instance where current :class:`.Point` is located.

        .. seealso:: http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames

        :param .Geocaching geocaching: Reference to :class:`.Geocaching` instance (passed to tile).
        :param int zoom: Zoom level of newly created tile.
        """
        lat_deg = self.latitude
        lon_deg = self.longitude
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        x = int((lon_deg + 180.0) / 360.0 * n)
        y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return Tile(geocaching, x, y, zoom)

    def __format__(self, format_spec):
        return "{:{}}".format(str(self), format_spec)

    def format_gc(self):
        """Return a location of this point in a typical Geocaching format.

        :return: Human-readable location.
        :rtype: :class:`str`
        """
        hemisphere_lat = self.latitude >= 0 and "N" or "S"
        hemisphere_lon = self.longitude >= 0 and "E" or "W"

        fmt = "%(degrees)d%(deg)s %(minutes).3f"
        lat = geopy.format.format_degrees(abs(self.latitude), fmt, geopy.format.UNICODE_SYMBOLS)
        lon = geopy.format.format_degrees(abs(self.longitude), fmt, geopy.format.UNICODE_SYMBOLS)

        return "{} {}, {} {}".format(hemisphere_lat, lat, hemisphere_lon, lon)


class Area:
    """Geometrical area."""
    pass


class Polygon(Area):
    """Area defined by bordering Point instances.

    Subclass of :class:`.Area`.
    """

    def __init__(self, *points):
        """Define polygon by list of consecutive Points."""
        assert len(points) >= 3
        self.points = points

    @property
    def bounding_box(self):
        """Get area's bounding box (:class:`.Rectangle` computed from min and max coordinates)."""
        lats = sorted([p.latitude for p in self.points])
        lons = sorted([p.longitude for p in self.points])
        return Rectangle(Point(min(lats), min(lons)),
                         Point(max(lats), max(lons)))

    @property
    def mean_point(self):
        """Return :class:`.Point` with average latitude and longitude of all area's points."""
        x = mean([p.latitude for p in self.points])
        y = mean([p.longitude for p in self.points])
        return Point(x, y)

    def to_tiles(self, gc, zoom=None):
        """Return list of tiles covering this area.

        :param .Geocaching gc: Reference to :class:`.Geocaching` instance (passed to tiles).
        :param int zoom: Desired zoom level. If :code:`None`, the `zoom` is computed so that tile
            width is smallest possible, but greater than area width.
        """
        corners = self.bounding_box.corners

        if not zoom:
            # calculate zoom, where tile width is just above bounding box width
            d_lon = corners[1].longitude - corners[0].longitude
            zoom = math.floor(math.log2(360 / d_lon))

        # get corner tiles
        nw_tile = corners[0].to_tile(gc, zoom)
        se_tile = corners[1].to_tile(gc, zoom)

        # sort corner coords because of range
        x1, x2 = sorted((nw_tile.x, se_tile.x))
        y1, y2 = sorted((nw_tile.y, se_tile.y))

        logging.debug("Area converted to {} tiles, zoom level {}".format(
            (x2 - x1) * (y2 - y1), zoom))

        # for each tile between corners
        for x, y in itertools.product(range(x1, x2 + 1), range(y1, y2 + 1)):
            yield Tile(gc, x, y, zoom)


class Rectangle(Polygon):
    """Upright rectangle.

    Subclass of :class:`.Polygon`.
    """

    def __init__(self, point_a, point_b):
        """Create rectangle defined by its corners.

        :param .Point point_a: Top left corner.
        :param .Point point_b: Bottom right corner.
        """
        if point_a.latitude < point_b.latitude:
            point_a.latitude, point_b.latitude = point_b.latitude, point_a.latitude
        if point_a.longitude > point_b.longitude:
            point_a.longitude, point_b.longitude = point_b.longitude, point_a.longitude

        assert point_a != point_b, "Corner points cannot be the same"
        self.corners = [point_a, point_b]
        self.points = [point_a, Point(point_a.latitude, point_b.longitude),
                       point_b, Point(point_b.latitude, point_a.longitude)]

    def __contains__(self, p):
        """Return if the rectangle contains a point.

        :param .Point p: Examined point.
        """
        lats = sorted([_.latitude for _ in self.points])
        lons = sorted([_.longitude for _ in self.points])
        return min(lats) <= p.latitude <= max(lats) and min(lons) <= p.longitude <= max(lons)

    @property
    def diagonal(self):
        """Return a lenght of bounding box diagonal in meters as :class:`int`."""
        return geopy.distance.distance(self.corners[0], self.corners[1]).meters


class Tile(object):
    """UTFGrid map tile.

    Geocaching.com serves so-called `UTFGrids <https://github.com/mapbox/utfgrid-spec>`_ on their
    tile map server. These can be used as information sources to get approximate locations
    of geocaches in a given area.
    """
    max_zoom = 18  # geocaching.com restriction
    size = 64      # UTFGrid implementation (will be checked)

    _baseurl = "http://tiles01.geocaching.com/"
    _urls = {
        "tile":              _baseurl + "map.png",
        "grid":              _baseurl + "map.info",
    }

    def __init__(self, geocaching, x, y, z):
        """Initialize a Tile.

        Parameters are map tile coordinates as specified in `Google Maps JavaScript API
        <https://developers.google.com/maps/documentation/javascript/maptypes#MapCoordinates>`_

        :param .Geocaching geocaching: Reference to :class:`.Geocaching` instance, used for loading
            a UTFGrid tile.
        :param int x: Map tile X coordinate.
        :param int y: Map tile Y coordinate.
        :param int z: Map tile Z coordinate.
        """

        self.geocaching = geocaching
        self.x = x
        self.y = y
        assert 0 <= z <= self.max_zoom, "Invalid zoom value"
        self.z = z

    @property
    @lazy_loaded
    def blocks(self):
        """Return loaded :class:`.Block`s for this tile."""
        return self._blocks.values()

    def _download_utfgrid(self, *, get_png=False):
        """Load UTFGrid tile from geocaching.com.

        It appears to be mandatory to first download map tile (.png file) and only then UTFGrid.
        However, this is not enforced all the time. There is probably some time limit from previous
        loading of the same tile and also a general traffic regulator involved. Try first to
        download grid and if it does not work, get .png and then try it again.

        :param bool get_png: Whether to download .png first.
        :return: JSON with raw tile data.
        :rtype: :class:`dict`
        """
        # TODO: It might be useful to store time when tile is last downloaded and act based on that.
        # Logging some statistics (time when tile is loaded + received status code + content length
        # + time spent on request) might help in algorithm design and evaluating if additional
        # traffic from .png loading is tolerable and if this should be done all the time.
        # Requesting for UTFgrid and waiting for 204 response takes also its time.

        logging.debug("Downloading UTFGrid for {}".format(self))

        params = {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }

        if get_png:
            logging.debug("Getting .png file")
            self.geocaching._request(self._urls["tile"], params=params, expect="raw")

        logging.debug("Getting UTFGrid")
        res = self.geocaching._request(self._urls["grid"], params=params, expect="raw")

        if res.status_code == 204:
            if get_png:
                logging.debug("There is really no content! Returning 0 caches.")
                return
            logging.debug("Cannot load UTFgrid: no content. Trying to load .png tile first")
            return self._download_utfgrid(get_png=True)

        if res.status_code == 200:
            try:
                return res.json()
            except ValueError as e:
                # this happened during testing, don't know why
                if get_png:
                    raise Error("Cannot load UTFgrid.") from e
                else:
                    logging.debug("JSON parsing failed, trying .png first")
                    return self._download_utfgrid(get_png=True)

    def load(self):
        """Load :class:`.Block`s for this tile.

        Geocaching.com UTFGrid do not follow `UTFGrid specification
        <https://github.com/mapbox/utfgrid-spec>`_ in grid contents and key values. List
        :code:`grid` contains valid code pixels that are individual, but list :code:`keys` contains
        a list of coordinates as :code:`(x, y)` for points where there are geocaches on the grid.
        Code pixels can however be decoded to produce index of coordinate point in list
        :code:`keys`. Grid resolution is 64x64 and coordinates run from NW corner. Dictionary
        :code:`data` has key-value pairs, where keys are same coordinates as previously described
        and values are lists of dictionaries each containing geocache waypoint code and name in
        form :code:`{"n": name, "i": waypoint}`.  Waypoints seem to appear nine times each, if
        the cache is not cut out from edges.
        """

        utfgrid = self._download_utfgrid()

        if not utfgrid:
            self._blocks = {}
            logging.debug("No block loaded to {}".format(self))
            return

        size = len(utfgrid["grid"])
        assert len(utfgrid["grid"][1]) == size, "UTFGrid is not square"
        if size != self.size:
            logging.warning("UTFGrid has unexpected size.")
            self.size = size

        self._blocks = {}   # format: { waypoint: <Block> }

        # for all non-empty in coords
        for coordinate_key in utfgrid["data"]:
            cache_list = utfgrid["data"][coordinate_key]
            x, y = (int(i) for i in coordinate_key.strip(" ()").split(","))
            point = UTFGridPoint(x, y)

            # store all caches for this coords to dictionary
            for cache in cache_list:
                waypoint, name = cache["i"], cache["n"]

                # if block doesn't exist yet, store it to dict
                if waypoint not in self._blocks:
                    self._blocks[waypoint] = Block(self, waypoint, name)

                # extend block points
                self._blocks[waypoint].add(point)

        # try to determine grid coordinate block size
        Block.determine_block_size()

        logging.debug("Loaded {} blocks to {}".format(len(self._blocks), self))

    def precision(self, point=None):
        """Return (x-axis) coordinate precision for current tile.

        :param .Point point: Optional point to increase precision calculation.
        """
        diam = geopy.distance.ELLIPSOIDS["WGS-84"][0] * 1e3 * 2
        lat_correction = math.cos(math.radians(point.latitude)) if point else 1
        tile_length = math.pi * diam * lat_correction * 2 ** (-self.z)
        return tile_length / self.size

    def __eq__(self, other):
        """Compare tiles by their coordinates and contained :class:`.Geocaching` reference."""
        for attr in ['geocaching', 'x', 'y', 'z']:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def __str__(self):
        """Return tile object ID and its coordinates."""
        return "<object Tile, id {}, coords ({}, {}, {})>".format(id(self), self.x, self.y, self.z)


UTFGridPoint = namedtuple("UTFGridPoint", "x y")
"""Point inside a :class:`.Tile`.

Represents Xth row and Yth column in UTFGrid tile from NW corner.
"""


class Block(object):
    """Container for grouped :class:`.UTFGridPoint`s inside a tile."""

    # this class can have a lot of instances so use __slots__
    __slots__ = "tile", "cache_wp", "cache_name", "_points", "_xlim", "_ylim", "__weakref__"

    instances = []

    # Assume that block points form a N*N matrix in the UTFGrid, or a part of it.
    # If N cannot be determined automatically, use this fallback value.
    size = 3

    def __init__(self, tile=None, wp=None, name=None):
        """Initialize an empty :class:`.Block`.

        Also add the new instance to class-level list of all instances, used for computing the
        block size.

        :param .Tile tile: Base map tile.
        :param str wp: Waypoint of :class:`.Cache` represented by this block.
        :param str wp: Human readable name of :class:`.Cache` represented by this block.
        """
        self.tile = tile
        self.cache_wp = wp
        self.cache_name = name
        self.points = []  # will trigger setting of other initial values
        self.__class__.instances.append(weakref.ref(self))

    @classmethod
    def determine_block_size(cls):
        """Update the class-level block size from the data of all instances."""

        # remove invalid instances
        cls.instances = list(filter(lambda i: i(), cls.instances))

        if len(cls.instances) < 20:
            logging.warning("Trying to determine block size with small number of blocks.")

        avg_block_size = round(mean((math.sqrt(len(i().points)) for i in cls.instances)))
        if cls.size != avg_block_size:
            logging.warning("UTFGrid coordinate block has unexpected size.")
            cls.size = avg_block_size

    @property
    def points(self):
        """Individual points in grid block.

        :setter: Set new points and internally update X, Y limits.
        :type: :class:`set`
        """
        return self._points

    @points.setter
    def points(self, values):
        self._points = set()
        self._xlim = float("inf"), float("-inf")
        self._ylim = float("inf"), float("-inf")
        self.update(values)

    def add(self, point):
        """Add a point to this block.

        :param .UTFGridPoint point: Point to add.
        """
        point = UTFGridPoint(*point)
        self._points.add(point)
        self._update_limits(point)

    def update(self, points):
        """Union poins in current block with given points.

        :param list point: List of :class:`.UTFGridPoint`s to union with existing block points.
        """
        for point in set(points):
            self.add(point)

    def _update_limits(self, point):
        """Update limits used for determining block middle point.

        :param .UTFGridPoint point: Point used to update limits.
        """
        self._xlim = min(self._xlim[0], point.x), max(self._xlim[1], point.x)
        self._ylim = min(self._ylim[0], point.y), max(self._ylim[1], point.y)

    @property
    def middle_point(self):
        """A middle point of this block.

        The points form a rectangular matrix, whose maximum size is :code:`self.size ** 2`, but it
        can be smaller if the matrix is at the edge of UTFGrid. This method threat the block
        as uncut square to determine its middle point.

        :type: :class:`.UTFGridPoint`
        """
        self._check_block()
        x = mean(self._get_corrected_limits(*self._xlim))
        y = mean(self._get_corrected_limits(*self._ylim))
        return UTFGridPoint(x, y)

    def _check_block(self):
        """Check if block is valid.

        :raise .BadBlockError: If block is not entirely filled with points or larger than expeced.
        """

        # check for missing points in rectangle
        for x in range(self._xlim[0], self._xlim[1] + 1):
            for y in range(self._ylim[0], self._ylim[1] + 1):
                if UTFGridPoint(x, y) not in self.points:
                    raise BadBlockError("Block is not entirely filled (some points are missing).")

        # check block size in both axes
        for lim in [self._xlim, self._ylim]:
            block_size = lim[1] - lim[0] + 1
            if block_size > self.size:
                raise BadBlockError("Block is larger than expected.")

    def _get_corrected_limits(self, lim_min, lim_max):
        """Calculate corrected limits for a block (works for both, X and Y limits).

        If the block is at the edge of UTFgrid, minimum or maximum x, y values for these points
        fall outside current grid size. This is intentional.

        :param int lim_min: Lower limit.
        :param int lim_max: Higher limit.
        :return tuple: Pair of corrected values of (lim_min, lim_max).
        :rtype: :class:`tuple` of :class:`int`
        """

        # if block has normal size in this axis, there is no need to fix limits
        if lim_max - lim_min + 1 == self.size:
            pass

        # if block touches left or up edge of tile
        elif lim_min == 0:
            lim_min = lim_max - self.size + 1

        # if block touches right or bottom edge of tile
        else:
            lim_max = lim_min + self.size - 1

        return lim_min, lim_max
