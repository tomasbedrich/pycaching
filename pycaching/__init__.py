#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__all__ = ["geocaching", "cache", "util"]


# import
from .__version__ import version, version_info
from .geocaching import Geocaching
from .cache import Cache
from .util import Util


# shortcut	
def login(username, password):
    """Logs the user in.

    A shortcut for Geocaching().login()."""

    g = Geocaching()
    
    if not g.login(username, password):
    	return

    return g