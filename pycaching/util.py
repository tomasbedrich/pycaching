#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from itertools import chain
from datetime import datetime
from pycaching import errors


class Util(object):

    _rot13codeTable = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM")

    _attributes_url = "http://www.geocaching.com/about/icons.aspx"

    @classmethod
    def rot13(cls, text):
        """Returns a text encoded by rot13 cipher."""
        return str.translate(text, cls._rot13codeTable)

    @staticmethod
    def to_decimal(deg, min):
        """Returns a decimal interpretation of coordinate in MinDec format."""
        return round(deg + min / 60, 5)

    @staticmethod
    def to_mindec(decimal):
        """Returns a DecMin interpretation of coordinate in decimal format."""
        return int(decimal), round(60 * (decimal - int(decimal)), 3)

    @staticmethod
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

    @classmethod
    def get_possible_attributes(cls):
        """Returns dict of all possible attributes parsed from Groundspeak's website."""
        try:
            page = BeautifulSoup(requests.get(cls._attributes_url).text)
        except requests.exceptions.ConnectionError as e:
            raise errors.Error("Cannot load attributes page.") from e

        # get all <img>s containing attributes from all <dl>s with specific class
        images = chain(*map(lambda i: i.find_all("img"), page.find_all("dl", "AttributesList")))
        # create dict as {"machine name": "human description"}
        attributes = {i.get("src").split("/")[-1].rsplit("-", 1)[0]: i.get("alt") for i in images}

        return attributes
