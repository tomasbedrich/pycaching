#!/usr/bin/env python3

__all__ = ["geocaching", "cache", "util", "point"]
from .geocaching import Geocaching  # NOQA
from .cache import Cache  # NOQA
from .util import Util  # NOQA
from .point import Point  # NOQA


# version info should conform to PEP 386
# (major, minor, micro, alpha/beta/rc/final, #)
# (1, 1, 2, 'alpha', 0) => "1.1.2.dev"
# (1, 2, 0, 'beta', 2) => "1.2b2"
__version__ = "3.0.dev"


def login(username, password):
    """Logs the user in. A shortcut for Geocaching().login()."""
    g = Geocaching()
    g.login(username, password)
    return g
