#!/usr/bin/env python3

import datetime
import enum
import json
import logging
import re
import subprocess
from os import path
from typing import Generator, Optional, Union
from urllib.parse import urljoin

import bs4
import requests
from bs4.element import Script  # Direct import as `bs4.Script` requires version >= 4.9.1.

from pycaching.cache import Cache
from pycaching.errors import Error, LoginFailedException, NotLoggedInException, PMOnlyException, TooManyRequestsError
from pycaching.geo import Point, Rectangle
from pycaching.log import Log
from pycaching.log import Type as LogType
from pycaching.trackable import Trackable
from pycaching.util import deprecated


class SortOrder(enum.Enum):
    """Enum of possible cache sort orderings returned in Groundspeak API."""

    # NOTE: extracted from https://www.geocaching.com/play/map/public/main.2b28b0dc1c9c10aaba66.js
    container_size = "containersize"
    date_last_visited = "datelastvisited"
    difficulty = "difficulty"
    distance = "distance"
    favorite_point = "favoritepoint"
    found_date = "founddate"
    found_date_of_found_by_user = "founddateoffoundbyuser"
    geocache_name = "geocachename"
    place_date = "placedate"
    terrain = "terrain"


class Geocaching(object):
    """Provides some basic methods for communicating with geocaching.com website.

    Provides methods to login and search. There are also some shortcut methods in this class to make
    working with pycaching more convinient.
    """

    _baseurl = "https://www.geocaching.com"
    _urls = {
        "login_page": "account/signin",
        "search": "play/search",
        "search_more": "play/search/more-results",
        "my_logs": "my/logs.aspx",
        "api_search": "api/proxy/web/search/v2",
    }
    _credentials_file = ".gc_credentials"

    def __init__(self, *, session=None):
        self._logged_in = False
        self._logged_username = None
        self._session = session or requests.Session()

    def _request(self, url, *, expect="soup", method="GET", login_check=True, **kwargs):
        """
        Do a HTTP request and return a response based on expect param.

        :param str url: Request target.
        :param str method: HTTP method to use.
        :param str expect: Expected type of data (either :code:`soup`, :code:`json` or :code:`raw`).
        :param bool login_check: Whether to check if user is logged in or not.
        :param kwargs: Passed to `requests.request
            <http://docs.python-requests.org/en/latest/api/#requests.request>`_ as is.
        """
        # check login unless explicitly turned off
        if login_check and not self._logged_in:
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
            if e.response.status_code == 429:  # Handle rate limiting errors
                raise TooManyRequestsError(
                    url, rate_limit_reset=int(e.response.headers.get("x-rate-limit-reset", "0"))
                ) from e

            raise Error("Cannot load page: {}".format(url)) from e

    def login(self, username=None, password=None):
        """Log in the user for this instance of Geocaching.

        If username or password is not set, try to load credentials from file. Then load login page
        and do some checks about currently logged user. As a last thing post the login form and
        check result.

        :param str username: User's username or :code:`None` to use data from credentials file.
        :param str password: User's password or :code:`None` to use data from credentials file.
        :raise .LoginFailedException: If login fails either because of bad credentials or
            non-existing credentials file.
        """
        logging.info("Logging in...")

        if not username or not password:
            try:
                username, password = self._load_credentials(username=username)
            except FileNotFoundError as e:
                raise LoginFailedException("Credentials file not found and no username and password is given.") from e
            except ValueError as e:
                raise LoginFailedException("Wrong format of credentials file.") from e
            except KeyError as e:
                raise LoginFailedException("Credentials file doesn't contain username or password/password_cmd.") from e
            except IOError as e:
                raise LoginFailedException("Credentials file reading error.") from e
            except subprocess.CalledProcessError as e:
                raise LoginFailedException("Error calling password retrieval command.") from e

        logging.debug("Checking for previous login.")
        if self._logged_in:
            logging.info("Already logged in as {}.".format(self._logged_username))
            if self._logged_username == username:
                return
            else:
                logging.info("Want to login as {} => logging out.".format(username))
                self.logout()

        login_page = self._request(self._urls["login_page"], login_check=False)

        # continue logging in, assemble POST
        logging.debug("Assembling POST data.")
        token_field_name = "__RequestVerificationToken"
        token_value = login_page.find("input", attrs={"name": token_field_name})["value"]
        post = {"UsernameOrEmail": username, "Password": password, token_field_name: token_value}

        # login to the site
        logging.debug("Submitting login form.")
        after_login_page = self._request(self._urls["login_page"], method="POST", data=post, login_check=False)

        logging.debug("Checking the result.")
        if self.get_logged_user(after_login_page):
            logging.info("Logged in successfully as {}.".format(username))
            self._logged_in = True
            self._logged_username = username
            return
        else:
            self.logout()

            if after_login_page.find("div", class_="g-recaptcha"):
                raise LoginFailedException("CAPTCHA is required to login to the site.")

            raise LoginFailedException("Cannot login to the site (probably wrong username or password).")

    def _load_credentials(self, username=None):
        """Load credentials from file.

        Find credentials file in either current directory or user's home directory. If exists, load
        it as a JSON and return credentials from it.

        :return: Tuple of username and password loaded from file.
        :rtype: :class:`tuple` of :class:`str`
        :raise .FileNotFoundError: If credentials file cannot be found.
        :raise .KeyError: If "username" was not found.
        :raise .KeyError: If neither "password" nor "password_cmd" where found.
        :raise .KeyError: If "password" and "password_cmd" where found at the
            same time.
        """
        credentials_file = self._credentials_file

        # find the location of a file
        if path.isfile(credentials_file):
            logging.info("Loading credentials file from current directory")
        else:
            credentials_file = path.join(path.expanduser("~"), self._credentials_file)
            if path.isfile(credentials_file):
                logging.info("Loading credentials file form home directory")
            else:
                raise FileNotFoundError("Credentials file not found in current nor home directory.")

        # load contents
        with open(credentials_file, "r") as f:
            cred = json.load(f)
            if isinstance(cred, dict):
                if username is None:
                    credentials = cred
                else:
                    if "username" in cred and cred["username"] == username:
                        credentials = cred
                    else:
                        raise KeyError("User {} requested but not found in credential.".format(username))
            elif isinstance(cred, list):
                if username is None and len(cred) > 0:
                    credentials = cred[0]
                else:
                    for c in cred:
                        if "username" in c and c["username"] == username:
                            credentials = c
                            break
                    else:
                        raise KeyError("User {} requested but not found in credentials.".format(username))
            else:
                raise KeyError("Credential data type is unexpected {}".format(type(cred)))

            if "password" in credentials and "password_cmd" in credentials:
                raise KeyError('Ambiguous keys. Choose either "password" or "password_cmd".')
            elif "password" in credentials:
                return credentials["username"], credentials["password"]
            elif "password_cmd" in credentials:
                stdout = subprocess.check_output(credentials["password_cmd"], shell=True)
                return credentials["username"], stdout.decode("utf-8").strip()
            else:
                raise KeyError("No password was key found. " 'Use either "password" or "password_cmd".')

    def logout(self):
        """Log out the user for this instance."""
        logging.info("Logging out.")
        self._logged_in = False
        self._logged_username = None
        self._session.cookies.clear()

    def get_logged_user(self, login_page=None):
        """Return the name of currently logged user.

        :param .bs4.BeautifulSoup login_page: Object containing already loaded page.
        :return: User's name or :code:`None`, if no user is logged in.
        :rtype: :class:`str` or :code:`None`
        """
        login_page = login_page or self._request(self._urls["login_page"], login_check=False)
        assert hasattr(login_page, "find_all") and callable(login_page.find_all)

        logging.debug("Checking for already logged user.")
        js_content = "\n".join(login_page.find_all(string=lambda i: isinstance(i, Script)))
        m = re.search(r'"username":\s*"(.*)"', js_content)
        return m.group(1) if m else None

    def search(
        self,
        point: Point,
        limit: int = float("inf"),
        *,
        sort_by: Union[str, SortOrder] = SortOrder.date_last_visited,
        reverse: bool = False,
        per_query: int = 200,
        wait_sleep: bool = True,
    ) -> Generator[Optional[Cache], None, None]:
        """Search for caches around a specified location using a search API.

        :param point: The :class:`.geo.Point` object representing the center point of the search.
        :param limit: The maximum number of caches to load.
            Defaults to infinity.
        :param sort_by: The criterion to sort the caches by.
            Defaults to :code:`SortOrder.date_last_visited`.
        :param reverse: If :code:`True`, the order of the results is reversed.
            Defaults to :code:`False`.
        :param per_query: The number of caches to request in each query.
            Defaults to :code:`200`.
        :param wait_sleep: In case of rate limits exceeding, wait appropriate time
            if set to :code:`True`, otherwise just yield :code:`None`.
            Defaults to :code:`True`.
        :return: A generator that yields :class:`.Cache` objects.
        """

        if not isinstance(sort_by, SortOrder):
            sort_by = SortOrder(sort_by)

        return self.advanced_search(
            {
                "origin": "{},{}".format(point.latitude, point.longitude),
                "asc": str(not reverse).lower(),
                "sort": sort_by.value,
            },
            per_query=per_query,
            limit=limit,
            wait_sleep=wait_sleep,
        )

    @deprecated
    def search_quick(self, area):
        """Search for caches in a specified :class:`.Rectangle` area.

        :param rect: The :class:`.Rectangle` object representing the search area.
        :type rect: geo.Rectangle
        :return: A generator that yields :class:`.Cache` objects.
        :rtype: Generator[Optional[Cache], None, None]
        """

        return self.search_rect(area)

    def search_rect(
        self,
        rect: Rectangle,
        limit: int = float("inf"),
        *,
        sort_by: Union[str, SortOrder] = SortOrder.date_last_visited,
        reverse: bool = False,
        per_query: int = 200,
        origin: Optional[Point] = None,
        wait_sleep: bool = True,
    ) -> Generator[Optional[Cache], None, None]:
        """Search for caches in a specified :class:`.Rectangle` area using a search API.

        :param rect: The :class:`.Rectangle` object representing the search area.
        :param limit: The maximum number of caches to load.
            Defaults to infinity.
        :param sort_by: The criterion to sort the caches by.
            Defaults to :code:`SortOrder.date_last_visited`.
        :param reverse: If :code:`True`, the order of the results is reversed.
            Defaults to :code:`False`.
        :param per_query: The number of caches to request in each query.
            Defaults to :code:`200`.
        :param origin: The origin point for search by distance, required when sorting by distance.
        :param wait_sleep: In case of rate limits exceeding, wait appropriate time
            if set to :code:`True`, otherwise just yield :code:`None`.
            Defaults to :code:`True`.
        :return: A generator that yields :class:`.Cache` objects.
        """

        if not isinstance(sort_by, SortOrder):
            sort_by = SortOrder(sort_by)

        params = {
            "box": "{},{},{},{}".format(
                rect.corners[0].latitude,
                rect.corners[0].longitude,
                rect.corners[1].latitude,
                rect.corners[1].longitude,
            ),
            "asc": str(not reverse).lower(),
            "sort": sort_by.value,
        }

        if sort_by is SortOrder.distance:
            assert isinstance(origin, Point)
            params["origin"] = "{},{}".format(origin.latitude, origin.longitude)

        return self.advanced_search(
            params,
            per_query=per_query,
            limit=limit,
            wait_sleep=wait_sleep,
        )

    def advanced_search(
        self,
        options: dict,
        limit: int = float("inf"),
        per_query: int = 200,
        wait_sleep: bool = True,
    ) -> Generator[Optional[Cache], None, None]:
        """Perform an advanced search for geocaches with specific search criteria.

        The search is performed using the options provided in the :code:`options` parameter.
        Example of the :code:`options` parameter::

            # https://www.geocaching.com/play/search?owner[0]=Geocaching%20HQ&a=0
            options = {"owner[0]": "Geocaching HQ", "a": "0"}

        :param options: A dictionary of search options.
        :param limit: The maximum number of caches to load.
            Defaults to infinity.
        :param per_query: The number of caches to request in each query.
            Defaults to :code:`200`.
        :param wait_sleep: In case of rate limits exceeding, wait appropriate time
            if set to :code:`True`, otherwise just yield :code:`None`.
            Defaults to :code:`True`.
        :return: A generator that yields :class:`.Cache` objects.
        """

        if limit <= 0:
            return

        take_amount = min(limit, per_query)

        params = options.copy()
        params.update(
            {
                "take": take_amount,
                "skip": 0,
            }
        )

        total, offset = None, 0
        while (offset < limit) and ((total is None) or (offset < total)):
            params["skip"] = offset

            try:
                resp = self._request(self._urls["api_search"], params=params, expect="json")
            except TooManyRequestsError as e:
                if wait_sleep:
                    e.wait_for()
                else:
                    yield None
                continue

            for record in resp["results"]:
                yield Cache._from_api_record(self, record)

            total = resp["total"]
            offset += take_amount

    # add some shortcuts ------------------------------------------------------

    def geocode(self, location):
        """Return a :class:`.Point` object from geocoded location.

        :param str location: Location to geocode.
        """
        return Point.from_location(self, location)

    def get_cache(self, wp=None, guid=None):
        """Return a :class:`.Cache` object by its waypoint or GUID.

        :param str wp: Cache waypoint.
        :param str guid: Cache GUID.

        .. note ::
           Provide only the GUID or the waypoint, not both.
        """
        if (wp is None) == (guid is None):
            raise TypeError("Please provide exactly one of `wp` or `guid`.")
        if wp is not None:
            return Cache(self, wp)
        return self._cache_from_guid(guid)

    def get_trackable(self, tid):
        """Return a :class:`.Trackable` object by its trackable ID.

        :param str tid: Trackable ID.
        """
        return Trackable(self, tid)

    def post_log(self, wp, text, type=LogType.found_it, date=None):
        """Post a log for cache.

        :param str wp: Cache waypoint.
        :param str text: Log text.
        :param .log.Type type: Type of log.
        :param datetime.date date: Log date. If set to :code:`None`, :meth:`datetime.date.today`
            is used instead.
        """
        if not date:
            date = datetime.date.today()
        log = Log(type=type, text=text, visited=date)
        self.get_cache(wp).post_log(log)

    def _cache_from_guid(self, guid):
        logging.info("Loading cache with GUID {!r}".format(guid))
        print_page = self._request(Cache._urls["print_page"], params={"guid": guid})
        return Cache._from_print_page(self, guid, print_page)

    def _try_getting_cache_from_guid(self, guid):
        """Try to get a cache from guid page if possible, otherwise from gccode.

        :param str guid: Guid of the cache that should be read in.
        """
        try:
            return self.get_cache(guid=guid)
        except PMOnlyException:
            url = self._request(Cache._urls["cache_details"], params={"guid": guid}, expect="raw").url
            wp = url.split("/")[4].split("_")[0]  # get gccode from redirected url
            return self.get_cache(wp)

    def my_logs(self, log_type=None, limit=float("inf")):
        """Get an iterable of the logged-in user's logs.

        :param log_type: The log type to search for. Use a :class:`~.log.Type` value.
            If set to ``None``, all logs will be returned (default: ``None``).
        :param limit: The maximum number of results to return (default: infinity).
        """
        logging.info("Getting {} of my logs of type {}".format(limit, log_type))
        url = self._urls["my_logs"]
        if log_type is not None:
            if isinstance(log_type, LogType):
                log_type = log_type.value
            url += "?lt={lt}".format(lt=log_type)
        cache_table = self._request(url).find(class_="Table")
        if cache_table is None:  # no logs on the account
            return
        cache_table = cache_table.tbody

        yielded = 0
        for row in cache_table.find_all("tr"):
            if yielded >= limit:
                break

            link = row.find(class_="ImageLink")["href"]

            # This line extracts a GC code from the cache URL
            # Example: https://www.geocaching.com/geocache/GC12345 -> GC12345
            wp = link.split("/")[4]

            current_cache = self.get_cache(wp)
            date = row.find_all("td")[2].text.strip()
            current_cache.visited = date

            yield current_cache
            yielded += 1

    def my_finds(self, limit=float("inf")):
        """Get an iterable of the logged-in user's finds.

        :param limit: The maximum number of results to return (default: infinity).
        """
        return self.my_logs(LogType.found_it, limit)

    def my_dnfs(self, limit=float("inf")):
        """Get an iterable of the logged-in user's DNFs.

        :param limit: The maximum number of results to return (default: infinity).
        """
        return self.my_logs(LogType.didnt_find_it, limit)
