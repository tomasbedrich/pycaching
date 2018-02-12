#!/usr/bin/env python3
import unittest
from datetime import date
from unittest import mock

from pycaching.cache import Cache, Type, Size, Waypoint
from pycaching.errors import ValueError as PycachingValueError, LoadError, PMOnlyException
from pycaching.geo import Point
from pycaching.geocaching import Geocaching
from pycaching.log import Log, Type as LogType
from pycaching.util import parse_date
from . import recorder, NetworkedTest


class TestProperties(unittest.TestCase):
    def setUp(self):
        self.gc = Geocaching()
        self.c = Cache(self.gc, "GC12345", name="Testing", type=Type.traditional, location=Point(), state=True,
                       found=False, size=Size.micro, difficulty=1.5, terrain=5, author="human", hidden=date(2000, 1, 1),
                       attributes={"onehour": True, "kids": False, "available": True}, summary="text",
                       description="long text", hint="rot13", favorites=0, pm_only=False,
                       original_location=Point(), waypoints={}, guid="53d34c4d-12b5-4771-86d3-89318f71efb1")

    def test___str__(self):
        self.assertEqual(str(self.c), "GC12345")

    def test___eq__(self):
        self.assertEqual(self.c, Cache(self.gc, "GC12345"))

    def test_geocaching(self):
        with self.assertRaises(PycachingValueError):
            Cache(None, "GC12345")

    def test_wp(self):
        self.assertEqual(self.c.wp, "GC12345")

        with self.subTest("filter invalid"):
            with self.assertRaises(PycachingValueError):
                self.c.wp = "xxx"

    def test_guid(self):
        self.assertEqual(self.c.guid, "53d34c4d-12b5-4771-86d3-89318f71efb1")

        with self.subTest("filter invalid"):
            with self.assertRaises(PycachingValueError):
                self.c.guid = "123"

    def test_name(self):
        self.assertEqual(self.c.name, "Testing")

    def test_type(self):
        self.assertEqual(self.c.type, Type.traditional)

        with self.subTest("filter invalid"):
            with self.assertRaises(PycachingValueError):
                self.c.type = "xxx"

    def test_location(self):
        self.assertEqual(self.c.location, Point())

        with self.subTest("automatic str conversion"):
            self.c.location = "S 36 51.918 E 174 46.725"
            self.assertEqual(self.c.location, Point.from_string("S 36 51.918 E 174 46.725"))

        with self.subTest("filter invalid string"):
            with self.assertRaises(PycachingValueError):
                self.c.location = "somewhere"

        with self.subTest("filter invalid types"):
            with self.assertRaises(PycachingValueError):
                self.c.location = None

    def test_original_location(self):
        self.assertEqual(self.c.original_location, Point())

        with self.subTest("automatic str conversion"):
            self.c.original_location = "S 36 51.918 E 174 46.725"
            self.assertEqual(self.c.original_location,
                             Point.from_string("S 36 51.918 E 174 46.725"))

        with self.subTest("None type"):
            self.c.original_location = None

        with self.subTest("filter invalid string"):
            with self.assertRaises(PycachingValueError):
                self.c.original_location = "somewhere"

        with self.subTest("filter invalid types"):
            with self.assertRaises(PycachingValueError):
                self.c.original_location = 123

    def test_waypoints(self):
        self.assertEqual(type(self.c.waypoints), type({}))

    def test_state(self):
        self.assertEqual(self.c.state, True)

    def test_found(self):
        self.assertEqual(self.c.found, False)

    def test_size(self):
        self.assertEqual(self.c.size, Size.micro)

        with self.subTest("filter invalid"):
            with self.assertRaises(PycachingValueError):
                self.c.size = "xxx"

    def test_difficulty(self):
        self.assertEqual(self.c.difficulty, 1.5)

        with self.subTest("filter invalid"):
            with self.assertRaises(PycachingValueError):
                self.c.difficulty = 10

    def test_terrain(self):
        self.assertEqual(self.c.terrain, 5)

        with self.subTest("filter invalid"):
            with self.assertRaises(PycachingValueError):
                self.c.terrain = -1

    def test_author(self):
        self.assertEqual(self.c.author, "human")

    def test_hidden(self):
        self.assertEqual(self.c.hidden, date(2000, 1, 1))

        with self.subTest("automatic str conversion"):
            self.c.hidden = "1/30/2000"
            self.assertEqual(self.c.hidden, date(2000, 1, 30))

        with self.subTest("filter invalid string"):
            with self.assertRaises(PycachingValueError):
                self.c.hidden = "now"

        with self.subTest("filter invalid types"):
            with self.assertRaises(PycachingValueError):
                self.c.hidden = None

    def test_attributes(self):
        self.assertEqual(self.c.attributes, {"onehour": True, "kids": False, "available": True})

        with self.subTest("filter unknown"):
            self.c.attributes = {attr: True for attr in ["onehour", "xxx"]}
            self.assertEqual(self.c.attributes, {"onehour": True})

        with self.subTest("filter invalid"):
            with self.assertRaises(PycachingValueError):
                self.c.attributes = None

    def test_summary(self):
        self.assertEqual(self.c.summary, "text")

    def test_description(self):
        self.assertEqual(self.c.description, "long text")

    def test_hint(self):
        self.assertEqual(self.c.hint, "rot13")

    def test_favorites(self):
        self.assertEqual(self.c.favorites, 0)

    def test_pm_only(self):
        self.assertEqual(self.c.pm_only, False)


class TestMethods(NetworkedTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.c = Cache(cls.gc, "GC1PAR2")
        with recorder.use_cassette('cache_setup'):
            cls.c.load()

    def test_load(self):
        with self.subTest("normal (with explicit call of load())"):
            with recorder.use_cassette('cache_explicit_load'):
                cache = Cache(self.gc, "GC4808G")
                cache.load()
            self.assertEqual("Nekonecne ticho", cache.name)

        with self.subTest("normal"):
            with recorder.use_cassette('cache_normal_normal'):
                cache = Cache(self.gc, "GC4808G")
                self.assertEqual("Nekonecne ticho", cache.name)

        with self.subTest("non-ascii chars"):
            with recorder.use_cassette('cache_non-ascii'):
                cache = Cache(self.gc, "GC5VJ0P")
                self.assertEqual("budka u paty stromu nedaleko tancící borovice", cache.hint)

        with self.subTest("PM only"):
            with recorder.use_cassette('cache_PMO'):
                with self.assertRaises(PMOnlyException):
                    cache = Cache(self.gc, "GC3AHDM")
                    cache.load()

        with self.subTest("fail"):
            with recorder.use_cassette('cache_normal_fail'):
                with self.assertRaises(LoadError):
                    cache = Cache(self.gc, "GC123456")
                    cache.load()

    def test_load_quick(self):
        with self.subTest("normal"):
            with recorder.use_cassette('cache_quick_normal'):
                cache = Cache(self.gc, "GC4808G")
                cache.load_quick()
            self.assertEqual(4, cache.terrain)
            self.assertEqual(Size.regular, cache.size)
            self.assertEqual(cache.guid, "15ad3a3d-92c1-4f7c-b273-60937bcc2072")

        with self.subTest("fail"):
            with recorder.use_cassette('cache_quickload_fail'):
                with self.assertRaises(LoadError):
                    cache = Cache(self.gc, "GC123456")
                    cache.load_quick()

    @mock.patch("pycaching.Cache.load")
    @mock.patch("pycaching.Cache.load_quick")
    def test_load_by_guid(self, mock_load_quick, mock_load):
        with self.subTest("normal"):
            cache = Cache(self.gc, "GC2WXPN", guid="5f45114d-1d79-4fdb-93ae-8f49f1d27188")
            with recorder.use_cassette('cache_guidload_normal'):
                cache.load_by_guid()
            self.assertEqual(cache.name, "Der Schatz vom Luftschloss")
            self.assertEqual(cache.location, Point("N 49° 57.895' E 008° 12.988'"))
            self.assertEqual(cache.type, Type.mystery)
            self.assertEqual(cache.size, Size.large)
            self.assertEqual(cache.difficulty, 2.5)
            self.assertEqual(cache.terrain, 1.5)
            self.assertEqual(cache.author, "engelmz & Punxsutawney Phil")
            self.assertEqual(cache.hidden, parse_date("23/06/2011"))
            self.assertDictEqual(cache.attributes, {
                "bicycles": True,
                "available": True,
                "parking": True,
                "onehour": True,
                "kids": True,
                "s-tool": True,
            })
            self.assertEqual(cache.summary, "Gibt es das Luftschloss wirklich?")
            self.assertIn("Seit dem 16.", cache.description)
            self.assertEqual(cache.hint, "Das ist nicht nötig")
            self.assertGreater(cache.favorites, 350)
            self.assertEqual(len(cache.waypoints), 2)

        with self.subTest("PM-only"):
            cache = Cache(self.gc, "GC6MKEF", guid="53d34c4d-12b5-4771-86d3-89318f71efb1")
            with recorder.use_cassette('cache_guidload_PMO'):
                with self.assertRaises(PMOnlyException):
                    cache.load_by_guid()

        with self.subTest("calls load_quick if no guid"):
            cache = Cache(self.gc, "GC2WXPN")
            with recorder.use_cassette('cache_guidload_fallback'):
                with self.assertRaises(Exception):
                    cache.load_by_guid()  # Raises error since we mocked load_quick()
            self.assertTrue(mock_load_quick.called)

    def test_load_trackables(self):
        cache = Cache(self.gc, "GC26737")  # TB graveyard - will surelly have some trackables
        with recorder.use_cassette('cache_trackables'):
            trackable_list = list(cache.load_trackables(limit=10))
        self.assertTrue(isinstance(trackable_list, list))

    def test_load_logbook(self):
        with recorder.use_cassette('cache_logbook'):
            # limit over 100 tests pagination
            log_authors = list(map(lambda log: log.author, self.c.load_logbook(limit=200)))
        for expected_author in ["Dudny-1995", "Sopdet Reviewer", "donovanstangiano83"]:
            self.assertIn(expected_author, log_authors)

    def test_load_log_page(self):
        expected_types = {t.value for t in (LogType.found_it, LogType.didnt_find_it, LogType.note)}

        with recorder.use_cassette('cache_logpage'):
            # make request
            valid_types, hidden_inputs = self.c._load_log_page()

        self.assertSequenceEqual(expected_types, valid_types)
        self.assertIn("__RequestVerificationToken", hidden_inputs.keys())

    @mock.patch.object(Cache, "_load_log_page")
    @mock.patch.object(Geocaching, "_request")
    def test_post_log(self, mock_request, mock_load_log_page):
        # mock _load_log_page
        valid_log_types = {
            # intentionally missing "found it" to test invalid log type
            "4",  # write note
            "3",  # didn't find it
        }
        mock_load_log_page.return_value = (valid_log_types, {})
        test_log_text = "Test log."

        with self.subTest("empty log text"):
            l = Log(text="", visited=date.today(), type=LogType.note)
            with self.assertRaises(PycachingValueError):
                self.c.post_log(l)

        with self.subTest("invalid log type"):
            l = Log(text=test_log_text, visited=date.today(), type=LogType.found_it)
            with self.assertRaises(PycachingValueError):
                self.c.post_log(l)

        with self.subTest("valid log"):
            l = Log(text=test_log_text, visited=date.today(), type=LogType.didnt_find_it)
            self.c.post_log(l)

            # test call to _request mock
            expected_post_data = {
                "LogTypeId": "3",  # DNF - see valid_log_types
                "LogDate": date.today().strftime("%Y-%m-%d"),
                "LogText": test_log_text,
            }
            mock_request.assert_called_with(self.c._get_log_page_url(), method="POST", data=expected_post_data)


class TestWaypointProperties(unittest.TestCase):
    def setUp(self):
        self.w = Waypoint("id", "Parking", Point("N 56° 50.006′ E 13° 56.423′"),
                          "This is a test")

    def test_id(self):
        with self.subTest("init"):
            self.assertEqual(self.w.identifier, "id")
        with self.subTest("setter"):
            self.w.identifier = "New id"
            self.assertEqual(self.w.identifier, "New id")

    def test_type(self):
        with self.subTest("init"):
            self.assertEqual(self.w.type, "Parking")
        with self.subTest("setter"):
            self.w.type = "Physical step"
            self.assertEqual(self.w.type, "Physical step")

    def test_location(self):
        with self.subTest("init"):
            self.assertEqual(self.w.location, Point("N 56° 50.006′ E 13° 56.423′"))
        with self.subTest("automatic str conversion"):
            self.w.location = "S 36 51.918 E 174 46.725"
            self.assertEqual(self.w.location, Point.from_string("S 36 51.918 E 174 46.725"))

        with self.subTest("filter invalid string"):
            with self.assertRaises(PycachingValueError):
                self.w.location = "somewhere"

        with self.subTest("filter invalid types"):
            with self.assertRaises(PycachingValueError):
                self.w.location = None

    def test_note(self):
        with self.subTest("init"):
            self.assertEqual(self.w.note, "This is a test")

        with self.subTest("Setter test"):
            self.w.note = "This is another test"
            self.assertEqual(self.w.note, "This is another test")

    def test_str(self):
        self.assertEqual(str(self.w), "id")
