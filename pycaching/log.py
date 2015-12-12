#!/usr/bin/env python3

import datetime
import enum
from pycaching import errors
from pycaching.util import parse_date

# prefix _type() function to avoid colisions with log type
_type = type


class Log(object):
    """Represents a log record with its properties."""

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
        """Return log text."""
        return self.text

    @property
    def type(self):
        """The log type.

        :setter: Set a log type. If :class:`str` is passed, then :meth:`.log.Type.from_string`
            is used and its return value is stored as a type.
        :type: :class:`.log.Type`
        """
        return self._type

    @type.setter
    def type(self, type):
        if _type(type) is not Type:
            type = Type.from_string(type)
        self._type = type

    @property
    def text(self):
        """The log text.

        :type: :class:`str`
        """
        return self._text

    @text.setter
    def text(self, text):
        text = str(text).strip()
        self._text = text

    @property
    def visited(self):
        """The log date.

        :setter: Set a log date. If :class:`str` is passed, then :meth:`.util.parse_date`
            is used and its return value is stored as a date.
        :type: :class:`datetime.date`
        """
        return self._visited

    @visited.setter
    def visited(self, visited):
        if _type(visited) is str:
            visited = parse_date(visited)
        elif _type(visited) is not datetime.date:
            raise errors.ValueError(
                "Passed object is not datetime.date instance nor string containing a date.")
        self._visited = visited

    @property
    def author(self):
        """The log author.

        :type: :class:`str`
        """
        return self._author

    @author.setter
    def author(self, author):
        self._author = author.strip()


class Type(enum.Enum):
    """Enum of possible log types.

    Values are human readable log types.
    """

    found_it = "found it"
    didnt_find_it = "didn't find it"
    note = "write note"
    publish_listing = "publish listing"
    enable_listing = "enable listing"
    archive = "archive"
    unarchive = "unarchive"
    temp_disable_listing = "temporarily disable listing"
    needs_archive = "needs archived"
    will_attend = "will attend"
    attended = "attended"
    retrieved_it = "retrieved it"
    placed_it = "placed it"
    grabbed_it = "grabbed it"
    needs_maintenance = "needs maintenance"
    owner_maintenance = "owner maintenance"
    update_coordinates = "update coordinates"
    discovered_it = "discovered it"
    post_reviewer_note = "post reviewer note"
    submit_for_review = "submit for review"
    visit = "visit"
    webcam_photo_taken = "webcam photo taken"
    announcement = "announcement"
    retract = "retract listing"
    marked_missing = "marked missing"
    oc_team_comment = "X1"

    @classmethod
    def from_string(cls, name):
        """Return a log type from its human readable name.

        :raise .ValueError: If log type cannot be determined.
        """
        name = name.strip().lower()

        try:
            return cls(name)
        except ValueError as e:
            raise errors.ValueError("Unknown log type '{}'.".format(name)) from e
