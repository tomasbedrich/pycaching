#!/usr/bin/env python3

import datetime
from pycaching.errors import ValueError
from pycaching.enums import LogType as Type
from pycaching.util import parse_date

# prefix _type() function to avoid colisions with log type
_type = type


class Log(object):

    def __init__(self, *, type=None, text=None, visited=None, author=None):
        if type is not None:
            self.type = type
        if text is not None:
            self.text = text
        if visited is not None:
            self.visited = visited
        if author is not None:
            self.author = author

    def __str__(self):
        return self.text

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        if _type(type) is not Type:
            type = Type.from_string(type)
        self._type = type

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        text = str(text).strip()
        self._text = text

    @property
    def visited(self):
        return self._visited

    @visited.setter
    def visited(self, visited):
        if _type(visited) is str:
            visited = parse_date(visited)
        elif _type(visited) is not datetime.date:
            raise ValueError("Passed object is not datetime.date instance nor string containing a date.")
        self._visited = visited

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, author):
        self._author = author.strip()
