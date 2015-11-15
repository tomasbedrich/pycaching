#!/usr/bin/env python3

import logging
import datetime
import requests
import bs4
from urllib.parse import urljoin
from pycaching.cache import Cache, Type, Size
from pycaching.log import Log, Type as LogType
from pycaching.geo import Point
from pycaching.trackable import Trackable
from pycaching.errors import Error, NotLoggedInException, LoginFailedException
from pycaching.util import parse_date, deprecated


class Geocaching(object):

    _baseurl = "https://www.geocaching.com"
    _urls = {
        "login_page":        "login/default.aspx",
        "search":            "play/search",
        "search_more":       "play/search/more-results",
    }

    def __init__(self):
        self._logged_in = False
        self._session = requests.Session()

    def _request(self, url, *, expect="soup", method="GET", login_check=True, **kwargs):
        # check login unless explicitly turned off
        if login_check and self._logged_in is False:
            raise NotLoggedInException("Login is needed.")

        url = url if "//" in url else urljoin(self._baseurl, url)

        try:
            res = self._session.request(method, url, **kwargs)
            res.raise_for_status()

            # return bs4.BeautifulSoup, JSON dict or raw requests.Response
            if expect == "soup":
                return bs4.BeautifulSoup(res.text, "html.parser")
            elif expect == "json":
                return res.json()
            elif expect == "raw":
                return res

        except requests.exceptions.RequestException as e:
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
        post.update({field["name"]: val for field, val in zip(
            login_elements, [username, password, 1])})

        # other nescessary fields
        other_elements = login_page.find_all("input", type=["hidden", "submit"])
        post.update({field["name"]: field["value"] for field in other_elements})

        # login to the site
        logging.debug("Submiting login form.")
        after_login_page = self._request(
            self._urls["login_page"], method="POST", data=post, login_check=False)

        logging.debug("Checking the result.")
        if self.get_logged_user(after_login_page):
            logging.info("Logged in successfully as %s.", username)
            self._logged_in = True
            return
        else:
            self.logout()
            raise LoginFailedException(
                "Cannot login to the site (probably wrong username or password).")

    def logout(self):
        """Logs out the user.

        Logs out the user by creating new session."""

        logging.info("Logging out.")
        self._logged_in = False
        self._session = requests.Session()

    def get_logged_user(self, login_page=None):
        """Returns the name of curently logged user or None, if no user is logged in."""

        login_page = login_page or self._request(self._urls["login_page"], login_check=False)
        assert isinstance(login_page, bs4.BeautifulSoup)

        logging.debug("Checking for already logged user.")
        try:
            return login_page.find("div", "LoggedIn").find("strong").text
        except AttributeError:
            return None

    def search(self, point, limit=float("inf")):
        """Returns a generator object of caches around some point."""

        assert isinstance(point, Point)

        logging.info("Searching at {}".format(point))

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
        logging.debug("Loading page from start_index {}".format(start_index))

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

            return bs4.BeautifulSoup(res["HtmlString"].strip(), "html.parser")

    def search_quick(self, area, *, strict=False, zoom=None):
        logging.info("Searching quick in {}".format(area))

        tiles = area.to_tiles(self, zoom)
        # TODO process tiles by multiple workers
        for tile in tiles:
            for block in tile.blocks:
                cache = Cache.from_block(block)
                if strict and cache.location not in area:
                    # if strict mode is on and cache is not in area
                    continue
                else:
                    # can yield more caches (which are not exactly in desired area)
                    yield cache

    # add some shortcuts ------------------------------------------------------

    def geocode(self, location):
        return Point.from_location(self, location)

    def get_cache(self, wp):
        """Return a cache by its WP."""
        return Cache(self, wp)

    def get_trackable(self, tid):
        """Return a cache by its TID."""
        return Trackable(self, tid)

    def post_log(self, wp, text, type=LogType.found_it, date=datetime.date.today()):
        """Post log for cache."""
        l = Log(type=type, text=text, visited=date)
        self.get_cache(wp).post_log(l)

    # ensure backwards compatibility ------------------------------------------
    # deprecated methods will be removed in next version!

    @deprecated
    def load_cache(self, wp):
        return self.get_cache(wp)

    @deprecated
    def load_trackable(self, tid):
        return self.get_trackable(tid)
