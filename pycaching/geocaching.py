#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging
import unittest
import cookielib
import urllib2
import geopy as geo
import json
from util import Util
from cache import Cache
from urlparse import urljoin
from urllib import urlencode
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from types import *


class Geocaching(object):

    baseurl = "https://www.geocaching.com/"
    mapurl = "http://tiles01.geocaching.com/map.details"

    urls = {
        "loginPage": "login/default.aspx",
        "cacheDetails": "seek/cache_details.aspx",
        "cachesNearest": "seek/nearest.aspx"
    }

    # interesting URLs:
    # http://tiles01.geocaching.com/map.details?i=GCNJ2Z
    # http://tiles01.geocaching.com/map.info?x=8803&y=5576&z=14 (http://www.mapbox.com/developers/utfgrid/)
    # http://tiles01.geocaching.com/map.png?x=8803&y=5576&z=14


    def __init__(self):
        self.loggedIn = False

        # Installs a cookie jar and associates it with urllib2.
        # Important to keep us logged on to the website.
        # Adapted http://www.voidspace.org.uk/python/articles/cookielib.shtml
        self.cookieJar = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar))
        urllib2.install_opener(opener)


    def login(self, username, password):
        """Logs the user in.

        Downloads the relevant cookies to keep the user logged in."""

        logging.info("Logging in...")

        rawPage = Util.urlopen(self._getURL("loginPage"))
        if not rawPage:
            logging.error("Cannot load login page.")
            return False
        soup = BeautifulSoup(rawPage.read())

        logging.debug("Checking for previous login.")
        logged = self.getLoggedUser(soup)
        if logged:
            if logged == username:
                logging.info("Already logged as %s.", logged)
                self.loggedIn = True
                return True
            else:
                logging.info("Already logged as %s, but want to log in as %s.", logged, username)
                self.logout()

        # continue logging in
        postValues = dict()
        logging.debug("Assembling POST data.")

        # login fields
        loginElements = soup("input", type=["text", "password", "checkbox"])
        for field, val in zip(loginElements, [username, password, 1]):
            postValues[field["name"]] = val

        # other nescessary fields
        for field in soup("input", type=["hidden", "submit"]):
            postValues[field["name"]] = field["value"]

        url = self._getURL("loginPage")

        # login to the site
        logging.debug("Submiting login form.")
        rawPage = Util.urlopen(url, postValues)
        if not rawPage:
            logging.error("Cannot load response after login.")
            return False
        soup = BeautifulSoup(rawPage.read())

        logging.debug("Checking the result.")
        if self.getLoggedUser(soup):
            logging.info("Logged in successfully as %s.", username)
            self.loggedIn = True
            return True
        else:
            logging.error("Cannot logon to the site (probably wrong username or password).")
            return False

    def logout(self):
        """Logs out the user.

        Logs out the user by cleaning cookies."""

        logging.info("Logging out.")
        self.cookieJar.clear()
        self.loggedIn = False


    def search(self, point, limit=0 ):
        """Returns a generator object of caches around some point."""

        if not self.loggedIn or not isinstance(point, geo.Point) or type(limit) is not IntType:
            return

        logging.info("Searching at %s...", point)

        pageNum = 1
        cacheNum = 0
        while True:
            page = self._searchGetPage(point, pageNum)
            for cache in page:
                yield cache

                cacheNum += 1
                if limit > 0 and cacheNum >= limit:
                    raise StopIteration()

            pageNum += 1


    def _searchGetPage(self, point, page=1):
        """Returns one page of caches as a list.

        Searches for a caches around a point and returns N-th page (specifiend by page argument)."""

        if not self.loggedIn or not isinstance(point, geo.Point) or type(page) is not IntType:
            return

        logging.info("Fetching page %d.", page)

        # assemble request
        params = urlencode({"lat": point.latitude, "lng": point.longitude})
        url = self._getURL("cachesNearest") + "?" + params

        # we have to add POST for other pages than 1st
        if page == 1:
            data = None
        else:
            # TODO handle searching on second page without first
            data = self.paggingHelpers
            data["__EVENTTARGET"] = self.paggingPostbacks[page]
            data["__EVENTARGUMENT"] = ""

        # make request
        rawPage = Util.urlopen(url, data)
        if not rawPage:
            logging.error("Cannot load search page.")
            return list()
        soup = BeautifulSoup(rawPage)

        # root of a few following elements
        pageBuilders = soup("td", "PageBuilderWidget")

        # parse pagging widget
        total, page, pageCount = map(lambda elm: int(elm.text), pageBuilders[0].findAll("b"))
        logging.debug("Found %d results. Showing page %d of %d.", total, page, pageCount)

        # save search postbacks for future usage
        if page == 1:
            paggingLinks = filter(lambda e: e.get("id"), pageBuilders[1].findAll("a"))
            paggingPostbacks = {int(link.text): link.get("href").split("'")[1] for link in paggingLinks}
            self.paggingPostbacks = paggingPostbacks

            # other nescessary fields
            self.paggingHelpers = dict()
            for field in soup("input", type="hidden"):
                self.paggingHelpers[field["name"]] = field["value"]

        # parse results table
        data = soup.find("table", "SearchResultsTable").findAll("tr", "Data")
        result = []
        for cache in data:

            # parse raw data
            typeLink, nameLink = cache("a", "lnk")
            direction, info, DandT, placed, lastFound = cache("span", "small")
            found = cache.find("img", title="Found It!") is not None
            size = cache.find("td", "AlignCenter").find("img")
            author, wp, area = map(lambda t: t.strip(), info.text.split("|"))

            # prettify data
            cacheType = typeLink.find("img").get("alt")
            name = nameLink.span.text.strip().encode("ascii", "xmlcharrefreplace")
            state = not "Strike" in nameLink.get("class")
            size = " ".join(size.get("alt").split()[1:]).lower()
            dif, ter = map(float, DandT.text.split("/"))
            hidden = datetime.strptime(placed.text, '%m/%d/%Y').date()
            author = author[3:].encode("ascii", "xmlcharrefreplace") # delete "by "

            # assemble cache object
            c = Cache(wp, name, cacheType, None, state, found, size, dif, ter, author, hidden)
            logging.debug("Parsing cache: %s", c)
            result.append(c)

        return result


    def loadCacheQuick(self, wp):
        """Loads details from map server.

        Loads just basic cache details, but very quickly"""

        if not self.loggedIn or not (isinstance(wp, StringTypes) and wp.startswith("GC")):
            return

        logging.info("Loading quick details about %s...", wp)

        # assemble request
        params = urlencode({"i": wp})
        url = self.mapurl + "?" + params

        # make request
        rawPage = Util.urlopen(url)
        if not rawPage:
            logging.error("Cannot load search page.")
            return
        res = json.loads(rawPage.read())

        # check for success
        if res["status"] != "success":
            return None
        data = res["data"][0]

        # prettify some data
        size = data["container"]["text"].lower()
        hidden = datetime.strptime(data["hidden"], '%m/%d/%Y').date()

        # assemble cache object
        c = Cache(wp, data["name"], data["type"]["text"], None, data["available"], None,
            size, data["difficulty"]["text"], data["terrain"]["text"],
            data["owner"]["text"], hidden, None)
        return c


    def loadCache(self, wp):
        """Loads details from cache page.

        Loads all cache details and return fully populated cache object."""

        if not self.loggedIn or not (isinstance(wp, StringTypes) and wp.startswith("GC")):
            return

        logging.info("Loading details about %s...", wp)

        # assemble request
        params = urlencode({"wp": wp})
        url = self._getURL("cacheDetails") + "?" + params

        # make request
        rawPage = Util.urlopen(url)
        if not rawPage:
            logging.error("Cannot load search page.")
            return
        soup = BeautifulSoup(rawPage)

        # parse raw data
        cacheDetails = soup.find(id="cacheDetails")
        name = cacheDetails.find("h2")
        cacheType = cacheDetails.find("img").get("alt")
        author = cacheDetails("a")[1]
        hidden = cacheDetails.find("div", "minorCacheDetails").findAll("div")[1]
        location = soup.find(id="uxLatLon")
        state = soup.find("ul", "OldWarning")
        found = soup.find("div", "FoundStatus")
        DandT = soup.find("div", "CacheStarLabels").findAll("img")
        size = soup.find("div", "CacheSize").find("img")
        attributesRaw = soup("div", "CacheDetailNavigationWidget")[0].findAll("img")
        userContent = soup("div", "UserSuppliedContent")
        hint = soup.find(id="div_hint")

        # prettify data
        name = name.text.encode("ascii", "xmlcharrefreplace")
        author = author.text.encode("ascii", "xmlcharrefreplace")
        hidden = datetime.strptime(hidden.text.split()[2], '%m/%d/%Y').date()
        location = location.text.encode("ascii", "xmlcharrefreplace")
        state = state is None
        found = found and "Found It!" in found.text or False
        dif, ter = map(lambda e: float(e.get("alt").split()[0]), DandT)
        size = " ".join(size.get("alt").split()[1:]).lower()
        attributesRaw = map(lambda e: e.get("src").split('/')[-1].split("-"), attributesRaw)
        attributes = {} # parse attributes by src to know yes/no
        for name, appendix in attributesRaw:
            if appendix.startswith("blank"):
                continue
            attributes[name] = appendix.startswith("yes")
        summary = userContent[0].text.encode("ascii", "xmlcharrefreplace")
        description = userContent[1]
        hint = Util.rot13decode(hint.text.strip())

        # assemble cache object
        c = Cache(wp, name, cacheType, location, state, found,
            size, dif, ter, author, hidden, attributes,
            summary, description, hint)
        return c


    def getLoggedUser(self, soup=None):
        """Returns the name of curently logged user.

        Or None if no user is logged in."""

        if not isinstance(soup, BeautifulSoup):
            logging.debug("No 'soup' passed, loading login page on my own.")
            page = Util.urlopen(self._getURL("loginPage"))
            soup = BeautifulSoup(page.read())

        logging.debug("Checking for already logged user.")
        try:
            return soup.find("div", "LoggedIn").find("strong").text
        except AttributeError:
            return None


    def _getURL(self, name):
        return urljoin(self.baseurl, self.urls[name])




class TestGeocaching(unittest.TestCase):

    # please DO NOT CHANGE!
    username, password = "cache-map", "pGUgNw59"

    def setUp(self):
        self.g = Geocaching()


    @unittest.skip("tmp")
    def test_login(self):
        # bad username
        self.assertFalse( self.g.login("", "") )
        # good username
        self.assertTrue( self.g.login(self.username, self.password) )
        # good username already logged
        self.assertTrue( self.g.login(self.username, self.password) )
        # bad username automatic logout
        self.assertFalse( self.g.login("", "") )


    @unittest.skip("tmp")
    def test_logout(self):
        self.assertTrue( self.g.login(self.username, self.password) )
        self.g.logout()
        self.assertIsNone( self.g.getLoggedUser() )


    @unittest.skip("tmp")
    def test_getLoggedUser(self):
        self.assertTrue( self.g.login(self.username, self.password) )
        self.assertEquals( self.g.getLoggedUser(), self.username )


    # @unittest.skip("tmp")
    def test_search(self):
        self.assertTrue( self.g.login(self.username, self.password) )

        # normal
        expected = ["GC41FJC", "GC17E8Y", "GC1ZAQV"]
        caches = self.g.search(geo.Point(49.733867, 13.397091), len(expected))
        for wp, cache in zip(expected, caches):
            self.assertEquals(wp, str(cache))

        # pagging
        caches = self.g.search(geo.Point(49.733867, 13.397091), 25)
        res = [c for c in caches]
        self.assertNotEquals(res[0], res[20])


    @unittest.skip("tmp")
    def test_loadCache(self):
        self.assertTrue( self.g.login(self.username, self.password) )

        c = self.g.loadCache("GC4808G")
        self.assertTrue( isinstance(c, Cache) )
        self.assertEquals( "GC4808G", Cache.__str__(c) )


    @unittest.skip("tmp")
    def test_loadCacheQuick(self):
        self.assertTrue( self.g.login(self.username, self.password) )

        c = self.g.loadCacheQuick("GC4808G")
        self.assertTrue( isinstance(c, Cache) )
        self.assertEquals( "GC4808G", Cache.__str__(c) )


    def tearDown(self):
        self.g.logout()



def main():
    """The main program"""

    logging.basicConfig(level=logging.INFO)
    # logging.basicConfig(level=logging.DEBUG)
    unittest.main()


if __name__ == "__main__":
    main()
