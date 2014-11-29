#!/usr/bin/env python3

import logging
import math

import requests

from pycaching.cache import Cache
from pycaching.point import Point
from pycaching.errors import Error


class UTFGrid:

    """Geocaching.com UTFGrid

    Geocaching.com serves so-called UTFGrids [1] on their tile map
    server.  These can be used as information sources to get approximate
    locations of geocaches in a given area.

    [1] https://github.com/mapbox/utfgrid-spec"""

    max_zoom = 18                    # geocaching.com restriction
    size = 64                        # UTFGrid implementation (will be checked)

    def __init__(self, geocaching, x, y, z):
        """Initialize UTFGrid

        Parameter geocaching is a Geocaching instance; parameters x, y
        and z are integer map tile coordinates as specified in Google
        Maps JavaScript API [1].  Geocaching instance is accessed to use
        its browser and stored URLs.

        [1] https://developers.google.com/maps/documentation/javascript/maptypes#MapCoordinates"""

        self._gc = geocaching
        self.x = x
        self.y = y
        self.z = z
        self._urls = {i: self._gc._urls[i] + "?x={}&y={}&z={}".format(x, y, z)
                      for i in ["tile", "grid"]}
        self.geocaches = []               # List of Cache instances

    def download(self, get_png_first=False):
        """Download UTFGrid from geocaching.com

        Return generator object of Cache instances, store geocaches also
        in self.geocaches.

        It appears to be mandatory to first download map tile (.png
        file) and only then UTFGrid.  However, this is not enforced all
        the time.  There is probably some time limit from previous
        loading of the same tile and also a general traffic regulator
        involved.  Try first to download grid and if it does not work,
        get .png first and then try again.

        TODO It might be useful to store time when tile is last
        downloaded and act based on that.  Logging some statistics (time
        when tile is loaded + received status code + content length +
        time spent on request) might help in algorithm design and
        evaluating if additional traffic from .png loading is tolerable
        and if this should be done all the time.  Requesting for UTFgrid
        and waiting for 204 response takes also its time."""

        logging.info("Downloading UTFGrid for tile ({}, {}, {})".format(
            self.x, self.y, self.z))
        try:
            if get_png_first:
                logging.debug(".. getting .png file first")
                self._gc._browser.get(self._urls["tile"])
            logging.debug(".. getting UTFGrid")
            res = self._gc._browser.get(self._urls["grid"])
            if res.status_code == 204:
                if get_png_first:
                    logging.debug("There is really no content! Returning 0 caches.")
                    return
                logging.debug("Cannot load UTFgrid: no content. "
                              "Trying to load .png tile first")
                new_caches = self.download(get_png_first=True)
        except requests.exceptions.ConnectionError as e:
            raise Error("Cannot load UTFgrid.") from e
        if res.status_code == 200:
            try:
                json_grid = res.json()
            except ValueError as e:
                # This happened during testing, don't know why.
                if get_png_first:
                    raise Error("Cannot load UTFgrid.") from e
                else:
                    logging.debug("JSON parsing failed, trying .png first")
                    return self.download(get_png_first=True)
            new_caches = self._parse_utfgrid(json_grid)
        for c in new_caches:
            self.geocaches.append(c)
            yield c

    def _parse_utfgrid(self, json_grid):
        """Parse geocache coordinates from UTFGrid

        Consume json-decoded UTFGrid data from MechanicalSoup browser.
        Calculate waypoint coordinates and return generator object of
        Cache instances.

        Geocaching.com UTFGrids do not follow UTFGrid specification [2]
        in grid contents and key values.  List "grid" contains valid
        code pixels that are individual, but list "keys" contain a list
        of coordinates as "(x, y)" for points where there are geocaches
        on the grid.  Code pixels can however be decoded to produce
        index of coordinate point in list "keys".  Grid resolution is
        64x64 and coordinates run from northwest corner.  Dictionary
        "data" has key-value pairs, where keys are same coordinates as
        previously described and values are lists of dictionaries each
        containing geocache waypoint code and name in form {"n": name,
        "i": waypoint}.  Waypoints seem to appear nine times each, if
        the cache is not cut out from edges.

        [2] https://github.com/mapbox/utfgrid-spec"""

        logging.debug("Parsing UTFGrid")
        caches = {}   # {waypoint: [<Cache>, <GridCoordinateBlock>]}
        size = len(json_grid["grid"])
        assert len(json_grid["grid"][1]) == size   # square grid
        if size != self.size:
            logging.warning("GC.com UTFGrid specs seem to have changed: "
                            "grid resolution is not 64!")
            self.size = size
        caches = {}
        for coordinate_key in json_grid["data"]:
            cache_list = json_grid["data"][coordinate_key]
            x_i, y_i = (int(i) for i in coordinate_key.strip(" ()").split(","))
            # Store all caches to dictionary
            for cache_dic in cache_list:
                waypoint = cache_dic["i"]
                # Store all found coordinate points
                if waypoint not in caches:
                    c = Cache(waypoint, self._gc, name=cache_dic["n"])
                    caches[waypoint] \
                        = [c, GridCoordinateBlock(self, (x_i, y_i),)]
                else:
                    caches[waypoint][1].add((x_i, y_i))
        # Try to determine grid coordinate block size
        GridCoordinateBlock.determine_block_size(
            *[len(caches[wp][1].points) for wp in caches])
        # Calculate geocache coordinates and yield objects
        for waypoint in caches:
            c, coord_block = caches[waypoint]
            c.location = coord_block.get_location()
            yield c
        logging.info("Found {} caches".format(len(caches)))


class GridCoordinateBlock:

    """Container for grouped coordinate points in UTFGrid"""

    # Assume that block points form a N*N matrix in the UTFGrid, or a part of
    # it.  If N cannot be determined automatically, use this fallback value.
    size = 3

    @classmethod
    def determine_block_size(cls, *block_points):
        """Estimate how large coordinate blocks are

        If more than 95% of all caches are of one size, change size
        from default.  This is quite a high value, but the grid size is
        not really supposed to change from the 3x3 size.  If it does, it
        is surely visible."""

        if not block_points or len(block_points) <= 20:
            return
        groups = set(block_points)
        frequency = {i: block_points.count(i) for i in groups}
        group_order = sorted(frequency, key=lambda k: frequency[k], reverse=True)
        if frequency[group_order[0]] > 0.95 * len(block_points):
            new_n = int(math.sqrt(group_order[0]))
            if new_n == cls.size:
                return
            logging.warning("Coordinate block in UTFGrid is not what we "
                            "expected.  Has something else changed?")
            # If new block is not a square, this class needs revising
            assert new_n == math.sqrt(group_order[0]), "Block should be square"
            cls.size = new_n

    def __init__(self, utf_grid, *points):
        """Initialize coordinate block

        Parameters: UTFGrid instance and optional list of (x, y)
        coordinates."""

        self.utf_grid = utf_grid
        self.points = points

    @property
    def points(self):
        """Individual points in grid block"""
        return self._points

    @points.setter
    def points(self, values):
        self._points = set(values)
        self._calculate_limits()

    def add(self, point):
        """Add (x, y) points to list"""
        self._points.add(point)
        self._calculate_limits()

    def update(self, points):
        """Update points with the union of existing and given points"""
        self.points.update(set(points))
        self._calculate_limits()

    def get_location(self):
        """Calculate actual coordinates of this grid block"""
        x_i, y_i = self._get_middle_point()
        return Point.from_tile(
            self.utf_grid.x, self.utf_grid.y, self.utf_grid.z,
            x_i, y_i, self.utf_grid.size)

    def _calculate_limits(self):
        """Calculate minimum and maximum coordinate values of points"""
        if not self.points:
            self._xlim = [None, None]
            self._ylim = [None, None]
        else:
            self._xlim, self._ylim = [(min(i), max(i))
                                      for i in zip(*self.points)]

    def _get_middle_point(self):
        """Get middle point from list of x, y coordinates

        The points form a rectangular matrix, whose maximum size is
        self.size ** 2, but it can be smaller if the matrix is at the
        edge of UTFGrid.  Investigate block and return x, y coordinates
        of uncut square block middle point."""

        check_status = self._check_block()
        if check_status == 0:
            raise Error("Something went wrong with geocache coordinate "
                        "parsing from UTFGrid.  Either the JSON parsing "
                        "failed or Groundspeak has changed something.")
        elif check_status == 1:
            return [sum(i) / 2 for i in [self._xlim, self._ylim]]
        else:
            return [sum(self._find_limits(axis)) / 2 for axis in ["x", "y"]]

    def _check_block(self):
        """Check that all points are properly aligned

        Return 0 if there are some problems, 1 if this is a rectangular
        grid of size self.size ** 2, 2 if some points fall out of the edge."""

        rv = None
        for lim in [self._xlim, self._ylim]:
            block_size = lim[1] - lim[0] + 1
            if block_size > self.size:
                return 0                  # Can't be this large
            elif block_size == self.size:
                rv = rv or 1              # Maximum size
            else:
                rv = 2
        for x_i in range(self._xlim[0], self._xlim[1] + 1):
            for y_i in range(self._ylim[0], self._ylim[1] + 1):
                if (x_i, y_i) not in self.points:
                    # Some points are missing from checked rectangle
                    return 0
        return rv

    def _find_limits(self, axis):
        """Calculate limits for a block of size self.size ** 2

        If the block is at the edge of UTFgrid, minimum or maximum x, y
        values for these points fall outside current grid size.  This is
        intentional."""

        square_width = self.size
        if axis == "x":
            lim_min, lim_max = self._xlim
        elif axis == "y":
            lim_min, lim_max = self._ylim
        if lim_min == 0:
            lim_min = lim_max - square_width + 1
        elif lim_max == self.utf_grid.size - 1:
            lim_max = lim_min + square_width - 1
        return lim_min, lim_max
