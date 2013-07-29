# -*- encoding: utf-8 -*-

import logging
import cookielib
import urllib2
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
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

    def login(self, username, password):
        """Logs the user in.

        Downloads the relevant cookies to keep the user logged in."""

        logging.info("Logging in...")

        try:
            page = self._urlopen(self._getURL("loginPage"))
            soup = BeautifulSoup(page.read())

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
            page = self._urlopen(url, postData, headers)
            soup = BeautifulSoup(page.read())

            logging.debug("Checking the result.")
            if not soup("div", "LoggedIn"):
                logging.error("Cannot logon to the site (probably wrong username or password).")
                return False

            logging.info("Logged in successfully as %s.", username)
            return True

        except urllib2.URLError, e:
            logging.error("Cannot access the website: %s", e)
            return False

    def _getURL(self, name):
        return urljoin(self.baseurl, self.urls[name])

    def _urlopen(self, url, *args, **kwargs):
        logging.debug("Making request on: %s", url)
        request = urllib2.Request(url, *args, **kwargs)
        return urllib2.urlopen(request)


def main():
    """The main program"""

    logging.basicConfig(level=logging.DEBUG)

    g = Geocaching()


if __name__ == "__main__":
    main()