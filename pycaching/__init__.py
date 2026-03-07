from pycaching.cache import Cache  # NOQA
from pycaching.geo import Point, Rectangle  # NOQA
from pycaching.geocaching import Geocaching  # NOQA
from pycaching.log import Log  # NOQA
from pycaching.trackable import Trackable  # NOQA

__version__ = "4.4.3"  # PEP 440


def login(username=None, password=None):
    """A shortcut for user login.

    Create a :class:`.Geocaching` instance and try to login a user. See :meth:`.Geocaching.login`.

    :return: Created :class:`.Geocaching` instance.
    """
    g = Geocaching()
    g.login(username, password)
    return g


def login_with_cookie(cookie, username=None, cookie_name="gspkauth"):
    """A shortcut for cookie-based user login.

    Create a :class:`.Geocaching` instance and import an authenticated cookie.

    :return: Created :class:`.Geocaching` instance.
    """
    g = Geocaching()
    g.login_with_cookie(cookie=cookie, username=username, cookie_name=cookie_name)
    return g
