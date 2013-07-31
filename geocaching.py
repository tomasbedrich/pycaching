# -*- encoding: utf-8 -*-

import logging
import unittest
import cookielib
import urllib2
import geopy as geo
from util import Util
from urllib import urlencode
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup


class Geocaching(object):

    baseurl = "https://www.geocaching.com/"

    urls = {
        "loginPage": "login/default.aspx",
        "cacheByWPT": "seek/cache_details.aspx?wp="
    }

    # Useragent: which browser/platform should this script masquerade as
    useragent = "User-Agent=Mozilla/5.0 (X11; U; Linux i686; en-US; rv:666)"


    def __init__(self):
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

        page = Util.urlopen(self._getURL("loginPage"))
        if not page:
            return False
        soup = BeautifulSoup(page.read())

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
        headers = {"User-Agent": self.useragent}
        postData = urlencode(postValues)

        # login to the site
        logging.debug("Submiting login form.")
        page = Util.urlopen(url, postData, headers)
        if not page:
            return False
        soup = BeautifulSoup(page.read())

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


    def search(self, point):
        if not self.loggedIn or isinstance(point, geo.Point()):
            return


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

    username, password = "cache-map", "pGUgNw59"

    def setUp(self):
        self.g = Geocaching()

    def test_login(self):
        # bad username
        self.assertFalse( self.g.login("", "") )
        # good username
        self.assertTrue( self.g.login(self.username, self.password) )
        # good username already logged
        self.assertTrue( self.g.login(self.username, self.password) )
        # bad username automatic logout
        self.assertFalse( self.g.login("", "") )

    def test_logout(self):
        self.assertTrue( self.g.login(self.username, self.password) )
        self.g.logout()
        self.assertEquals( self.g.getLoggedUser(), None )

    def test_getLoggedUser(self):
        self.assertTrue( self.g.login(self.username, self.password) )
        self.assertEquals( self.g.getLoggedUser(), self.username )




def main():
    """The main program"""

    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)
    unittest.main()


if __name__ == "__main__":
    main()