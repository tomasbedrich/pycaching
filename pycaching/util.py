#!/usr/bin/env python3

import logging
import re
import warnings
import inspect
import functools
from datetime import datetime
from pycaching import errors


_rot13codeTable = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM"
)

_attributes_url = "http://www.geocaching.com/about/icons.aspx"


def lazy_loaded(func):
    """Decorator providing lazy loading."""
    @functools.wraps(func)
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


# copied from:
# https://wiki.python.org/moin/PythonDecoratorLibrary#Generating_Deprecation_Warnings
def deprecated(func):
    """Decorator to mark fuction as deprecated.

    It will result in a warning being emitted when the function is used.
    """
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn_explicit(
            "Call to deprecated function {}.".format(func.__name__),
            category=FutureWarning,
            filename=inspect.getfile(func),
            lineno=inspect.getsourcelines(func)[1] + 1
        )
        return func(*args, **kwargs)
    return new_func


def rot13(text):
    """Return a text encoded by rot13 cipher."""
    return str.translate(text, _rot13codeTable)


def parse_date(raw):
    """Return a parsed date."""
    raw = raw.strip()
    patterns = ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y",
                "%d.%m.%Y", "%d/%b/%Y", "%d.%b.%Y", "%b/%d/%Y", "%d %b %y")

    for pattern in patterns:
        try:
            return datetime.strptime(raw, pattern).date()
        except ValueError:
            pass

    raise errors.ValueError("Unknown date format - '{}'.".format(raw))


def format_date(date, user_date_format):
    """Format a date according to user_date_format."""
    # parse user format
    date_format = user_date_format.lower()
    date_format = re.split("(\W+)", date_format)
    formats = {
        "dd": r'%d',
        "d": r'%-d',
        "mmm": r'%b',
        "mm": r'%m',
        "m": r'%-m',
        "yyyy": r'%Y',
        "yy": r'%y',
    }
    date_format = "".join((formats[c] if c in formats else c for c in date_format))
    return date.strftime(date_format)


def get_possible_attributes():
    """Return a dict of all possible attributes parsed from Groundspeak's website."""
    # imports are here not to slow down other parts of program which normally doesn't use this method
    from itertools import chain
    import requests
    from bs4 import BeautifulSoup

    try:
        page = BeautifulSoup(requests.get(_attributes_url).text, "html.parser")
    except requests.exceptions.ConnectionError as e:
        raise errors.Error("Cannot load attributes page.") from e

    # get all <img>s containing attributes from all <dl>s with specific class
    images = chain(*map(lambda i: i.find_all("img"), page.find_all("dl", "AttributesList")))
    # create dict as {"machine name": "human description"}
    attributes = {i.get("src").split("/")[-1].rsplit("-", 1)[0]: i.get("alt") for i in images}

    return attributes
