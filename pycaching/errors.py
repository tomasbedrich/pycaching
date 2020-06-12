#!/usr/bin/env python3


class Error(Exception):
    """General pycaching error.

    .. note:
       This class is a superclass of all errors produced by pycaching module, so you can use it to
       catch all pycaching related errors.
    """
    pass


class NotLoggedInException(Error):
    """Tried to perform an operation which requires logging in first."""
    pass


class LoginFailedException(Error, ValueError):
    """Login failed.

    The provided credentials probably doesn't work to log in.
    """
    pass


class GeocodeError(Error, ValueError):
    """Geocoding failed.

    Probably because of non-existing location.
    """
    pass


class LoadError(Error, OSError):
    """Object loading failed.

    Probably because of non-existing object or missing informations required to load it.
    """
    pass


class PMOnlyException(Error):
    """Requested cache is PM only."""
    pass


class BadBlockError(Error):
    pass


class ValueError(Error, ValueError):
    """Wrapper for Pythons native ValueError.

    Can be raised in various situations, but most commonly when unexpected property value is set.
    """
    pass


class TooManyRequestsError(Error):
    """Geocaching API rate limit has been reached."""

    def __init__(self, url: str, rate_limit_reset: int = 0):
        """
        Initialize TooManyRequestsError.

        :param url: Requested url.
        :param rate_limit_reset: Number of seconds to wait before rate limit reset.
        """
        self.url = url
        self.rate_limit_reset = rate_limit_reset

    def wait_for(self):
        """Wait enough time to release Rate Limits."""
        import time
        time.sleep(self.rate_limit_reset + 5)
