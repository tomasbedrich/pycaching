#!/usr/bin/env python3

import logging
import requests
import bs4
import geopy as geo
import mechanicalsoup as ms
from urllib.parse import urlencode
from datetime import datetime

from .util import Util
from .cache import Cache


class NotLoggedInException(BaseException):
    pass


class LoginFailedException(BaseException):
    pass


def login_needed(func):
    """Decorator for method which needs login first."""

    def wrapper(*args, **kwargs):
        assert isinstance(args[0], Geocaching)
        if not args[0]._logged_in:
            raise NotLoggedInException()
        return func(*args, **kwargs)
    return wrapper


class Geocaching(object):

    _baseurl = "https://www.geocaching.com/"

    _urls = {
        "login_page":       _baseurl + "login/default.aspx",
        "cache_details":    _baseurl + "seek/cache_details.aspx",
        "caches_nearest":   _baseurl + "seek/nearest.aspx",
        "map":              "http://tiles01.geocaching.com/map.details"
    }

    # interesting URLs:
    # http://tiles01.geocaching.com/map.details?i=GCNJ2Z
    # http://tiles01.geocaching.com/map.info?x=8803&y=5576&z=14 (http://www.mapbox.com/developers/utfgrid/)
    # http://tiles01.geocaching.com/map.png?x=8803&y=5576&z=14

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
            logging.error("Cannot load login page.")
            raise e

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
            logging.error("Cannot load response after submiting login form.")
            raise e

        logging.debug("Checking the result.")
        if self.get_logged_user(after_login_page):
            logging.info("Logged in successfully as %s.", username)
            self._logged_in = True
            return
        else:
            logging.error("Cannot login to the site (probably wrong username or password).")
            self.logout()
            raise LoginFailedException()

    def logout(self):
        """Logs out the user.

        Logs out the user by creating new browser."""

        logging.info("Logging out.")
        self._logged_in = False
        self._browser = ms.Browser()

    @login_needed
    def search(self, point, limit=0):
        """Returns a generator object of caches around some point."""

        assert isinstance(point, geo.Point)
        assert type(limit) is int

        logging.info("Searching at %s...", point)

        page_num = 1
        cache_num = 0
        while True:
            try:  # try to load search page
                page = self._search_get_page(point, page_num)
            except requests.exceptions.ConnectionError as e:
                logging.error("Cannot load search page.")
                raise StopIteration() from e

            for cache in page:
                yield cache

                cache_num += 1
                if limit > 0 and cache_num >= limit:
                    raise StopIteration()

            page_num += 1

    @login_needed
    def _search_get_page(self, point, page_num):
        """Returns one page of caches as a list.

        Searches for a caches around a point and returns N-th page (specifiend by page argument)."""

        assert isinstance(point, geo.Point)
        assert type(page_num) is int

        logging.info("Fetching page %d.", page_num)

        # assemble request
        params = urlencode({"lat": point.latitude, "lng": point.longitude})
        url = self._urls["caches_nearest"] + "?" + params

        # we have to add POST for other pages than 1st
        if page_num == 1:
            post = None
        else:
            # TODO handle searching on second page without first
            post = self._pagging_helpers
            post["__EVENTTARGET"] = self._pagging_postbacks[page_num]
            post["__EVENTARGUMENT"] = ""

        # make request (possible exception is raised)
        root = self._browser.post(url, post).soup

        # root of a few following elements
        widget_general = root.find_all("td", "PageBuilderWidget")

        # parse pagging widget
        caches_total, page_num, page_count = [int(elm.text) for elm in widget_general[0].find_all("b")]
        logging.debug("Found %d results. Showing page %d of %d.", caches_total, page_num, page_count)

        # save search postbacks for future usage
        if page_num == 1:
            pagging_links = [e for e in widget_general[1].find_all("a") if e.get("id")]
            self._pagging_postbacks = {int(link.text): link.get("href").split("'")[1] for link in pagging_links}

            # other nescessary fields
            self._pagging_helpers = {field["name"]: field["value"] for field in root.find_all("input", type="hidden")}

        # parse results table
        data = root.find("table", "SearchResultsTable").find_all("tr", "Data")
        return [self._search_parse_cache(c) for c in data]

    @login_needed
    def _search_parse_cache(self, root):
        """Returns a Cache object parsed from BeautifulSoup Tag."""

        assert isinstance(root, bs4.Tag)

        # parse raw data
        typeLink, nameLink = root("a", "lnk")
        direction, info, DandT, placed, lastFound = root("span", "small")
        found = root.find("img", title="Found It!") is not None
        size = root.find("td", "AlignCenter").find("img")
        author, wp, area = [t.strip() for t in info.text.split("|")]

        # prettify data
        cache_type = typeLink.find("img").get("alt")
        name = nameLink.span.text.strip()
        state = "Strike" not in nameLink.get("class")
        size = " ".join(size.get("alt").split()[1:]).lower()
        dif, ter = list(map(float, DandT.text.split("/")))
        hidden = datetime.strptime(placed.text, '%m/%d/%Y').date()
        author = author[3:]  # delete "by "

        # assemble cache object
        c = Cache(wp, name, cache_type, None, state, found, size, dif, ter, author, hidden)
        logging.debug("Cache parsed: %s", c)
        return c

    @login_needed
    def load_cache_quick(self, wp):
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
            logging.error("Cannot load quick cache details page.")
            raise e

        # check for success
        if res["status"] != "success":
            logging.error("Response 'status' is not 'success'.")
            raise IOError()
        data = res["data"][0]

        # prettify some data
        size = data["container"]["text"].lower()
        hidden = datetime.strptime(data["hidden"], '%m/%d/%Y').date()

        # assemble cache object
        return Cache(wp, data["name"], data["type"]["text"], None, data["available"], None,
                     size, data["difficulty"]["text"], data["terrain"]["text"],
                     data["owner"]["text"], hidden, None)

    @login_needed
    def load_cache(self, wp):
        """Loads details from cache page.

        Loads all cache details and return fully populated cache object."""

        assert type(wp) is str and wp.startswith("GC")
        logging.info("Loading details about %s...", wp)

        # assemble request
        params = urlencode({"wp": wp})
        url = self._urls["cache_details"] + "?" + params

        try:
            root = self._browser.get(url).soup
        except requests.exceptions.ConnectionError as e:
            logging.error("Cannot load cache details page.")
            raise e

        # parse raw data
        cache_details = root.find(id="cacheDetails")
        name = cache_details.find("h2")
        cache_type = cache_details.find("img").get("alt")
        author = cache_details("a")[1]
        hidden = cache_details.find("div", "minorCacheDetails").find_all("div")[1]
        location = root.find(id="uxLatLon")
        state = root.find("ul", "OldWarning")
        found = root.find("div", "FoundStatus")
        DandT = root.find("div", "CacheStarLabels").find_all("img")
        size = root.find("div", "CacheSize").find("img")
        attributes_raw = root.find_all("div", "CacheDetailNavigationWidget")[0].find_all("img")
        user_content = root.find_all("div", "UserSuppliedContent")
        hint = root.find(id="div_hint")
        favorites = root.find("span", "favorite-value")

        # prettify data
        name = name.text
        author = author.text
        hidden = datetime.strptime(hidden.text.split()[2], '%m/%d/%Y').date()
        try:
            lat, lon = Util.parseRaw(location.text)
            location = geo.Point(Util.toDecimal(*lat), Util.toDecimal(*lon))
        except ValueError as e:
            logging.error("Could not parse coordinates")
            raise e
        state = state is None
        found = found and "Found It!" in found.text or False
        dif, ter = [float(_.get("alt").split()[0]) for _ in DandT]
        size = " ".join(size.get("alt").split()[1:]).lower()
        attributes_raw = [_.get("src").split('/')[-1].rsplit("-", 1) for _ in attributes_raw]
        attributes = {attribute_name: appendix.startswith("yes")
                      for attribute_name, appendix in attributes_raw if not appendix.startswith("blank")}
        summary = user_content[0].text
        description = user_content[1].html
        hint = Util.rot13(hint.text.strip())
        favorites = int(favorites.text)

        # assemble cache object
        c = Cache(wp, name, cache_type, location, state, found,
                  size, dif, ter, author, hidden, attributes,
                  summary, description, hint, favorites)
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
