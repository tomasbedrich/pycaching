#!/usr/bin/env python3

import datetime
import enum
from pycaching import errors
from pycaching.util import parse_date

# prefix _type() function to avoid colisions with log type
_type = type


class Log(object):
    """Represents a log record with its properties."""

    def __init__(self, *, uuid=None, type=None, text=None, visited=None, author=None):
        if uuid is not None:
            self.uuid = uuid
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
    def uuid(self):
        """The log unique identifier.

        :type: :class:`str`
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):
        self._uuid = uuid

    @property
    def type(self):
        """The log type.

        :type: :class:`.log.Type`
        """
        return self._type

    @type.setter
    def type(self, type):
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

    Values are log type IDs (as used in HTML <option value=XX> on the log page).
    Also the log images can be found there - https://www.geocaching.com/images/logtypes/[VALUE].png
    """

    announcement = "74"
    archive = "5"
    attended = "10"
    didnt_find_it = "3"
    discovered_it = "48"
    enable_listing = "23"
    found_it = "2"
    grabbed_it = "19"
    marked_missing = "16"
    needs_archive = "7"
    needs_maintenance = "45"
    note = "4"
    oc_team_comment = "83"  # doesn't have an image
    owner_maintenance = "46"
    placed_it = "14"
    post_reviewer_note = "18"
    publish_listing = "24"
    retract = "25"
    retrieved_it = "13"
    submit_for_review = "76"
    temp_disable_listing = "22"
    unarchive = "12"
    update_coordinates = "47"
    visit = "75"
    webcam_photo_taken = "11"
    will_attend = "9"

    @classmethod
    def from_filename(cls, filename):
        """Return a log type from its image filename."""
        if filename == "1003":
            # 2 different IDs for publish_listing
            return cls.publish_listing
        elif filename == "1001":
            # 2 different IDs for visit
            return cls.visit
        elif filename == "68":
            # 2 different IDs for post_reviewer_note
            return cls.post_reviewer_note

        try:
            return cls(filename)
        except ValueError as e:
            raise errors.ValueError("Unknown log type '{}'.".format(filename)) from e
