#!/usr/bin/env python3

import logging
from datetime import datetime
from pycaching import errors


_rot13codeTable = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM")

_attributes_url = "http://www.geocaching.com/about/icons.aspx"


def lazy_loaded(func):
    """Decorator providing lazy loading. Used by Cache and Trackable."""

    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            return func(*args, **kwargs)
        except AttributeError:
            logging.debug("Lazy loading {} into <object {} id {}>".format(
                func.__name__, type(self), id(self)))
            self.load()
            return func(*args, **kwargs)  # try to return it again

    return wrapper


def rot13(text):
    """Returns a text encoded by rot13 cipher."""
    return str.translate(text, _rot13codeTable)


def parse_date(raw):
    """Returns parsed date."""
    raw = raw.strip()
    patterns = ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y",
                "%d.%m.%Y", "%d/%b/%Y", "%d.%b.%Y", "%b/%d/%Y", "%d %b %y")

    for pattern in patterns:
        try:
            return datetime.strptime(raw, pattern).date()
        except ValueError:
            pass

    raise errors.ValueError("Unknown date format - '{}'.".format(raw))


def get_possible_attributes():
    """Returns dict of all possible attributes parsed from Groundspeak's website."""

    # imports are here not to slow down other parts of program which normally
    # doesn't use this method
    from itertools import chain
    import requests
    from bs4 import BeautifulSoup

    try:
        page = BeautifulSoup(requests.get(_attributes_url).text)
    except requests.exceptions.ConnectionError as e:
        raise errors.Error("Cannot load attributes page.") from e

    # get all <img>s containing attributes from all <dl>s with specific class
    images = chain(*map(lambda i: i.find_all("img"), page.find_all("dl", "AttributesList")))
    # create dict as {"machine name": "human description"}
    attributes = {i.get("src").split("/")[-1].rsplit("-", 1)[0]: i.get("alt") for i in images}

    return attributes
