#!/usr/bin/env python3

__all__ = ["geocaching", "cache", "util"]


# import
from .__version__ import version, version_info
from .geocaching import Geocaching
from .cache import Cache
from .util import Util
from .point import Point


# shortcut
def login(username, password):
    """Logs the user in.

    A shortcut for Geocaching().login()."""

    g = Geocaching()
    g.login(username, password)
    return g
