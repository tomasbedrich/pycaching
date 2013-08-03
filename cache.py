# -*- encoding: utf-8 -*-

import logging
import unittest
import datetime
import geopy as geo
from types import *


class Cache(object):

    attributesMap = {
        "dog": "Dogs",
        "dogs": "Dogs allowed",
        "fee": "Access or parking fee",
        "rappelling": "Climbing gear",
        "boat": "Boat",
        "scuba": "Scuba gear",
        "kids": "Recommended for kids",
        "onehour": "Takes less than an hour",
        "scenic": "Scenic view",
        "hike_med": "Hike between 1km - 10km",
        "hiking": "Significant hike",
        "climbing": "Difficult climbing",
        "wading": "May require wading",
        "swimming": "May require swimming",
        "available": "Available at all times",
        "night": "Recommended at night",
        "winter": "Available during winter",
        "poisonoak": "Poison plants",
        "snakes": "Snakes",
        "ticks": "Ticks",
        "mines": "Abandoned mines",
        "cliff": "Cliff / falling rocks",
        "hunting": "Hunting",
        "danger": "Dangerous area",
        "wheelchair": "Wheelchair accessible",
        "parkngrab": "Park and grab",
        "parking": "Parking available",
        "public": "Public transportation",
        "water": "Drinking water nearby",
        "restrooms": "Public restrooms nearby",
        "phone": "Telephone nearby",
        "picnic": "Picnic tables nearby",
        "camping": "Camping available",
        "bicycles": "Bicycles",
        "motorcycles": "Motorcycles",
        "quads": "Quads",
        "jeeps": "Off-road vehicles",
        "snowmobiles": "Snowmobiles",
        "horses": "Horses",
        "campfires": "Campfires",
        "thorns": "Thorns",
        "thorn": "Thorns!",
        "stealth": "Stealth required",
        "stroller": "Stroller accessible",
        "firstaid": "Needs maintenance",
        "cow": "Watch for livestock",
        "flashlight": "Flashlight required",
        "landf": "Lost And Found Tour",
        }

    typeMap = [
        "Traditional Cache",
        "Multi-cache",
        "Unknown Cache",
        "Project APE Cache",
        "Letterbox Hybrid",
        "Wherigo Cache",
        "Event Cache",
        "Mega-Event Cache",
        "Cache In Trash Out Event",
        "Earthcache",
        "GPS Adventures Exhibit",
        "Virtual Cache",
        "Webcam Cache",
        "Lost and Found Event Cache",
        "Locationless (Reverse) Cache",
        ]

    sizeMap = [
        "micro",
        "small",
        "regular",
        "large",
        "not chosen",
        "other",
        "virtual",
        ]

    def __init__(self, wp, name=None, cacheType=None, location=None, state=None,
        found=None, size=None, difficulty=None, terrain=None, author=None, hidden=None,
        attributes=None, summary=None, description=None, hint=None):
        self.wp = wp
        self.name = name
        self.cacheType = cacheType
        self.location = location
        self.state = state
        self.found = found
        self.size = size
        self.difficulty = difficulty
        self.terrain = terrain
        self.author = author
        self.hidden = hidden
        self.attributes = attributes
        self.summary = summary
        self.description = description
        self.hint = hint

    
    @property
    def wp(self):
        return self._wp

    @wp.setter
    def wp(self, wp):
        if isinstance(wp, StringTypes) and wp.startswith("GC"):
            self._wp = wp
        elif wp:
            logging.warning("Invalid WP '%s', ignoring.", wp)

    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if isinstance(name, StringTypes):
            self._name = name

    
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
        if cacheType in self.typeMap:
            self._cacheType = cacheType
        elif cacheType:
            logging.warning("Invalid cache type '%s', ignoring.", cacheType)


    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if type(state) is BooleanType:
            self._state = state
        elif state:
            logging.warning("Invalid state '%s', ignoring.", state)


    @property
    def found(self):
        return self._found

    @found.setter
    def found(self, found):
        if type(found) is BooleanType:
            self._found = found
        elif found:
            logging.warning("Invalid found state, ignoring.")


    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        if size in self.sizeMap:
            self._size = size
        elif size:
            logging.warning("Invalid size '%s', ignoring.", size)


    @property
    def difficulty(self):
        return self._difficulty

    @difficulty.setter
    def difficulty(self, difficulty):
        if isinstance(difficulty, (int, float)) and \
            difficulty >= 1 and difficulty <= 5 and \
            difficulty * 10 % 5 == 0:
            self._difficulty = difficulty
        elif difficulty:
            logging.warning("Invalid difficulty, ignoring.")


    @property
    def terrain(self):
        return self._terrain

    @terrain.setter
    def terrain(self, terrain):
        if isinstance(terrain, (int, float)) and \
            terrain >= 1 and terrain <= 5 and \
            terrain * 10 % 5 == 0:
            self._terrain = terrain
        elif terrain:
            logging.warning("Invalid terrain, ignoring.")


    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, author):
        if isinstance(author, StringTypes):
            self._author = author


    @property
    def hidden(self):
        return self._hidden

    @hidden.setter
    def hidden(self, hidden):
        if type(hidden) is datetime.date:
            self._hidden = hidden
        elif hidden:
            logging.warning("Invalid hidden date, ignoring.")


    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        if type(attributes) is ListType: # convert to dict
            attributes = {a: True for a in attributes}

        if type(attributes) is DictType:
            self._attributes = {}
            for name, allowed in attributes.iteritems():
                if name in self.attributesMap:
                    self._attributes[name] = allowed
                else:
                    logging.warning("Unknown attribute '%s', ignoring.", name)
        elif attributes:
            logging.warning("Invalid attributes format (%s), ignoring.", type(attributes))


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
            self._hint = hint


    def __str__(self):
        return self.wp


        
class TestUtil(unittest.TestCase):

    def setUp(self):
        self.c = Cache("GC12345")

    def test_wp(self):
        self.assertEquals( self.c.wp, "GC12345" )

    def test_difficulty(self):
        self.c.difficulty = 1.5
        self.assertEquals( self.c.difficulty, 1.5 )

    def test_type(self):
        self.c.cacheType = "Traditional Cache"
        self.assertEquals( self.c.cacheType, "Traditional Cache" )
        # filter invalid
        self.c.cacheType = "xxx"
        self.assertEquals( self.c.cacheType, "Traditional Cache" )

    def test_description(self):
        self.c.description = "test"
        self.assertEquals( self.c.description, "test" )

    def test_attributes(self):
        self.c.attributes = ["onehour", "kids", "available"]
        self.assertEquals( self.c.attributes, {"onehour":1, "kids":1, "available":1} )
        # filter unknown
        self.c.attributes = ["onehour", "xxx"]
        self.assertEquals( self.c.attributes, {"onehour":1} )


def main():
    """The main program"""

    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)
    unittest.main()


if __name__ == "__main__":
    main()