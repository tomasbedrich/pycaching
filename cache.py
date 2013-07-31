# -*- encoding: utf-8 -*-

import logging
import unittest
import geopy as geo
from types import *
import datetime


class Cache(object):

    attributesMap = {
        "dog": (1, "Dogs"),
        "dogs": (1, "Dogs allowed"),
        "fee": (2, "Access or parking fee"),
        "rappelling": (3, "Climbing gear"),
        "boat": (4, "Boat"),
        "scuba": (5, "Scuba gear"),
        "kids": (6, "Recommended for kids"),
        "onehour": (7, "Takes less than an hour"),
        "scenic": (8, "Scenic view"),
        "hiking": (9, "Significant hike"),
        "climbing": (10, "Difficult climbing"),
        "wading": (11, "May require wading"),
        "swimming": (12, "May require swimming"),
        "available": (13, "Available at all times"),
        "night": (14, "Recommended at night"),
        "winter": (15, "Available during winter"),
        "poisonoak": (17, "Poison plants"),
        "snakes": (18, "Snakes"),
        "ticks": (19, "Ticks"),
        "mines": (20, "Abandoned mines"),
        "cliff": (21, "Cliff / falling rocks"),
        "hunting": (22, "Hunting"),
        "danger": (23, "Dangerous area"),
        "wheelchair": (24, "Wheelchair accessible"),
        "parking": (25, "Parking available"),
        "public": (26, "Public transportation"),
        "water": (27, "Drinking water nearby"),
        "restrooms": (28, "Public restrooms nearby"),
        "phone": (29, "Telephone nearby"),
        "picnic": (30, "Picnic tables nearby"),
        "camping": (31, "Camping available"),
        "bicycles": (32, "Bicycles"),
        "motorcycles": (33, "Motorcycles"),
        "quads": (34, "Quads"),
        "jeeps": (35, "Off-road vehicles"),
        "snowmobiles": (36, "Snowmobiles"),
        "horses": (37, "Horses"),
        "campfires": (38, "Campfires"),
        "thorns": (39, "Thorns"),
        "thorn": (39, "Thorns!"),
        "stealth": (40, "Stealth required"),
        "stroller": (41, "Stroller accessible"),
        "firstaid": (42, "Needs maintenance"),
        "cow": (43, "Watch for livestock"),
        "flashlight": (44, "Flashlight required"),
        "landf": (45, "Lost And Found Tour")
        }

    typeMap = {
        "traditional": "2",
        "multicache": "3",
        "ape": "ape_32",
        "mystery": "8",
        "letterbox": "5",
        "whereigo": "1858",
        "event": "6",
        "megaevent": "mega",
        "cito": "13",
        "earthcache": "earthcache",
        "adventuremaze": "1304",
        "virtual": "4",
        "webcam": "11",
        "10years": "10Years_32",
        "locationless": "12",
        }

    sizeMap = [
        "micro",
        "small",
        "regular",
        "large",
        "not chosen",
        "other",
        "virtual",
        ]

    def __init__(self, wp, location=None, cacheType=None, state=None, size=None,
        difficulty=None, terrain=None, author=None, hidden=None, attributes=None,
        summary=None, description=None, hint=None):
        self.wp = wp
        self.location = location
        self.cacheType = cacheType
        self.state = state
        self.size = size
        self.difficulty = difficulty
        self.terrain = terrain
        self.author = author
        self.hidden = hidden
        self.attributes = attributes
        self.summary = summary
        self.description = description
        self.hint = hint


    def load(self):
        """Loads details from cache page."""
        pass

    
    @property
    def wp(self):
        return self._wp

    @wp.setter
    def wp(self, wp):
        if isinstance(wp, StringTypes) and wp.strip()[:2] == "GC":
            self._wp = wp

    
    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        if isinstance(location, geo.Point):
            self._location = location


    @property
    def cacheType(self):
        return self._cacheType

    @cacheType.setter
    def cacheType(self, cacheType):
        if cacheType in self.typeMap.keys():
            self._cacheType = cacheType


    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if type(state) is BooleanType:
            self._state = state


    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        if size in self.sizeMap:
            self._size = size


    @property
    def difficulty(self):
        return self._difficulty

    @difficulty.setter
    def difficulty(self, difficulty):
        if isinstance(difficulty, (int, float)) and \
            difficulty >= 1 and difficulty <= 5 and \
            difficulty * 10 % 5 == 0:
            self._difficulty = difficulty


    @property
    def terrain(self):
        return self._terrain

    @terrain.setter
    def terrain(self, terrain):
        if isinstance(terrain, (int, float)) and \
            terrain >= 1 and terrain <= 5 and \
            terrain * 10 % 5 == 0:
            self._terrain = terrain


    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, author):
        self._author = author


    @property
    def hidden(self):
        return self._hidden

    @hidden.setter
    def hidden(self, hidden):
        if type(hidden) is datetime.date: # test!!!
            self._hidden = hidden


    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        if type(attributes) is ListType:
            self._attributes = filter(lambda attr: attr in Cache.attributesMap, attributes)


    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        if isinstance(summary, StringTypes):
            self._summary = summary


    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        if isinstance(description, StringTypes):
            self._description = description


    @property
    def hint(self):
        return self._hint

    @hint.setter
    def hint(self, hint):
        if isinstance(hint, StringTypes):
            self.hint = hint


        
class TestUtil(unittest.TestCase):

    def setUp(self):
        self.c = Cache("GC12345")

    def test_wp(self):
        self.assertEquals( self.c.wp, "GC12345" )

    def test_difficulty(self):
        self.c.difficulty = 1.5
        self.assertEquals( self.c.difficulty, 1.5 )


def main():
    """The main program"""

    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)
    unittest.main()


if __name__ == "__main__":
    main()