#!/usr/bin/env python3

import unittest
from datetime import date
from unittest import mock

from pycaching import Geocaching, Trackable
from pycaching.errors import ValueError as PycachingValueError, LoadError
from pycaching.log import Log, Type as LogType
from . import NetworkedTest


class TestProperties(unittest.TestCase):
    def setUp(self):
        self.gc = Geocaching()
        self.t = Trackable(self.gc, "TB123AB", name="Testing", type="Travel Bug", location="in the hands of human",
                           owner="human", description="long text", goal="short text")
        self.t._log_page_url = "/track/details.aspx?id=6359246"

    def test___str__(self):
        self.assertEqual(str(self.t), "TB123AB")

    def test___eq__(self):
        self.assertEqual(self.t, Trackable(self.gc, "TB123AB"))

    def test_tid(self):
        self.assertEqual(self.t.tid, "TB123AB")

    def test_name(self):
        self.assertEqual(self.t.name, "Testing")

    def test_type(self):
        self.assertEqual(self.t.type, "Travel Bug")

    def test_owner(self):
        self.assertEqual(self.t.owner, "human")

    def test_location(self):
        self.assertEqual(self.t.location, "in the hands of human")

    def test_description(self):
        self.assertEqual(self.t.description, "long text")

    def test_goal(self):
        self.assertEqual(self.t.goal, "short text")

    def test_log_page_url(self):
        self.assertEqual(self.t._log_page_url, "/track/details.aspx?id=6359246")


class TestMethods(NetworkedTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.t = Trackable(cls.gc, "TB1KEZ9")
        with cls.recorder.use_cassette('trackable_setup'):
            cls.t.load()

    def test_load(self):
        with self.subTest("tid"):
            trackable = Trackable(self.gc, "TB1KEZ9")
            with self.recorder.use_cassette('trackable_load_tid'):
                self.assertEqual("Lilagul #2: SwedenHawk Geocoin", trackable.name)

        with self.subTest("trackable url"):
            url = "http://www.geocaching.com/track/details.aspx?guid=cff00ac4-f562-486e-b303-32b2d01ed386"
            trackable = Trackable(self.gc, None, url=url)
            with self.recorder.use_cassette('trackable_load_url'):
                self.assertEqual("Lilagul #2: SwedenHawk Geocoin", trackable.name)

        with self.subTest("fail lazyload"):
            trackable = Trackable(self.gc, None)
            with self.assertRaises(LoadError):
                trackable.name

    def test_load_log_page(self):
        expected_types = {t.value for t in (LogType.grabbed_it, LogType.note, LogType.discovered_it)}
        expected_inputs = "__EVENTTARGET", "__VIEWSTATE"  # and more ...
        expected_date_format = "M/d/yyyy"  # if test is re-recorded, update for your testing account

        # make request
        with self.recorder.use_cassette('trackable_load_page'):
            valid_types, hidden_inputs, user_date_format = self.t._load_log_page()

        self.assertSequenceEqual(expected_types, valid_types)
        for i in expected_inputs:
            self.assertIn(i, hidden_inputs.keys())
        self.assertEqual(expected_date_format, user_date_format)  # failure may be due to account switch

    @mock.patch.object(Trackable, "_load_log_page")
    @mock.patch.object(Geocaching, "_request")
    def test_post_log(self, mock_request, mock_load_log_page):
        # mock _load_log_page
        valid_log_types = {
            # intentionally missing "grabbed it" to test invalid log type
            "4",  # write note
            "48",  # discovered it
        }
        mock_load_log_page.return_value = (valid_log_types, {}, "mm/dd/YYYY")
        test_log_text = "Test log."
        test_log_date = date.today()
        test_tracking_code = "ABCDEF"

        with self.subTest("empty log text"):
            l = Log(text="", visited=test_log_date, type=LogType.note)
            with self.assertRaises(PycachingValueError):
                self.t.post_log(l, test_tracking_code)

        with self.subTest("invalid log type"):
            l = Log(text=test_log_text, visited=test_log_date, type=LogType.grabbed_it)
            with self.assertRaises(PycachingValueError):
                self.t.post_log(l, test_tracking_code)

        with self.subTest("valid log"):
            l = Log(text=test_log_text, visited=test_log_date, type=LogType.discovered_it)
            self.t.post_log(l, test_tracking_code)

            # test call to _request mock
            expected_post_data = {
                "ctl00$ContentBody$LogBookPanel1$btnSubmitLog": "Submit Log Entry",
                "ctl00$ContentBody$LogBookPanel1$ddLogType": "48",  # discovered it - see valid_log_types
                "ctl00$ContentBody$LogBookPanel1$uxDateVisited": test_log_date.strftime("%m/%d/%Y"),
                "ctl00$ContentBody$LogBookPanel1$tbCode": test_tracking_code,
                "ctl00$ContentBody$LogBookPanel1$uxLogInfo": test_log_text,
            }
            mock_request.assert_called_with(self.t._log_page_url, method="POST", data=expected_post_data)

    def test_get_KML(self):
        with self.recorder.use_cassette('trackable_kml'):
            kml = self.t.get_KML()
        self.assertTrue("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" in kml)
        self.assertTrue("<kml xmlns=\"http://earth.google.com/kml/2.2\">" in kml)
        self.assertTrue("#tbTravelStyle" in kml)
        self.assertTrue("<visibility>1</visibility>" in kml)
        self.assertTrue("</Placemark></Document></kml>" in kml)
