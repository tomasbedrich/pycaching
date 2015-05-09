#!/usr/bin/env python3

import logging
import math
import requests
import mechanicalsoup as ms
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from pycaching.area import Area
from pycaching.cache import Cache
from pycaching.util import Util
from pycaching.point import Point
from pycaching.utfgrid import UTFGrid
from pycaching.errors import Error, NotLoggedInException, LoginFailedException, GeocodeError, LoadError, PMOnlyException
import geopy.distance


def login_needed(func):
    """Decorator for method which needs login first."""

    def wrapper(*args, **kwargs):
        assert isinstance(args[0], Geocaching)
        if not args[0]._logged_in:
            raise NotLoggedInException("Login is needed.")
        return func(*args, **kwargs)

    return wrapper


class Geocaching(object):

    _baseurl = "https://www.geocaching.com/"
    _tile_url = "http://tiles01.geocaching.com/"

    _urls = {
        "login_page":       _baseurl + "login/default.aspx",
        "cache_details":    _baseurl + "geocache/{wp}",
        "search":           _baseurl + "play/search",
        "search_more":      _baseurl + "play/search/more-results",
        "geocode":          _baseurl + "api/geocode",
        "map":              _tile_url + "map.details",
        "tile":             _tile_url + "map.png",
        "grid":             _tile_url + "map.info",
    }

    def __init__(self):
        self._logged_in = False
        self._browser = ms.Browser()

    def login(self, username, password):
        """Logs the user in.

        Downloads the relevant cookies to keep the user logged in."""

        logging.info("Logging in...")

        try:
            login_page = self._browser.get(self._urls["login_page"])
        except requests.exceptions.ConnectionError as e:
            raise Error("Cannot load login page.") from e

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
        login_elements = login_page.soup.find_all("input", type=["text", "password", "checkbox"])
        post.update({field["name"]: val for field, val in zip(login_elements, [username, password, 1])})

        # other nescessary fields
        other_elements = login_page.soup.find_all("input", type=["hidden", "submit"])
        post.update({field["name"]: field["value"] for field in other_elements})

        # login to the site
        logging.debug("Submiting login form.")

        try:
            after_login_page = self._browser.post(self._urls["login_page"], post)
        except requests.exceptions.ConnectionError as e:
            raise Error("Cannot load response after submiting login form.") from e

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
        self._browser = ms.Browser()

    def geocode(self, query):
        """Tries to fetch coordinates for given query."""

        assert type(query) is str

        url = self._urls["geocode"] + "?q=" + query
        try:
            res = self._browser.get(url).json()
        except requests.exceptions.ConnectionError as e:
            raise Error("Cannot load geocode page.") from e

        if res["status"] != "success":
            raise GeocodeError(res["msg"])

        return Point(float(res["data"]["lat"]), float(res["data"]["lng"]))

    @login_needed
    def search(self, point, limit=0):
        """Returns a generator object of caches around some point."""

        assert isinstance(point, Point)
        assert type(limit) is int

        logging.info("Searching at %s...", point)

        start_index = 0
        while True:
            # get one page
            page = self._search_get_page(point, start_index)

            if not page:
                # result is empty - no more caches
                raise StopIteration()

            # parse caches in result
            for start_index, row in enumerate(BeautifulSoup(page).find_all("tr"), start_index):

                if limit > 0 and start_index == limit:
                    raise StopIteration()

                # parse raw data
                cache_details = row.find("span", "cache-details").text.split("|")
                wp = cache_details[1].strip()

                # create and fill cache object
                c = Cache(wp, self)
                c.cache_type = cache_details[0].strip()
                c.name = row.find("span", "cache-name").text
                c.found = row.find("img", title="Found It!") is not None
                c.favorites = int(row.find(attrs={"data-column": "FavoritePoint"}).text)
                c.state = not (row.get("class") and "disabled" in row.get("class"))
                c.pm_only = row.find("td", "pm-upsell") is not None

                if c.pm_only:
                    # PM only caches doesn't have other attributes filled in
                    yield c
                    continue

                c.size = row.find(attrs={"data-column": "ContainerSize"}).text
                c.difficulty = float(row.find(attrs={"data-column": "Difficulty"}).text)
                c.terrain = float(row.find(attrs={"data-column": "Terrain"}).text)
                c.hidden = Util.parse_date(row.find(attrs={"data-column": "PlaceDate"}).text)
                c.author = row.find("span", "owner").text[3:]  # delete "by "

                logging.debug("Cache parsed: %s", c)
                yield c

            start_index += 1

    @login_needed
    def _search_get_page(self, point, start_index):

        logging.debug("Loading page from start_index: %d", start_index)

        if start_index == 0:
            # first request has to load normal search page
            logging.debug("Using normal search endpoint")

            params = urlencode({"origin": point.format(None, "", "", "")})
            url = self._urls["search"] + "?" + params

            # make request
            try:
                return str(self._browser.get(url).soup.find(id="geocaches"))
            except requests.exceptions.ConnectionError as e:
                raise Error("Cannot load search results.") from e

        else:
            # other requests can use AJAX endpoint
            logging.debug("Using AJAX search endpoint")

            params = urlencode({
                "inputOrigin": point.format(None, "", "", ""),
                "startIndex": start_index,
                "originTreatment": 0
            })
            url = self._urls["search_more"] + "?" + params

            # make request
            try:
                return self._browser.get(url).json()["HtmlString"].strip()
            except requests.exceptions.ConnectionError as e:
                raise Error("Cannot load search results.") from e

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
        assert isinstance(area, Area)
        # Calculate initial tiles
        tiles, starting_precision = self._calculate_initial_tiles(area)

        # Check for continuation requirement and download tiles
        geocaches = self._get_utfgrid_caches(*tiles)
        if precision is not None:
            # On which zoom level grid details exceed required precision
            new_zoom = self._get_zoom_by_distance(
                precision, area.mean_point.latitude, UTFGrid.size, "ge")
            new_precision = area.mean_point.precision_from_tile_zoom(
                new_zoom, UTFGrid.size)
            assert precision >= new_precision
            new_zoom = min(new_zoom, UTFGrid.max_zoom)
        if precision is None or precision >= starting_precision \
                or new_zoom == tiles[0][-1]:   # Previous zoom
            # No need to continue: start yielding caches
            for c in geocaches:
                if strict and not c.inside_area(area):
                    continue
                yield c
            return

        # Define new tiles for downloading
        logging.info("Downloading again at zoom level {} "
                     "(precision {:.1f} m)".format(new_zoom, new_precision))
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
        starting_zoom = self._get_zoom_by_distance(
            dist, area.mean_point.latitude, 1, "le")
        starting_tile_width = area.mean_point.precision_from_tile_zoom(
            starting_zoom, 1)
        starting_precision = starting_tile_width / UTFGrid.size
        assert dist <= starting_tile_width
        zoom = min(starting_zoom, UTFGrid.max_zoom)
        logging.info("Starting at zoom level {} (precision {:.1f} m, "
                     "tile width {:.0f} m)".format(
                         zoom, starting_precision, starting_tile_width))
        x1, y1, _ = area.bounding_box.corners[0].to_map_tile(zoom)
        x2, y2, _ = area.bounding_box.corners[1].to_map_tile(zoom)
        tiles = []                        # [(x, y, z), ...]
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
        logging.debug("Extending search to tiles {}".format(
            new_tiles))
        for c in self._get_utfgrid_caches(*new_tiles):
            missing_caches.pop(c.wp, None)   # Mark as found
            yield c
        if missing_caches:
            logging.debug("Could not just find these caches anymore: "
                          .format(missing_caches))
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

        diam = geopy.distance.ELLIPSOIDS["WGS-84"][0] * 1e3 * 2
        if comparison == "le":
            convert = math.floor
        elif comparison == "ge":
            convert = math.ceil
        return convert(-math.log(dist * tile_resolution / (math.pi * diam * math.cos(math.radians(lat)))) / math.log(2))

    def load_cache_quick(self, wp, destination=None):
        """Loads details from map server.

        Loads just basic cache details, but very quickly."""

        assert type(wp) is str and wp.startswith("GC")
        logging.info("Loading quick details about %s...", wp)

        # assemble request
        params = urlencode({"i": wp})
        url = self._urls["map"] + "?" + params

        try:
            res = self._browser.get(url).json()
        except requests.exceptions.ConnectionError as e:
            raise Error("Cannot load quick cache details page.") from e

        if res["status"] == "failed" or len(res["data"]) != 1:
            raise LoadError("Waypoint '{}' cannot be loaded: {}".format(wp, res["msg"]))

        data = res["data"][0]

        # create cache object
        c = destination or Cache(wp, self)
        assert isinstance(c, Cache)

        # prettify data
        c.name = data["name"]
        c.cache_type = data["type"]["text"]
        c.state = data["available"]
        c.size = data["container"]["text"]
        c.difficulty = data["difficulty"]["text"]
        c.terrain = data["terrain"]["text"]
        c.hidden = Util.parse_date(data["hidden"])
        c.author = data["owner"]["text"]
        c.favorites = int(data["fp"])
        c.pm_only = data["subrOnly"]

        logging.debug("Cache loaded: %r", c)
        return c

    @login_needed
    def load_cache(self, wp, destination=None):
        """Loads details from cache page.

        Loads all cache details and return fully populated cache object."""

        assert type(wp) is str and wp.startswith("GC")
        logging.info("Loading details about %s...", wp)

        url = self._urls["cache_details"].format(wp=wp)
        try:
            root = self._browser.get(url).soup
        except requests.exceptions.ConnectionError as e:
            raise Error("Cannot load cache details page.") from e

        cache_details = root.find(id="cacheDetails")

        # check for PM only caches if using free account
        if cache_details is None:
            if root.select(".PMOWarning") is not None:
                raise PMOnlyException("Premium Members only.")

        # parse raw data
        name = cache_details.find("h2")
        cache_type = cache_details.find("img").get("src")
        author = cache_details("a")[1]
        hidden = cache_details.find("div", "minorCacheDetails").find_all("div")[1]
        location = root.find(id="uxLatLon")
        state = root.find("ul", "OldWarning")
        found = root.find("div", "FoundStatus")
        D_T = root.find("div", "CacheStarLabels").find_all("img")
        size = root.find("div", "CacheSize").find("img")
        attributes_raw = root.find_all("div", "CacheDetailNavigationWidget")[0].find_all("img")
        user_content = root.find_all("div", "UserSuppliedContent")
        hint = root.find(id="div_hint")
        favorites = root.find("span", "favorite-value")

        # create cache object
        c = destination or Cache(wp, self)
        assert isinstance(c, Cache)

        # prettify data
        c.name = name.text
        c.cache_type = Cache.get_cache_type_by_img(cache_type)
        c.author = author.text
        c.hidden = Util.parse_date(hidden.text.split(":")[-1])
        c.location = Point.from_string(location.text)
        c.state = state is None
        c.found = found and "Found It!" in found.text or False
        c.difficulty, c.terrain = [float(_.get("alt").split()[0]) for _ in D_T]
        c.size = size.get("src").split("/")[-1].rsplit(".", 1)[0]  # filename of img[src]
        attributes_raw = [_.get("src").split('/')[-1].rsplit("-", 1) for _ in attributes_raw]
        c.attributes = {attribute_name: appendix.startswith("yes")
                        for attribute_name, appendix in attributes_raw if not appendix.startswith("blank")}
        c.summary = user_content[0].text
        c.description = str(user_content[1])
        c.hint = Util.rot13(hint.text.strip())
        c.favorites = int(favorites.text)

        logging.debug("Cache loaded: %r", c)
        return c

    def get_logged_user(self, login_page=None):
        """Returns the name of curently logged user or None, if no user is logged in."""

        login_page = login_page or self._browser.get(self._urls["login_page"])
        assert isinstance(login_page, requests.Response)

        logging.debug("Checking for already logged user.")
        try:
            return login_page.soup.find("div", "LoggedIn").find("strong").text
        except AttributeError:
            return None
