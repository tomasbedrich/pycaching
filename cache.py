# -*- encoding: utf-8 -*-

import unittest
import geopy as geo


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

    def __init__(self, wp, location=None, type=None, state=None, size=None,
        difficulty=None, terrain=None, author=None, hidden=None, summary=None,
        description=None, hint=None, attributes=None):
        pass

    def load(self):
        """Loads cache details from cache page."""
        pass