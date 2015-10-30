#!/usr/bin/env python3

import logging
import math
import requests
from mechanicalsoup import Browser
from bs4 import BeautifulSoup
from geopy.distance import ELLIPSOIDS
from pycaching.cache import Cache
from pycaching.point import Point
from pycaching.utfgrid import UTFGrid
from pycaching.enums import Type, Size
from pycaching.errors import Error, NotLoggedInException, LoginFailedException
from pycaching.util import parse_date


class Geocaching(object):

    _baseurl = "https://www.geocaching.com"
    _urls = {
        "login_page":        "login/default.aspx",
        "search":            "play/search",
        "search_more":       "play/search/more-results",
    }

    def __init__(self):
        self._logged_in = False
        self._browser = Browser()

    def _request(self, url, *, expect="soup", method="GET", login_check=True, **kwargs):
        # check login unless explicitly turned off
        if login_check and self._logged_in is False:
            raise NotLoggedInException("Login is needed.")

        # TODO maybe use urljoin()
        url = url if "//" in url else "/".join([self._baseurl, url])

        try:
            res = self._browser.request(method, url, **kwargs)

            # return bs4.BeautifulSoup, JSON dict or raw requests.Response
            if expect == "soup":
                return res.soup
            elif expect == "json":
                return res.json()
            elif expect == "raw":
                return res

        except requests.exceptions.ConnectionError as e:
            raise Error("Cannot load page: {}".format(url)) from e

    def login(self, username, password):
        """Logs the user in.

        Downloads the relevant cookies to keep the user logged in."""

        logging.info("Logging in...")
        login_page = self._request(self._urls["login_page"], login_check=False)

        logging.debug("Checking for previous login.")
        logged = self.get_logged_user(login_page)
        if logged:
            if logged == username:
                logging.info("Already logged as %s.", logged)
                self._logged_in = True
                return
            else:
                logging.info("Already logged as %s, but want to log in as %s.", logged, username)
                self.logout()

        # continue logging in
        post = {}
        logging.debug("Assembling POST data.")

        # login fields
        login_elements = login_page.find_all("input", type=["text", "password", "checkbox"])
        post.update({field["name"]: val for field, val in zip(login_elements, [username, password, 1])})

        # other nescessary fields
        other_elements = login_page.find_all("input", type=["hidden", "submit"])
        post.update({field["name"]: field["value"] for field in other_elements})

        # login to the site
        logging.debug("Submiting login form.")
        after_login_page = self._request(self._urls["login_page"], method="POST", data=post, login_check=False)

        logging.debug("Checking the result.")
        if self.get_logged_user(after_login_page):
            logging.info("Logged in successfully as %s.", username)
            self._logged_in = True
            return
        else:
            self.logout()
            raise LoginFailedException("Cannot login to the site (probably wrong username or password).")

    def logout(self):
        """Logs out the user.

        Logs out the user by creating new browser."""

        logging.info("Logging out.")
        self._logged_in = False
        self._browser = Browser()

    def get_logged_user(self, login_page=None):
        """Returns the name of curently logged user or None, if no user is logged in."""

        login_page = login_page or self._request(self._urls["login_page"], login_check=False)
        assert isinstance(login_page, BeautifulSoup)

        logging.debug("Checking for already logged user.")
        try:
            return login_page.find("div", "LoggedIn").find("strong").text
        except AttributeError:
            return None

    def search(self, point, limit=float("inf")):
        """Returns a generator object of caches around some point."""

        assert isinstance(point, Point)

        logging.info("Searching at %s...", point)

        start_index = 0
        while True:
            # get one page
            page = self._search_get_page(point, start_index)

            if not page:
                # result is empty - no more caches
                raise StopIteration()

            # parse caches in result
            for start_index, row in enumerate(page.find_all("tr"), start_index):

                limit -= 1  # handle limit
                if limit < 0:
                    raise StopIteration()

                # parse raw data
                cache_details = row.find("span", "cache-details").text.split("|")
                wp = cache_details[1].strip()

                # create and fill cache object
                c = Cache(self, wp)
                c.type = Type.from_string(cache_details[0].strip())
                c.name = row.find("span", "cache-name").text
                c.found = row.find("img", title="Found It!") is not None
                c.favorites = int(row.find(attrs={"data-column": "FavoritePoint"}).text)
                c.state = not (row.get("class") and "disabled" in row.get("class"))
                c.pm_only = row.find("td", "pm-upsell") is not None

                if c.pm_only:
                    # PM only caches doesn't have other attributes filled in
                    yield c
                    continue

                c.size = Size.from_string(row.find(attrs={"data-column": "ContainerSize"}).text)
                c.difficulty = float(row.find(attrs={"data-column": "Difficulty"}).text)
                c.terrain = float(row.find(attrs={"data-column": "Terrain"}).text)
                c.hidden = parse_date(row.find(attrs={"data-column": "PlaceDate"}).text)
                c.author = row.find("span", "owner").text[3:]  # delete "by "

                logging.debug("Cache parsed: %s", c)
                yield c

            start_index += 1

    def _search_get_page(self, point, start_index):
        logging.debug("Loading page from start_index: %d", start_index)

        if start_index == 0:
            # first request has to load normal search page
            logging.debug("Using normal search endpoint")

            # make request
            res = self._request(self._urls["search"], params={
                "origin": point.format(None, "", "", "")
            })
            return res.find(id="geocaches")

        else:
            # other requests can use AJAX endpoint
            logging.debug("Using AJAX search endpoint")

            # make request
            res = self._request(self._urls["search_more"], params={
                "inputOrigin": point.format(None, "", "", ""),
                "startIndex": start_index,
                "originTreatment": 0
            }, expect="json")

            return BeautifulSoup(res["HtmlString"].strip())

    def search_quick(self, area, precision=None, strict=False):
        """Get geocaches inside area, with approximate coordinates

        Download geocache map tiles from geocaching.com and calculate
        approximate location of based on tiles.  Parameter area is Area
        instance, optional parameter precision is desired location
        precision for the cache in meters.  More precise results require
        increasingly more pages to be loaded.

        If not strict, return all found geocaches from overlapping
        tiles; else make sure that only caches within given area are
        returned.

        Return generator object of Cache instances."""

        logging.info("Performing quick search for cache locations")
        # Calculate initial tiles
        tiles, starting_precision = self._calculate_initial_tiles(area)

        # Check for continuation requirement and download tiles
        geocaches = self._get_utfgrid_caches(*tiles)

        if precision is not None:
            # On which zoom level grid details exceed required precision
            new_zoom = self._get_zoom_by_distance(precision, area.mean_point.latitude, UTFGrid.size, "ge")
            new_precision = area.mean_point.precision_from_tile_zoom(new_zoom, UTFGrid.size)
            assert precision >= new_precision
            new_zoom = min(new_zoom, UTFGrid.max_zoom)

        if precision is None or precision >= starting_precision or new_zoom == tiles[0][-1]:  # Previous zoom
            # No need to continue: start yielding caches
            for c in geocaches:
                if strict and not c.inside_area(area):
                    continue
                yield c
            return

        # Define new tiles for downloading
        logging.info("Downloading again at zoom level {} (precision {:.1f} m)".format(new_zoom, new_precision))
        round_1_caches = {}
        tiles = set()
        for c in geocaches:
            round_1_caches[c.wp] = c
            tiles.add(c.location.to_map_tile(new_zoom))
        # Perform query, yield found caches
        for c in self._get_utfgrid_caches(*tiles):
            round_1_caches.pop(c.wp, None)   # Mark as found
            if strict and not c.inside_area(area):
                continue
            yield c

        # Check if previously found caches are missing
        if not round_1_caches:
            return
        else:
            logging.debug("Oh no, these geocaches were not found: {}.".format(round_1_caches.keys()))
            for c in self._search_from_bordering_tiles(tiles, new_zoom, **round_1_caches):
                if strict and not c.inside_area(area):
                    continue
                yield c

    def _calculate_initial_tiles(self, area):
        """Calculate which tiles are downloaded initially

        Return list of tiles and starting precision."""

        dist = area.diagonal
        # Get zoom where distance between points is less or equal to tile width
        starting_zoom = self._get_zoom_by_distance(dist, area.mean_point.latitude, 1, "le")
        starting_tile_width = area.mean_point.precision_from_tile_zoom(starting_zoom, 1)
        starting_precision = starting_tile_width / UTFGrid.size
        assert dist <= starting_tile_width
        zoom = min(starting_zoom, UTFGrid.max_zoom)
        logging.info("Starting at zoom level {} (precision {:.1f} m, "
                     "tile width {:.0f} m)".format(zoom, starting_precision, starting_tile_width))
        x1, y1, _ = area.bounding_box.corners[0].to_map_tile(zoom)
        x2, y2, _ = area.bounding_box.corners[1].to_map_tile(zoom)
        tiles = []  # [(x, y, z), ...]
        for x_i in range(min(x1, x2), max(x1, x2) + 1):
            for y_i in range(min(y1, y2), max(y1, y2) + 1):
                tiles.append((x_i, y_i, zoom))
        return tiles, starting_precision

    def _get_utfgrid_caches(self, *tiles):
        """Get location of geocaches within tiles, using UTFGrid service

        Parameter tiles contains one or more tuples dictionaries that
        are of form (x, y, z).  Return generator object of Cache
        instances."""

        found_caches = set()
        for tile in tiles:
            ug = UTFGrid(self, *tile)
            for c in ug.download():
                # Some geocaches may be found multiple times if they are on the
                # border of the UTFGrid. Throw additional ones away.
                if c.wp in found_caches:
                    logging.debug("Found cache {} again".format(c.wp))
                    continue
                found_caches.add(c.wp)
                yield c
        logging.info("{} tiles downloaded".format(len(tiles)))

    def _search_from_bordering_tiles(self, previous_tiles, new_zoom, **missing_caches):
        """Extend geocache search to neighbouring tiles

        Parameter previous_tiles is a set of tiles that were already
        downloaded.  Parameter missing_caches is a dictionary
        {waypoint:<Cache>} and contains those caches that were found in
        previous zoom level but not anymore. Search around their
        expected coordinates and yield some more caches."""

        new_tiles = set()
        for wp in missing_caches:
            tile = missing_caches[wp].location.to_map_tile(new_zoom, fractions=True)
            neighbours = self._bordering_tiles(*tile)
            new_tiles.update(neighbours.difference(previous_tiles))
        logging.debug("Extending search to tiles {}".format(new_tiles))
        for c in self._get_utfgrid_caches(*new_tiles):
            missing_caches.pop(c.wp, None)   # Mark as found
            yield c
        if missing_caches:
            logging.debug("Could not just find these caches anymore: ".format(missing_caches))
            for wp in missing_caches:
                yield missing_caches[wp]

    @staticmethod
    def _bordering_tiles(x_float, y_float, z, fraction=0.1):
        """Get possible map tiles near the edge where geocache was found

        Return set of (x, y, z) tile coordinates."""

        orig_tile = (int(x_float), int(y_float), z)
        tiles = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_tile = (int(x_float + i * fraction), int(y_float + j * fraction), z)
                if new_tile != orig_tile and new_tile not in tiles:
                    tiles.add(new_tile)
        return tiles

    @staticmethod
    def _get_zoom_by_distance(dist, lat, tile_resolution=256, comparison="le"):
        """Calculate tile zoom level

        Return zoom level on which distance dist (in meters) >= tile
        width / tile_resolution (comparison="ge") or dist <= tile width
        / tile_resolution (comparison="le").  Calculations are performed
        for point where latitude is lat, assuming spherical earth.

        Return zoom level as integer."""

        diam = ELLIPSOIDS["WGS-84"][0] * 1e3 * 2
        if comparison == "le":
            convert = math.floor
        elif comparison == "ge":
            convert = math.ceil
        return convert(-math.log(dist * tile_resolution / (math.pi * diam * math.cos(math.radians(lat)))) / math.log(2))
